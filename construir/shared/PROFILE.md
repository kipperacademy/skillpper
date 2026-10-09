# Perfil e conceitos

## Detectar o modo

No início de uma sessão, chame get_learner_profile do MCP kipper sem argumentos, se disponível.
Com ok: true, use o perfil conectado. Tool ausente, falha ou ok: false: estude localmente e
registre evidências locais, sem expor erros brutos ou inserir oferta comercial.

Na passagem entre skills dentro da mesma sessão, reutilize perfil e canon salvos. Para novo
assunto, consulte list_canon_concepts e salve correspondências honestas na missão. Se a consulta
falha, use só ids presentes no perfil, registre o pedido localmente e preserve a cobertura como
não determinada. Conceitos fora do catálogo continuam estudáveis com registro local.

## Interpretar evidências

Use objetivo, preferências e evidências relevantes: weak_concepts, strong_concepts,
recent_review_misses, recent_lapses e histórico da skill. Cite a origem real quando justificar
uma escolha. Conhecimento forte encurta confirmações; dificuldade relevante orienta ajuda.

- difficulty descreve a pergunta, não a senioridade do aluno.
- Múltipla escolha observa reconhecimento; explicação e aplicação mostram outros aspectos.
- skipped e technical_failure distinguem ausência de resposta e falha técnica de erro conceitual.
- assessment_status diferente de ready indica avaliação ainda indisponível; listas vazias não
  demonstram ausência de dificuldade. Preserve placement_score nulo e limitations do perfil.
- Um erro antigo ou domínio amplo de revisão é uma hipótese a confirmar no contexto atual.

Práticas, conteúdos, avaliações e conquistas oficiais usam apenas ferramentas que o host
realmente expõe. O contrato atual de eventos não concede badges nem altera notas por declaração
da skill. O agendamento de revisão pertence à Kipper; due_reviews pode informar a relevância
quando houver acesso real à prática, sem criar agenda local nem simular ferramenta ausente.

Use apenas materiais com referência verificada. Relatos de aulas assistidas exigem evidência.
