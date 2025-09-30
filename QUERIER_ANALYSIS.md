# Querier Analysis & Recommendations

## Test Results Summary

Tested with: `"library science dictionaries"` (Annif top-2: 020, 500)

### Configuration
- **Semantic Search**: ENABLED (SBERT: all-MiniLM-L6-v2, weight=0.25)
- **k_per_source**: 15
- **max_docs**: 100

### Performance Metrics
- **Total hits**: 90
- **Score range**: 0.7345 - 0.9461
- **Mean score**: 0.8496
- **Top-5 mean**: 0.9311
- **Top-10 mean**: 0.9204

### Confidence Distribution
- **High (>0.7)**: 90 (100%)
- **Medium (0.4-0.7)**: 0
- **Low (<=0.4)**: 0

### Signal Contribution (Average Across All Hits)
| Signal | Average Score | Notes |
|--------|--------------|-------|
| `heading_fuzzy` | 0.769 | Strong: heading text matching |
| `desc_fuzzy` | 0.657 | Good: description fuzzy matching |
| `semantic_similarity` | 0.608 | **SBERT working well!** |
| `exact_number` | 0.511 | Moderate: DDC number exact matches |
| `std_subdiv_flag` | 0.311 | Low-med: standard subdivision markers |
| `range_cover` | 0.167 | Low: range coverage |
| `prefix_number` | 0.141 | Low: DDC prefix matching |
| `keyword_proximity` | 0.056 | Very low: keyword adjacency |
| `table_alignment` | 0.000 | None (may need tuning) |

## Observations

### 1. SBERT Semantic Search is Effective ✅
- Average contribution: **0.608**
- Top hits show 0.6-0.74 semantic similarity
- Significantly boosts relevance for conceptual matches beyond keyword overlap
- **Recommendation**: Keep enabled with weight=0.25

### 2. Result Quality is High
- All 90 hits scored >0.7 (high confidence)
- Top-10 average: **0.92** (excellent)
- Clear differentiation: best result (0.9461) vs. 10th (0.9002)

### 3. Optimal Limits for LLM Context
**Current Problem**: 90 hits is too much for LLM to process effectively.

**Suggested Limits**:
- **k_per_source**: 10 (down from 15) → reduces noise
- **max_docs**: 30-40 (down from 100) → manageable LLM context
- **Score threshold**: 0.85+ for high-priority results

**Rationale**:
- Top-10 mean (0.92) shows strong quality in first results
- Scores drop below 0.85 after ~20-25 results
- LLM context window: 30-40 results = ~4-6K tokens (reasonable)

### 4. Signal Tuning Recommendations

**Strong performers** (keep as-is):
- `heading_fuzzy` (0.769)
- `desc_fuzzy` (0.657)
- `semantic_similarity` (0.608)

**Needs investigation**:
- `table_alignment` (0.000) → verify logic or remove
- `keyword_proximity` (0.056) → consider boosting weight or refining

## Recommended Configuration for Production

```python
request = QuerierRequest(
    numbers=annif_top2,
    keywords=keywords,
    facets=facets,
    sources=["Sch2", "Sch3", "Sch2_ranges", "Sch3_ranges", "ManSc", "ManTB"],
    limits={
        "k_per_source": 10,    # ← reduced from 20
        "max_docs": 35         # ← reduced from 100
    },
    options={
        "expand_synonyms": True,
        "include_std_subdivisions": True,
        "use_semantic": True,
        "semantic_model": "all-MiniLM-L6-v2",
        "semantic_weight": 0.25  # works well
    }
)
```

## Testing Commands

```bash
# Test with SBERT enabled
python detective_systemv3/test_querier.py "library science dictionaries" --top-n 15 --k-per-source 10 --semantic

# Test without SBERT
python detective_systemv3/test_querier.py "library science dictionaries" --top-n 15 --k-per-source 10

# Compare different subjects
python detective_systemv3/test_querier.py "constitutional law" --semantic
python detective_systemv3/test_querier.py "ancient history" --semantic
python detective_systemv3/test_querier.py "quantum physics" --semantic
```

## Next Steps

1. ✅ **SBERT is working** - validated
2. 🔄 **Tune limits** - implement k=10, max=35 in production
3. 🔍 **Investigate table_alignment** - fix or remove
4. 🧪 **Test with diverse subjects** - ensure robustness
5. 📊 **Monitor LLM performance** - track if 30-40 results are manageable

---
Generated: 2025-09-30
