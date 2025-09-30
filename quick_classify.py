"""
Quick classification script with minimal dependencies.
Usage: python quick_classify.py "subject text"
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import everything we need
from detective_systemv3.retrieval.loaders import load_all_sources
from detective_systemv3.retrieval.search import DDCSearchEngine
from detective_systemv3.agents.querier import Querier
from detective_systemv3.retrieval.schemas import QuerierRequest
from detective_system.omikuji import get_suggestions


def quick_classify(subject_text, annif_top2=None):
    """
    Quick classification without LLM (retrieval only).

    This is useful for testing the retrieval engine without needing an LLM.
    """
    if annif_top2 is None:
        # Required: get Annif suggestions via Docker (no fallback)
        try:
            suggestions = get_suggestions(subject_text, limit=2, use_docker=True)
            if len(suggestions) >= 2:
                annif_top2 = [suggestions[0].notation, suggestions[1].notation]
                print(f"[Annif] Got top-2: {annif_top2} (scores: {suggestions[0].score:.3f}, {suggestions[1].score:.3f})")
            elif len(suggestions) == 1:
                annif_top2 = [suggestions[0].notation, "000"]
                print(f"[Annif] Got top-1: {annif_top2[0]} (score: {suggestions[0].score:.3f})")
            else:
                print("[ERROR] Annif returned no suggestions.")
                sys.exit(1)
        except RuntimeError as e:
            print(f"[ERROR] Annif Docker failed: {e}")
            print("Ensure 'annif-omikuji:latest' is built: cd D:\\Projects\\Annif pro && python annifctl.py build")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("  Quick DDC Classification (Retrieval-Only)")
    print("=" * 70)
    print(f"Subject: {subject_text}")
    print(f"Annif suggestions: {annif_top2}")
    print("=" * 70 + "\n")

    # Initialize Querier
    print("[*] Loading DDC sources...")
    querier = Querier()
    print(f"[+] Loaded {len(querier.all_sources)} source types\n")
    print()

    # Extract keywords from subject
    keywords = [word.strip().lower() for word in subject_text.split() if len(word) > 3]

    # Create search request
    request = QuerierRequest(
        numbers=annif_top2,
        keywords=keywords,
        facets={
            "subject": subject_text,
            "discipline": None,
            "geo": None,
            "time": None,
            "form": None,
            "audience": None
        },
        sources=["Sch2", "Sch3", "Sch2_ranges", "Sch3_ranges", "ManSc", "ManTB"],
        limits={"k_per_source": 20, "max_docs": 50},
        options={
            "expand_synonyms": True,
            "include_std_subdivisions": True,
            # Enable semantic similarity by default for demo
            "use_semantic": True,
            "semantic_model": "all-MiniLM-L6-v2",
            # Weight contribution of semantic similarity (final influence ~= 0.25)
            "semantic_weight": 0.25
        }
    )

    # Execute search
    print("Searching...")
    response = querier.execute(request)

    # Display results
    print("\n" + "=" * 70)
    print("  SEARCH RESULTS")
    print("=" * 70)
    print(f"Total hits: {len(response.hits)}")
    print()

    if response.hits:
        print("[*] Top 10 matches:")
        print("-" * 70)
        for i, hit in enumerate(response.hits[:10], 1):
            print(f"\n{i:2d}. {hit.doc.ddc_number:12s} {hit.doc.heading[:45]:45s}")
            print(f"    Source: {hit.doc.source:15s} Score: {hit.score:.4f}")

            # Show top signals
            top_signals = sorted(hit.signals.items(), key=lambda x: x[1], reverse=True)[:3]
            signals_str = ", ".join([f"{name}={val:.3f}" for name, val in top_signals if val > 0])
            if signals_str:
                print(f"    Signals: {signals_str}")

            # Show snippet
            if hit.doc.description:
                snippet = hit.doc.description[:100]
                print(f"    {snippet}...")

        # Best match
        best = response.hits[0]
        print("\n" + "=" * 70)
        print("  RECOMMENDED DDC")
        print("=" * 70)
        print(f"[+] DDC: {best.doc.ddc_number}")
        print(f"[+] Heading: {best.doc.heading}")
        print(f"[+] Confidence: {best.score:.2%}")
        print(f"Source: {best.doc.source}")

    else:
        print("No matches found.")
        print()
        print("Possible reasons:")
        print("  - Data files in detective_system/data_processed/ are empty")
        print("  - Subject keywords don't match DDC headings")
        print("  - Annif suggestions are not in the loaded data")
        print()
        print("Falling back to Annif suggestion: {}".format(annif_top2[0]))
        print("=" * 60)
        print("RECOMMENDED DDC")
        print("=" * 60)
        print(f"DDC: {annif_top2[0]}")
        print(f"Confidence: 0.50 (fallback)")

    print()
    print("Numbers found: {}".format(response.numbers_found))
    print()
    print("Diagnostics:")
    for key, value in response.diagnostics.items():
        print(f"  {key}: {value}")

    print()
    print("=" * 60)

    return response


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_classify.py \"subject text\" [annif1] [annif2]")
        print()
        print("Examples:")
        print('  python quick_classify.py "constitutional law"')
        print('  python quick_classify.py "library science" 026 020')
        print('  python quick_classify.py "ancient history" 930 900')
        sys.exit(1)

    subject = sys.argv[1]
    annif = None

    if len(sys.argv) >= 4:
        annif = [sys.argv[2], sys.argv[3]]

    try:
        quick_classify(subject, annif)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()