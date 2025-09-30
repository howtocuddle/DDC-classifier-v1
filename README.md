# Detective System v3: Two-Agent DDC Classification

A sophisticated two-agent system for Dewey Decimal Classification (DDC) that combines LLM-driven analysis with programmatic retrieval over comprehensive DDC data sources.

## Architecture

### Core Components

```
detective_systemv3/
├── retrieval/          # Multi-signal search engine
│   ├── schemas.py      # Data models (DDCDoc, SearchHit, etc.)
│   ├── loaders.py      # Load all data_processed/** JSON
│   ├── range_index.py  # DDC number normalization & range parsing
│   ├── search.py       # Multi-signal search across sources
│   ├── scoring.py      # Signal fusion and scoring
│   └── synonyms.py     # Keyword expansion
├── agents/             # Two-agent system
│   ├── querier.py      # Programmatic search executor (no LLM)
│   └── analyzer.py     # LLM-driven analysis with memory & stop logic
├── memory_ext/         # Memory management
│   ├── memory_store.py # Artifact storage with deduplication
│   └── abstraction.py  # LLM-ready context building
├── orchestrator.py     # Two-agent loop coordinator
├── prompts.py          # Analyzer prompts
└── tests/              # Unit and integration tests
```

## Features

### Retrieval Engine
- **Multi-signal scoring**: Combines 8+ signals (exact number, prefix, range coverage, fuzzy text, keywords, standard subdivisions, table alignment)
- **Robust range parsing**: Handles malformed ranges (e.g., `220.1-220.Summary`, `822.3301-822.2`) with prefix-coverage fallbacks
- **Parent inference**: Derives parent when null without modifying source data
- **Standard subdivisions**: Dual-search strategy (parent ranges + child normal schedules)
- **Synonym expansion**: Curated maps + optional SBERT embeddings

### Data Sources
- **Schedules**: Sch2, Sch3 (normal + ranges)
- **Manuals**: Tables book & Schedules (normal + flowcharts)
- **Tables**: T1 (standard subdivisions, form, time, audience), T2 (geographic), T3A/B/C (literature variants)

### Analyzer Agent (LLM-driven)
- **Facet tracking**: Maintains 6 facets (subject, discipline, geo, time, form, audience)
- **Memory management**: Relevance-weighted artifacts with deduplication (max 500)
- **Stop criteria**:
  - Relevance trend: 2 consecutive drops > 0.05
  - Absolute threshold: relevance < 0.35 with no high-signal artifacts
  - Confidence: ≥ 0.85
- **Evidence-based synthesis**: Cites specific artifacts in final justification

### Querier Agent (Programmatic)
- Stateless search executor
- No LLM calls (fast, cacheable)
- Returns top-k hits with signals, facet candidates, diagnostics

## Usage

### Basic Classification

```python
from detective_systemv3.orchestrator import classify_subject

# Assuming you have an llm_manager instance
result = classify_subject(
    subject_text="Dictionaries of library science",
    annif_top2=["026", "020"],
    llm_manager=your_llm_manager,
    max_rounds=5,
    verbose=True
)

print(f"Final DDC: {result['final_ddc']}")
print(f"Confidence: {result['confidence']}")
print(f"Justification: {result['justification']}")
```

### Advanced Usage

```python
from detective_systemv3.orchestrator import TwoAgentOrchestrator

orchestrator = TwoAgentOrchestrator(
    llm_manager=your_llm_manager,
    max_rounds=5,
    verbose=True
)

result = orchestrator.classify(
    subject_text="Library catalogs and collections management",
    annif_top2=["026", "025.3"]
)

# Access detailed metadata
print(result['metadata']['rounds_executed'])
print(result['metadata']['memory_stats'])
print(result['metadata']['relevance_history'])
print(result['metadata']['facets'])

# Access cited evidence
for evidence in result['cited_evidence']:
    print(f"{evidence['ddc_number']} ({evidence['source']}) - {evidence['role']}")
```

## Running Tests

```bash
# Range parser tests
python detective_systemv3/tests/test_range_parser.py

# Scoring tests
python detective_systemv3/tests/test_scoring.py

# Integration tests (requires data_processed/)
python detective_systemv3/tests/test_integration.py
```

## Scoring Signals

| Signal | Weight | Description |
|--------|--------|-------------|
| `exact_number` | 0.7 | Exact DDC number match |
| `prefix_number` | 0.4 | Prefix similarity |
| `range_cover` | 0.6 | Number covered by range |
| `heading_fuzzy` | 0.6 | Fuzzy match on heading (RapidFuzz) |
| `desc_fuzzy` | 0.3 | Fuzzy match on description |
| `keyword_proximity` | 0.3 | Keyword coverage in text |
| `std_subdiv_flag` | 0.2 | Standard subdivision indicator |
| `table_alignment` | 0.3 | Table aligns with facets |

**Combiner**: Soft-OR (probabilistic sum): `S = 1 - ∏(1 - w·s)`

## Range Parsing Examples

```python
from detective_systemv3.retrieval.range_index import parse_range, covers, parse_ddc_number

# Fully numeric
range_tuple = parse_range("331.3810001-331.3810009")
number_key = parse_ddc_number("331.3810005")
assert covers(range_tuple, number_key) == True

# Hybrid suffix
range_tuple = parse_range("220.1-220.Summary")
# Falls back to prefix coverage

# Descending (auto-swap)
range_tuple = parse_range("822.3301-822.2")
# Swaps bounds automatically

# Loose span
range_tuple = parse_range("001-008")
# Covers all 001.*, 002.*, ..., 008.*
```

## Memory Management

- **Deduplication**: Hash on `(ddc_number, source, snippet[:100])`
- **Pruning**: Top-scoring artifacts retained when exceeding max (500)
- **Tags**: `exact-match`, `standard-subdivision`, `table-T1`, `range`
- **Filtering**: Query by tags, number, source

## Prompt Structure

### System Prompt
- Defines Analyzer role and responsibilities
- Lists available sources
- Specifies JSON response schema

### Round Prompts
- Initial: Extract facets, plan first searches
- Iterative: Update facets, compute relevance, decide stop/continue
- Final: Synthesize complete DDC with justification

## Dependencies

- `rapidfuzz` (fuzzy string matching)
- `sentence-transformers` (optional, for SBERT embeddings)
- Your LLM manager (e.g., from detective_system)

## Integration with Existing System

To integrate with `detective_system`:

```python
from detective_system.llm_manager import LLMManager
from detective_systemv3.orchestrator import classify_subject

llm_manager = LLMManager(...)  # Your existing manager

result = classify_subject(
    subject_text="...",
    annif_top2=["...", "..."],
    llm_manager=llm_manager
)
```

## Performance Notes

- **Loading**: All sources loaded once at initialization (~1-5s depending on dataset size)
- **Search**: In-memory fuzzy + exact + range matching (~50-200ms per request)
- **Querier**: Programmatic, no LLM calls (fast)
- **Analyzer**: LLM-driven, 1 call per round (~1-3s per round depending on model)
- **Total**: Typically 3-5 rounds, ~10-30s end-to-end

## Future Enhancements

1. **SBERT embeddings**: Pre-compute and index for semantic reranking
2. **Calibration**: Isotonic regression on signal fusion with labeled validation set
3. **Caching**: Cache RapidFuzz results keyed by query
4. **Parallel requests**: Execute multiple Querier requests in true parallel
5. **Iterative refinement**: Allow Analyzer to refine past queries based on new insights

## Known Limitations

- **Inconsistent data**: Handled heuristically (no source edits)
- **LLM parsing**: Fallback to default requests on JSON parse failures
- **No multi-modal**: Text-only (no image/PDF analysis)

## License

[Freee]

## Contact


[HowToCuddle]
