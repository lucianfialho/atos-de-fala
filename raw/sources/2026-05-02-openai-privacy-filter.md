# OpenAI Privacy Filter — Raw Source

**URL:** https://openai.com/index/privacy-filter/
**Author:** OpenAI
**Type:** Blog post / model release announcement
**Date ingested:** 2026-05-02

## Note
Raw source. Do not modify. See `wiki/sources/2026-05-02-openai-privacy-filter.md` for the processed summary.

---

Apresentando o Filtro de Privacidade da OpenAI — Nosso modelo de última geração para mascarar informações pessoalmente identificáveis (PII) em texto

Hoje estamos lançando o Filtro de Privacidade da OpenAI, um modelo de pesos abertos para detectar e ocultar informações pessoalmente identificáveis (PII) em texto. Este lançamento faz parte de nosso esforço mais amplo para apoiar um ecossistema de software mais resiliente, oferecendo aos desenvolvedores infraestrutura prática para criar com IA de forma segura.

O Filtro de Privacidade é um modelo pequeno com capacidade de detecção de dados pessoais de nível de fronteira. Ele foi projetado para fluxos de trabalho de privacidade de alto throughput e consegue realizar detecção de PII sensível ao contexto em texto não estruturado. Ele pode rodar localmente, o que significa que dados PII podem ser mascarados ou ocultados sem sair da sua máquina. Ele processa entradas longas com eficiência, tomando decisões de ocultação em uma passada única e rápida.

Na OpenAI, usamos uma versão ajustada do Filtro de Privacidade em nossos próprios fluxos de trabalho que preservam a privacidade. A versão do Filtro de Privacidade que estamos lançando hoje alcança desempenho de última geração no benchmark PII-Masking-300k.

**Arquitetura:** O Filtro de Privacidade é um modelo bidirecional de classificação de tokens com decodificação de spans. Ele começa a partir de um checkpoint pré-treinado autorregressivo e depois é adaptado para um classificador de tokens sobre uma taxonomia fixa de rótulos de privacidade. Em vez de gerar texto token a token, ele rotula uma sequência de entrada em uma única passada e, em seguida, decodifica spans coerentes com um procedimento de Viterbi restrito.

Propriedades: Rápido (todos os tokens rotulados em uma única forward pass), sensível ao contexto, suporte a até 128.000 tokens de contexto, configurável.

**Tamanho:** 1.5B parâmetros totais, com 50M parâmetros ativos.

**8 categorias de PII detectadas:**
- private_person
- private_address
- private_email
- private_phone
- private_url
- private_date
- account_number
- secret

Os rótulos são decodificados com tags de spans BIOES.

**Como foi construído:**
1. Taxonomia de privacidade definindo os tipos de spans
2. Checkpoint autorregressivo convertido em classificador bidirecional de tokens (substituição da cabeça de LM por cabeça de classificação)
3. Treinado em mistura de dados públicos + sintéticos
4. Decodificação de spans via decodificação de sequência restrita (Viterbi)

**Performance:** Score F1 de 96% no benchmark PII-Masking-300k (94.04% precisão, 98.04% recall). Fine-tuning com poucos dados: F1 sobe de 54% para 96%.

**Disponibilidade:** Apache 2.0, disponível no Hugging Face e GitHub.
