# Desenhos (Excalidraw)

## Quando desenhar

Quando outra representação tornar o mecanismo mais claro, após tentativas sem avanço ou a
pedido do aluno. Uma ideia por desenho. O desenho pode apoiar estudo e construção.

## O que desenhar

- Uma ideia por desenho, no máximo **15 elementos**: caixas, setas, rótulos curtos em pt-BR.
- O mecanismo da situação estudada; quando há projeto, use os nomes das funções e serviços dele.
- Comportamento no tempo (retry, timeout, mensagem duplicada): passos numerados da esquerda para
  a direita (`1.`, `2.`, `3.` no rótulo da seta).

## Onde salvar

`<estado>/topics/<label>/reference/drawings/NNNN-<slug>.excalidraw` (NNNN sequencial). Linke o
arquivo na cola do tópico em `reference/`. Diga ao aluno, em uma linha, como abrir:
`abra no excalidraw.com (Open) ou com a extensão Excalidraw do VS Code/Cursor`.

Depois do desenho, peça uma aplicação **sobre ele** ("no desenho, em qual seta a
mensagem pode chegar duplicada?").

## Como montar

Parta SEMPRE deste esqueleto; nunca escreva o formato de memória. Ele tem as três peças que um
desenho precisa: caixa com texto dentro, segunda caixa, seta ligada às duas com rótulo.

Para cada caixa nova: copie um `rectangle` e seu `text`, troque os `id`, `x`/`y` e o texto, e
mantenha a ligação recíproca — o `text` aponta `containerId` para a caixa e a caixa lista o texto em
`boundElements`. Para cada seta: `startBinding`/`endBinding` apontam as caixas, e cada caixa lista a
seta em `boundElements`. `points` é relativo ao `x`/`y` da seta. Ids curtos e únicos (`box-pedido`,
`txt-pedido`, `arr-1`). Caixas de 200×80, 120 px de espaço entre elas.

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/kipperdev/skillpper",
  "elements": [
    { "id": "box-a", "type": "rectangle", "x": 0, "y": 0, "width": 200, "height": 80, "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null, "roundness": { "type": 3 }, "seed": 1, "version": 1, "versionNonce": 1, "isDeleted": false, "boundElements": [{ "id": "txt-a", "type": "text" }, { "id": "arr-1", "type": "arrow" }], "updated": 1, "link": null, "locked": false },
    { "id": "txt-a", "type": "text", "x": 50, "y": 27, "width": 100, "height": 25, "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null, "roundness": null, "seed": 2, "version": 1, "versionNonce": 2, "isDeleted": false, "boundElements": null, "updated": 1, "link": null, "locked": false, "text": "pedido", "fontSize": 20, "fontFamily": 5, "textAlign": "center", "verticalAlign": "middle", "containerId": "box-a", "originalText": "pedido", "autoResize": true, "lineHeight": 1.25 },
    { "id": "box-b", "type": "rectangle", "x": 320, "y": 0, "width": 200, "height": 80, "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null, "roundness": { "type": 3 }, "seed": 3, "version": 1, "versionNonce": 3, "isDeleted": false, "boundElements": [{ "id": "txt-b", "type": "text" }, { "id": "arr-1", "type": "arrow" }], "updated": 1, "link": null, "locked": false },
    { "id": "txt-b", "type": "text", "x": 360, "y": 27, "width": 120, "height": 25, "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null, "roundness": null, "seed": 4, "version": 1, "versionNonce": 4, "isDeleted": false, "boundElements": null, "updated": 1, "link": null, "locked": false, "text": "pagamento", "fontSize": 20, "fontFamily": 5, "textAlign": "center", "verticalAlign": "middle", "containerId": "box-b", "originalText": "pagamento", "autoResize": true, "lineHeight": 1.25 },
    { "id": "arr-1", "type": "arrow", "x": 204, "y": 40, "width": 112, "height": 0, "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null, "roundness": { "type": 2 }, "seed": 5, "version": 1, "versionNonce": 5, "isDeleted": false, "boundElements": [{ "id": "txt-arr-1", "type": "text" }], "updated": 1, "link": null, "locked": false, "points": [[0, 0], [112, 0]], "lastCommittedPoint": null, "startBinding": { "elementId": "box-a", "focus": 0, "gap": 4 }, "endBinding": { "elementId": "box-b", "focus": 0, "gap": 4 }, "startArrowhead": null, "endArrowhead": "arrow", "elbowed": false },
    { "id": "txt-arr-1", "type": "text", "x": 225, "y": 15, "width": 70, "height": 20, "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent", "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1, "opacity": 100, "groupIds": [], "frameId": null, "roundness": null, "seed": 6, "version": 1, "versionNonce": 6, "isDeleted": false, "boundElements": null, "updated": 1, "link": null, "locked": false, "text": "1. cobra", "fontSize": 16, "fontFamily": 5, "textAlign": "center", "verticalAlign": "middle", "containerId": "arr-1", "originalText": "1. cobra", "autoResize": true, "lineHeight": 1.25 }
  ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": null },
  "files": {}
}
```
