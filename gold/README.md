# Gold multi-domínio — guia de adjudicação

Este diretório guarda o **gold humano** que avalia o modelo por domínio
(`atos.train.multidomain`). Gold humano é a única régua com autoridade: sem ele,
todo número de qualidade é chute ou circular (medir o modelo contra o próprio
teacher que o treinou).

> **Por que isso importa:** o eval só de notícia (Porttinari) é **cego** aos atos
> sociais/comissivos — `oferecer`, `saudar`, `despedir` nem aparecem lá (10/13 atos).
> Foi essa cegueira que impediu de decidir se o v4 (+review) ficou *burro de verdade*
> ou só *pareceu* burro. Este gold é o que tira a dúvida — **se** for feito direito.

## O que é adjudicar

Você **não anota do zero**. O modelo (silver) já propôs os spans; seu trabalho é
**corrigir**: confirmar o que está certo, arrumar ato/fronteira errados, apagar o que
não é ato, e **adicionar** o que faltou. Corrigir é muito mais rápido que autorar — e
o resultado é gold humano legítimo.

Regras de anotação, os 13 atos e os casos de borda: **`config/rubric.md`** (leia uma vez).

## Formato do worksheet

Cada linha do `*-worksheet.jsonl` é um item. Spans são **trechos de texto** (`quote`),
não números — você edita palavras, nunca offsets.

```json
{"domain": "sac", "text": "Bom dia, posso te ajudar com o pedido?", "reviewed": false,
 "spans": [{"quote": "Bom dia", "act": "saudar"},
           {"quote": "posso te ajudar com o pedido?", "act": "oferecer"}],
 "notes": ""}
```

Para cada linha:
1. Leia o `text`.
2. Conserte os `spans`: ato errado → troque o `act`; fronteira errada → ajuste o `quote`
   (tem que ser substring **exata** do texto); não é ato → remova; faltou → adicione
   `{"quote": "...", "act": "..."}`. Spans **não se sobrepõem**.
3. Na dúvida genuína, **não force** — deixe o trecho sem span (rúbrica, regra 10).
4. Quando a linha estiver certa, mude **`"reviewed": false` → `true`**.

Linhas com `reviewed: false` são ignoradas no harvest. Linhas cujos `quote` não batem
no texto, ou com ato fora dos 13, são **rejeitadas** (não viram gold silenciosamente) —
o harvest reporta quantas caíram.

## Meta de quantidade (pra o número ter autoridade)

F1 de um ato com 3 exemplos é ruído. Mire:

- **~40 itens adjudicados por domínio** (review, sac, entrevista; notícia já vem do Porttinari).
- **~15–20 exemplos por ato** nos atos que a notícia não cobre — escolha texto que
  contenha `oferecer`, `saudar`, `despedir`, `prometer`, `desculpar` (SAC/atendimento é
  a melhor fonte deles; review pega `expressar_emocao`/`discordar`/`oferecer`).

Abaixo disso o resultado é **direcional** ("parece que…"), não **final** ("é").

## Pipeline (rodar na box — precisa de torch/onnxruntime)

```bash
# 1. silver: o teacher pré-anota texto real do domínio
python -m atos.gen.annotate_corpus --text-file data/sac.txt --out data/sac-silver.jsonl

# 2. build: silver -> worksheet (spans viram quotes, reviewed:false)
python -m atos.collect.worksheet build --in data/sac-silver.jsonl --domain sac \
    --out gold/sac-worksheet.jsonl

# 3. >>> humano adjudica gold/sac-worksheet.jsonl <<<  (o passo que tira a dúvida)

# 4. harvest: worksheet revisado -> gold (offsets + domínio, validado)
python -m atos.collect.worksheet harvest --in gold/sac-worksheet.jsonl --out gold/sac.jsonl

# repita para review/entrevista; notícia e entrevista-do-jogo vêm prontas:
python -m atos.train.porttinari --domain noticia --out gold/noticia.jsonl
python -m atos.collect export-holdout --domain entrevista --out gold/entrevista.jsonl

# junta e avalia por domínio
cat gold/noticia.jsonl gold/entrevista.jsonl gold/review.jsonl gold/sac.jsonl > gold/multidomain.jsonl
python -m atos.train.multidomain --model models/v3 --gold gold/multidomain.jsonl --mode span
```

## O experimento que encerra a dúvida do v4

Com review/SAC adjudicados, rode v3 e v4 lado a lado:

```bash
python -m atos.train.multidomain --model models/v3 --gold gold/multidomain.jsonl --mode span
python -m atos.train.multidomain --model models/v4 --gold gold/multidomain.jsonl --mode span
```

- **v4 ≥ v3 nos atos sociais e sem perder na notícia** → review de treino estava certo;
  o Porttinari é que era cego, revertemos errado.
- **v4 cai na notícia sem compensar nos sociais** → review machucou (OOD); v3 certo.

## Arquivos aqui

- `multidomain.jsonl` — gold agregado (hoje **só `noticia`**, do Porttinari; preencha os outros domínios).
- `honeypots.jsonl` — itens de controle de qualidade (atenção do anotador).
- `*-worksheet.jsonl` — worksheets em adjudicação (não commitar com dados sensíveis).
- `<domínio>.jsonl` — gold harvested por domínio.

> Nota honesta: o código deixa a adjudicação o mais barata possível, mas **não substitui o
> humano**. ~40 itens/domínio é ~meia hora de trabalho que vale mais que semanas de
> retreino no escuro.
