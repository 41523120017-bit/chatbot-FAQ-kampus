# Graph Report - .  (2026-07-27)

## Corpus Check
- Corpus is ~2,259 words - fits in a single context window. You may not need a graph.

## Summary
- 19 nodes · 23 edges · 4 communities (3 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 4 input · 442 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Dialog State Management|Dialog State Management]]
- [[_COMMUNITY_NLP Training Pipeline|NLP Training Pipeline]]
- [[_COMMUNITY_Python Dependencies|Python Dependencies]]

## God Nodes (most connected - your core abstractions)
1. `DialogManager` - 6 edges
2. `preprocess_text()` - 4 edges
3. `Python Dependency Manifest` - 4 edges
4. `Membaca database JSON secara real-time` - 1 edges
5. `Reset alur percakapan ke kondisi awal` - 1 edges
6. `Streamlit` - 1 edges
7. `Joblib` - 1 edges
8. `NumPy` - 1 edges
9. `scikit-learn` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Python Runtime Dependency Set** — requirements_streamlit, requirements_joblib, requirements_numpy, requirements_scikit_learn [EXTRACTED 1.00]

## Communities (4 total, 1 thin omitted)

### Community 0 - "Dialog State Management"
Cohesion: 0.38
Nodes (3): DialogManager, Membaca database JSON secara real-time, Reset alur percakapan ke kondisi awal

### Community 2 - "Python Dependencies"
Cohesion: 0.40
Nodes (5): Joblib, NumPy, Python Dependency Manifest, scikit-learn, Streamlit

## Knowledge Gaps
- **4 isolated node(s):** `Streamlit`, `Joblib`, `NumPy`, `scikit-learn`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DialogManager` connect `Dialog State Management` to `NLP Training Pipeline`, `Streamlit Interface`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Why does `preprocess_text()` connect `NLP Training Pipeline` to `Dialog State Management`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **What connects `Membaca database JSON secara real-time`, `Reset alur percakapan ke kondisi awal`, `Streamlit` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._