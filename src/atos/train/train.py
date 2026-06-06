import argparse
import torch
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
)
from atos.taxonomy import load_taxonomy, bioes_labels, label_maps
from atos.train.data import load_jsonl
from atos.train.features import encode_example
from atos.train.model import build_model, apply_lora


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.train.train",
        description="Fine-tune BERTimbau (LoRA) as a BIOES speech-act token classifier.",
    )
    p.add_argument("--train", required=True, help="training JSONL")
    p.add_argument("--out", required=True, help="output dir for the adapter/model")
    p.add_argument("--model", default="neuralmind/bert-base-portuguese-cased")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--epochs", type=float, default=5.0)
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--grad-accum", type=int, default=1,
                   help="gradient accumulation steps (raise effective batch on small VRAM)")
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--fp16", action="store_true",
                   help="mixed-precision fp16 (use on Turing GPUs e.g. RTX 2070; NOT bf16)")
    p.add_argument("--class-weights", action="store_true",
                   help="inverse-frequency (sklearn 'balanced') class weights in the loss — "
                        "counters act imbalance so rare acts aren't collapsed to the majority")
    p.add_argument("--cpu", action="store_true", help="force CPU (smoke/debug)")
    return p


class _Dataset(torch.utils.data.Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


def compute_class_weights(rows, num_labels, device):
    """sklearn 'balanced' weights over BIOES labels: total / (num_labels * count).
    Zero-count labels get weight 1.0 (neutral). Counters the act imbalance in the loss."""
    import collections
    counts = collections.Counter()
    for r in rows:
        for lab in r["labels"]:
            if lab != -100:
                counts[lab] += 1
    total = sum(counts.values())
    weights = torch.ones(num_labels, dtype=torch.float)
    for i in range(num_labels):
        c = counts.get(i, 0)
        if c > 0:
            weights[i] = total / (num_labels * c)
    return weights.to(device)


class WeightedTrainer(Trainer):
    """Trainer with a class-weighted token-classification loss (ignore_index=-100)."""

    def __init__(self, *a, class_weights=None, **kw):
        super().__init__(*a, **kw)
        self._cw = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(weight=self._cw, ignore_index=-100)
        loss = loss_fct(logits.view(-1, logits.size(-1)), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    taxonomy = load_taxonomy(args.taxonomy)
    label2id, _ = label_maps(bioes_labels(taxonomy.acts))

    model, tokenizer = build_model(args.model, taxonomy)
    # pitfall: move base model to device BEFORE LoRA wrapping
    device = "cpu" if args.cpu else ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model = apply_lora(model)

    anns = load_jsonl(args.train)
    rows = [
        encode_example(a.text, a.spans, tokenizer, label2id, args.max_length)
        for a in anns
    ]
    dataset = _Dataset(rows)
    collator = DataCollatorForTokenClassification(tokenizer)

    targs = TrainingArguments(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        logging_steps=10,
        save_strategy="no",
        report_to=[],
        fp16=args.fp16,
        use_cpu=args.cpu,
    )
    common = dict(
        model=model,
        args=targs,
        train_dataset=dataset,
        data_collator=collator,
        processing_class=tokenizer,
    )
    if args.class_weights:
        weights = compute_class_weights(rows, len(label2id), device)
        trainer = WeightedTrainer(**common, class_weights=weights)
    else:
        trainer = Trainer(**common)
    trainer.train()
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
