import argparse
import torch
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
)
from chomsky.taxonomy import load_taxonomy, bioes_labels, label_maps
from chomsky.train.data import load_jsonl
from chomsky.train.features import encode_example
from chomsky.train.model import build_model, apply_lora


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chomsky.train.train",
        description="Fine-tune BERTimbau (LoRA) as a BIOES speech-act token classifier.",
    )
    p.add_argument("--train", required=True, help="training JSONL")
    p.add_argument("--out", required=True, help="output dir for the adapter/model")
    p.add_argument("--model", default="neuralmind/bert-base-portuguese-cased")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--epochs", type=float, default=5.0)
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--cpu", action="store_true", help="force CPU (smoke/debug)")
    return p


class _Dataset(torch.utils.data.Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


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
        learning_rate=args.lr,
        logging_steps=10,
        save_strategy="no",
        report_to=[],
        use_cpu=args.cpu,
    )
    trainer = Trainer(
        model=model,
        args=targs,
        train_dataset=dataset,
        data_collator=collator,
        processing_class=tokenizer,
    )
    trainer.train()
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
