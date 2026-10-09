# Plano do projeto

Em topics/<label>/BUILD.md. A posição dos eventos fica em SESSION.md (WORKSPACE-FORMAT.md).

```md
# Construção: idempotência

Projeto: consumidor de pagamentos com entregas repetidas em memória.
Comando: java Main.java
Origem: aprender                   <!-- aprender | direto -->

1. [x] reproduzir duas cobranças — previsão do aluno confirmada
2. [~] impedir efeito duplicado — implementação pelo aluno
3. [ ] confirmação perdida — depurar
4. [ ] aplicar em uma condição nova

## Checkpoint atual
- Critério: distinguir chave do pedido de tentativa de entrega
- Tarefa pendente: escolher onde guardar o efeito já realizado
- Ajuda já dada: estrutura do consumidor; decisão central em aberto
- Arquivos: Main.java

## Evidência e lacunas
- Checkpoint 1: reconheceu a repetição do efeito sem ajuda (data).
- Checkpoint 2: ainda sem resposta.

## Retomada
- Continuar a escolha pendente antes de implementar.
```

Use [x] concluído, [~] em andamento e [ ] a fazer; acrescente “assistido” aos checkpoints
concluídos com solução fornecida. Eles podem avançar sem virar prova de domínio.
Para tópico antigo com checkpoints em PLAN.md, retome esse arquivo como BUILD.md legado;
a próxima escrita pode migrá-lo para BUILD.md preservando conteúdo e indicando em PLAN.md o destino.
