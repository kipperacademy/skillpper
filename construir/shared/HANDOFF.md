# Passagem entre estudo e construção

## Quando passar

aprender propõe construir quando a experiência precisa de arquivos, execução e etapas
persistentes para tornar o mecanismo observável. Um exercício isolado continua no estudo.
A aceitação do aluno autoriza aquela construção; pedidos diretos de projeto entram em construir.
Se ele preferir continuar com perguntas, prepare outro formato para o mesmo resultado.

## Entregar contexto

Salve HANDOFF.md em topics/<label>/ com direção, estado da passagem e os campos abaixo:

- Missão e resultado esperado.
- Caminho absoluto da raiz de estado e do tópico.
- Plano de estudo e plano do projeto, quando existem.
- Conceitos e ids verificados; perfil já obtido e seu momento de consulta.
- Evidências relevantes com origem; equívocos ainda abertos e ajuda já oferecida.
- Tarefa suspensa e critério esperado.
- Experimento proposto ou resultado do projeto.
- Sessão e evento pendente: referencie SESSION.md como fonte da chave e posição.

Passe esses dados à skill disponível no host. construir permite model-invocation porque
aprender precisa alcançá-la. aprender é user-invoked: na volta, continue seu fluxo já ativo
com o resultado salvo; em outro chat, forneça o pedido /aprender com o tópico e a raiz de estado.
A leitura do documento não inicia subagente, não envia mensagem a outro chat e não instala skills.

Se construir não está instalada ou o host não permite chamá-la, preserve o estado e informe
como continuar com /construir no host que a oferece. Ofereça exercício isolado enquanto isso;
não declare que a skill foi executada.

## Separar os planos

Em tópico novo, PLAN.md é estudo e BUILD.md é projeto. Para tópico antigo cujo PLAN.md já
contém checkpoints, preserve-o como projeto legado e use STUDY.md para estudo. As skills leem
ambos quando necessário, mas cada uma atualiza seu plano. Falta de projeto nunca reinicia o estudo.

## Devolver

Ao sair do projeto, atualize a passagem com comportamento executado, contribuição do aluno,
ajuda, dificuldades, arquivos e próximo passo proposto. Marque devolvida e retome a tarefa de
estudo suspensa ou ajuste-a pela evidência nova. Se o aluno ficar no projeto, mantenha a construção.
A passagem não gera topic_requested nem repete eventos: referência à evidência não é observação nova.
