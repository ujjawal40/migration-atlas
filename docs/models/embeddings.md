# Graph Embeddings

Node2Vec embeddings on the knowledge graph, producing a 64-dimensional vector for every country, visa, law, and industry node.

## Two capabilities

### 1. Similarity

`most_similar('mexico')` returns countries whose neighborhoods most resemble Mexico's. With the seed graph, this recovers the Central American corridor (El Salvador, Guatemala, Honduras) — countries that share visa pathways (TPS, family-based), industries (construction, agriculture), and historical patterns (post-1980 modern wave).

### 2. Link prediction

Given two nodes that aren't connected, score the cosine similarity of their embeddings as a proxy for edge plausibility. Useful for surfacing gaps in the seed data — e.g., the model might suggest that "Brazil → tech" is a plausible edge that isn't currently in the graph.

## Why Node2Vec, not a GNN

For a graph this small (~50 nodes, ~60 edges), GNNs are overkill and overfit immediately. Node2Vec — a random-walk-based shallow embedding — is the appropriate tool. If the graph grows to thousands of nodes (e.g., adding state-level nodes, finer industry decomposition), revisit with GraphSAGE or a small GAT.

## Hyperparameters

The defaults in `configs/embeddings.yaml` use balanced random walks (p=q=1). Tune p and q for different views:

- **p < 1, q > 1** — BFS-like, captures structural roles ("which nodes play similar roles")
- **p > 1, q < 1** — DFS-like, captures community / homophily ("which nodes are in the same neighborhood")

The default is community-flavored. For a structural-role view, set p=2, q=0.5.
