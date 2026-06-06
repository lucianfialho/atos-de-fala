"""Export the merged token-classification model to ONNX + int8 quantize (Transformers.js/WebGPU).

Produces OUT/ laid out as the HF model repo expects:
  OUT/config.json, OUT/tokenizer*, OUT/onnx/model_quantized.onnx
Transformers.js with dtype "q8" loads `onnx/model_quantized.onnx`.

    .venv/bin/python scripts/export_onnx.py [SRC] [OUT]
    # defaults: SRC=runs/sa-merged  OUT=onnx_out
"""
import os
import shutil
import sys
from optimum.onnxruntime import ORTModelForTokenClassification
from transformers import AutoTokenizer
from onnxruntime.quantization import quantize_dynamic, QuantType

SRC = sys.argv[1] if len(sys.argv) > 1 else "runs/sa-merged"
OUT = sys.argv[2] if len(sys.argv) > 2 else "onnx_out"


def main() -> int:
    fp32 = os.path.join(OUT, "_fp32")
    model = ORTModelForTokenClassification.from_pretrained(SRC, export=True)
    model.save_pretrained(fp32)
    AutoTokenizer.from_pretrained(SRC).save_pretrained(OUT)
    shutil.copy(os.path.join(fp32, "config.json"), os.path.join(OUT, "config.json"))

    onnx_dir = os.path.join(OUT, "onnx")
    os.makedirs(onnx_dir, exist_ok=True)
    quantize_dynamic(
        os.path.join(fp32, "model.onnx"),
        os.path.join(onnx_dir, "model_quantized.onnx"),
        weight_type=QuantType.QUInt8,
    )
    shutil.rmtree(fp32, ignore_errors=True)
    print(f"exported + quantized -> {OUT}/onnx/model_quantized.onnx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
