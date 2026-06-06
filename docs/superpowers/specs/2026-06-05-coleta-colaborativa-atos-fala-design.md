# Coleta Colaborativa de Atos de Fala — Design

**Status:** aprovado no brainstorming (2026-06-05), aguardando review do spec antes do plano.

**Codinome interno:** atos · **Produto público:** jogo de coleta (nome a definir).

## Goal

Construir um web app público em forma de **jogo** onde pessoas anônimas avaliam os atos
de fala que o modelo v1 (BERTimbau+LoRA) atribuiu a frases em PT-BR, e opcionalmente
sugerem outras formas de dizer o mesmo trecho. Cada participante informa um perfil
demográfico (idade, gênero, região, escolaridade). O produto gera três saídas:

1. **Dataset gold aberto** — spans com ato confirmado por concordância humana (treina v2).
2. **Banco de paráfrases humanas** — variações com o mesmo ato (aumento de dados).
3. **Análise de percepção por perfil** — *pessoas de perfis diferentes percebem atos de
   fala diferentes na mesma frase?* (a contribuição de pesquisa inédita pro PT-BR).

É a **camada 4** da estratégia de crescimento em camadas: a forma de escalar a coleta de
gold humano (camada 2) com controle de qualidade.

## Background / por que

- Não existe modelo nem corpus span-level de atos de fala pra PT-BR (varredura do HF Hub).
  O v1 foi destilado de teacher LLM; o teto de qualidade é o teacher.
- A eval no Porttinari (notícias) confirmou: o modelo é bom em `informar`/`perguntar`
  (accuracy 0.83 sentence-level), mas o corpus é **cego** aos 11 atos sociais/diretivos
  /comissivos — eles quase não aparecem em notícia. Logo, o gold humano precisa ser
  **conversacional e balanceado por ato**, e medido num holdout congelado.
- Atos de fala são **subjetivos**: pra muitas frases não há "resposta certa". Essa
  subjetividade não é ruído a eliminar — é o **objeto de estudo**. O design trata
  discordância como sinal, não como erro.

## Arquitetura (fronteira limpa)

Dois subsistemas, acoplados por dois handoffs (lote pra anotar → votos coletados):

```
[0] atos (Python, offline)  →  exporta LOTE de itens (frases + spans + atos da IA)
[1] Web app (Next.js/Vercel)   →  entrada anônima + perfil
[2] Web app                    →  loop do jogo: ✓/✗ por caixinha + sugestão opcional
        (envolto por progressão; v1 = 1 domínio, Fase 1 profundidade)
        ↓ votos + sugestões + perfil (Postgres/Neon)
[3] atos (Python, offline)  →  ingere + agrega (agreement.py, peso por confiabilidade)
[4] atos                    →  saídas: gold aberto · paráfrases · análise por perfil
        ↑ saídas melhoram o modelo → lotes melhores (loop fecha)
```

**Princípio:** o web app **só coleta**. Toda lógica de ML, agregação e análise fica em
Python, reusando o pacote `atos` existente (`taxonomy`, `schema`, `agreement`, o
adjudicador DeepSeek). O app não importa Python — recebe/entrega JSON via a base Postgres.

## Stack

- **Web app:** Next.js (App Router) hospedado na **Vercel**.
- **Banco:** **Postgres (Neon)** — serverless, free tier, integra com Vercel.
- **Auth:** **nenhuma** — participação anônima; id (uuid v4) gerado no cliente e guardado
  em `localStorage`. (Sumiu a complexidade de provider de auth.)
- **Pipeline offline:** pacote `atos` (Python 3.10, já existente), rodando na máquina
  do dev / box tailscale. Lê/escreve no mesmo Postgres (read-replica ou dump).

## Componentes

### Web app (Next.js)

- **Onboarding (`/`):** formulário de 4 campos (faixa de idade, gênero, região/UF,
  escolaridade) + consentimento de uso em dataset aberto. Grava `participant` e o uuid
  no `localStorage`. Sem senha.
- **Jogo (`/jogar`):** busca o próximo item via API, renderiza a frase com as caixinhas
  (spans da IA, cada uma com o ato proposto), botões ✓/✗ por caixinha, campo opcional
  "sugerir outra forma", placar (pontos, streak), barra de progresso, botão "próxima".
- **API routes:**
  - `GET /api/next-item?participant=<uuid>` — serve o próximo item (ver Serving).
  - `POST /api/vote` — grava votos (✓/✗ + correção opcional) de um item.
  - `POST /api/suggestion` — grava uma sugestão de paráfrase.
  - `GET /api/me?participant=<uuid>` — pontos, streak, confiabilidade, itens feitos.

### Pipeline Python (`atos`)

- **`atos.collect.export_batch`** — seleciona itens (frases já anotadas pela IA) +
  injeta honeypots; grava na tabela `item`/`item_span` do Postgres.
- **`atos.collect.ingest`** — lê votos/sugestões do Postgres; reduz a `Annotation`s.
- **`atos.collect.aggregate`** — por span, voto majoritário **ponderado pela
  confiabilidade** do participante; emite gold quando a concordância ponderada ≥ limiar
  (reusa `agreement.py`). Marca itens de baixa concordância para a análise de percepção.
- **`atos.collect.confirm_suggestions`** — manda cada sugestão pendente ao adjudicador
  DeepSeek: "esta paráfrase preserva o ato X?" → `confirmed`/`rejected`.
- **`atos.collect.perception`** — cruza discordância × demografia; relatório por eixo.

## Modelo de dados (Postgres)

- **`participant`**: `id` (uuid), `age_band`, `gender`, `region` (UF), `education`,
  `created_at`. (anônimo)
- **`item`**: `id`, `text`, `source` (`synthetic`|`news`), `is_honeypot` (bool),
  `created_at`.
- **`item_span`**: `id`, `item_id`, `char_start`, `char_end`, `ai_act`, `display_order`.
- **`span_gold`**: `item_span_id`, `gold_act` — só para spans de honeypot (resposta
  conhecida, usada pra pontuar confiabilidade).
- **`vote`**: `id`, `participant_id`, `item_span_id`, `verdict` (`agree`|`disagree`),
  `corrected_act` (nullable, quando `disagree` e o usuário corrige), `created_at`.
  Único por (`participant_id`, `item_span_id`).
- **`suggestion`**: `id`, `participant_id`, `item_span_id`, `text`, `status`
  (`pending`|`confirmed`|`rejected`), `created_at`.
- **`participant_stats`** (ou materializado): `participant_id`, `points`, `streak`,
  `reliability` (0..1, começa em 0.5), `items_done`.

## Mecânica de pontos

Decisões travadas no brainstorming:

- **Imediatos (diversão):** +10 por caixinha avaliada · multiplicador de **streak**
  (frases seguidas) · +20 por enviar uma sugestão (provisório).
- **Bônus retroativo:** +50 quando uma sugestão é **confirmada** pelo adjudicador
  DeepSeek (mantém o ato) → sobe no ranking.
- **Sugestão é bônus OPCIONAL — nunca penaliza quem não sugere** (penalizar gera
  sugestão-lixo). O "aperto" vem do streak + das frases-isca.
- **Confiabilidade (controle de qualidade):** a cada ~7 frases entra uma **frase-isca**
  (honeypot, com `span_gold` conhecido). Acertar sobe a confiabilidade; errar desce.
  **A confiabilidade é o peso do voto** na agregação — filtra spammer sem punir em
  público e sem exigir "resposta certa" nas frases normais.
- **Não se pontua "concordar com a IA":** isso incentivaria carimbar ✓ e destruiria o
  sinal de discordância. Correção/honestidade vêm só das iscas.

## Controle de qualidade / agregação

- **Serving (Fase 1 — profundidade):** pool de ~200 itens conversacionais. Serve itens
  que o participante ainda não viu, priorizando os com **menos votos** (espalha o overlap
  rumo a um alvo de ~20 votos/item). A cada ~7 itens servidos, um é honeypot. Quando o
  pool acaba pro participante, ele é avisado.
- **Dedup:** `vote` único por (participante, span) impede voto duplo. Anônimo pode
  burlar trocando navegador — mitigado por: peso por confiabilidade + honeypots + limiar
  de concordância. (Robustez extra fica pro "depois".)
- **Agregação:** por span, voto ponderado por confiabilidade → ato vencedor; vira gold
  se a concordância ponderada ≥ limiar. Empates / baixa concordância → conjunto de
  "percepção" (não vira gold, mas alimenta a análise).
- **Sugestões:** confirmadas pelo adjudicador DeepSeek (reusa prompts existentes);
  só `confirmed` entram no banco de paráfrases.

## Saída de pesquisa (percepção por perfil)

Para spans com discordância significativa, cruzar o `verdict`/`corrected_act` com os
eixos demográficos (idade, gênero, região, escolaridade). Pergunta central: existe
diferença estatisticamente relevante de percepção de ato por eixo? Relatório por eixo
+ exemplos. (Métodos estatísticos detalhados ficam pro plano de análise; o v1 garante
os **dados** pra responder.)

## Escopo

**v1 (MVP):**
- Onboarding anônimo (4 campos) + consentimento + id no navegador.
- Loop: frase com spans da IA → ✓/✗ por caixinha → próxima.
- Sugerir variação (bônus opcional).
- Pontos imediatos + streak.
- Honeypots + confiabilidade = peso do voto.
- `atos.collect`: export de lote + ingest + aggregate + confirm_suggestions.
- Fase 1 (profundidade): ~200 frases, 1 domínio (conversacional/sintético).
- Sugestões confirmadas pelo adjudicador DeepSeek.

**Depois (fora do v1):**
- Progressão de níveis desbloqueando domínios (→ notícias →…).
- Ranking público / camada social.
- Peer review de sugestão (confirmação por outro jogador).
- Login social opcional + sincronização entre devices.
- Fase 2: cobertura em escala.
- Publicação automatizada do dataset aberto no HF.

## Testing

- **Python (`atos.collect`):** pytest (setup existente, gate de 150 linhas/arquivo).
  Unit: seleção de lote + injeção de honeypot; ingest (votos→Annotation); agregação
  ponderada por confiabilidade; pontuação de honeypot; confirm_suggestions (com
  adjudicador mockado). Reusa `agreement.py`/`schema` já testados.
- **Web (Next.js):** testes de rota de API (next-item serve sem repetir e injeta isca;
  vote/suggestion persistem e validam contra a taxonomia); teste de componente do loop;
  um e2e do fluxo onboarding→avaliar→próxima com banco semeado.

## Decomposição p/ o plano

São dois deliverables que se desenvolvem em paralelo após o schema do banco:
1. **Pipeline `atos.collect`** (Python) — testável isolado contra um Postgres local.
2. **Web app** (Next.js) — testável isolado contra o mesmo schema com seed.

O plano de implementação deve começar pelo **schema do Postgres** (contrato comum),
depois ramificar nos dois. Pode virar um plano com duas trilhas ou dois planos
encadeados — decisão do writing-plans.

## Decisões em aberto (não bloqueiam o v1)

- **Nome público do jogo** (codinome atos permanece interno).
- **Limiar de concordância** pra virar gold e **alvo de votos/item** — calibrar com os
  primeiros dados reais.
- **Onde o Python lê o Postgres** (read-replica Neon vs dump periódico) — detalhe de infra.
