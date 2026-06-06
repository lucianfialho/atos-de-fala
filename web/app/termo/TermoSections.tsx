const H2_STYLE: React.CSSProperties = {
  fontSize: "clamp(18px, 2.5vw, 22px)",
  marginBottom: 12,
};

const P_STYLE: React.CSSProperties = {
  fontSize: 16,
  lineHeight: 1.75,
  color: "var(--body)",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 32 }}>
      <h2 className="display" style={H2_STYLE}>{title}</h2>
      {children}
    </section>
  );
}

export function TermoSections() {
  return (
    <>
      <Section title="1. O que é o Atos de Fala">
        <p style={P_STYLE}>
          O Atos de Fala é um projeto de pesquisa aberta que coleta anotações humanas sobre a
          intenção (ato de fala) de trechos de texto em português brasileiro, para treinar e
          avaliar modelos de inteligência artificial de linguagem. A participação é voluntária
          e anônima.
        </p>
      </Section>

      <Section title="2. O que coletamos">
        <ul style={{ ...P_STYLE, paddingLeft: 20, marginBottom: 16 }}>
          <li style={{ marginBottom: 8 }}>
            Suas avaliações (confirmar, corrigir ou marcar "não sei") e suas sugestões de
            outras formas de dizer.
          </li>
          <li style={{ marginBottom: 8 }}>
            Um perfil demográfico anônimo: faixa de idade, gênero, estado (UF) e escolaridade.
          </li>
          <li>
            Um identificador anônimo gerado e guardado no seu navegador, só para evitar
            repetições e somar seus pontos.
          </li>
        </ul>
        <p style={P_STYLE}>
          Não coletamos nome, e-mail, telefone, nem qualquer dado que identifique você
          diretamente.
        </p>
      </Section>

      <Section title="3. Como usamos">
        <p style={P_STYLE}>
          Suas contribuições são usadas para (a) construir um conjunto de dados de atos de fala
          em português; (b) treinar e avaliar modelos de IA; (c) pesquisar se perfis diferentes
          percebem intenções diferentes na mesma frase.
        </p>
      </Section>

      <Section title="4. Dataset aberto (CC BY 4.0)">
        <p style={P_STYLE}>
          As contribuições anônimas podem ser publicadas em um dataset aberto sob licença
          Creative Commons Atribuição 4.0 (CC BY 4.0) e reutilizadas por qualquer pessoa,
          inclusive para treinar IA. Ao participar, você concorda com essa publicação.
        </p>
      </Section>

      <Section title="5. Voluntariedade e idade">
        <p style={P_STYLE}>
          A participação é voluntária e você pode parar quando quiser. É restrita a maiores
          de 18 anos.
        </p>
      </Section>

      <Section title="6. Privacidade (LGPD)">
        <p style={P_STYLE}>
          Tratamos os dados de forma anônima; a base legal é o seu consentimento (Lei nº
          13.709/2018 – LGPD). Como o dataset é agregado e anonimizado, contribuições já
          publicadas não podem ser revertidas individualmente. Enquanto seus dados estiverem
          associados ao identificador do seu navegador, você pode solicitar a remoção pelo
          contato abaixo.
        </p>
      </Section>

      <Section title="7. Seus direitos">
        <p style={P_STYLE}>
          Nos termos da LGPD, você pode solicitar informações sobre o tratamento e a eliminação
          dos dados ainda associados ao seu identificador, pelo contato abaixo.
        </p>
      </Section>

      <Section title="8. Contato">
        <p style={P_STYLE}>
          <a href="mailto:lucian@metricasboss.com.br" style={{ color: "var(--body)", textDecoration: "underline", textUnderlineOffset: 3 }}>
            lucian@metricasboss.com.br
          </a>
        </p>
      </Section>

      <section>
        <h2 className="display" style={H2_STYLE}>9. Alterações</h2>
        <p style={P_STYLE}>
          Este termo pode ser atualizado; a data no topo indica a última versão.
        </p>
      </section>
    </>
  );
}
