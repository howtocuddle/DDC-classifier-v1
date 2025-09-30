# Detective System v3 - Usage Guide

## Quick Start Scripts

We provide two standalone scripts for easy usage:

### 1. Quick Classification (No LLM Required)

**File**: `quick_classify.py`

This script uses only the retrieval engine without requiring an LLM. Perfect for testing and quick lookups.

```bash
# Basic usage
python quick_classify.py "constitutional law"

# With custom Annif suggestions
python quick_classify.py "library science" 026 020

# Another example
python quick_classify.py "ancient history" 930 900
```

**Features**:
- No LLM required
- Fast retrieval-only search
- Shows top 10 matches with scores
- Displays signal breakdowns
- Falls back to Annif suggestions if no matches

### 2. Full Classification (With LLM)

**File**: `run_classification.py`

This script runs the full two-agent system with Analyzer and Querier.

```bash
# Basic usage
python run_classification.py "constitutional law"

# With verbose output
python run_classification.py "library science" --verbose

# Custom settings
python run_classification.py "ancient history" --max-rounds 3 --annif-top2 930 900

# Stream output (same as verbose for now)
python run_classification.py "philosophy" --stream
```

**Options**:
- `--annif-top2 NUM1 NUM2`: Specify Annif top 2 suggestions (default: 342 340)
- `--max-rounds N`: Maximum rounds (default: 5)
- `--verbose`: Show detailed progress
- `--stream`: Stream output (alias for --verbose)

**Features**:
- Full two-agent system (Analyzer + Querier)
- Multi-round evidence gathering
- Relevance-based stopping
- Detailed justifications
- Alternative classifications
- Cited evidence

## Output Explanation

### Quick Classify Output

```
SEARCH RESULTS
--------------
Total hits: 10

Top 10 matches:
1. 342 - Constitutional law
   Source: Sch2
   Score: 0.850
   Signals: exact_number=1.00, heading_fuzzy=0.75
   Description: Laws of specific jurisdictions and areas...

RECOMMENDED DDC
---------------
DDC: 342
Confidence: 0.85
Source: Sch2
```

### Full Classification Output

```
CLASSIFICATION RESULT
---------------------
Final DDC: 342
Confidence: 0.85

Justification:
342 is the standard DDC classification for Constitutional
and Administrative Law...

Alternatives Considered:
  - 340: Too broad - covers all law
  - 320: Political science, not law

Cited Evidence:
  - 342 (Sch2)
    Score: 0.92
    Role: primary base number

Metadata:
  Rounds: 2
  Time: 1.5s
  Artifacts: 15
```

## When to Use Which Script

### Use `quick_classify.py` when:
- You want fast results without LLM
- Testing the retrieval engine
- You have good Annif suggestions
- You don't need detailed justifications
- You want to see raw retrieval scores

### Use `run_classification.py` when:
- You need detailed analysis
- You want multi-round refinement
- You need justifications and alternatives
- You want facet analysis
- You have an LLM manager to integrate

## Integration with Your LLM Manager

To use your own LLM manager instead of the mock:

**Edit `run_classification.py`**:

```python
# Replace this:
llm_manager = MockLLMManager()

# With this:
from your_system.llm_manager import YourLLMManager
llm_manager = YourLLMManager(
    model="your-model",
    api_key="your-key"
)
```

Or import from detective_system:

```python
from detective_system.llm_manager import LLMManager

llm_manager = LLMManager(
    model_name="gpt-4",
    # ... your config
)
```

## Programmatic Usage

### Quick Retrieval Search

```python
from detective_systemv3.agents.querier import Querier
from detective_systemv3.retrieval.schemas import QuerierRequest

querier = Querier()

request = QuerierRequest(
    numbers=["342", "340"],
    keywords=["constitutional", "law"],
    facets={},
    sources=["Sch2", "Sch3"],
    limits={"k_per_source": 20, "max_docs": 50},
    options={"expand_synonyms": True}
)

response = querier.execute(request)

for hit in response.hits[:10]:
    print(f"{hit.doc.ddc_number}: {hit.doc.heading} (score: {hit.score:.3f})")
```

### Full Classification

```python
from detective_systemv3.orchestrator import classify_subject
from your_system.llm_manager import YourLLMManager

llm_manager = YourLLMManager()

result = classify_subject(
    subject_text="constitutional law",
    annif_top2=["342", "340"],
    llm_manager=llm_manager,
    max_rounds=5,
    verbose=True
)

print(f"DDC: {result['final_ddc']}")
print(f"Confidence: {result['confidence']}")
print(result['justification'])
```

## Common Issues

### No matches found (0 hits)

This is expected if:
- Data files in `detective_system/data_processed/` are empty
- You haven't populated the DDC data yet
- The JSON files exist but contain empty arrays

**Solution**: Populate your data files with actual DDC entries, or use the fallback Annif suggestions.

### Import errors

If you get `ImportError: attempted relative import`:
- Use the standalone scripts (`quick_classify.py` or `run_classification.py`)
- Don't run `orchestrator.py` directly
- Make sure you're in the correct directory

### Unicode encoding errors on Windows

Already fixed! The system now uses ASCII-compatible symbols:
- `->` instead of `→`
- `[OK]` instead of `✓`
- `[FAIL]` instead of `✗`
- `[WARN]` instead of `⚠️`

## Testing with Real Data

To test with real DDC data:

1. Populate `detective_system/data_processed/` with your DDC JSON files
2. Each file should contain an array of DDC entries:

```json
[
  {
    "ddc_number": "342",
    "heading": "Constitutional law",
    "description": "Laws of specific jurisdictions...",
    "parent": "340",
    "children": ["342.01", "342.02"],
    "page": 123
  }
]
```

3. Run the scripts again to see real results

## Performance Tips

1. **First run is slow**: Loading all sources takes 1-5 seconds
2. **Subsequent searches are fast**: In-memory searches are 50-200ms
3. **Use quick_classify.py for batch processing**: No LLM overhead
4. **Cache the Querier instance**: Reuse it for multiple searches

## Examples

### Library Science
```bash
python quick_classify.py "library catalogs and collections" 026 025
```

### Ancient History
```bash
python run_classification.py "Ancient Roman history" --annif-top2 937 930
```

### Philosophy
```bash
python run_classification.py "epistemology and theory of knowledge" --verbose
```

### Literature
```bash
python quick_classify.py "American poetry 20th century" 811 810
```

## Getting Help

```bash
python run_classification.py --help
```

For more information, see:
- `README.md` - Full system documentation
- `INSTALLATION_SUCCESS.md` - Installation details
- `example_usage.py` - Code examples