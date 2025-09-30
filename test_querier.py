"""
Test Querier with different limits and semantic settings to find optimal thresholds.
Usage: python test_querier.py "subject text" [--top-n 10] [--semantic] [--k-per-source 20]
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from detective_systemv3.agents.querier import Querier
from detective_systemv3.retrieval.schemas import QuerierRequest
from detective_system.omikuji import get_suggestions


def test_querier(
    subject_text: str,
    annif_top2: list,
    top_n: int = 20,
    k_per_source: int = 20,
    max_docs: int = 100,
    use_semantic: bool = False,
    semantic_weight: float = 0.25
):
    """Test querier and display relevance statistics."""
    
    print("\n" + "=" * 70)
    print("  Querier Relevance Test")
    print("=" * 70)
    print(f"Subject: {subject_text}")
    print(f"Annif top-2: {annif_top2}")
    print(f"Semantic: {use_semantic} (weight={semantic_weight if use_semantic else 'N/A'})")
    print(f"Limits: k_per_source={k_per_source}, max_docs={max_docs}")
    print("=" * 70 + "\n")

    # Initialize Querier
    print("[*] Loading DDC sources...")
    querier = Querier()
    print(f"[+] Loaded {len(querier.all_sources)} source types\n")

    # Extract keywords
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
        limits={"k_per_source": k_per_source, "max_docs": max_docs},
        options={
            "expand_synonyms": True,
            "include_std_subdivisions": True,
            "use_semantic": use_semantic,
            "semantic_model": "all-MiniLM-L6-v2",
            "semantic_weight": semantic_weight
        }
    )

    # Execute search
    print("[*] Searching...")
    response = querier.execute(request)

    # Display top N results with signals
    print(f"\n[*] Top {top_n} Results (showing signals breakdown):")
    print("-" * 70)
    
    for i, hit in enumerate(response.hits[:top_n], 1):
        print(f"\n{i:2d}. {hit.doc.ddc_number:12s} {hit.doc.heading[:40]:40s}")
        print(f"    Source: {hit.doc.source:15s} Score: {hit.score:.4f}")
        
        # Show top signals
        top_signals = sorted(hit.signals.items(), key=lambda x: x[1], reverse=True)[:5]
        signals_str = ", ".join([f"{name}={val:.3f}" for name, val in top_signals if val > 0])
        if signals_str:
            print(f"    Signals: {signals_str}")

    # Relevance statistics
    print("\n" + "-" * 70)
    print("[*] Relevance Statistics:")
    print("-" * 70)
    
    if response.hits:
        scores = [h.score for h in response.hits]
        print(f"  Total hits: {len(response.hits)}")
        print(f"  Score range: {min(scores):.4f} - {max(scores):.4f}")
        print(f"  Mean score: {sum(scores)/len(scores):.4f}")
        print(f"  Top-5 mean: {sum(scores[:5])/min(5, len(scores)):.4f}")
        print(f"  Top-10 mean: {sum(scores[:10])/min(10, len(scores)):.4f}")
        
        # Count high-confidence hits (score > 0.7)
        high_conf = sum(1 for s in scores if s > 0.7)
        med_conf = sum(1 for s in scores if 0.4 < s <= 0.7)
        low_conf = sum(1 for s in scores if s <= 0.4)
        
        print(f"\n  Confidence distribution:")
        print(f"    High (>0.7): {high_conf}")
        print(f"    Medium (0.4-0.7): {med_conf}")
        print(f"    Low (<=0.4): {low_conf}")
        
        # Signal averages
        print(f"\n  Average signals:")
        for signal, val in response.diagnostics.get("top_signals", {}).items():
            print(f"    {signal:25s}: {val:.3f}")
    
    print("\n" + "=" * 70)
    
    return response


def main():
    parser = argparse.ArgumentParser(
        description="Test Querier with different settings",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("subject", help="Subject text to classify")
    parser.add_argument("--annif-top2", nargs=2, default=None, help="Override Annif top-2")
    parser.add_argument("--top-n", type=int, default=20, help="Number of results to display (default: 20)")
    parser.add_argument("--k-per-source", type=int, default=20, help="Top-k per source (default: 20)")
    parser.add_argument("--max-docs", type=int, default=100, help="Max total docs (default: 100)")
    parser.add_argument("--semantic", action="store_true", help="Enable semantic similarity (SBERT)")
    parser.add_argument("--semantic-weight", type=float, default=0.25, help="Semantic weight (default: 0.25)")
    
    args = parser.parse_args()
    
    # Get Annif suggestions if not provided
    annif_top2 = args.annif_top2
    if annif_top2 is None:
        print("[*] Fetching Annif suggestions...")
        try:
            sugg = get_suggestions(args.subject, limit=2, use_docker=True)
            if len(sugg) >= 2:
                annif_top2 = [sugg[0].notation, sugg[1].notation]
            elif len(sugg) == 1:
                annif_top2 = [sugg[0].notation, "000"]
            else:
                print("[ERROR] No Annif suggestions")
                sys.exit(1)
        except RuntimeError as e:
            print(f"[ERROR] Annif failed: {e}")
            sys.exit(1)
    
    test_querier(
        args.subject,
        annif_top2,
        top_n=args.top_n,
        k_per_source=args.k_per_source,
        max_docs=args.max_docs,
        use_semantic=args.semantic,
        semantic_weight=args.semantic_weight
    )


if __name__ == "__main__":
    main()
