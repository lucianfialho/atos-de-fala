# Atos de Fala PT-BR 🗣️



## Demonstração

Veja abaixo uma demonstração rápida do fluxo principal do projeto:

[Assistir demonstração do projeto Atos de Fala](docs/assets/demo.mp4)

**Atos de Fala PT-BR** é um projeto aberto para ensinar computadores a entender não só *o que* uma pessoa escreveu, mas *com que intenção* ela escreveu.

Em vez de olhar para uma frase apenas como positiva, negativa ou neutra, o projeto identifica trechos do texto e classifica cada um como um **ato de fala**: informar, perguntar, pedir, agradecer, discordar, prometer, sugerir e outros movimentos comunicativos comuns no português brasileiro.

> Exemplo: em “Oi! Você pode revisar isso? Obrigado!”, há pelo menos três intenções: **saudar**, **pedir** e **agradecer**.

## Por que isso importa?

Grande parte da comunicação humana está na intenção. Uma mesma frase pode informar, pedir, ironizar, concordar, recusar ou encerrar uma conversa. Para sistemas de IA em português, reconhecer essas intenções ajuda a criar ferramentas mais úteis, educadas e sensíveis ao contexto.

Este projeto pode apoiar pesquisas e aplicações em:

- análise de conversas e atendimento;
- educação linguística e pragmática;
- melhoria de assistentes virtuais em PT-BR;
- estudo de como diferentes pessoas interpretam intenções;
- construção de bases abertas para PLN em português.

## O que o projeto faz

O repositório reúne um ecossistema completo para classificação de atos de fala em português brasileiro:

- **Taxonomia de 13 atos de fala**, inspirada em estudos de pragmática, Searle e ISO 24617-2;
- **Anotação por spans**, isto é, cada trecho relevante do texto recebe sua própria intenção;
- **Modelo de classificação por tokens**, usando BERTimbau com marcação BIOES;
- **Ferramentas de validação, estatísticas e avaliação** para medir qualidade dos dados e do modelo;
- **Interface colaborativa em formato de jogo**, onde pessoas podem revisar classificações e sugerir melhorias;
- **Demo em Gradio**, pensada para experimentar o classificador de forma simples.

## Atos reconhecidos

A versão atual trabalha com os seguintes atos:

| Ato | Ideia central |
|---|---|
| `informar` | declarar ou fornecer informação |
| `perguntar` | solicitar informação |
| `concordar` | manifestar acordo |
| `discordar` | manifestar desacordo |
| `pedir` | solicitar uma ação |
| `sugerir` | propor uma ação sem impor |
| `oferecer` | oferecer ajuda, recurso ou ação |
| `prometer` | assumir compromisso futuro |
| `saudar` | iniciar contato social |
| `agradecer` | expressar gratidão |
| `desculpar` | pedir desculpas |
| `despedir` | encerrar contato social |
| `expressar_emocao` | manifestar emoção ou avaliação afetiva |

## Estrutura do repositório

```text
config/        Taxonomia e rubrica de anotação
src/chomsky/   Código Python principal: dados, treino, avaliação e utilitários
web/           Interface colaborativa em Next.js
db/            Esquema de dados da coleta colaborativa
space/         Demo Gradio para experimentação
tests/         Testes automatizados do projeto
wiki/          Notas de pesquisa e síntese teórica
```

## Como experimentar

### Código Python

```bash
pip install -e .[dev]
pytest
```

### Demo Gradio

```bash
cd space
pip install -r requirements.txt
python app.py
```

### Interface web

```bash
cd web
npm install
npm test
```

## Como colaborar

Este projeto precisa de pessoas com diferentes perfis. Você pode ajudar mesmo sem ser especialista em IA.

Boas formas de contribuição:

- revisar exemplos e dizer se a intenção marcada faz sentido;
- sugerir frases reais do português brasileiro, de diferentes regiões e contextos;
- melhorar textos, documentação e materiais didáticos;
- testar a interface e relatar problemas de usabilidade;
- propor refinamentos na taxonomia;
- adicionar testes;
- melhorar avaliação, visualização e análise dos resultados;
- contribuir com pesquisa linguística, pragmática e PLN.

Se você gosta de língua portuguesa, linguística, dados abertos, IA responsável ou ferramentas educacionais, este é um ótimo lugar para colaborar.

## Visão

A ambição do **Atos de Fala PT-BR** é criar uma base aberta, didática e útil para que modelos entendam melhor as intenções comunicativas em português brasileiro.

Queremos que o projeto seja ao mesmo tempo:

- **científico**, com base teórica clara;
- **prático**, com código testável e modelos utilizáveis;
- **colaborativo**, com participação humana na melhoria dos dados;
- **didático**, para aproximar PLN, linguística e comunidade.

## Licença

Consulte os arquivos do projeto para detalhes de licença e uso.

---

**Participe.** Cada frase revisada ajuda a ensinar a IA a compreender melhor como brasileiros realmente se comunicam.
