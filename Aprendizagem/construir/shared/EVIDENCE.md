# Evidência e assistência

Defina antes da atividade o mecanismo e a consequência esperados. Julgue o conteúdo pelo
critério, aceitando soluções válidas diferentes da prevista.

- solid: a resposta explica o mecanismo e sua consequência, ou implementa/depura e explica o
  comportamento observado. Uma justificativa verbal não substitui execução quando ela é o critério.
- shallow: reconhece a alternativa ou acerta sem explicar o mecanismo necessário.
- none: a resposta contém um equívoco relevante ou declara que não sabe.

Esses estados descrevem aquela resposta. Fluência, velocidade e código produzido pela IA
não são medidas de domínio. Questão ambígua, resposta ilegível, ausência de resposta e falha
técnica ficam pendentes, sem atribuição automática de none.

## Assistência

Salve no plano o apoio já fornecido: nenhuma ajuda conhecida, pista, exemplo, solução fornecida
ou assistência desconhecida. Registre respostas pós-ajuda como tais; um solid após ensino não
comprova independência nem retenção. Em answer_summary ou where, preserve contribuição e ajuda
em texto conciso, dentro dos limites do contrato. O servidor não possui campo de assistência:
mantenha detalhes no plano; não acrescente campos inventados ao payload.

Uma resposta a uma tarefa conceitual gera probe_answered. Uma aplicação observada pelo aluno,
como previsão correta com mecanismo ou correção explicada, pode gerar concept_applied. Código
que apenas roda e checkpoint concluído pela IA ficam no plano, sem concept_applied automático.
Registre struggled_on quando há equívoco concreto observado ou tentativas sem avanço; ajuda
pedida, silêncio e desenho solicitado não bastam. Pedidos e preferências não são respostas.

## Progresso

Use as evidências para escolher a próxima atividade. Um acerto pode justificar avanço; a
aplicação em situação nova verifica transferência. Guarde o que continua incerto e evite
reavaliar o mesmo ponto sem motivo. Conclusão assistida permite continuar com a lacuna registrada.
A revisão posterior pela Kipper pode observar retenção; esta sessão observa o desempenho atual.
