# Código guiado por comentários

Use ao preparar uma função ou classe que o aluno deve completar, numa atividade de aprender
ou num checkpoint de construir. Os comentários são o roteiro da implementação dentro do código.

## Preparar a tarefa

Explique o problema e o comportamento esperado. Identifique o arquivo, a função ou o método
que será alterado e delimite a parte que cabe ao aluno. Apresente as interfaces e operações
disponíveis quando forem necessárias; deixe explícitos os detalhes que o aluno deve decidir.
Em exercício só pelo chat, identifique o trecho em vez de inventar um caminho de arquivo.

Forneça a estrutura e o código periférico necessários. Dentro do corpo a completar, escreva
comentários numerados na ordem do raciocínio. Em classes, coloque os passos nos métodos
relevantes; explique a responsabilidade da classe antes deles.

Cada passo indica uma ação concreta e seu efeito esperado. Explicite condições, origem dos
dados, retorno e efeitos colaterais quando fazem parte da tarefa. Use frases curtas e palavras
familiares; apresente o significado de termos como HIT e MISS ao usá-los pela primeira vez.

Os comentários orientam o comportamento; a implementação do mecanismo continua sendo a
participação do aluno. Ajuste a quantidade de apoio ao que ele já demonstrou e registre a ajuda
conforme EVIDENCE.md. Se a decisão sobre a ordem for o próprio objetivo, peça essa decisão
antes de fornecer um roteiro ordenado.

## Exemplo de estrutura para completar

Contexto: evitar consultas repetidas ao banco usando cache. O aluno implementará getProduto;
o projeto já fornece as operações de leitura e gravação no Redis e a consulta ao banco,
com suas assinaturas explicadas. HIT significa dado encontrado no cache; MISS, dado ausente.

```js
export async function getProduto(id) {
  const chave = `produto:${id}`;

  // 1. Leia no Redis o valor associado a esta chave.

  // 2. Se encontrar o produto (HIT), devolva-o sem consultar o banco.

  // 3. Se não encontrar (MISS), busque o produto no banco.

  // 4. Grave o produto no Redis com o tempo de expiração combinado.

  // 5. Devolva o produto encontrado no banco.
}
```

Esse trecho é uma estrutura incompleta para o aluno implementar. Antes de pedir a alteração,
defina no contexto o tempo de expiração e o formato dos dados, ou identifique essas escolhas
como parte da tarefa. Acrescente o caso de produto inexistente se ele estiver no escopo.

## Conferir e acompanhar

**Pronto para apresentar quando:** o aluno consegue localizar o trecho, entender o motivo da
alteração e identificar cada ação e o resultado esperado sem adivinhar requisitos. O contexto
e os comentários descrevem o mesmo comportamento, com as dependências disponíveis.

Peça a implementação e indique como observar o resultado. No exemplo, uma leitura com cache
vazio consulta o banco e preenche o cache; outra leitura com dado presente devolve o produto
sem nova consulta. Compare esses comportamentos com a tentativa do aluno e dê feedback específico.
Comentários preenchidos ou código gerado pela IA, sozinhos, não demonstram aprendizagem.
