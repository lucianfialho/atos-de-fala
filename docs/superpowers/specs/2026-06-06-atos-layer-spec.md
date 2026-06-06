# Spec — Camada de Atos de Fala (ORAKTRON Layer 3, axis 1)

**Data:** 2026-06-06
**Escopo:** travar (garantir) a camada de atos de fala como a **primeira camada** do plano em
camadas do [[oraktron-pragmatic-os]]. As outras dimensões (eixos) ficam esboçadas no fim — o foco
aqui é deixar o atos sólido, medido e útil **sozinho**, antes de empilhar eixos.

> Por que focar: a camada de atos é a "intencionalidade primitiva" — a base de que os outros eixos
> derivam. Se ela não estiver firme e barata, o resto não tem em que se apoiar.

---

## 1. O reframe que dá valor imediato à camada (a sacada)

Hoje, quando um LLM decide a **intenção** de um texto, ele faz isso **probabilisticamente**, gastando
tokens raciocinando sobre a estrutura semântica. Caro e não-auditável.

A proposta: um **classificador pequeno e barato** rotula conjuntos de tokens (spans) com atos de fala.
Disso sai um **sinal de intenção primitiva quase de graça**:

- "80% deste texto é `informar`" → primitivamente, o texto **quer informar**.
- Os derivados (outros eixos: evidencialidade, apreciação, polidez…) são as **camadas** seguintes.
- O **conjunto** dos eixos = a intenção.

Isso destrava três usos concretos **antes** do ORAKTRON completo:

1. **Baratear o LLM** — em vez do LLM gastar tokens decidindo a intenção, a gente **injeta no prompt**
   a distribuição de atos já computada (ex.: `{informar: 0.8, perguntar: 0.1, pedir: 0.1}`). O LLM
   parte do sinal pronto.
2. **Roteamento (mixture-of-experts)** — a distribuição de atos decide qual expert/caminho ativar
   (texto majoritariamente `pedir` → expert de tarefa/ação; `expressar_emocao` → expert de suporte).
   Menos tokens pra decidir, decisão mais determinística.
3. **Âncora determinística** — o classificador é um forward pass fixo (mesmo input → mesma saída),
   não amostragem token-a-token. É a "trust architecture" do [[2026-06-oraktron-competitive-differential]]:
   classificação barata + agregação determinística, separada do raciocínio probabilístico do LLM.

> Validar com Claude: dar o mesmo texto (a) cru e (b) com a distribuição de atos injetada, e medir
> se (b) decide a intenção com **menos tokens** e/ou mais consistência. É o experimento que prova o
> uso 1. (Hipótese, a medir — não vender como fato.)

---

## 2. O que "garantir a camada de atos" significa (critério de pronto)

A camada está **travada** quando:

- **Contrato estável** (seção 3) — entrada/saída fixas, versionadas.
- **Barra de qualidade medida** contra benchmark público: sentence-level no **Porttinari**
  (holdout PT-BR), reportando macro-F1 por ato (não só weighted — o desbalanço esconde os atos raros).
  Meta de referência (do doc competitivo): **≥ 70% do F1 do classificador SOTA dedicado** no eixo de
  atos. Abaixo disso, recuar pro claim arquitetural.

### Baseline medido (2026-06-06, zero-shot / fora-de-domínio)

`atos.train.eval_cli --model runs/sa-lora --holdout data/porttinari-holdout.jsonl --mode sentence`
(n=4091). O modelo treinou em **sintético**, avaliado **zero-shot** no Porttinari (notícia real):

| Granularidade | accuracy | macro-F1 | destaque |
|---|---|---|---|
| 13 atos | 0.827 | **0.201** | informar 0.91, perguntar 0.62; oferecer/despedir/desculpar = 0.0 |
| coarse (Searle) | 0.879 | **0.407** | assertivo 0.94, pergunta 0.62; comissivo 0.02 |

Baseline do paper (BERTimbau treinado **no** Porttinari, in-domain) = **0.295 macro-F1**. Estamos em
**~68% disso, zero-shot** — logo abaixo da barra de 70%, mas é comparação dura (eles in-domain, nós não).

### Fine-tune in-domain (variante A, 2026-06-06) — resultado negativo revelador

Split 80/20 do Porttinari (train 3272 / test 819), LoRA 5 épocas, **sem class weights**:

| Modelo | acc | macro-F1 (13) | macro-F1 (coarse) |
|---|---|---|---|
| zero-shot (só sintético) | 0.827 | 0.201 | 0.407 |
| in-domain FT (sem pesos) | 0.938 | 0.214 | 0.388 |
| **in-domain FT (+ class weights)** | 0.850 | **0.262** | **0.439** |
| paper SOTA (in-domain + pesos) | ~0.92 | **0.295** | — |

Sem pesos: `informar` 0.967, `perguntar` 0.96, **resto 0.0** → **colapso na classe majoritária**
(accuracy alta, macro-F1 parado, coarse piora). Os resultados do paper usam `weights_True`.

Com `--class-weights` (commit que adiciona `WeightedTrainer`, loss inverse-frequency): macro-F1
**0.214→0.262** (fino) e **0.388→0.439** (coarse, melhor número até agora); atos raros saem do zero
(`sugerir` 0.31, `discordar` 0.19). Accuracy cai (0.94→0.85) — o peso troca acerto da maioria por
cobertura das minorias (por isso macro-F1 é a métrica, não accuracy). **~89% do SOTA do paper
(0.262/0.295), só com o conserto da loss — sem trabalho de dado.** Os 0.0 restantes (agradecer/
prometer/pedir/expressar_emocao) são em boa parte atos quase ausentes em notícia (poucos positivos
no teste), não puro erro.

**Conclusão:** o gargalo era **desbalanço, não domínio** (confirma "class imbalance is the killer").
A loss ponderada deu +0.05 macro sozinha. O mesmo `--class-weights` deve ajudar o **modelo de
produção (sintético)** nos atos raros — **sem depender da regen/chave de API**.

### Produção: sintético + `--class-weights` (zero-shot, 2026-06-06)

Retreino do modelo de produção (data/dataset.jsonl, 5086, span-level) com `--class-weights`,
avaliado zero-shot no Porttinari:

| Modelo | acc | macro-F1 (13) | macro-F1 (coarse) |
|---|---|---|---|
| produção atual (sa-lora) | 0.827 | 0.201 | 0.407 |
| **sintético + class-weights** | 0.834 | **0.233** | **0.428** |

Melhora Pareto: macro-F1 +0.032 (fino) / +0.021 (coarse); `perguntar` 0.62→0.705; `informar` 0.91
estável; **atos raros saem do chão** (desculpar 0.25, concordar 0.20, discordar/expressar 0.15,
agradecer 0.13, sugerir 0.13, prometer 0.10, pedir 0.07) — só `oferecer`/`despedir` seguem 0.0.
Conseguido **sem regen e sem chave de API**, só com a loss ponderada. **Próximo: mergear
`runs/sa-lora-weighted` → ONNX int8 → subir no HF** pra atualizar o modelo que roda no site.

**O que os números dizem (baseline zero-shot):**
- O **sinal de intenção primitiva** (assertivo 0.94, pergunta 0.62) é **sólido pros atos dominantes** —
  exatamente o que `act_distribution`/`primitive_intent` precisam ("80% informar → informar").
- A fraqueza está concentrada em atos **raros/comissivos/diretivos** (oferecer/prometer/desculpar/
  despedir/pedir). Causa: viés do sintético — ele está **inflado justo nos atos que notícia real quase
  não tem** (saudar/agradecer/pedir). `agradecer` deu precision 1.0 / recall 0.08 → quase não existe no
  Porttinari. É a mesma raiz do desbalanço (0.47). Conserto: regen rebalanceada + gold humano + (talvez)
  fine-tune in-domain.
- **Distribuição saudável** no dataset de treino: `balance_ratio` alvo ~0.9 (hoje 0.47 — depende da
  regen rebalanceada, travada em chave de API).
- **Gold humano real** entrando pela coleta (`/jogar` + `/assistir`) e fechando o ciclo via
  `atos.collect export-spans` → retreino.

---

## 3. Contrato da camada (input → output)

**Input:** texto arbitrário PT-BR (não só diálogo — é o diferencial vs ISO/DIT++).

**Output (JSON estável):**
```json
{
  "text": "...",
  "spans": [{"start": 0, "end": 8, "act": "saudar", "score": 0.99}],
  "act_distribution": {"informar": 0.8, "pedir": 0.1, "perguntar": 0.1},
  "primitive_intent": "informar"
}
```
- `spans` — decomposição span-level (BIOES → spans), o que já roda no navegador.
- `act_distribution` — fração do texto coberta por cada ato (peso por nº de tokens/chars do span).
- `primitive_intent` — o ato dominante = a intenção primitiva (o "80% informar → informar").

Este contrato é o que os usos da seção 1 consomem (prompt injection / MoE router).

---

## 4. Modelo

- **BERTimbau + LoRA**, token classifier BIOES (13 atos → 53 labels). Já existe, mergeado, ONNX int8,
  roda no navegador (Transformers.js/WebGPU) e em Gradio Space.
- **Determinístico no sentido prático:** forward pass discriminativo, sem amostragem. A agregação
  (`act_distribution`, `primitive_intent`) é cálculo puro server-side/cliente.
- **Por que LoRA importa pro plano:** a camada de atos é o **adapter 1**. Os próximos eixos entram
  como adapters ortogonais sobre o **mesmo encoder congelado** ([[layered-pragmatic-axes]]) — sem
  retreinar este. Garantir o atos = garantir o adapter-base + o pipeline que os outros vão copiar.

---

## 5. Dados (o que alimenta e como fecha o ciclo)

- **Sintético v1** (5086 ex, balance 0.47) — base atual; rebalancear via steering negativo
  (`--avoid-k`) quando a chave de API voltar.
- **Gold humano** — `/jogar` (modelo propõe → humano vota/corrige) e `/assistir` (transcrição real
  FAPESP → humano corrige), priorizados por active learning (`atos.collect prioritize`).
- **Export** — `atos.collect export-spans` transforma correções em JSONL de treino → retreino.
- **Output de pesquisa (único nosso):** medir se **perfis demográficos diferentes percebem atos
  diferentes** na mesma frase (`atos.collect perception`). Isso vira preprint do eixo de atos —
  a prioridade estratégica do doc competitivo (depositar datado antes de mover comercialmente).

---

## 6. Extensão em camadas (esboço — fora do foco desta fase)

Depois que o atos estiver travado, cada novo eixo (evidencialidade, apreciação, polidez, negação,
pressuposição, argumentação…) entra como **adapter ortogonal** sobre o encoder congelado, construído
em **paralelo** pelo time, com um **pool compartilhado** (mesmas frases anotadas em todos os eixos)
como a joia da coroa. A **síntese cross-eixo → intenção** é um estágio separado e **não-provado** —
a aposta. Detalhe completo em [[layered-pragmatic-axes]] e [[oraktron-pragmatic-os]].

---

## 7. Ressalvas honestas

- O uso "baratear/rotear LLM" (seção 1) é **hipótese a medir** com o experimento Claude — não dado.
- `primitive_intent` = ato dominante é uma **aproximação grosseira** da intenção; a intenção real é
  o conjunto dos eixos, que ainda não temos. Não confundir "ato dominante" com "intenção".
- Barra ≥70% SOTA: **medido — ~68% zero-shot** (seção 2). Quase lá, mas ainda não "competitivo"
  pelo critério; fechar a lacuna depende de rebalancear/gold/in-domain. Comparação é dura (paper é
  in-domain), então 68% zero-shot valida transferência, não vende competitividade.
- Determinístico = forward pass fixo, **não** regra simbólica; é um modelo aprendido. Documentar isso
  pra não prometer determinismo que não existe.
