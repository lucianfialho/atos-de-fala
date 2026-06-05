---
type: entity
tags: [tool, synthetic-data, brazilian-pii, api]
sources: 1
updated: 2026-05-06
---

# 4devs API

## What It Is

Web tool at https://www.4devs.com.br with an unofficial JSON API for generating synthetic Brazilian personal data. Used as the data source for the Privacy Filter BR project.

## Significance

The single endpoint that made the Privacy Filter BR dataset possible. Generates valid CPF/CNPJ/RG/etc. with correct checksums, mathematically valid, but completely fake. No LGPD issues because no real person is involved.

## Key Facts

**Endpoint:** `POST https://www.4devs.com.br/ferramentas_online.php`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
```

**Available actions (acao):**
| acao | Returns |
|---|---|
| `gerar_cpf` | CPF (formatted with `pontuacao=S`) |
| `gerar_cnpj` | CNPJ formatted |
| `gerar_rg` | RG with checksum |
| `gerar_cnh` | CNH (driver's license) number |
| `gerar_titulo_eleitor` | Voter ID (per state) |
| `gerar_pis` | PIS/PASEP number |
| `gerador_certidao` | Birth/marriage/death certificate number |
| `gerar_ie` | Inscrição Estadual (per state, all 27 formats) |
| `gerar_pessoa` | **Full profile**: name, CPF, RG, email, phone, address, etc. |

**Example usage (Python):**
```python
import requests
resp = requests.post(
    "https://www.4devs.com.br/ferramentas_online.php",
    headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
             "X-Requested-With": "XMLHttpRequest"},
    data="acao=gerar_pessoa&sexo=I&pontuacao=S&idade=0&cep_estado=SP&txt_qtde=1&cep_cidade=",
)
profile = resp.json()[0]
# {"nome": "Maria Silva", "cpf": "...", "rg": "...", "email": "...", ...}
```

**Limitations:**
- No public API contract (might change without notice)
- Rate limiting unclear — used 0.3s delay between calls
- Occasional 503 errors during high traffic
- Must use POST with form-encoded body, not JSON

**Stability:** During the Privacy Filter BR project, served 11k+ requests over 2 days with ~95% success rate (after retry with backoff).

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
