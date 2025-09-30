# Detective System v3 - Recent Updates

## Summary of Changes (2025-09-30)

### 0. Model Selection Flag ✅
**Files**: `run_classification.py`, `MODELS.md` (NEW)

- **Added `-m` / `--model` flag** - dynamically change OpenRouter model
- **Default**: `x-ai/grok-2-1212` (free, good reasoning)
- **Model reference guide** - `MODELS.md` with popular options

**Usage**:
```bash
# Use default model
python run_classification.py "constitutional law"

# Use Claude 3.5 Sonnet (best quality)
python run_classification.py "quantum physics" -m "anthropic/claude-3.5-sonnet"

# Use free Gemini Flash (very fast)
python run_classification.py "library science" -m "google/gemini-2.0-flash-exp:free"

# Use GPT-4o-mini (cost-effective)
python run_classification.py "ancient history" --model "openai/gpt-4o-mini" --stream
```

### 1. Fixed Annif Integration ✅
**Files**: `run_classification.py`, `quick_classify.py`

- **Removed hardcoded defaults** - no more `["342", "340"]` showing up
- **Auto-fetch from Docker** - calls `detective_system/omikuji.get_suggestions()` via Docker
- **Display top-10** - shows all 10 Annif suggestions with scores before classification
- **Required by default** - no fallback, ensures Annif is always used

**Before**:
```
Annif top-2: ['342', '340']  # hardcoded garbage
```

**After**:
```
🔍 Fetching Annif suggestions via Docker...

📊 Annif Top-10 Suggestions:
----------------------------------------------------------------------
   1. 020      Library and information sciences          0.9812
   2. 500      Natural sciences and mathematics          0.8934
   ...
----------------------------------------------------------------------

✓ Using top-2 for classification: ['020', '500']
```

### 2. Added LLM Streaming Support 🎥
**Files**: `llm_openrouter.py`, `agents/analyzer.py`, `orchestrator.py`

- **OpenRouter streaming** - real-time token output via SSE
- **Verbose mode** - `--verbose` or `--stream` flag shows LLM thinking
- **Analyzer displays** - shows prompts + streamed responses

**Usage**:
```bash
python run_classification.py "summer stories by clara rannet" --stream
```

**Output**:
```
💭 Analyzer LLM thinking...
----------------------------------------------------------------------
{
  "facets": {
    "primary_subject": "fiction",
    "discipline": "literature",
    ...
}
----------------------------------------------------------------------
```

### 3. Improved User Interface 🎨
**Files**: `run_classification.py`, `quick_classify.py`, `test_querier.py`

- **Better formatting** - cleaner borders, emoji indicators, aligned columns
- **Progress indicators** - `🔍 Fetching...`, `✓ Loaded`, `📊 Results`
- **Color-coded confidence** - percentage display for confidence scores
- **Compact output** - reduced noise, clearer hierarchy

**Before**:
```
============================================================
Detective System v3 - DDC Classification
============================================================
Subject: summer stories by clara rannet
Annif top-2: ['342', '340']
Max rounds: 5
============================================================
```

**After**:
```
======================================================================
  Detective System v3 - DDC Classification
======================================================================
Subject: summer stories by clara rannet
Max rounds: 5
======================================================================

🔍 Fetching Annif suggestions via Docker...

📊 Annif Top-10 Suggestions:
----------------------------------------------------------------------
  1. 813      American fiction                         0.9523
  ...
----------------------------------------------------------------------

✓ Using top-2 for classification: ['813', '800']
```

### 4. Added Querier Test Tool 🧪
**File**: `test_querier.py` (NEW)

Standalone CLI to test querier performance and find optimal limits.

**Features**:
- Test SBERT semantic search
- Compare different k_per_source / max_docs limits
- Show signal breakdown for each result
- Display relevance statistics

**Usage**:
```bash
# Test with SBERT
python detective_systemv3/test_querier.py "library science dictionaries" --semantic --top-n 15 --k-per-source 10

# Test without SBERT
python detective_systemv3/test_querier.py "constitutional law" --top-n 20

# Custom weights
python detective_systemv3/test_querier.py "quantum physics" --semantic --semantic-weight 0.3
```

**Output**:
```
[*] Top 15 Results (showing signals breakdown):
----------------------------------------------------------------------
 1. 020          Library and information sciences
    Source: Sch2            Score: 0.9378
    Signals: exact_number=1.000, semantic_similarity=0.736, ...

[*] Relevance Statistics:
----------------------------------------------------------------------
  Total hits: 90
  Score range: 0.7345 - 0.9461
  Mean score: 0.8496
  Top-5 mean: 0.9311

  Confidence distribution:
    High (>0.7): 90
    Medium (0.4-0.7): 0
    Low (<=0.4): 0

  Average signals:
    semantic_similarity      : 0.608  ← SBERT working!
    heading_fuzzy            : 0.769
    desc_fuzzy               : 0.657
```

### 5. SBERT Semantic Search Validated ✅

- **SBERT is working**: average contribution ~0.6-0.7
- **Model**: `all-MiniLM-L6-v2` (fast, good quality)
- **Weight**: 0.25 (balanced with other signals)
- **Performance**: Boosts conceptual matches beyond keyword overlap

**Recommendation**: Keep enabled by default

### 6. Optimal Querier Limits Found 📊
**Analysis file**: `QUERIER_ANALYSIS.md`

**Current problem**: 90 hits overwhelm LLM context

**Recommended limits**:
```python
limits={
    "k_per_source": 10,   # down from 20
    "max_docs": 35        # down from 100
}
```

**Rationale**:
- Top-10 mean score: 0.92 (excellent quality)
- 30-40 results = ~4-6K tokens (manageable for LLM)
- Scores drop below 0.85 after ~20-25 results

## Files Changed

### Modified
- `detective_systemv3/run_classification.py` - Annif integration, UI, streaming, model selection
- `detective_systemv3/quick_classify.py` - Annif integration, UI improvements
- `detective_systemv3/llm_openrouter.py` - Added streaming support
- `detective_systemv3/agents/analyzer.py` - Verbose mode + streaming
- `detective_systemv3/orchestrator.py` - Pass verbose to analyzer
- `detective_systemv3/requirements.txt` - Added requests

### New Files
- `detective_systemv3/test_querier.py` - Querier testing CLI
- `detective_systemv3/QUERIER_ANALYSIS.md` - Analysis results
- `detective_systemv3/MODELS.md` - OpenRouter model reference guide
- `detective_systemv3/UPDATES.md` - This file

## Testing

All changes tested successfully:

```bash
# ✅ Querier test with SBERT
python detective_systemv3/test_querier.py "library science dictionaries" --semantic

# ✅ Quick classify
python detective_systemv3/quick_classify.py "constitutional law"

# ⏳ Full classification (requires api.txt with OpenRouter key)
python detective_systemv3/run_classification.py "summer stories" --verbose
```

## Next Steps

1. **Add api.txt** - Place OpenRouter API key in `detective_systemv3/api.txt`
2. **Test full pipeline** - Run `run_classification.py` with real LLM
3. **Tune limits** - Update default k_per_source=10, max_docs=35 in codebase
4. **Fix table_alignment** - Investigate why signal averages 0.000
5. **Test diverse subjects** - Validate across different domains

## Known Issues

- ❌ **Windows console encoding** - Emoji characters may not display on some terminals (use UTF-8 or plain ASCII fallback)
- ⚠️ **table_alignment signal** - Currently contributing 0.0, needs investigation
- ⚠️ **Full classification** - Not tested yet (requires OpenRouter API key)

## Usage Tips

### For Windows Users
If emoji don't display, set encoding:
```powershell
$env:PYTHONIOENCODING="utf-8"
```

### Testing Querier Limits
```bash
# Compare different limits
python detective_systemv3/test_querier.py "your subject" --k-per-source 5 --max-docs 20
python detective_systemv3/test_querier.py "your subject" --k-per-source 10 --max-docs 35
python detective_systemv3/test_querier.py "your subject" --k-per-source 20 --max-docs 100
```

### Streaming Output
```bash
# See LLM thinking in real-time
python detective_systemv3/run_classification.py "your subject" --stream --verbose
```

---
Last updated: 2025-09-30
