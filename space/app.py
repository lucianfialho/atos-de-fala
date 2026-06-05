"""Hugging Face Space — chomsky speech-act classifier (PT-BR).

Self-contained: loads BERTimbau + the bundled LoRA adapter, tags speech-act spans,
shows them highlighted. Gradio is imported only in __main__ so `predict` is importable
for a quick non-UI test (e.g. on the training box).
"""
import json
import os
import torch
import yaml
from transformers import AutoModelForTokenClassification, AutoTokenizer
from peft import PeftModel

ADAPTER_DIR = os.path.join(os.path.dirname(__file__), "adapter")
TAXONOMY = os.path.join(os.path.dirname(__file__), "taxonomy.yaml")


def _acts():
    with open(TAXONOMY, encoding="utf-8") as f:
        return [a["name"] for a in yaml.safe_load(f)["acts"]]


def _labels(acts):
    out = ["O"]
    for a in acts:
        out += [f"B-{a}", f"I-{a}", f"E-{a}", f"S-{a}"]
    return out


ACTS = _acts()
LABELS = _labels(ACTS)
ID2LABEL = {i: l for i, l in enumerate(LABELS)}
LABEL2ID = {l: i for i, l in enumerate(LABELS)}


def _load_model():
    base_name = json.load(open(os.path.join(ADAPTER_DIR, "adapter_config.json")))["base_model_name_or_path"]
    base = AutoModelForTokenClassification.from_pretrained(
        base_name, num_labels=len(LABELS), id2label=ID2LABEL, label2id=LABEL2ID
    )
    model = PeftModel.from_pretrained(base, ADAPTER_DIR)
    model.eval()
    tok = AutoTokenizer.from_pretrained(ADAPTER_DIR, use_fast=True)
    return model, tok


MODEL, TOK = _load_model()


def _decode(offsets, tags):
    spans, start, end, act = [], None, 0, None

    def close():
        nonlocal start, act
        if start is not None and act is not None:
            spans.append((start, end, act))
        start, act = None, None

    for (s, e), tag in zip(offsets, tags):
        if s == e:
            close(); continue
        if tag == "O":
            close(); continue
        prefix, _, a = tag.partition("-")
        if prefix == "S":
            close(); spans.append((s, e, a))
        elif prefix == "B":
            close(); start, end, act = s, e, a
        elif prefix == "I":
            if act == a:
                end = e
            else:
                close(); start, end, act = s, e, a
        elif prefix == "E":
            if act == a:
                end = e; close()
            else:
                close(); spans.append((s, e, a))
    close()
    return spans


def predict(text):
    """Return Gradio HighlightedText tuples: [(substring, act|None), ...] covering text."""
    if not text or not text.strip():
        return [(text or "", None)]
    enc = TOK(text, return_offsets_mapping=True, truncation=True, max_length=256, return_tensors="pt")
    offsets = enc.pop("offset_mapping")[0].tolist()
    with torch.no_grad():
        logits = MODEL(**enc).logits[0]
    tags = [ID2LABEL[i] for i in logits.argmax(-1).tolist()]
    spans = _decode([tuple(o) for o in offsets], tags)
    out, cur = [], 0
    for s, e, a in sorted(spans, key=lambda x: x[0]):
        if cur < s:
            out.append((text[cur:s], None))
        out.append((text[s:e], a))
        cur = e
    if cur < len(text):
        out.append((text[cur:], None))
    return out or [(text, None)]


if __name__ == "__main__":
    import gradio as gr

    demo = gr.Interface(
        fn=predict,
        inputs=gr.Textbox(lines=3, label="Texto (PT-BR)",
                          placeholder="Bom dia! Você poderia revisar o relatório? Obrigado."),
        outputs=gr.HighlightedText(label="Atos de fala", combine_adjacent=False),
        title="chomsky · classificador de atos de fala (PT-BR)",
        description="BERTimbau + LoRA, destilado de DeepSeek. 13 atos de fala (ISO 24617-2 + Searle): "
                    "informar, perguntar, concordar, discordar, pedir, sugerir, oferecer, prometer, "
                    "saudar, agradecer, desculpar, despedir, expressar_emocao.",
        examples=[
            ["Bom dia! Você poderia revisar o relatório até amanhã? Obrigado."],
            ["Não concordo com essa decisão, acho um erro. Que tal revisarmos amanhã?"],
            ["Desculpe pelo atraso, prometo entregar hoje. Até mais!"],
        ],
        allow_flagging="never",
    )
    demo.launch()
