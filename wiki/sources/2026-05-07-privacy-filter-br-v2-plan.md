---
type: source
tags: [planning, privacy-filter, b2b, v2, strategy, dataset]
sources: 1
updated: 2026-05-07
---

# Privacy Filter BR v2 — Plano de Treino B2B

**Status:** Planejado, não iniciado
**Decision date:** 2026-05-07
**Target start:** TBD (não hoje)

## Contexto

Privacy Filter BR v1 (treinado em 2026-05-06) atingiu F1 macro 0.97 em holdout interno mas:
- **Concorrente apareceu durante o build:** `arthrod/gliner-opf-ptbr-pii-v1` (914k samples, F1 0.885)
- **Posicionamento original ("BR generalista") perdido** para arthrod
- **Especialização B2B ainda livre** — arthrod cobre PII pessoal mas não tem CNPJ, IE, CNH, Certidão como categorias específicas

## Decisão Estratégica

Reposicionar v2 como **especialista em B2B/comercial brasileiro**, mantendo paridade em PII pessoal usando o dataset público do arthrod.

**Não competir** com arthrod no nicho de PII pessoal (perdeu). **Construir** o nicho de PII em documentos comerciais B2B (sem concorrente).

## Justificativa LGPD/Mercado

B2B é mercado mal-coberto em ferramentas LGPD porque empresas acham "B2B = sem LGPD". Errado:

- CNPJ MEI = pessoa física, é PII
- Holerite tem dados sensíveis (Art. 5º II): saúde, sindicato, plano
- NF-e com tomador PF tem CPF
- Email corporativo identificável é PII (Art. 5º I)
- Procurações têm outorgante/outorgado pessoa física
- Contratos B2B têm representante legal (CPF + nome)

Mercado-alvo: ERPs, BPOs fiscais, consultorias, agências, SaaS B2B.

## Estratégia de Dataset

```
Base de treino combinada:

  arthrod/oai-pf-ptbr-chunked-v2      914k samples (Apache 2.0)
    ↓ re-label para nossa taxonomia
  + 50-100k novos B2B-específicos
    ↓ gerados via MiniMax (1500 req/h)
  = ~1M samples de cobertura geral + B2B

Modelo base: openai/privacy-filter (mesma base do arthrod)
  → garantia de paridade arquitetural
  → comparação justa
```

## Estratégia de Geração B2B

Templates novos focados em documentos B2B brasileiros:

**Fiscal/Tributário:**
- NF-e completa (com tomador/prestador, ICMS, CFOP)
- DARF (CNPJ + código de receita + valor)
- DAS (Simples Nacional)

**Contábil/Financeiro:**
- Boleto bancário B2B
- Comprovante PIX corporativo
- Fatura serviço (com CNPJ + IE)

**RH:**
- Holerite completo (com convênios, INSS, IRRF)
- Termo admissão/demissão

**Comercial:**
- Contrato B2B
- Procuração corporativa
- Pedido/cotação

**Pipeline de geração (decidido):**
1. Claude Managed Agents gera 30 templates B2B realistas (~$10, 1 sessão)
2. MiniMax preenche com PII sintético via 4devs (1500 req/h, 3 dias para 100k)
3. Validação de spans verbatim (existente)
4. BIOES auto-labeling

## Custo Estimado

**Geração de dataset:**
- Claude Managed Agents (templates): ~$10
- MiniMax API (100k examples): ~$15
- Total geração: **~$25**

**Treino (Colab Pro existente):**
- 100k × 3 epochs A100 = ~9h = ~120 unidades (cabe em 1 mês de Pro)
- 250k × 3 epochs A100 = ~22h = ~290 unidades (precisa Pro+ ou pay-as-you-go ~$15)

**Recomendação:** começar com 100k (cabe no Pro atual). Se F1 não bater 0.95+, escalar para 250k.

## Plano de Execução

| Etapa | Duração | Dependências |
|---|---|---|
| 1. Download dataset arthrod | 30min | HF Hub |
| 2. Re-label para nossa taxonomy | 2-4h | Script de mapeamento |
| 3. Upload re-labeled dataset para HF Hub privado | 30min | Acesso HF |
| 4. Claude gera 30 templates B2B | 1h | Anthropic API |
| 5. MiniMax gera 50-100k novos exemplos | 3 dias background | MiniMax API |
| 6. Combina datasets | 1h | Tudo acima |
| 7. Treina v2 LoRA (Colab A100) | ~9h | Pro plan |
| 8. Benchmark + comparação | 1h | Holdout sets |
| 9. Publica HF + atualiza repo | 1h | Decisão de publicar |

**Total:** ~5 dias calendar (3 deles em background).

## Categorias Alvo v2

Manter as 13 atuais + considerar adicionar:

```
Atuais:
  PRIVATE_CPF, PRIVATE_CNPJ, PRIVATE_RG, PRIVATE_CNH
  PRIVATE_PIS, PRIVATE_TITULO_ELEITOR, PRIVATE_CERTIDAO
  PRIVATE_IE, PRIVATE_PERSON, PRIVATE_EMAIL
  PRIVATE_PHONE, PRIVATE_ADDRESS, PRIVATE_DATE

Considerar adicionar v2 (B2B-específicas):
  PRIVATE_DARF_CODE     # código receita DARF
  PRIVATE_PIX_KEY       # chave PIX (CPF/CNPJ/email/telefone/aleatória)
  PRIVATE_BANK_AGENCY   # agência bancária
  PRIVATE_BANK_ACCOUNT  # conta bancária
  PRIVATE_NFE_KEY       # chave acesso NF-e (44 dígitos)
  PRIVATE_INSCRICAO_MUNICIPAL  # IM
```

**Decisão:** começar com as 13 atuais para v2. Adicionar novas categorias só em v3 se houver demanda real.

## Métricas de Sucesso

v2 considerado bem-sucedido se:
- F1 macro ≥ 0.92 em holdout B2B (não-sintético)
- F1 individual em CNPJ/IE/CNH ≥ 0.95
- Para evaluation justa contra arthrod: rodar ambos no mesmo benchmark de 1k exemplos B2B reais

## Riscos

1. **MiniMax pode rebaixar qualidade do português.** Mitigação: testar com 100 amostras antes de escalar para 100k.
2. **Re-label do dataset arthrod pode introduzir ruído.** Mitigação: validação amostral via Claude.
3. **Treino 100k pode estourar limit do Colab Pro.** Mitigação: dividir em chunks com checkpoints.
4. **F1 não melhora suficientemente sobre v1.** Mitigação: aceitar v2 como expansão de cobertura mesmo sem ganho de F1 macro.

## Estado Atual

- **v1 treinado, baixado, validado:** `~/Downloads/privacy-filter-br-merged.zip` (2.5GB, 53 labels, F1 0.97 holdout interno)
- **Dataset v1:** 11k synthetic, no HF (privado)
- **Colab Pro:** $10/mês ativo
- **MiniMax API:** 1500 req/h disponível
- **Próxima ação:** download do dataset arthrod (decidido). Quando: TBD pelo usuário.

## Sources

- [Privacy Filter BR Build (v1)](2026-05-06-privacy-filter-br-build.md)
- [arthrod/gliner-opf-ptbr-pii-v1](../entities/arthrod-privacy-filter-ptbr.md)
- [4devs API](../entities/4devs-api.md)
