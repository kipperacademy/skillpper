# Estado compartilhado

Raiz: APRENDER_HOME ou ~/.kipperacademy/aprender/. Ambas as skills usam a mesma raiz, preservando
o histórico existente. Uma mudança de skill não cria uma segunda memória do aluno.

```text
<estado>/
  NOTES.md
  learning-records/0001-<slug>.md
  events.jsonl
  topics/<label>/
    MISSION.md
    SESSION.md
    PLAN.md                         # estudo; STUDY.md quando PLAN.md é projeto legado
    BUILD.md                        # projeto; pode começar em PLAN.md legado
    HANDOFF.md
    reference/*.md
    reference/drawings/*.excalidraw
```

NOTES guarda preferências; missão e planos guardam o contexto local também para membros.
Aprendizagem conectada usa o MCP; learning records são locais. events.jsonl recebe eventos
locais e fallback conectado conforme EVENTS-FORMAT.md. O projeto contém código e README;
os arquivos sobre o aluno ficam no estado.

## Sessão e retomada

Use SESSION.md como fonte única de session_ref e próxima posição dos eventos, comum às skills.
Para uma sessão nova, gere um UUID pelo host e use-o como session_ref (36 caracteres); posição
inicial 0. A passagem no mesmo estudo mantém a sessão. Retomada posterior abre nova sessão
com posição 0, sem registrar topic_requested novamente para um tópico já existente.

Antes de cada evento novo leia a posição, salve o evento pendente com kind e payload completos
e reserve a próxima posição. Depois do resultado, marque enviado ou fallback. Em interrupção,
retome o evento pendente com a mesma chave e payload; um retry não reserva outra posição.
Um session_ref de UUID cabe no limite de 48 e a chave com posição cabe em 64.

Formato mínimo de SESSION.md:

```md
Sessão: <UUID>
Próxima posição: 2
Modo: conectado
Perfil consultado em: <data e hora>

## Evento pendente
- Status: pendente                    <!-- pendente | enviado | fallback -->
- Posição reservada: 1
- Requisição: <JSON completo de kind, payload e session_ref>
```

Ao terminar um envio, retenha o status e a requisição até reservar o próximo. Se o servidor
fornecer outra event_key após colisão, salve a chave corrigida no pendente e ajuste a próxima
posição para além dela antes do retry. Salve também o modo atual após rate_limited.

Retome pelo tópico explicitamente pedido, pela passagem aceita ou pelo project_path quando
há projeto e nenhum tópico foi indicado. Se há vários candidatos, pergunte qual continuar.
Leia tarefa pendente, critério, ajuda e evidências antes de apresentar outra atividade.
Falta de project_path é normal no estudo; não significa tópico interrompido ou novo.

## Estado antigo

Preserve tópicos e preferências existentes. Em planos antigos com a linha “Sessão”, migre o
session_ref e a posição para SESSION.md na primeira retomada; substitua a linha por referência
para SESSION.md, preservando checkpoints. Faça essa migração antes de registrar ou reenviar.
Leia HANDOFF.md para separar plano de estudo e projeto sem perder a atividade anterior.

## Fallback

Sem escrita na pasta pessoal, use ./.aprender/ no diretório de trabalho atual. Informe uma vez
o caminho e sua limitação de continuidade fora desse diretório. As duas skills reutilizam o
mesmo caminho durante a passagem, mesmo quando o projeto é criado em outra pasta. Se não pode
persistir nem ali, explique que a retomada entre sessões não está garantida e forneça ao pausar
um resumo copiável de missão, tarefa, ajuda e evidências. Não declare estado salvo sem escrita.

Crie diretórios ao gravar o primeiro arquivo. Respeite permissões do host e instruções do
repositório escolhido para o projeto.
