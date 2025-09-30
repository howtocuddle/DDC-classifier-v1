# Detective System v3 - Quick Start Guide

## Installation

1. **Install dependencies**:
   ```bash
   cd "D:\Projects\Annif pro\huggingface_bundle"
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r detective_systemv3/requirements.txt
   ```

2. **Set up OpenRouter API** (optional for testing, required for full classification):
   - Sign up at https://openrouter.ai/
   - Get API key from https://openrouter.ai/keys
   - Create `detective_systemv3/api.txt`:
     ```
     sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

3. **Ensure Annif Docker is running**:
   ```bash
   cd "D:\Projects\Annif pro"
   python annifctl.py build    # First time only
   ```

## Basic Usage

### 1. Quick Classification (Retrieval-Only)

Test the retrieval system without LLM:

```bash
python detective_systemv3/quick_classify.py "constitutional law"
python detective_systemv3/quick_classify.py "library science dictionaries"
python detective_systemv3/quick_classify.py "quantum mechanics"
```

**Output**:
- Annif suggestions
- Top 10 matching DDC entries
- Recommended DDC number with confidence score

### 2. Test Querier Performance

Analyze retrieval quality and find optimal limits:

```bash
# Test with SBERT semantic search
python detective_systemv3/test_querier.py "library science" --semantic --top-n 15

# Compare different limits
python detective_systemv3/test_querier.py "constitutional law" --k-per-source 10 --max-docs 35

# Test without semantic search
python detective_systemv3/test_querier.py "ancient history" --top-n 20
```

**Output**:
- Top N results with signal breakdown
- Relevance statistics
- Confidence distribution
- Average signal contributions

### 3. Full Classification with LLM

Run the complete 2-agent system:

```bash
# Default model (Grok 2)
python detective_systemv3/run_classification.py "summer stories by clara rannet"

# With verbose output
python detective_systemv3/run_classification.py "constitutional law" --verbose

# With streaming (see LLM thinking in real-time)
python detective_systemv3/run_classification.py "quantum physics" --stream

# Limit rounds
python detective_systemv3/run_classification.py "library science" --max-rounds 3
```

## Model Selection

### Quick Examples

```bash
# Default (free, good)
python run_classification.py "constitutional law"

# Best quality (paid)
python run_classification.py "quantum physics" -m "anthropic/claude-3.5-sonnet" --stream

# Fast & free
python run_classification.py "ancient history" -m "google/gemini-2.0-flash-exp:free"

# Cost-effective (paid)
python run_classification.py "library science" -m "openai/gpt-4o-mini"
```

### Popular Models

| Model | Command Flag | Cost | Best For |
|-------|-------------|------|----------|
| Grok 2 (default) | `(none)` | Free | General use, testing |
| Claude 3.5 Sonnet | `-m "anthropic/claude-3.5-sonnet"` | $$$ | Best quality, complex reasoning |
| Gemini Flash | `-m "google/gemini-2.0-flash-exp:free"` | Free | Speed, iteration |
| GPT-4o-mini | `-m "openai/gpt-4o-mini"` | $ | Good balance, cost-effective |
| GPT-4o | `-m "openai/gpt-4o"` | $$$ | Strong performance |

See `MODELS.md` for complete list.

## Command Reference

### run_classification.py

```bash
python run_classification.py [OPTIONS] "subject text"

Required:
  "subject text"          Subject to classify

Options:
  --annif-top2 N1 N2     Override Annif suggestions (default: auto-fetch)
  --max-rounds N         Maximum rounds (default: 5)
  --verbose              Show detailed output
  --stream               Stream LLM responses in real-time
  -m, --model MODEL      OpenRouter model (default: x-ai/grok-2-1212)
  -h, --help             Show help message
```

### quick_classify.py

```bash
python quick_classify.py "subject text" [annif1] [annif2]

Arguments:
  "subject text"         Subject to classify
  annif1, annif2        Optional: override Annif suggestions

Examples:
  python quick_classify.py "constitutional law"
  python quick_classify.py "library science" 026 020
```

### test_querier.py

```bash
python test_querier.py [OPTIONS] "subject text"

Required:
  "subject text"         Subject to test

Options:
  --annif-top2 N1 N2    Override Annif suggestions
  --top-n N             Number of results to display (default: 20)
  --k-per-source N      Top-k per source (default: 20)
  --max-docs N          Max total docs (default: 100)
  --semantic            Enable SBERT semantic search
  --semantic-weight W   Semantic weight (default: 0.25)
  -h, --help            Show help message
```

## Workflow Examples

### Example 1: Test a Subject

```bash
# 1. Quick check
python detective_systemv3/quick_classify.py "ancient Roman history"

# 2. Analyze querier performance
python detective_systemv3/test_querier.py "ancient Roman history" --semantic --top-n 20

# 3. Full classification with streaming
python detective_systemv3/run_classification.py "ancient Roman history" --stream
```

### Example 2: Compare Models

```bash
# Test with free models
python run_classification.py "quantum mechanics" -m "x-ai/grok-2-1212"
python run_classification.py "quantum mechanics" -m "google/gemini-2.0-flash-exp:free"

# Test with paid model
python run_classification.py "quantum mechanics" -m "anthropic/claude-3.5-sonnet"
```

### Example 3: Optimize Querier Settings

```bash
# Test different limits
python test_querier.py "library science" --k-per-source 5 --max-docs 20
python test_querier.py "library science" --k-per-source 10 --max-docs 35
python test_querier.py "library science" --k-per-source 20 --max-docs 100

# Compare with/without semantic search
python test_querier.py "library science" --semantic --top-n 15
python test_querier.py "library science" --top-n 15
```

## Understanding Output

### quick_classify.py Output

```
[*] Annif Top-10 Suggestions:
  1. 342      Constitutional law                           1.0000
  ...

[*] Top 10 matches:
  1. 342-349      Branches of law...
     Source: Sch2_ranges     Score: 0.9573
     Signals: exact_number=1.000, range_cover=1.000, ...

[+] DDC: 342-349
[+] Confidence: 95.73%
```

**Key metrics**:
- **Score**: Combined signal score (0-1)
- **Signals**: Individual matching signals (exact match, fuzzy, semantic, etc.)
- **Confidence**: Final recommendation confidence

### test_querier.py Output

```
[*] Relevance Statistics:
  Total hits: 90
  Score range: 0.7345 - 0.9461
  Mean score: 0.8496
  Top-5 mean: 0.9311

  Confidence distribution:
    High (>0.7): 90
    Medium (0.4-0.7): 0
    Low (<=0.4): 0

  Average signals:
    semantic_similarity      : 0.608  ← SBERT contribution
    heading_fuzzy            : 0.769
    desc_fuzzy               : 0.657
```

**What to look for**:
- **Top-10 mean > 0.90**: Excellent retrieval quality
- **High confidence hits**: Most results should be >0.7
- **Semantic similarity**: Should be ~0.6-0.7 when enabled
- **Total hits**: Should be manageable (30-50 ideal for LLM)

### run_classification.py Output (with --stream)

```
[*] Using OpenRouter model: anthropic/claude-3.5-sonnet

[*] Annif Top-10 Suggestions:
  ...

💭 Analyzer LLM thinking...
----------------------------------------------------------------------
{
  "facets": {
    "primary_subject": "fiction",
    ...
  },
  "requests": [...]
}
----------------------------------------------------------------------

[+] Final DDC: 813.6
[+] Confidence: 92.00%

Justification:
  Fiction work by contemporary American author...
```

## Troubleshooting

### Annif Docker Issues

```
[ERROR] Annif Docker failed: ...
```

**Solution**:
```bash
cd "D:\Projects\Annif pro"
python annifctl.py build
```

### OpenRouter API Issues

```
[WARN] OpenRouter unavailable (OpenRouter API key not found)
```

**Solution**:
1. Create `detective_systemv3/api.txt` with your key
2. Or set env: `set OPENROUTER_API_KEY=sk-or-v1-xxx`

### Unicode/Emoji Display Issues (Windows)

```
UnicodeEncodeError: 'charmap' codec can't encode...
```

**Solution**: Already fixed in latest version (uses ASCII indicators)

### Model Not Found

```
Error: Model 'xyz' not found
```

**Solution**: Check model ID at https://openrouter.ai/models

## Performance Tips

1. **Start with quick_classify** - test retrieval before full LLM run
2. **Use test_querier** - optimize limits before production
3. **Try free models first** - validate prompt/flow before paid models
4. **Use --stream** - see LLM thinking, catch issues early
5. **Limit rounds** - use `--max-rounds 3` for faster testing

## Next Steps

1. ✅ Test with `quick_classify.py`
2. ✅ Analyze with `test_querier.py`
3. 📝 Add your OpenRouter API key to `api.txt`
4. 🚀 Run full classification with `run_classification.py`
5. 🎯 Optimize limits based on test results
6. 🔄 Compare different models for your use case

---
For detailed model information, see `MODELS.md`
For analysis results, see `QUERIER_ANALYSIS.md`
For complete changes, see `UPDATES.md`
