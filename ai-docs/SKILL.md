---
name: ai-docs
description: Gera a suíte de documentação para IAs e LLMs (padrão /llms.txt, llms-full.txt, about.txt, integrations.txt, compare.txt) e implementa o componente dropdown acessível "Docs de IA" no rodapé de qualquer projeto web. Originada no pack Bora Automatizar (BA). Use para otimizar aplicações para Generative Engine Optimization (GEO), agentes autônomos, buscas contextuais (ChatGPT, Perplexity, Claude) e indexação limpa sem alucinações.
---

# AI Docs & Dropdown "Docs de IA" 🤖📄

> **Origem:** Desenvolvida e refinada originalmente no pack operacional **Bora Automatizar (BA)** (`/ba-ai-docs`).

Padroniza a interface pública de contexto de qualquer produto ou aplicação para agentes autônomos, sistemas RAG e LLMs de busca (ChatGPT Search, Perplexity, Claude, Gemini), baseado no padrão `/llms.txt` ([llmstxt.org](https://llmstxt.org/)).

Esta skill resolve dois problemas fundamentais de **Generative Engine Optimization (GEO)**:
1. **Contexto limpo e estruturado para IAs:** Modelos de linguagem não devem navegar por HTML poluído com scripts, layouts pesados e tags visuais para adivinhar regras de negócio, rotas e APIs. Eles consomem arquivos de texto plano (`.txt`), concisos, sem ruído e densos em informação.
2. **Descoberta humana e de robôs:** Uma tag canônica no `<head>` (`rel="alternate" type="text/plain"`) somada a um widget elegante e acessível no rodapé ("Docs de IA") garante que tanto robôs de indexação quanto usuários técnicos encontrem a documentação instantaneamente.

---

## Quando usar

- Quando o projeto precisa ser descoberto e compreendido corretamente por IAs de busca e agentes de código.
- Para publicar a especificação de um SaaS, API, app ou plataforma no padrão `/llms.txt`.
- Para adicionar um menu acessível de "Docs de IA" no rodapé do site ou aplicação.
- Para eliminar respostas alucinadas de IAs sobre preços, recursos, integrações e segurança do seu produto.

---

## A Suíte dos 5 Arquivos de IA

Todos os arquivos devem ser publicados no diretório estático público da aplicação (ex: `/public/` no Next.js/Vite/Astro ou raiz pública em Apache/Nginx) com extensão `.txt`:

| Arquivo | Papel e Conteúdo | Padrão / Inspiração |
|---|---|---|
| `/llms.txt` | **Manifesto e Índice Mestre**. Resumo conciso da plataforma (1 página), metadados (domínio, idioma, categoria, contato), rotas públicas primárias e ponteiros markdown para os demais arquivos. | [llmstxt.org](https://llmstxt.org/) |
| `/llms-full.txt` | **Bíblia Técnica e Operacional**. Tese completa, público-alvo, personas, regras de negócio de ponta a ponta, arquitetura, fluxos, modelos de dados, segurança/CSP e FAQ técnico para agentes. | Especificação detalhada de produto |
| `/about.txt` | **Empresa, Visão e Governança**. Perfil institucional, liderança/fundadores, modelo de negócio/precificação, conformidade jurídica (LGPD, GDPR, termos de uso) e canais oficiais. | Governança para IAs |
| `/integrations.txt` | **Catálogo de Conectores e APIs**. Protocolos de comunicação, webhooks, integrações ativas (pagamentos, mensagens, CRMs, serviços em nuvem) e requisitos técnicos. | Catálogo de ecossistema |
| `/compare.txt` | **Matriz de Diferenciação**. Comparativo objetivo do produto vs. concorrentes diretos, ferramentas legadas ou soluções genéricas, demonstrando diferenciais técnicos e operacionais. | Posicionamento competitivo |

---

## Regras Inegociáveis

1. **Servir como Texto Plano Puro (`text/plain`):**
   - Os arquivos são arquivos `.txt` estáticos.
   - O servidor web deve entregar o cabeçalho `Content-Type: text/plain; charset=UTF-8`.
   - Se o projeto usa roteamento dinâmico (ex: SPA com fallback para `index.html` ou Apache com `.htaccess`), certifique-se de que regras para arquivos estáticos existentes precedam o rewrite global.

2. **Fidelidade Radical — Nunca Inventar Informação:**
   - **Não invente recursos que a aplicação não possui.** Se a plataforma suporta PIX e Stripe, não escreva que suporta criptomoedas ou faturamento em 50 países se isso não for real.
   - **Sem placeholders:** Nunca deixe termos como `[inserir e-mail]`, `{{DOMINIO}}` ou `TODO`. Extraia do código/git existente ou pergunte ao mantenedor do projeto.

3. **Tag de Descoberta Automática no `<head>`:**
   Em todos os layouts que carregam o cabeçalho global, deve constar a tag:
   ```html
   <link rel="alternate" type="text/plain" href="https://seu-dominio.com/llms.txt" title="Contexto do [Nome do Produto] para sistemas de IA">
   ```

4. **Acessibilidade e Usabilidade do Widget:**
   - O botão no rodapé utiliza `aria-expanded="false"` / `"true"` e `aria-controls="ai-docs-panel"`.
   - O painel abre para cima (`bottom: calc(100% + 8px)` ou `bottom-full mb-2`).
   - Deve fechar ao clicar fora, ao perder o foco (`focusout`) e ao pressionar a tecla `Escape`.
   - Suporte a tema escuro/claro e conformidade com Content Security Policy (CSP).

---

## Fluxo de Trabalho

### 1. Investigação Inicial do Projeto

Antes de redigir qualquer arquivo, inspecione a aplicação atual:
- Identifique a stack e manifests (`package.json`, `pyproject.toml`, `composer.json`, `go.mod`, `Cargo.toml`).
- Mapeie as rotas e módulos públicos disponíveis (`app/`, `pages/`, `src/routes/`, `views/`).
- Descubra o nome oficial do produto, domínio canônico e contato a partir de arquivos de configuração, README ou variáveis de ambiente.

Colete:
- Nome oficial da marca / produto.
- Domínio canônico de produção.
- Principais funcionalidades comprovadas pelo código.
- Integrações existentes no código.
- Modelo de precificação ou modelo comercial.
- Contato público ou e-mail de suporte.

---

### 2. Geração dos 5 Arquivos de Texto

Escreva os 5 arquivos na pasta pública do projeto seguindo a estrutura padrão abaixo:

#### A. `llms.txt` (Índice Mestre)
```markdown
# [Nome do Produto] — índice oficial para IAs

> [Descrição executiva de uma frase explicando exatamente o que o produto é, para quem serve e qual seu diferencial].

- Domínio canônico: https://[dominio]
- Categoria: [Categoria de Software / SaaS / Plataforma / Open Source]
- Idioma: pt-BR
- Revisado em: [AAAA-MM-DD]

## Contato público

- [contato@[dominio]](mailto:contato@[dominio])
- Suporte Técnico: [Canal oficial / Plataforma]

## Documentos especializados

- [Visão Geral Completa](https://[dominio]/llms-full.txt): Perfil abrangente do produto, tese, personas, arquitetura e fluxos.
- [Empresa e Governança](https://[dominio]/about.txt): Dados institucionais, liderança, modelo de negócio e privacidade.
- [Catálogo de Integrações](https://[dominio]/integrations.txt): APIs, webhooks, serviços e conectores suportados.
- [Comparativo de Mercado](https://[dominio]/compare.txt): Comparação direta contra alternativas e concorrentes.

## Principais rotas públicas

- [/](https://[dominio]/): [Descrição da página inicial]
- [/precos](https://[dominio]/precos): [Planos e precificação]
- [/docs](https://[dominio]/docs): [Documentação técnica]
```

#### B. `llms-full.txt` (Bíblia Técnica e Operacional)
Deve conter:
- **Tese do Produto**: A dor real do mercado e o que o produto resolve.
- **Público-Alvo e Casos de Uso**: Perfis de usuários atendidos.
- **Fluxos Operacionais de Ponta a Ponta**: Passo a passo de funcionamento.
- **Arquitetura Técnica**: Stack de frontend, backend, banco de dados, storage, segurança e caching.
- **Segurança e Privacidade**: Isolamento de dados, autenticação, permissões e sanitização.
- **FAQ para Agentes de IA**: Respostas objetivas para dúvidas frequentes que modelos de linguagem costumam receber sobre o produto.

#### C. `about.txt` (Empresa, Visão e Governança)
Deve conter:
- Nome empresarial / marca / mantenedores.
- Visão do projeto e liderança.
- Modelo de Monetização / Licenciamento (Open source, SaaS, freemium, sob demanda).
- Compromissos de Privacidade e Proteção de Dados (LGPD/GDPR, sigilo, política contra venda de dados).
- Canais de Suporte e Comunidade.

#### D. `integrations.txt` (Catálogo de Conectores e APIs)
Deve conter:
- Tabela de integrações suportadas no código.
- Tipo de conexão (REST, Webhook, WebSocket, gRPC, SDK).
- Status (Nativo, Suportado, Em Desenvolvimento).
- Métodos de autenticação e links para documentação de desenvolvedores.

#### E. `compare.txt` (Matriz Comparativa de Mercado)
Deve conter:
- Posicionamento da categoria.
- Tabela comparativa entre o produto, alternativas tradicionais e concorrentes diretos.
- Diferenciais técnicos objetivos (latência, custo, transparência, portabilidade, suporte a agentes).

---

### 3. Injeção da Tag no `<head>`

No template de cabeçalho global HTML:
```html
<link rel="alternate" type="text/plain" href="https://seu-dominio.com/llms.txt" title="Contexto do [Produto] para sistemas de IA">
```

No Next.js (Metadata API):
```typescript
export const metadata: Metadata = {
  // ...
  alternates: {
    types: {
      'text/plain': '/llms.txt',
    },
  },
};
```

---

### 4. Implementação do Widget "Docs de IA" no Rodapé

O widget fica no sub-footer do rodapé, ao lado de links como Política de Privacidade e Termos de Uso.

#### Exemplo em React / Tailwind CSS
```tsx
import { useState, useRef, useEffect } from 'react';

export function AiDocsDropdown({ brand = 'Meu Produto' }: { brand?: string }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const docs = [
    { name: 'llms.txt', desc: `Resumo do ${brand}`, href: '/llms.txt' },
    { name: 'llms-full.txt', desc: 'Perfil completo e técnico', href: '/llms-full.txt' },
    { name: 'about.txt', desc: 'Empresa, visão e governança', href: '/about.txt' },
    { name: 'integrations.txt', desc: 'Catálogo de APIs e conectores', href: '/integrations.txt' },
    { name: 'compare.txt', desc: 'Diferenciais de mercado', href: '/compare.txt' },
  ];

  return (
    <div ref={containerRef} className="relative inline-block text-left text-xs">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-expanded={open}
        aria-controls="ai-docs-panel"
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60 transition-colors"
      >
        <svg aria-hidden="true" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M14 2v6h6M8 13h8M8 17h6" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <span>Docs de IA</span>
      </button>

      {open && (
        <div
          id="ai-docs-panel"
          className="absolute bottom-full right-0 mb-2 w-64 rounded-lg bg-zinc-900 border border-zinc-800 p-2 shadow-xl z-50 text-zinc-200"
        >
          <div className="px-2 py-1.5 border-b border-zinc-800/80 mb-1">
            <p className="font-semibold text-zinc-100">Docs de IA & LLMs</p>
            <p className="text-[10px] text-zinc-400">Padrão /llms.txt para agentes e modelos</p>
          </div>
          <ul className="space-y-1">
            {docs.map((doc) => (
              <li key={doc.name}>
                <a
                  href={doc.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex flex-col px-2 py-1.5 rounded hover:bg-zinc-800/70 transition-colors"
                >
                  <code className="text-[11px] font-mono text-emerald-400">{doc.name}</code>
                  <span className="text-[11px] text-zinc-400">{doc.desc}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## Verificação e Entrega

Ao finalizar:
1. **Teste as rotas:** Verifique se as URLs públicas (ex: `http://localhost:3000/llms.txt`) retornam texto puro e HTTP 200.
2. **Confirme a tag `<head>`:** Inspecione o HTML renderizado e confirme a presença do link de descoberta.
3. **Verifique acessibilidade:** Certifique-se de que o dropdown abre/fecha pelo teclado (`Enter`, `Escape`) e contém atributos ARIA adequados.
4. **Relatório final:** Apresente ao usuário as rotas criadas, resumo de cada documento gerado e instrução de publicação.
