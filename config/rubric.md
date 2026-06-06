<!-- config/rubric.md -->
<!-- FROZEN v1 (2026-06-05) — 13 acts (ISO 24617-2 + Searle); rules from Fase-0 papers. -->
# Rúbrica de Anotação — Atos de Fala (PT-BR)

Você anota **atos de fala** em texto portugues. Cada span e um trecho **contiguo e literal**
do texto que realiza um ato. Spans **NAO se sobrepoem**. Use APENAS os 13 atos abaixo.

## Os 13 atos

- **informar** — prover/declarar informacao (assertivo). Ex.: "O relatorio esta pronto."
- **perguntar** — solicitar informacao. Ex.: "Que horas sao?"
- **concordar** — manifestar acordo. Ex.: "Sim, exatamente."
- **discordar** — manifestar desacordo. Ex.: "Nao acho isso."
- **pedir** — requisitar ou ordenar uma acao (inclui instrucao/comando). Ex.: "Me envia o arquivo?" / "Aperte a tecla 13."
- **sugerir** — propor sem obrigar. Ex.: "Talvez seja melhor esperar."
- **oferecer** — oferecer-se para fazer/dar algo. Ex.: "Posso te ajudar com isso."
- **prometer** — comprometer-se com acao futura. Ex.: "Eu te aviso amanha."
- **saudar** — iniciar contato. Ex.: "Bom dia!"
- **agradecer** — expressar gratidao. Ex.: "Muito obrigado!"
- **desculpar** — pedir desculpas. Ex.: "Me desculpe pelo atraso."
- **despedir** — encerrar contato. Ex.: "Ate logo!"
- **expressar_emocao** — manifestar emocao/avaliacao afetiva (inclui elogio, parabens, pesar). Ex.: "Que alivio!" / "Parabens!"

## Regras (importantes)

1. **Rotulo mais especifico.** Se um trecho e informacao E desacordo, use `discordar`. "Isso e uma vergonha" -> `discordar`, nao `informar`.
2. **Descrever um ato != realizar o ato.** Relatar que alguem fez algo e `informar`. Ex.: "Vettel pediu desculpas a equipe" -> `informar` (relata uma desculpa), NAO `desculpar`.
3. **Pedido indireto = `pedir`.** Em PT-BR, interrogativa com poder/querer/conseguir e diretivo. "Voce poderia me enviar?" -> `pedir`, nao `perguntar`.
4. **Nao distinguir o que fundimos.** Responder/elaborar/explicar/confirmar -> `informar`. Instruir/ordenar -> `pedir`. Elogiar/parabenizar/lamentar -> `expressar_emocao`.
5. **Quotes literais.** Cada "quote" deve ser uma substring EXATA e contigua do texto.
6. **Spans nao se sobrepoem.** Trechos sem ato ficam de fora (sem rotulo).

## Exemplo anotado

Texto: "Oi! Voce poderia me mandar o relatorio? Prometo revisar hoje. Obrigado!"
```json
{"text": "Oi! Voce poderia me mandar o relatorio? Prometo revisar hoje. Obrigado!",
 "spans": [
   {"quote": "Oi!", "act": "saudar"},
   {"quote": "Voce poderia me mandar o relatorio?", "act": "pedir"},
   {"quote": "Prometo revisar hoje.", "act": "prometer"},
   {"quote": "Obrigado!", "act": "agradecer"}
 ]}
```

## Apêndice A — casos de borda (adaptado de SweDicS / Tufvesson 2024)

Regras de borda das guidelines do SweDicS (`raw/sources/2024-swedics-tufvesson-annotation-guidelines.pdf`),
traduzidas pro nosso modelo. **Divergência-chave:** o SweDicS é *sentence-level* e rotula a
frase complexa pelo **ato principal pretendido** (uma subordinada que só dá contexto some no ato
da principal). **Nós NÃO fazemos isso** — somos *span-level*: cada ato vira seu próprio span.
Então só importamos os casos **atômicos** abaixo, não a regra de colapso.

7. **Desejo/medo ≠ pedido.** Expressar querer/temer algo é `expressar_emocao`, não `pedir` nem `prometer`. "Queria tanto um carro!" / "Nunca faria isso." -> `expressar_emocao`.
8. **Link/data/número/nome sozinho = `informar`** (é uma asserção). Com "?" no fim -> `perguntar`. Ex.: "2017-08-22" -> `informar`; "Henrique?" -> `perguntar`.
9. **Lixo não vira span.** Fragmento quebrado, frases coladas por erro de segmentação, emoji solto, ou texto majoritariamente em outra língua (>50%): **deixe fora** (sem rótulo). É o nosso equivalente ao "Other" deles (que eles descartam).
10. **Na dúvida, não force.** Trecho genuinamente ambíguo entre atos: prefira **deixar sem rótulo** a chutar. (Equivale ao "Unsure", também descartado por eles.) Para o gold humano coletivo isso vira um botão "incerto/lixo" — controle de qualidade, não label.
11. **Pergunta retórica = use a regra 1 (mais específico).** Interrogativa que na real é crítica/desacordo -> `discordar`/`expressar_emocao`, não `perguntar`. (O SweDicS, por ser coarse, mantém como Question; nós somos mais finos.)
12. **Saudar ≠ despedir.** Eles juntam ambos em "Greeting"; aqui são atos distintos: abertura (`saudar`) vs encerramento (`despedir`).

## Apêndice B — macro-classes (eval coarse)

Para avaliação coarse / sentence-level (`atos.train.eval_cli --coarse`), os 13 atos colapsam
nas classes ilocucionárias de Searle (campo `macro` em `config/taxonomy.yaml`):
`assertivo` (informar, concordar, discordar) · `pergunta` (perguntar) · `diretivo` (pedir, sugerir) ·
`comissivo` (oferecer, prometer) · `expressivo` (saudar, agradecer, desculpar, despedir, expressar_emocao).
Nota: o esquema 4-classes do SweDicS **não tem comissivo** — `oferecer`/`prometer` não têm casa lá;
por isso aqui usamos as 5 de Searle, mais corretas, e não as 4 deles.
