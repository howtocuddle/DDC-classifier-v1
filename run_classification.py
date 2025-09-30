"""
Standalone script to run DDC classification.
Usage: python run_classification.py "subject text" [--max-rounds 5] [--verbose]
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from detective_systemv3.orchestrator import classify_subject
from detective_systemv3.llm_openrouter import OpenRouterLLM
from detective_system.omikuji import get_suggestions


class MockLLMManager:
    """Mock LLM manager for demonstration."""

    def generate(self, messages):
        """Mock LLM response."""
        user_prompt = messages[-1]["content"]

        # Parse subject from prompt to make better mock responses
        if "Initial Analysis" in user_prompt:
            return """{
                "facets": {
                    "subject": "constitutional law",
                    "discipline": "law",
                    "geo": null,
                    "time": null,
                    "form": null,
                    "audience": null
                },
                "next_requests": [
                    {
                        "numbers": ["342"],
                        "keywords": ["constitutional", "law", "constitution"],
                        "facets": {},
                        "sources": ["Sch2", "Sch3", "Sch2_ranges", "ManSc"],
                        "limits": {"k_per_source": 20, "max_docs": 100},
                        "options": {"expand_synonyms": true, "include_std_subdivisions": true}
                    }
                ],
                "round_relevance": 0.8,
                "stop_decision": false,
                "confidence": 0.7,
                "reasoning": "Constitutional law is typically classified in 342",
                "synthesis": {
                    "ddc_number": "342",
                    "components": {"base": "342"},
                    "justification": "342 is for constitutional and administrative law"
                }
            }"""
        elif "Round" in user_prompt:
            return """{
                "facets": {
                    "subject": "constitutional law",
                    "discipline": "law",
                    "geo": null,
                    "time": null,
                    "form": null,
                    "audience": null
                },
                "next_requests": [],
                "round_relevance": 0.75,
                "stop_decision": true,
                "confidence": 0.85,
                "reasoning": "Strong evidence for 342, stopping",
                "synthesis": {
                    "ddc_number": "342",
                    "components": {"base": "342"},
                    "justification": "342 confirmed for constitutional law"
                }
            }"""
        else:
            # Final synthesis
            return """{
                "final_ddc": "342",
                "confidence": 0.85,
                "components": {
                    "base": "342",
                    "standard_subdivisions": [],
                    "tables": []
                },
                "justification": "342 is the standard DDC classification for Constitutional and Administrative Law. This includes constitutional law of specific jurisdictions, constitutional history, and related topics.",
                "alternatives": [
                    {
                        "ddc": "340",
                        "reason_rejected": "Too broad - covers all law, not specific to constitutional law"
                    },
                    {
                        "ddc": "320",
                        "reason_rejected": "Political science, not law specifically"
                    }
                ],
                "cited_evidence": [
                    {
                        "ddc_number": "342",
                        "source": "Sch2",
                        "score": 0.92,
                        "role": "primary base number for constitutional law"
                    }
                ]
            }"""


def main():
    parser = argparse.ArgumentParser(
        description="Run DDC classification on a subject",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_classification.py "constitutional law"
  python run_classification.py "library science dictionaries" --max-rounds 3
  python run_classification.py "ancient history" --verbose
  python run_classification.py "quantum physics" -m "anthropic/claude-3.5-sonnet"
  python run_classification.py "summer stories" -m "google/gemini-2.0-flash-exp:free" --stream
        """
    )

    parser.add_argument(
        "subject",
        help="Subject text to classify"
    )

    parser.add_argument(
        "--annif-top2",
        nargs=2,
        default=None,
        help="Override Annif top 2 suggestions (default: fetch from Annif Docker)"
    )

    parser.add_argument(
        "--max-rounds",
        type=int,
        default=5,
        help="Maximum rounds (default: 5)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream output (same as --verbose for now)"
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        default="x-ai/grok-2-1212",
        help="OpenRouter model to use (default: x-ai/grok-2-1212). Popular options: anthropic/claude-3.5-sonnet, google/gemini-2.0-flash-exp:free, openai/gpt-4o"
    )

    args = parser.parse_args()

    # Create OpenRouter LLM manager; fallback to mock if missing API key
    try:
        llm_manager = OpenRouterLLM(model=args.model)
        print(f"[*] Using OpenRouter model: {args.model}\n")
    except Exception as e:
        print(f"[WARN] OpenRouter unavailable ({e}). Falling back to MockLLMManager.")
        llm_manager = MockLLMManager()

    print("\n" + "=" * 70)
    print("  Detective System v3 - DDC Classification")
    print("=" * 70)
    print(f"Subject: {args.subject}")
    print(f"Max rounds: {args.max_rounds}")
    print("=" * 70 + "\n")

    # Fetch Annif suggestions (required; use Docker)
    annif_top2 = args.annif_top2
    if annif_top2 is None:
        # User did not override, fetch from Annif via Docker
        print("[*] Fetching Annif suggestions via Docker...")
        try:
            sugg = get_suggestions(args.subject, limit=10, use_docker=True)
            if not sugg:
                print("[ERROR] Annif returned no suggestions. Ensure Docker image 'annif-omikuji:latest' is built.")
                sys.exit(1)
            
            # Display top 10
            print("\n[*] Annif Top-10 Suggestions:")
            print("-" * 70)
            for i, s in enumerate(sugg[:10], 1):
                print(f"  {i:2d}. {s.notation:8s} {s.label:45s} {s.score:.4f}")
            print("-" * 70)
            
            # Use top 2 for classification
            if len(sugg) >= 2:
                annif_top2 = [sugg[0].notation, sugg[1].notation]
                print(f"\n[+] Using top-2 for classification: {annif_top2}\n")
            elif len(sugg) == 1:
                annif_top2 = [sugg[0].notation, "000"]
                print(f"\n[+] Using top-1 for classification: {annif_top2}\n")
        except RuntimeError as e:
            print(f"\n[ERROR] Annif Docker failed: {e}")
            print("Ensure 'annif-omikuji:latest' is built: cd D:\\Projects\\Annif pro && python annifctl.py build")
            sys.exit(1)
    else:
        print(f"\n[+] Using user-provided Annif top-2: {annif_top2}\n")

    # Run classification
    result = classify_subject(
        subject_text=args.subject,
        annif_top2=annif_top2,
        llm_manager=llm_manager,
        max_rounds=args.max_rounds,
        verbose=args.verbose or args.stream
    )

    # Display results
    print("\n" + "=" * 70)
    print("  CLASSIFICATION RESULT")
    print("=" * 70)
    print(f"[+] Final DDC: {result['final_ddc']}")
    print(f"[+] Confidence: {result['confidence']:.2%}")
    print("\nJustification:")
    print(f"  {result['justification']}")
    print()

    if result.get('alternatives'):
        print("Alternatives Considered:")
        for alt in result['alternatives']:
            print(f"  [-] {alt['ddc']}: {alt['reason_rejected']}")
        print()

    if result.get('cited_evidence'):
        print("Cited Evidence:")
        for evidence in result['cited_evidence']:
            print(f"  • {evidence['ddc_number']} ({evidence['source']})")
            print(f"    Score: {evidence.get('score', 'N/A')}, Role: {evidence['role']}")
        print()

    print("Metadata:")
    print(f"  Rounds: {result['metadata']['rounds_executed']}")
    print(f"  Time: {result['metadata']['elapsed_seconds']}s")
    print(f"  Artifacts: {result['metadata']['memory_stats']['total_artifacts']}")
    print()

    if result['metadata'].get('facets'):
        print("Facets Detected:")
        for facet, value in result['metadata']['facets'].items():
            if value:
                print(f"  • {facet.capitalize()}: {value}")

    print("=" * 70)


if __name__ == "__main__":
    main()