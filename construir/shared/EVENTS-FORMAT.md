# Eventos

Toda resposta a uma atividade conceitual vira um evento; preferências e pedidos de ajuda ficam
no plano. O mesmo evento vai para um de dois lugares:

- **Conectado (membro):** `record_lesson_event` do MCP `kipper`, com `{ kind, payload, session_ref }`.
- **Local:** uma linha em `events.jsonl` (ver "Modo local" no fim).

Regras comuns:

- `schema_version` é sempre `1`; pode omitir, o servidor preenche.
- `session_ref`: o mesmo valor para todos os eventos de uma sessão, inclusive o `topic_requested`,
  UUID gerado pelo host, **até 48 caracteres**. As duas skills compartilham a sessão durante
  a passagem; retomada posterior usa uma nova sessão.
- `event_key` = `${session_ref}:${posição}` (cabe em 64). Um tópico novo registra
  `topic_requested` na posição `0`; retomada começa em `0` sem novo pedido. Cada
  **evento novo** soma 1, e a posição nunca se repete — uma pergunta refeita depois de ensinar
  ganha a próxima posição. Um reenvio (retry do mesmo payload, ou a correção pedida por
  `invalid_payload`) não é evento novo: usa a mesma chave. Envie sempre um `event_key`: sem ele o
  servidor deriva um do payload inteiro, e um reenvio reescrito vira um evento a mais.
  A reserva de posição e o payload pendente ficam em SESSION.md; leia
  [WORKSPACE-FORMAT.md](./WORKSPACE-FORMAT.md) antes de registrar ou retomar um envio.
- Só um reenvio **idêntico** volta `duplicate: true`. A mesma chave com outro payload volta
  `invalid_payload` (ver "Erros").
- Conectado: `concept_ids` só com ids casados no início (salvos em `canon` no `MISSION.md`,
  [MISSION-FORMAT.md](./MISSION-FORMAT.md)) ou do perfil. Resposta sobre algo que não casou com o
  canon é gravada só localmente.
- Nunca envie `studentId` nem `source`: o servidor tira do token.

## Contrato

### `topic_requested`

Uma vez, ao abrir um tópico novo.

| campo | regra |
|---|---|
| `schema_version` | opcional; sempre `1`, o servidor preenche se faltar |
| `topic` | o pedido do aluno, texto cru, 1–120 |
| `label` | rótulo normalizado: pt-BR, minúsculo, 1–40, sem espaço no início ou no fim, sem `/` nem `\`: vira nome de pasta — use `ci-cd`, não `ci/cd`; o nome mais comum do assunto (`microsserviços`, não `microservices`) |
| `matched_concept_ids` | 0 a 10 ids do canon que o tópico cobre, sem repetir |
| `coverage` | `full` (tudo casou), `partial` (parte), `none` (nada; lista vazia) |
| `uncovered` | ≤200, o que o aluno pediu e o canon não cobre; obrigatório exceto em `full`, proibido em `full` (em `full`, omita) |
| `event_key` | opcional no servidor, ≤64; envie sempre (ver regras comuns) |

```json
{ "schema_version": 1, "topic": "quero aprender microservices", "label": "microsserviços", "matched_concept_ids": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"], "coverage": "partial", "uncovered": "service mesh e descoberta de serviço", "event_key": "5ca5a680-e2e8-48c0-9153-dd01e5414b81:0" }
```

### `probe_answered`

Toda resposta conceitual de estudo ou construção; interpretação em [EVIDENCE.md](./EVIDENCE.md).

| campo | regra |
|---|---|
| `schema_version` | opcional; sempre `1`, o servidor preenche se faltar |
| `concept_ids` | 1 a 5 ids |
| `question` | a pergunta feita, ≤300 |
| `answer_summary` | resumo fiel da resposta, ≤300 |
| `depth` | `none`, `shallow` ou `solid` (ver [EVIDENCE.md](./EVIDENCE.md)) |
| `event_key` | opcional no servidor, ≤64; envie sempre (ver regras comuns) |
| `checkpoint` | opcional, ≤60, ex.: `2/5 fila de pagamentos` |

```json
{ "schema_version": 1, "concept_ids": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"], "question": "Fila ou chamada direta entre pedido e pagamento? Por quê?", "answer_summary": "Fila, para o pedido não cair junto; não soube dizer o que acontece com mensagem repetida.", "depth": "shallow", "event_key": "5ca5a680-e2e8-48c0-9153-dd01e5414b81:1", "checkpoint": "2/5 fila de pagamentos" }
```

### `struggled_on`

Equívoco concreto observado, previsão conceitual errada ou tentativas sem avanço ([EVIDENCE.md](./EVIDENCE.md)).

| campo | regra |
|---|---|
| `schema_version` | opcional; sempre `1`, o servidor preenche se faltar |
| `concept_ids` | 1 a 5 ids |
| `what` | onde travou, concreto, ≤300 |
| `event_key` | opcional no servidor, ≤64; envie sempre (ver regras comuns) |
| `checkpoint` | opcional, ≤60 |

```json
{ "schema_version": 1, "concept_ids": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"], "what": "achou que a fila entrega cada mensagem uma vez só", "event_key": "5ca5a680-e2e8-48c0-9153-dd01e5414b81:4", "checkpoint": "2/5 fila de pagamentos" }
```

### `concept_applied`

Aplicação observada do aluno: previsão correta com mecanismo, implementação ou depuração explicada.
Conclusão assistida e execução de código fornecido ficam no plano, sem aplicação automática.

| campo | regra |
|---|---|
| `schema_version` | opcional; sempre `1`, o servidor preenche se faltar |
| `concept_ids` | 1 a 5 ids |
| `where` | onde aplicou, ≤200 |
| `event_key` | opcional no servidor, ≤64; envie sempre (ver regras comuns) |
| `checkpoint` | opcional, ≤60 |

```json
{ "schema_version": 1, "concept_ids": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"], "where": "chave de idempotência no consumidor de pagamentos", "event_key": "5ca5a680-e2e8-48c0-9153-dd01e5414b81:6", "checkpoint": "3/5 idempotência" }
```

## Erros (modo conectado)

O envelope é `{ ok: false, code, message, retry_after_s?, issues? }`; `issues` só vem em
`invalid_payload`: `[{ path: 'payload.depth', message: 'o que era esperado' }]`.

`invalid_payload` é a única falha com nova tentativa. Leia `issues`, corrija exatamente esses
campos e envie **uma** vez mais, com o mesmo `event_key` — exceto quando o item é
`payload.event_key` (a chave já registrou outro evento): aí use a chave nova que a mensagem traz.
Se voltar `invalid_payload` de novo e o único item for `payload.event_key`, reenvie mais uma vez
com a chave nova. Em qualquer outro caso, desista **deste** evento (fallback local, abaixo) e siga
registrando os próximos no MCP. Nunca invente campos fora do schema: o servidor descarta.
Um `kind` desconhecido ou um `session_ref` com mais de 64 caracteres é recusado pelo próprio
protocolo MCP, antes do envelope (um erro de validação em texto, sem `ok`): trate como
`invalid_payload`.

Qualquer outra falha — `{ ok: false, code }` com outro `code`, `401`/`403`, ou tool ausente: grave localmente
(ver "Fallback conectado" abaixo) e siga, sem mostrar nada ao aluno. `rate_limited`: pare de
enviar ao MCP pelo resto da sessão e grave tudo localmente. `unknown_concept`: o id não é do
canon — grave localmente, não tente outro id. Um id de `recent_review_misses` pode vir de um
conceito arquivado depois da correção e também voltar `unknown_concept`; o mesmo fallback local
resolve.

Se `list_canon_concepts` falhar (`ok: false`, erro, ou a tool ausente) ao abrir um tópico,
registre o pedido no formato local, omitindo cobertura desconhecida. Continue usando apenas
os ids verificados no perfil; preserve correspondências anteriores com sua origem na missão.

## Modo local

Cada linha de `events.jsonl` é um objeto:

```
{"kind": "<kind>", "payload": { ... }, "session_ref": "<session_ref>", "occurred_at": "<ISO 8601>"}
```

Duas exceções ao contrato acima, porque não há canon local:

- `concept_ids` leva **slugs** do conceito (`idempotencia`, `filas`), minúsculos, sem acento, com
  hífen — não UUID. Use sempre o mesmo slug para o mesmo conceito; confira os que já existem no
  arquivo antes de criar um.
- `topic_requested` não leva `matched_concept_ids` nem `coverage`; `uncovered` também sai.

Acrescente sempre no fim; nunca reescreva nem apague linhas.

### Fallback conectado

`events.jsonl` é o registro de modo local — mas também é onde um evento conectado que não pôde
ser enviado (ver "Erros" acima) cai, para não se perder. Acrescente ao mesmo `events.jsonl` uma
linha igual às de modo conectado (payload com UUID, não slug — os ids que já foram usados), mais
o campo `"mode": "connected"`. Um fallback sem ids verificados usa o formato local com slugs e omite cobertura desconhecida.
Modo local, ao reaproveitar slug para o mesmo conceito, ignora
essas linhas: o reaproveitamento de slug é sobre `concept_ids` em texto, e uma linha `connected`
não carrega slug nenhum.
