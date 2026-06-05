---
type: concept
tags: [lora, peft, fine-tuning, debugging, pitfalls]
sources: 1
updated: 2026-05-06
---

# LoRA Fine-tuning Pitfalls (PEFT)

## Definition

Practical issues encountered when fine-tuning Privacy Filter with LoRA via the HuggingFace PEFT library. Documented from real debugging during the Privacy Filter BR project.

## Pitfalls Discovered

### 1. PEFT doesn't propagate `.cuda()` to base model

```python
# WRONG — model stays on CPU
model = AutoModelForTokenClassification.from_pretrained(...)
model = get_peft_model(model, lora_config)
model = model.cuda()  # doesn't reach base model embeddings

# RIGHT — move BEFORE wrapping
model = AutoModelForTokenClassification.from_pretrained(...).cuda()
model = get_peft_model(model, lora_config)
```

### 2. New head needs explicit dtype

When using `ignore_mismatched_sizes=True` to replace the classifier head, the new head is initialized in float32. If the base model is bf16, the dtype mismatch causes NaN logits in the forward pass.

```python
# Force fp32 to match the new head
model = AutoModelForTokenClassification.from_pretrained(
    ...,
    ignore_mismatched_sizes=True,
    dtype=torch.float32,  # critical
)
```

### 3. `modules_to_save` requires exact layer name

PEFT expects the EXACT module name. For Privacy Filter the head is called `score`, not `classifier`:

```python
lora_config = LoraConfig(
    ...
    modules_to_save=['score'],  # not 'classifier'!
)
```

To find the right name: print model and look for the final linear layer.

### 4. torchao version conflict

PEFT requires `torchao >= 0.16.0`. Default Colab has 0.10.0. Manual upgrade required:

```bash
pip install --upgrade torchao
```

### 5. Sanity check forward pass before training

Always run a sanity check after loading:

```python
model.eval()
with torch.no_grad():
    test_input = torch.randint(0, 100, (1, 10)).cuda()
    out = model(input_ids=test_input)
    assert not torch.isnan(out.logits).any(), "NaN in logits — fix before training"
```

If this fails, no point starting training.

## How LoRA Was Configured (Working)

```python
lora_config = LoraConfig(
    task_type=TaskType.TOKEN_CLS,
    r=16,                                # rank — capacity vs size tradeoff
    lora_alpha=32,                       # scale factor
    lora_dropout=0.1,
    target_modules=['q_proj', 'v_proj'], # attention projections
    modules_to_save=['score'],           # train new head fully
)
```

Result: 328k trainable / 1.4B total = 0.02% — extremely parameter-efficient.

## Related Concepts

- [Fine-tuning Efficiency](fine-tuning-efficiency.md)
- [Token Classification](token-classification.md)
- [Mixed Precision Training](mixed-precision-training.md)

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
