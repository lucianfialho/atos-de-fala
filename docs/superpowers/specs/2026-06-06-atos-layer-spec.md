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
- **Barra de qualidade medida** contra benchmark público: span/sentence-level no **Porttinari**
  (holdout PT-BR), reportando macro-F1 por ato (não só weighted — o desbalanço esconde os atos raros).
  Meta de referência (do doc competitivo): **≥ 70% do F1 do classificador SOTA dedicado** no eixo de
  atos. Abaixo disso, recuar pro claim arquitetural.
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
- A barra ≥70% SOTA depende de rodar o eval no Porttinari — ainda não medido formalmente.
- Determinístico = forward pass fixo, **não** regra simbólica; é um modelo aprendido. Documentar isso
  pra não prometer determinismo que não existe.
