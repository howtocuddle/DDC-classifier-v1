"""
Verification script to check if detective_systemv3 is properly installed.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("Detective System v3 - Installation Verification")
print("=" * 60)

# Test 1: Import core modules
print("\n[1/5] Testing core imports...")
try:
    from detective_systemv3.retrieval.schemas import DDCDoc, SearchHit
    from detective_systemv3.retrieval.range_index import parse_ddc_number, parse_range
    from detective_systemv3.retrieval.scoring import combine_signals
    from detective_systemv3.agents.querier import Querier
    from detective_systemv3.agents.analyzer import Analyzer
    from detective_systemv3.orchestrator import TwoAgentOrchestrator
    print("   [OK] All core modules imported successfully")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Check rapidfuzz dependency
print("\n[2/5] Testing rapidfuzz dependency...")
try:
    from rapidfuzz import fuzz
    test_score = fuzz.partial_ratio("libraries", "library science")
    print(f"   [OK] rapidfuzz working (test score: {test_score})")
except Exception as e:
    print(f"   [FAIL] rapidfuzz failed: {e}")
    sys.exit(1)

# Test 3: Test range parser
print("\n[3/5] Testing range parser...")
try:
    # Test normal range
    range_tuple = parse_range("331.3810001-331.3810009")
    print(f"   [OK] Parsed range: {range_tuple[2].value}")

    # Test malformed range
    range_tuple = parse_range("220.1-220.Summary")
    print(f"   [OK] Parsed malformed range: {range_tuple[2].value}")

    # Test DDC number parsing
    table, segments, orig = parse_ddc_number("026.073")
    print(f"   [OK] Parsed DDC number: segments={segments}")
except Exception as e:
    print(f"   [FAIL] Range parser failed: {e}")
    sys.exit(1)

# Test 4: Test scoring
print("\n[4/5] Testing scoring combiner...")
try:
    signals = {
        "exact_number": 0.8,
        "heading_fuzzy": 0.6
    }
    score = combine_signals(signals)
    print(f"   [OK] Combined score: {score:.3f}")
except Exception as e:
    print(f"   [FAIL] Scoring failed: {e}")
    sys.exit(1)

# Test 5: Check data_processed directory
print("\n[5/5] Checking data_processed directory...")
try:
    from detective_systemv3.retrieval.loaders import find_data_processed_dir
    data_dir = find_data_processed_dir()
    print(f"   [OK] Found data directory: {data_dir}")

    # Check if files exist
    schedules_dir = data_dir / "schedules"
    if schedules_dir.exists():
        files = list(schedules_dir.glob("*.json"))
        print(f"   [OK] Found {len(files)} schedule files")
    else:
        print(f"   [WARN] Schedules directory not found (expected for first run)")
except Exception as e:
    print(f"   [WARN] Data directory check: {e}")
    print(f"   (This is expected if detective_system/data_processed/ doesn't exist)")

print("\n" + "=" * 60)
print("[SUCCESS] Installation verification completed!")
print("=" * 60)
print("\nNext steps:")
print("1. Ensure detective_system/data_processed/ directory exists")
print("2. Run: python detective_systemv3/tests/test_range_parser.py")
print("3. Run: python detective_systemv3/tests/test_scoring.py")
print("4. Run: python detective_systemv3/example_usage.py")
print("\nFor full functionality, integrate with your LLM manager:")
print("  from detective_systemv3.orchestrator import classify_subject")
print("  result = classify_subject(text, annif_top2, llm_manager)")