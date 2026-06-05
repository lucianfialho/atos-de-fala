from typing import Dict, List

IGNORE_INDEX = -100


def align_labels(
    tags: List[str], special_mask: List[int], label2id: Dict[str, int]
) -> List[int]:
    """Map BIOES tags to label ids; special tokens (mask==1) get IGNORE_INDEX (-100)."""
    return [
        IGNORE_INDEX if special_mask[i] else label2id[tags[i]]
        for i in range(len(tags))
    ]


def encode_example(text, spans, tokenizer, label2id, max_length: int = 256) -> Dict:
    """Tokenize text and produce input_ids/attention_mask/labels for token-cls training.

    Requires a *fast* tokenizer (offset mapping). Uses chomsky.bioes.char_spans_to_bioes
    to derive per-token BIOES tags, then align_labels to map them to ids with -100 on
    special tokens.
    """
    from chomsky.bioes import char_spans_to_bioes

    enc = tokenizer(
        text,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
        truncation=True,
        max_length=max_length,
    )
    tags = char_spans_to_bioes(spans, enc["offset_mapping"])
    labels = align_labels(tags, enc["special_tokens_mask"], label2id)
    return {
        "input_ids": enc["input_ids"],
        "attention_mask": enc["attention_mask"],
        "labels": labels,
    }
