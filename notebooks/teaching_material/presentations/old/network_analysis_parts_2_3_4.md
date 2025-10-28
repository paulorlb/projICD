---
title: "Network Analysis for Bibliometrics — Parts 2–4"
author: "Master in Data Science for the Social Sciences"
date: 2025-10-07
format:
  revealjs:
    theme: dark
    slide-number: true
    incremental: true
    center: false
    margin: 0.04
    navigation-mode: linear
    transition: fade
    toc: false
    code-fold: false
    embed-resources: true
    mermaid: {}
    code-overflow: wrap
execute:
  echo: false
  warning: false
  message: false
editor: visual
---

# Part 2 — Graph Types & Bibliometric Representations

## Map bibliometric data to graphs

- **Undirected** vs **Directed**
- **Weighted** vs **Unweighted**
- **Bipartite** (two-mode) graphs
- Typical projections: **Author–Paper → Author–Author**, **Paper–Keyword → Keyword–Keyword**

::: {.columns}
::: {.column width="48%"}
**Cheat table**

| Network | Nodes | Edge | Directed? | Weight? | Typical Use |
|---|---|---|:---:|:---:|---|
| Co-authorship | Authors | Wrote together | ✗ | ✓ | Collaboration structure |
| Citation | Papers | A cites B | ✓ | ✓ | Knowledge flow |
| Co-citation | Papers | C cites A & B together | ✗ | ✓ | Intellectual proximity |
| Bibliographic coupling | Papers | Share references | ✗ | ✓ | Topical similarity |
| Keyword co-occurrence | Keywords | Appear together | ✗ | ✓ | Concept map |
| Institution collaboration | Orgs | Joint papers by members | ✗ | ✓ | Inter-org networks |
:::

::: {.column width="52%"}
**Unified view (Mermaid)**

```{mermaid}
graph LR
  subgraph BIPARTITE[Two-mode]
    A1[Author] --- P1[Paper]
    A2[Author] --- P1
    P1 --- K1[(Keyword)]
    P2[Paper] --- K1
    P2 --- K2[(Keyword)]
  end
  subgraph PROJECTIONS[Projections]
    A1a[Author] --- A2a[Author]
    K1a[(Keyword)] --- K2a[(Keyword)]
  end
  BIPARTITE --> PROJECTIONS
```
:::
:::

---

## Choosing graph type wisely

::: {.columns}
::: {.column width="50%"}
**When to use directed**
- Citation, retweets, hyperlinks
- Causal/temporal interpretation
- Path-based measures make sense
:::

::: {.column width="50%"}
**When to keep bipartite**
- Preserve affiliation structure
- Avoid projection artifacts (inflated cliques)
- Later: use weighted projections or null models
:::
:::

> **Tip:** For dense co-occurrence, filter edges by weight threshold (e.g., ≥2) to improve readability.

---

## Data transformation pipeline (bibliometrics)

```{mermaid}
flowchart LR
  A[Scopus CSV/Excel] --> B[Parse fields: Authors, Year, Title, Author Keywords, References]
  B --> C[Clean & normalize: name disambiguation, keyword stemming]
  C --> D[Build edges: pairs/co-occur, citation edges]
  D --> E[Graph object: directed/undirected, weighted]
  E --> F[Projection (if needed): bipartite → one-mode]
  F --> G[Filter & threshold]
  G --> H[Metrics & community detection]
  H --> I[Visualization & interpretation]
```

---

# Part 3 — Key Network Measures

## Global structure metrics

::: {.columns}
::: {.column width="50%"}
**Density**
- Realized edges / possible edges
- High in small teams; low in broad fields

**Components**
- Disconnected subgraphs → isolated streams

**Average path length**
- Typical steps to connect two nodes
:::

::: {.column width="50%"}
**Clustering coefficient**
- Triadic closure tendency (team/clique tendency)

**Assortativity**
- Like-with-like mixing (e.g., institution, country)

**Degree distribution**
- Skewness → hubs vs egalitarian networks
:::
:::

---

## Node-level centralities (interpretation table)

| Measure | Intuition | Bibliometric meaning | Caveats |
|---|---|---|---|
| Degree | Number of ties | Collaboration/citation breadth | Sensitive to sampling & name variants |
| Strength | Sum of weights | Intensity of ties | Weights depend on preprocessing |
| Betweenness | Shortest-path brokerage | Interdisciplinary connectors, bridges | Can be unstable in dense graphs |
| Closeness | Average distance to all | Accessibility/reach to others | Not defined in disconnected graphs |
| Eigenvector | Connected to the important | Prestige/influential neighborhoods | Favors well-connected cores |
| PageRank | Random-surfer prestige | Influential papers in citation nets | Damped by parameter choice |

---

## Communities & meso-structure

- **Goal:** find densely connected subgroups (topics, schools).
- Algorithms: **Louvain**, **Leiden** (modularity); **Infomap** (flows); **Girvan–Newman** (edge betweenness).
- Output: community id per node (use for color in plots; summarize by top keywords/authors).

```{mermaid}
graph TD
  subgraph Net[Network]
    A --- B; B --- C; C --- A
    D --- E; E --- F; F --- D
    C --- D
  end
  classDef c1 fill:#7dcfb6; classDef c2 fill:#f9a03f;
  class A,B,C c1; class D,E,F c2
```

> **Practice:** Compare modularity before/after filtering edges by weight.

---

## Robustness & validation

- **Sensitivity** to preprocessing (author disambiguation, keyword normalization)
- **Null models**: compare to random graphs preserving degree/strength
- **Stability checks**: rerun communities with different seeds/algorithms
- **Temporal slices**: see if clusters persist over years

---

# Part 4 — Visual Representation & Interpretation

## Core visualization principles

1. **Encode meaning**: size → centrality, color → community, edge width → weight
2. **Use readable layouts**: force-directed for discovery; circular/arc for order
3. **Filter for clarity**: threshold low-weight edges; show top-N nodes by metric
4. **Label sparingly**: annotate hubs/bridges; add legends
5. **Avoid misreadings**: layout distance ≠ metric distance

---

## Layouts at a glance

::: {.columns}
::: {.column width="50%"}
**Force-directed** (Fruchterman–Reingold / ForceAtlas2)

```{mermaid}
graph TD
  A---B;A---C;A---D;B---C;C---E;D---E;E---F;F---G;G---H;H---E
```
- Good for cluster emergence
- Unstable w.r.t random seeds; not geographic
:::

::: {.column width="50%"}
**Circular / Arc diagrams**

```{mermaid}
flowchart LR
  A((A)) --- B((B))
  B --- C((C))
  C --- D((D))
  D --- E((E))
  E --- F((F))
```
- Good for ordered entities (years, journals)
- Less informative for community detection
:::
:::

---

## Making dense graphs legible

- **Edge filtering:** keep edges with weight ≥ *k*
- **Node filtering:** top *N* by degree/PageRank per community
- **Facet by community:** separate mini-views rather than one hairball
- **Legends:** explicit mapping of size/color/width
- **Interactivity:** hand off to Gephi / Cytoscape / pyvis for exploration

---

## Visual checklist (slide-level)

- Title communicates the **question**
- Legend explains **encodings**
- Text answers: *What is the pattern? Why does it matter?*
- Cite **data source** and **filters** (reproducibility)

---

## Example slide scaffold (replace with your figure)

::: {.columns}
::: {.column width="55%"}
**Co-authorship network (topic X, 2015–2024)**

- Nodes sized by degree
- Colors = Leiden communities
- Edges filtered: weight ≥ 2

![Replace with exported PNG](images/your_coauthor_network.png){width="100%"}
:::

::: {.column width="45%"}
**Interpretation**

- 4 communities: policy-modeling, energy-systems, metrics, governance
- Two bridge authors link governance ↔ modeling
- Peripheral cluster = emerging topic (post-2022)
:::
:::

> **Tip:** If the image is too tall, add `{width="85%"}` or split into two slides.

---

## Common pitfalls & remedies

| Pitfall | Symptom | Remedy |
|---|---|---|
| Too dense | Hairball | Threshold weights; facet by community |
| Label clutter | Overlapping text | Label only top nodes; add hover in interactive tools |
| Misleading distances | "Far" nodes read as unrelated | Explain layout limits; show adjacency/matrix view |
| Over-interpretation | Spurious clusters | Cross-check with keywords, venues, time |

---

## Export & reporting

- Export **PNG/SVG** with fixed legend & caption
- Include **methods box**: data source, cleaning, thresholds, algorithms
- Provide **summary table**: top nodes per metric, community sizes, density

```{=html}
<div class="scroll">
<table>
  <thead><tr><th>Metric</th><th>Top Node</th><th>Value</th></tr></thead>
  <tbody>
    <tr><td>Degree</td><td>Author A</td><td>34</td></tr>
    <tr><td>Betweenness</td><td>Author B</td><td>0.21</td></tr>
    <tr><td>PageRank</td><td>Paper X</td><td>0.008</td></tr>
  </tbody>
</table>
</div>
```

---

# Wrap-up

- **Part 2**: choose the right graph and transformation
- **Part 3**: measure global, meso, and node roles carefully
- **Part 4**: visualize to reveal structure—filter and annotate responsibly

> Next: hands-on notebook to build co-authorship and keyword networks from Scopus exports.

