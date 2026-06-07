"""ONNX inference for the speech-act model (onnxruntime, no torch).

Mirrors atos.train.eval_cli.predict_annotations but runs an .onnx file directly, so we can
benchmark quantization variants (int8 vs fp16) against the same gold the PyTorch path uses,
before deciding which one ships to the browser (Transformers.js/WebGPU).

Labels come from the taxonomy (not config.json) so the id->label order is guaranteed to match
training, exactly like eval_cli does. Only the inputs the graph actually declares are fed, so
the same code works whether or not the export kept token_type_ids.
"""
from typing import List

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

from atos.schema import Annotation
from atos.taxonomy import load_taxonomy, bioes_labels, label_maps
from atos.train.decode import bioes_tags_to_spans


def predict_annotations_onnx(
    onnx_path: str,
    tokenizer_dir: str,
    texts: List[str],
    taxonomy_path: str = "config/taxonomy.yaml",
    max_length: int = 256,
) -> List[Annotation]:
    labels = bioes_labels(load_taxonomy(taxonomy_path).acts)
    _, id2label = label_maps(labels)
    tok = AutoTokenizer.from_pretrained(tokenizer_dir, use_fast=True)
    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_names = {i.name for i in sess.get_inputs()}

    out: List[Annotation] = []
    for text in texts:
        enc = tok(
            text, return_offsets_mapping=True, truncation=True,
            max_length=max_length, return_tensors="np",
        )
        offsets = enc.pop("offset_mapping")[0].tolist()
        feeds = {k: np.asarray(v, dtype=np.int64) for k, v in enc.items() if k in input_names}
        logits = sess.run(None, feeds)[0][0]  # (seq_len, num_labels)
        ids = logits.argmax(-1).tolist()
        tags = [id2label[i] for i in ids]
        spans = bioes_tags_to_spans([tuple(o) for o in offsets], tags)
        out.append(Annotation(text=text, spans=spans))
    return out
