<h1 align="center">Welcome to Skillpper 🐿️ </h1>

<p align="center">
<img src="./logo.png" alt="Skillpper mascot" width="150">
</p>

<p align="center">
 <em> Practical skills for developers and their AI coding agents 🤓 </em>
</p>

---

Skillpper is a community collection of reusable instructions for everyday development work: designing interfaces, researching technical topics, and sharing workflows that work. Each skill gives your agent a focused process, useful references, and clear expectations for the result.

Browse the collection, install the skills that fit your work, and contribute what you learn along the way.

## Skills

This index is generated from the `name` and `description` in each root-level skill's `SKILL.md`. Descriptions keep their original language.

<!-- SKILLS:START -->

| Skill | Description |
| --- | --- |
| [ai-docs](./ai-docs/SKILL.md) | Gera a suíte de documentação para IAs e LLMs (padrão /llms.txt, llms-full.txt, about.txt, integrations.txt, compare.txt) e implementa o componente dropdown acessível "Docs de IA" no rodapé de qualquer projeto web. Originada no pack Bora Automatizar (BA). Use para otimizar aplicações para Generative Engine Optimization (GEO), agentes autônomos, buscas contextuais (ChatGPT, Perplexity, Claude) e indexação limpa sem alucinações. |
| [ai-memory-obsidian](./ai-memory-obsidian/SKILL.md) | Portable workflows for persistent memory and Obsidian across macOS, Linux, and Windows. Use when the user asks to recall or save past context, record decisions, create vault notes, or configure ai-memory, Obsidian CLI, or an Obsidian MCP bridge. |
| [aprender](./aprender/SKILL.md) | Estude programação com explicações, perguntas e pequenos desafios adaptados ao que você demonstra entender. |
| [concept-to-excalidraw](./concept-to-excalidraw/SKILL.md) | Transformar conceitos técnicos em diagramas e boards visuais editáveis no Excalidraw, entregando arquivo .excalidraw. Usar para explicar mecanismos, revisar visuais abstratos ou textuais e executar planos visuais de aulas; criar slides nativos e exportar imagens quando solicitados. |
| [construir](./construir/SKILL.md) | Construir um projeto para aprender programação. Use quando o aluno pede um projeto ou quando aprender entrega uma atividade que precisa de arquivos, execução e etapas persistentes. |
| [design-craft](./design-craft/SKILL.md) | Opinionated product-design skill for building, reviewing, polishing, and iterating on landing pages, apps, dashboards, AI products, design systems, and brand touchpoints. UX and comprehension first, then restraint (three type sizes, delete decoration), then foundations, then tactical craft — hierarchy, spacing systems, type scales, HSL palettes, shadows, finishing touches. Distilled from 20 YC Design Review videos (Linear, Stripe, Cursor, Framer) plus the Refactoring UI book. Use whenever the user asks to design, redesign, critique, or polish anything user-facing: "make it look better/more professional/trustworthy", de-slop the AI/vibe-coded look, fix a landing or pricing page, improve conversion, design an AI feature or agent UI, set up tokens or a design system, review a URL/screenshot/mockup. Also trigger for tactical UI questions — spacing feels off, visual hierarchy, choosing colors, typography, empty states, Tailwind/CSS styling — even without the word "design". Not for pure backend/DevOps work. |
| [good-design](./good-design/SKILL.md) | Design and audit product experiences for ethical conversion, activation, retention, and expansion using product and behavioral-design principles. Use for SaaS UX, landing pages, onboarding, dashboards, forms, pricing, and feature decisions—not for visual styling alone. |
| [grill-me](./grill-me/SKILL.md) | Interview the user to clarify requirements, architecture, design, and business rules before implementation. Use the host's available interactive question interface and ask in rounds sized to its limits. Works across macOS, Linux, and Windows. Use when the user asks to grill an idea, plan a major feature, or invokes /grill-me. |
| [prepare-technical-slides](./prepare-technical-slides/SKILL.md) | Pesquisar e preparar slides de aulas e palestras técnicas em PT-BR, com fontes verificáveis, sequência didática, contexto e um conceito por slide. Preserva o catálogo aprovado e a rastreabilidade de afirmações; usa concept-to-excalidraw para produzir diagramas, imagens e a apresentação nativa editável no Excalidraw. |
| [project-init](./project-init/SKILL.md) | Início de projeto e documentação contínua no mesmo fluxo. Originada no pack Bora Automatizar (BA). Em repositórios novos (pouco ou nenhum código) — guia a escolha de stack justificada, estrutura inicial, qualidade e segurança day-1, cravando CHANGELOG.md, ARCHITECTURE.md e ROADMAP.md desde o primeiro commit. Em repositórios em andamento — investiga código e histórico git reais para atualizar os 3 documentos com fidelidade, sem inventar nada. |
| [skillpper-saver](./skillpper-saver/SKILL.md) | Aggressive token, context, and cost optimization mode for AI coding agents (Claude Code, Antigravity, Cursor, etc.). Prevents marathon sessions, eliminates redundant file re-reading, prioritizes text extraction over screenshots in browser automation, and manages context windows with surgical cutoff triggers. Use when the user requests token savings, context optimization, quota conservation, or when starting extensive refactoring, browsing, or debugging tasks. |
| [study-quiz](./study-quiz/SKILL.md) | Use ao pedir quiz, teste, prova, simulado, questões de múltipla escolha, mini-desafio, gabarito, “me testa sobre X”, “gera um quiz de X” ou uma avaliação sobre um assunto, em um nível ou numa faixa de níveis. Use também quando o usuário responder um quiz gerado aqui e quiser a correção. Não use para palestras, slides, design, flashcards, resumo ou plano de estudo. |

<!-- SKILLS:END -->

We also have a bunch of recomendation of third-party skills you can use on your daily workflow, [check it out!](RECOMENDATIONS.md)

Community votes can be shown in the [GitHub Pages dashboard](docs/index.html) and summarized in [RANKING.md](RANKING.md). Maintainers can enable the low-friction voting workflow by following [the community voting setup](docs/community-voting.md).

### Suggest a recommendation

Open a pull request adding a row to this table with the project name, original repository, author, a short description of its use case, and official installation instructions. Include an example of how you used it in the pull request so maintainers can assess the recommendation.

This list is curated manually and stays separate from the automatically generated index of this repository's own skills.

## How to install

### 1. Check the prerequisites

Install [Node.js](https://nodejs.org/en/download) with npm, and use an agent supported by the [Skills CLI](https://github.com/vercel-labs/skills), such as Claude Code, Codex, or Cursor.

```bash
node --version
npm --version
```

### 2. Choose your skills

Open a terminal in the project where you want to use the skills. Preview the available skills:

```bash
npx skills add kipperdev/skillpper --list
```

Then launch the interactive installer:

```bash
npx skills add kipperdev/skillpper
```

Follow the prompts to select your skills, target agents, and installation scope. Project installation makes the skills available in that project; global installation makes them available across your projects.

To install just one skill:

```bash
npx skills add kipperdev/skillpper --skill design-craft
```

To install it globally for Codex:

```bash
npx skills add kipperdev/skillpper --skill design-craft --agent codex --global
```

### 3. Put a skill to work

Start a new session in your agent and ask for a task that matches the skill. For example:

> Use design-craft to review this landing page and suggest the three most useful improvements.

Read the skill's `SKILL.md` for its workflow and prerequisites. Some skills require additional tools or services; `prepare-technical-slides`, for example, uses `concept-to-excalidraw` for editable diagrams and native Excalidraw presentations. Install both skills for that workflow; editing a live scene or configuring native slides also requires access to the appropriate Excalidraw account.

## How to contribute

New skills, improvements to existing workflows, clearer documentation, and bug reports are welcome. A useful skill solves a concrete problem and helps another developer repeat your process.

### 1. Fork and clone the repository

[Create a fork](https://github.com/kipperdev/skillpper/fork), then clone your fork and create a branch (replace `YOUR-USERNAME` with your GitHub username):

```bash
git clone https://github.com/YOUR-USERNAME/skillpper.git
cd skillpper
git switch -c add/my-skill
```

### 2. Add or improve a skill

Create one folder per skill at the repository root. Use a lowercase, hyphen-separated name:

```text
my-skill/
├── SKILL.md           # Required: metadata and instructions
├── references/        # Optional: supporting documentation
├── scripts/           # Optional: helpers used by the skill
└── assets/            # Optional: templates or other resources
```

Start `SKILL.md` with YAML frontmatter. The `name` must match the folder name, and both fields must be non-empty strings:

```markdown
---
name: my-skill
description: >-
  Explain what the skill does and when an agent should use it.
---

# My Skill

## When to use

Describe the problem this skill solves and any required tools or setup.

## Workflow

1. Gather the context needed for the task.
2. Follow concrete, repeatable steps.
3. Verify the result against clear success criteria.

## Expected output

Describe what the user should receive and include an example.
```

Keep instructions focused, link supporting files with relative paths, and document dependencies. Use examples that another developer can try without access to your private environment. Include only material you have permission to share, and credit sources where appropriate.

### 3. Try it locally

From your clone, install your working copy for your agent:

```bash
npx skills add . --skill my-skill
```

Try a realistic task and check that the skill produces the expected result. For an existing skill, check that your changes still support its original use case.

Index generation supports Python 3.10 or later. Skill validation and the full test suite use Python 3.12, matching the CI runtime:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python --version
python scripts/update_skills_index.py
python scripts/validate_skills.py --worktree . --json /tmp/skill-validation.json --markdown /tmp/skill-validation.md
python scripts/update_skills_index.py --check
python scripts/update_skill_votes.py --check
python -m unittest discover -s tests
```

Edit skill descriptions in their `SKILL.md` files. Run `python scripts/update_skills_index.py` and commit the resulting README table change with your pull request. The index check is read-only; it does not commit or push changes for you.

### 4. Open a pull request

```bash
git add my-skill/
git commit -m "feat: add my-skill"
git push -u origin add/my-skill
```

Open a pull request from your branch to this repository's default branch. Explain the problem your skill solves, include a happy-path and boundary example, and describe how you tested it. For improvements, explain what changes for the user. Include the review manifest, declared access, and any regenerated `.skill` archive when applicable. The README index change must be generated and committed in the pull request.

For ideas or problems that do not need a pull request yet, [open an issue](https://github.com/kipperdev/skillpper/issues).

## How the index stays up to date

The [skills index workflow](.github/workflows/update-skills-index.yml) discovers root-level `*/SKILL.md` files and checks that the alphabetical table matches their YAML metadata. Run `python scripts/update_skills_index.py` after adding, renaming, removing, or changing a skill, then commit the generated README change in the same pull request. The generator preserves everything outside the exact `SKILLS:START` and `SKILLS:END` markers.

Skill review validation is static. It does not install or execute skills, call an AI model, fetch third-party URLs, or run the manifest examples. A passing check is not a safety certification. See [SECURITY.md](SECURITY.md) for scope and finding disposition. Merge blocking requires an administrator to activate required checks and code-owner review.
