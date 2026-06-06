"""Export the merged token-classification model to ONNX (for Transformers.js / WebGPU).

Produces onnx_out/ with model.onnx + config + tokenizer. Transformers.js expects the ONNX
under an `onnx/` subfolder in the HF repo, so the upload step places it there.

    .venv/bin/python scripts/export_onnx.py
"""
from optimum.onnxruntime import ORTModelForTokenClassification
from transformers import AutoTokenizer

SRC = "runs/sa-merged"
OUT = "onnx_out"


def main() -> int:
    model = ORTModelForTokenClassification.from_pretrained(SRC, export=True)
    model.save_pretrained(OUT)
    AutoTokenizer.from_pretrained(SRC).save_pretrained(OUT)
    print(f"exported -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
