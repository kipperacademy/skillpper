---
name: project-init
description: Início de projeto e documentação contínua no mesmo fluxo. Originada no pack Bora Automatizar (BA). Em repositórios novos (pouco ou nenhum código) — guia a escolha de stack justificada, estrutura inicial, qualidade e segurança day-1, cravando CHANGELOG.md, ARCHITECTURE.md e ROADMAP.md desde o primeiro commit. Em repositórios em andamento — investiga código e histórico git reais para atualizar os 3 documentos com fidelidade, sem inventar nada.
---

# Project Init & Continuous Documentation 🚀📋

> **Origem:** Desenvolvida e refinada originalmente no pack operacional **Bora Automatizar (BA)** (`/ba-init`).

Esta skill coloca o agente em **modo init**. Ela opera com **duas abordagens complementares**, dependendo do estágio do repositório:

- **Projeto novo** (pouco ou nenhum commit): você atua como um arquiteto day-1. Ajuda a definir stack justificada, estrutura de diretórios limpa, padrões de qualidade (lint, format, types), segurança inicial e já inicia o projeto documentado desde o primeiro commit.
- **Projeto em andamento** (já possui código e histórico): você não altera código de negócio. Investiga o histórico do git, manifests e diretórios reais para criar ou atualizar os 3 documentos essenciais sem alucinações.

O objetivo final é garantir que qualquer desenvolvedor — ou você mesmo daqui a alguns meses — entenda em 5 minutos o que o projeto é, como foi arquitetado e para onde está caminhando.

---

## Os 3 Documentos Canônicos

| Arquivo | O que registra | Fonte da Verdade |
|---|---|---|
| `CHANGELOG.md` | O que mudou e quando | Git log real, formato [Keep a Changelog](https://keepachangelog.com/) |
| `ARCHITECTURE.md` | Como o projeto é construído e por quê | Manifests, pastas, dependências reais e decisões documentadas |
| `ROADMAP.md` | O que já foi entregue vs. o que falta | Changelog + TODOs/issues no código + alinhamento com o usuário |

---

## Quando usar

- Ao criar um repositório novo e precisar de uma estrutura consistente, profissional e documentada.
- Ao entrar em uma base de código existente para mapear sua arquitetura real e histórico.
- Ao fechar marcos de desenvolvimento, releases ou sprints para atualizar a documentação de forma contínua e idempotente.
- Para manter o contexto técnico vivo e acessível para desenvolvedores e agentes de IA.

---

## Como trabalhar

### 1. Detecte o estágio do projeto

Antes de executar ações, inspecione o estado atual:
```bash
# Verificar maturidade do histórico git
git log --oneline | wc -l

# Verificar se os documentos já existem
ls CHANGELOG.md ARCHITECTURE.md ROADMAP.md 2>/dev/null
```

Isso determina se você seguirá o fluxo de **Projeto Novo** ou **Projeto em Andamento**.

---

### 2a. Fluxo: Projeto Novo (Pouco ou nenhum código)

O primeiro commit define o padrão da base de código:

1. **Escolha de stack justificada:**
   - Proponha tecnologias adequadas ao escopo e objetivos do projeto.
   - Justifique cada escolha com uma frase objetiva (evite "porque é popular" ou "porque sempre usamos").
2. **Estrutura de diretórios limpa:**
   - Organize pastas de forma modular e intuitiva (`src/`, `tests/`, `docs/`, etc.).
3. **Qualidade desde o Day-1:**
   - Configurações reais de linter e formatação (ex: Biome, ESLint, Prettier, Ruff, golangci-lint).
   - `.env.example` com chaves documentadas e valores de exemplo seguros (nunca credenciais reais).
   - Tipagem estrita ativada quando suportada pela linguagem.
4. **Segurança e isolamento:**
   - Se houver containerização (Docker): `.dockerignore` obrigatório, multi-stage build, execução como usuário não-root e nenhuma secret embutida na imagem.
5. **Criação dos 3 documentos iniciais:**
   - `CHANGELOG.md`: Versão `[Unreleased]` ou `[0.1.0]` com os primeiros itens reais criados.
   - `ARCHITECTURE.md`: Stack decidida, estrutura de pastas e comandos exatos para rodar o projeto localmente.
   - `ROADMAP.md`: Checklist com o que foi entregue no setup inicial (`- [x]`) e próximos passos imediatos (`- [ ]`).

---

### 2b. Fluxo: Projeto em Andamento (Código existente)

**Investigue antes de escrever — nunca suponha:**

1. **Investigue o histórico de commits:**
   ```bash
   git log --all --date=short --pretty=format:"%ad %s"
   git tag
   ```
2. **Inspecione a stack e dependências reais:**
   - Analise `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json` ou equivalentes.
   - Mapeie a árvore de diretórios principal.
3. **Mapeie pendências técnicas no código:**
   - Procure marcadores como `TODO`, `FIXME` e `HACK` para identificar trabalhos em aberto.
4. **Respeite o que já existe:**
   - Se os documentos já existirem, leia-os na íntegra primeiro.
   - Faça uma atualização incremental (delta) das novidades desde a última versão registrada, preservando o histórico anterior.

---

### 3. Padrão de Redação dos Documentos

#### `CHANGELOG.md`
- Estrutura baseada em [Keep a Changelog](https://keepachangelog.com/):
  ```markdown
  # Changelog

  Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.
  O formato é baseado em [Keep a Changelog](https://keepachangelog.com/).

  ## [Unreleased]
  ### Added
  - Nova funcionalidade descrita em linguagem clara.

  ### Fixed
  - Correção de bug baseada em commits reais.
  ```
- Agrupe commits relacionados em itens claros e compreensíveis para humanos.

#### `ARCHITECTURE.md`
Seções essenciais:
- **Visão Geral e Stack:** Tecnologias adotadas e o motivo pragmático de cada uma.
- **Estrutura de Pastas:** Papel de cada pasta principal no repositório.
- **Como Rodar:** Comandos reais, testados e funcionais (instalação, execução, testes).
- **Serviços Externos:** Bancos de dados, filas, APIs e provedores de infraestrutura.
- **Decisões Arquiteturais e Trade-offs:** Escolhas técnicas deliberadas que diferem do padrão óbvio. Caso o motivo não seja identificável no código, sinalize como `(motivo não documentado — confirmar)` em vez de criar justificativas fictícias.

#### `ROADMAP.md`
- **Feito (`- [x]`):** Entregas comprovadas no código e no changelog.
- **Em andamento (`- [ ]`):** Tarefas identificadas em branches ativas ou comentários de código.
- **Planejado (`- [ ]`):** Próximos passos confirmados com os mantenedores.
- Evite datas rígidas de calendário; prefira checklists ordenados por prioridade.

---

## Regras Inegociáveis

1. **Fidelidade absoluta aos fatos:** Nunca invente decisões arquiteturais, justificativas ou entradas de changelog que o código ou o git não sustentem.
2. **Idempotência:** A reexecução da skill em um repositório deve atualizar os documentos existentes de forma aditiva, sem sobrescrever ou apagar histórico válido.
3. **Não alterar código de produto no modo em andamento:** No modo de projeto existente, apenas a documentação (`CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`) é alterada. Não faça refatorações nem mude dependências sem solicitação explícita.
4. **Sem placeholders vazios no Day-1:** Em projetos novos, tudo o que for gerado deve funcionar de verdade (comandos reais e testáveis).

---

## Resultado Esperado

Ao concluir a execução, o agente deve relatar:
- Quais documentos foram criados ou atualizados.
- Resumo conciso (2 a 4 linhas) do delta ou da arquitetura documentada.
- Lista explícita de dúvidas ou decisões que necessitam de confirmação com o time.
