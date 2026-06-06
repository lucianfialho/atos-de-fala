const H2_STYLE: React.CSSProperties = {
  fontSize: "clamp(18px, 2.5vw, 22px)",
  marginBottom: 12,
};

const P_STYLE: React.CSSProperties = {
  fontSize: 16,
  lineHeight: 1.75,
  color: "var(--body)",
};

const LINK_STYLE: React.CSSProperties = {
  color: "var(--body)",
  textDecoration: "underline",
  textUnderlineOffset: 3,
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 32 }}>
      <h2 className="display" style={H2_STYLE}>{title}</h2>
      {children}
    </section>
  );
}

export function SobreSections() {
  return (
    <>
      <Section title="Por que existe">
        <p style={P_STYLE}>
          Quando você diz &ldquo;você poderia revisar isso?&rdquo;, não é uma pergunta — é um
          pedido. Esses são os atos de fala: o que a gente faz com as palavras (pedir, agradecer,
          discordar, prometer, se despedir). Modelos de IA erram isso o tempo todo em português,
          porque não existe — até onde sabemos — um corpus nem um modelo aberto que classifique
          atos de fala trecho a trecho (span-level) para o português brasileiro. O Atos de Fala
          existe pra mudar isso, com dado aberto e gente real.
        </p>
      </Section>

      <Section title="A pergunta de pesquisa">
        <p style={P_STYLE}>
          Tem uma questão que ninguém respondeu pro PT-BR: pessoas de perfis diferentes percebem
          intenções diferentes na mesma frase? Um nordestino e um paulista, alguém de 20 e alguém
          de 50 — leem o mesmo &ldquo;que tal?&rdquo; como sugestão ou como cobrança? Por isso o
          jogo é anônimo, mas pergunta seu perfil (idade, gênero, região, escolaridade): a variação
          de percepção por perfil é o que torna esse dataset único.
        </p>
      </Section>

      <Section title="Como funciona">
        <p style={P_STYLE}>
          Um modelo (BERTimbau ajustado) chuta o ato de cada trecho de uma frase. Você confirma,
          corrige, ou marca &ldquo;não sei&rdquo;. De vez em quando entra uma frase-isca com
          resposta conhecida — é o controle de qualidade: quem acerta as iscas tem o voto com
          mais peso na hora de fechar o &ldquo;gold&rdquo;. Quando várias pessoas concordam, o
          trecho vira dado confiável; quando discordam, isso é justamente o sinal de pesquisa.
        </p>
      </Section>

      <Section title="Honestidade do v1">
        <p style={P_STYLE}>
          O texto que você anota hoje é sintético: foi gerado por um LLM (DeepSeek), que também
          deu o primeiro palpite dos atos. Funciona pra começar (não havia corpus pronto), mas
          tem o sabor e o viés de texto de máquina. É por isso que o jogo existe: as suas
          correções viram o gold humano que treina o v2 — melhor e mais real. O modelo erra;
          melhorar isso é um esforço coletivo.
        </p>
      </Section>

      <Section title="Aberto de ponta a ponta">
        <ul style={{ ...P_STYLE, paddingLeft: 20, marginBottom: 0 }}>
          <li style={{ marginBottom: 8 }}>
            <a
              href="https://github.com/lucianfialho/atos-de-fala"
              style={LINK_STYLE}
              target="_blank"
              rel="noopener noreferrer"
            >
              Código no GitHub
            </a>
          </li>
          <li style={{ marginBottom: 8 }}>
            <a
              href="https://huggingface.co/lucianfialho/atos-de-fala-ptbr"
              style={LINK_STYLE}
              target="_blank"
              rel="noopener noreferrer"
            >
              Modelo no Hugging Face
            </a>
          </li>
          <li style={{ marginBottom: 8 }}>
            <a
              href="https://huggingface.co/spaces/lucianfialho/atos-de-fala-ptbr"
              style={LINK_STYLE}
              target="_blank"
              rel="noopener noreferrer"
            >
              Demo (Space)
            </a>
          </li>
          <li>
            Dataset: será publicado sob licença CC BY 4.0 quando houver volume.
          </li>
        </ul>
      </Section>

      <Section title="Quem">
        <p style={P_STYLE}>
          Feito por Lucian Fialho. Contato:{" "}
          <a href="mailto:lucian@metricasboss.com.br" style={LINK_STYLE}>
            lucian@metricasboss.com.br
          </a>
        </p>
        <p style={{ ...P_STYLE, fontSize: 14, color: "var(--muted)", marginTop: 12 }}>
          O codinome interno do projeto é &ldquo;chomsky&rdquo; — uma ironia de propósito: a base
          teórica é a pragmática (Searle / ISO 24617-2), não a sintaxe chomskyana.
        </p>
      </Section>
    </>
  );
}
