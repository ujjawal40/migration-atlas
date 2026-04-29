# Neo4j (optional)

The default `GRAPH_BACKEND=networkx` is fine for a portfolio project — the seed graph fits in memory and queries are fast. Switch to Neo4j when:

- You add state-level or county-level detail and the graph grows past a few thousand nodes
- You want persistent storage across deploys
- You want the visual Neo4j Browser for ad-hoc Cypher queries

## Local Neo4j (Docker)

The `docker-compose.yml` already includes Neo4j. Bring it up:

```bash
docker-compose up neo4j
# Browser UI: http://localhost:7474
# Bolt: bolt://localhost:7687
# Default credentials in .env.example: neo4j / atlasdev
```

Then build the graph:

```bash
GRAPH_BACKEND=neo4j make graph
```

## Neo4j Aura (free tier, hosted)

Aura's free tier gives you a managed Neo4j instance at no cost.

1. Sign up at [neo4j.com/aura](https://neo4j.com/aura/).
2. Create a free instance. Save the credentials.
3. Set in `.env`:
   ```
   GRAPH_BACKEND=neo4j
   NEO4J_URI=neo4j+s://YOUR_INSTANCE.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=YOUR_PASSWORD
   ```
4. Run `make graph` — the build script writes to Aura.

## Sample Cypher queries

After loading, try these in the Neo4j Browser:

```cypher
// Countries enabled by the 1965 INA
MATCH (l:Law {id: 'ina-1965'})-[:ENABLES]->(c:Country)
RETURN c.name ORDER BY c.foreign_born_us DESC

// Visa pathways used by Indian immigrants
MATCH (c:Country {id: 'india'})-[:USES_VISA]->(v:Visa)
RETURN v.name

// Multi-hop: laws that created visas used by Mexican immigrants
MATCH (l:Law)-[:CREATES]->(v:Visa)<-[:USES_VISA]-(c:Country {id: 'mexico'})
RETURN l.name, v.name
```
