import type { Metadata } from "next";
import { IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

const plex = IBM_Plex_Sans({
  variable: "--font-sans",
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://atos-de-fala.vercel.app"),
  title: "Atos de Fala — ensine a IA a entender a intenção em português",
  description:
    "Jogo de dataset aberto: ajude a IA a entender a intenção (ato de fala) por trás do que a gente diz em português brasileiro. Anônimo, leva 2 minutos.",
  openGraph: {
    title: "Atos de Fala — ensine a IA a entender a intenção em português",
    description:
      "Ajude a IA a entender a intenção por trás do que a gente diz. Dataset aberto, anônimo.",
    url: "https://atos-de-fala.vercel.app",
    siteName: "Atos de Fala",
    locale: "pt_BR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Atos de Fala — ensine a IA a entender a intenção",
    description: "Dataset aberto de atos de fala em PT-BR. Anônimo, 2 minutos.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={plex.variable}>
      <body>{children}</body>
    </html>
  );
}
