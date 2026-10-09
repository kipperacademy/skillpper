# Plano de estudo

Em topics/<label>/PLAN.md. A posição dos eventos fica em SESSION.md (WORKSPACE-FORMAT.md).

```md
# Estudo: idempotência

Resultado: decidir como evitar cobrar duas vezes o mesmo pedido.
Estado: estudando                  <!-- estudando | construindo | pausado | fechado -->

## Atividade atual
- Formato: previsão
- Conceito: idempotência
- Situação: confirmação perdida depois de uma cobrança
- Critério: distinguir repetição da entrega de repetição do efeito
- Pergunta pendente: o que acontece se o produtor reenviar?
- Ajuda já dada: nenhuma

## Evidência
- Identificou duas entregas do mesmo pedido; ainda não explicou o efeito (data).

## Próxima possibilidade
- Experimentar uma confirmação perdida se o mecanismo estiver claro.

## Retomada
- Continuar da pergunta pendente, sem mostrar a solução.
```

Salve antes de apresentar a atividade e após cada resposta. Critério e ajuda precisam estar
presentes para interpretar a resposta. Marque uma atividade suspensa na passagem para construção;
o resultado do projeto pode mudar a próxima atividade. Para tópicos antigos, preserve o PLAN.md
com checkpoints como plano do projeto e crie STUDY.md neste formato; a habilidade de estudo
retoma STUDY.md quando ambos existirem.
