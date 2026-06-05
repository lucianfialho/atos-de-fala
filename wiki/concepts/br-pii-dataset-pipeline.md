---
type: concept
tags: [dataset, pipeline, synthetic, brazilian-pii, jinja, 4devs, validation]
sources: 2
updated: 2026-05-16
---

# Brazilian PII Dataset Pipeline

## Definition

Pipeline end-to-end pra gerar dataset sintético de PII brasileiro labeled pra fine-tuning de token classifier. Vai de "API de gerador de dado fake" até `dataset.jsonl` pronto pro HuggingFace `datasets`.

## Architecture Overview

```
4devs API                  → CPF, CNPJ, RG, nome, endereço, etc. (PII sintético válido com checksum)
       ↓
pessoa.py                  → consolida em "perfil completo" (~17 campos)
       ↓
variants.py                → expande cada PII em 2-4 formato variants
       ↓
random.choice(variants)    → escolhe uma variante por campo pra usar no template
       ↓
Jinja2 templates (18)      → renderiza documento BR realista com PII inserido
       ↓
LLM (Claude/MiniMax)       → reescreve mantendo PII verbatim, deixando texto natural
       ↓
validator.py               → descarta examples inválidos (5 failure modes)
       ↓
labeler.py                 → encontra spans de cada PII conhecido, gera BIOES
       ↓
JSONL output (append)      → 1 linha por exemplo: {text, entities[]}
```

Cada peça é um arquivo Python ~50-100 linhas. Independentemente testável.

## Stage 1: PII Generation (4devs API)

[4devs.com.br](../entities/4devs-api.md) tem endpoint POST que gera PII brasileiro válido:

```python
# Mapping dos endpoints
"gerar_cpf"             → "680.075.670-97" (checksum válido)
"gerar_cnpj"            → "72.682.864/0001-41"
"gerar_rg"              → "27.141.489-3" (varia por estado)
"gerar_cnh"             → "12345678901"
"gerar_pis"             → "123.45678.90-1"
"gerar_titulo_eleitor"  → "228214550167"
"gerar_ie&estado=SP"    → "818.800.070.960" (formato varia entre 27 estados)
"gerador_certidao"      → "256757 01 55 2022 1 08962 159 2623902-70"
"gerar_pessoa"          → dict completo (nome, CPF, RG, email, endereço, telefone...)
```

**Throughput:** ~3 requests/segundo com `time.sleep(0.3)` entre chamadas. Retry 3x com backoff exponencial em erro.

## Stage 2: Variant Expansion

Cada PII numérico vira **2-4 variantes de formato** pra cobrir como aparece em sistemas reais:

```python
def variantes_cpf(cpf: str) -> list[tuple[str, str]]:
    # cpf = "680.075.670-97"
    return [
        ("680.075.670-97",  "PRIVATE_CPF"),  # formatado (cartões, documentos)
        ("68007567097",     "PRIVATE_CPF"),  # raw (databases, JSONs)
        ("680.075.***-**",  "PRIVATE_CPF"),  # parcial (sistemas de verificação)
        ("680 075 670 97",  "PRIVATE_CPF"),  # com espaços (alguns PDFs/OCR)
    ]
```

Mesmo padrão pra CNPJ, RG, CEP, telefone. **Razão:** modelos treinados só em formato canônico falham em variantes reais (descobrimos no v1).

## Stage 3: Template Rendering

18 templates Jinja2 cobrindo categorias de documento brasileiro:

```
Originais (8):       email, nfe, contrato, holerite, certidao,
                     cadastro, comunicado, relatorio
B2B fiscal (6):      nfe_completa, darf, boleto, comprovante_pix,
                     extrato_bancario, fatura_servico
E-commerce (4):      pedido_marketplace, dashboard_vendas,
                     comprovante_delivery, relatorio_faturamento
```

Cada template é um `.jinja2` com placeholders `{{ cpf_valor }}`, `{{ nome }}`, etc. Renderiza estrutura realista; depois LLM transforma em prose natural.

**Por que template antes do LLM?** Garante que o LLM **recebe estrutura conhecida** com PII em posições conhecidas, reduzindo chance de ele inventar dados ou esquecer campos.

## Stage 4: LLM Rewrite

Prompt fixo:
```
Reescreva o texto abaixo em português BR natural e formal,
mantendo TODOS os valores exatamente como estão (CPF, CNPJ, nomes, etc).
NÃO altere nenhum número ou dado pessoal:

{template_rendered}
```

**Provider-agnostic:** funciona com Claude CLI subprocess, Anthropic API, ou MiniMax HTTP. Ver [multi-provider-generation](multi-provider-generation.md).

**Por que reescrever?** Template puro fica robotizado. LLM dá variação linguística que ajuda o modelo NER a generalizar.

## Stage 5: Validation (5 failure modes)

`validator.py` descarta exemplos antes de labelar:

```python
class ValidationResult(Enum):
    VALID = "valid"
    TEXT_TOO_SHORT = "text_too_short"          # < 50 chars
    NO_ENTITIES = "no_entities"                # falhou em encontrar PII
    SPAN_OUT_OF_BOUNDS = "span_out_of_bounds"  # bug de offset
    OVERLAPPING_SPANS = "overlapping_spans"    # PII conflitante
```

**Modos comuns de falha:**
- LLM ignora a regra "preserve PII verbatim" → algum span não aparece no texto
- LLM trunca o texto → curto demais
- LLM rearranja dados → spans sobrepostos

Acceptance rate típica: **80-95%** dependendo do provider.

## Stage 6: BIOES Auto-labeling

`labeler.py` recebe `(text, dict_de_pii_inserido)` e:

1. Pra cada PII conhecido, faz `re.escape(value)` e procura no text
2. Resolve overlaps (matches mais longos ganham)
3. Converte spans char-level pra BIOES tags por token

```python
def find_spans(text, inserted):
    # inserted = {"680.075.670-97": "PRIVATE_CPF", "João Silva": "PRIVATE_PERSON"}
    raw_spans = []
    for value, label in inserted.items():
        for m in re.finditer(re.escape(value), text):
            raw_spans.append({"start": m.start(), "end": m.end(), "label": label})
    # ... resolve overlaps, return sorted spans
```

**Por que `re.escape`?** PII tem `.`, `-`, `/`, etc. que regex interpretaria.

**Por que registrar TODAS as variantes (não só a usada)?** Se LLM reformatar `68007567097` pra `680.075.670-97`, ainda achamos.

## Stage 7: Persistence (Resume-Safe)

`generate_dataset.py` escreve cada exemplo **imediatamente** com `f.flush()`. Suporta:
- **Resume:** count `wc -l` no início, gera apenas `target - existing`
- **Multi-provider:** ambos appendam ao mesmo arquivo (file lock via threading.Lock)
- **Kill-anytime:** sem perda de dados (não acumula em memória)

```python
write_lock = threading.Lock()
# ...
with write_lock:
    f.write(json.dumps(example, ensure_ascii=False) + "\n")
    f.flush()
```

## Custos Reais (1 execução de 100k)

| Stage | Cost | Time (sequencial) |
|---|---|---|
| 4devs API | $0 (público) | ~10h |
| Template render | $0 (Jinja local) | ~0.5h |
| LLM rewrite | $0 (Claude subscription) ou $5-15 (MiniMax/API) | ~50h |
| Validation + label | $0 (Python local) | ~0.5h |
| **Total** | **$0-15** | **~50-80h** |

Com Claude + MiniMax paralelos: ~40-50h total.

## Reusable for Other Domains

Pipeline é **domain-agnostic**. Pra adaptar pra outro tipo de NER:

1. Trocar 4devs por outro gerador sintético
2. Trocar Jinja templates por documentos do novo domínio
3. Trocar variants.py por formatos relevantes pra essa categoria
4. Manter labeler.py, validator.py, generate_dataset.py inalterados

Pra medical PII: usar [Faker BR](https://faker.readthedocs.io/) + templates de prontuário.
Pra legal: gerar OAB sintética + templates de petição/sentença.

## Related Concepts

- [Synthetic Data Generation](synthetic-data-generation.md) — versão genérica
- [Multi-Provider Generation](multi-provider-generation.md) — paralelismo
- [BIOES Tagging](bioes-tagging.md) — output format
- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md) — próxima etapa

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
- [Privacy Filter BR v2 Execution](../sources/2026-05-16-privacy-filter-br-v2-execution.md)
