"""
Example usage of detective_systemv3.

This script demonstrates how to use the two-agent system for DDC classification.
"""
import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))


def mock_llm_manager():
    """
    Create a mock LLM manager for demonstration.
    Replace this with your actual LLM manager.
    """
    class MockLLMManager:
        def generate(self, messages):
            """
            Mock LLM response.
            In production, this would call your actual LLM.
            """
            # Extract user prompt
            user_prompt = messages[-1]["content"]

            # Mock response based on prompt keywords
            if "Initial Analysis" in user_prompt:
                return """{
                    "facets": {
                        "subject": "library science",
                        "discipline": "information management",
                        "geo": null,
                        "time": null,
                        "form": "reference work",
                        "audience": null
                    },
                    "next_requests": [
                        {
                            "numbers": ["026", "020"],
                            "keywords": ["libraries", "library science", "collections"],
                            "facets": {},
                            "sources": ["Sch2", "Sch3", "Sch2_ranges", "ManSc"],
                            "limits": {"k_per_source": 20, "max_docs": 100},
                            "options": {"expand_synonyms": true, "include_std_subdivisions": true}
                        }
                    ],
                    "round_relevance": 0.8,
                    "stop_decision": false,
                    "confidence": 0.6,
                    "reasoning": "Starting with Annif's top suggestions, searching schedules and manuals",
                    "synthesis": {
                        "ddc_number": "026",
                        "components": {"base": "026"},
                        "justification": "Preliminary: 026 for libraries, collections"
                    }
                }"""
            elif "Round" in user_prompt:
                return """{
                    "facets": {
                        "subject": "library science",
                        "discipline": "information management",
                        "geo": null,
                        "time": null,
                        "form": "reference work",
                        "audience": null
                    },
                    "next_requests": [],
                    "round_relevance": 0.75,
                    "stop_decision": true,
                    "confidence": 0.85,
                    "reasoning": "Strong evidence for 026, stopping",
                    "synthesis": {
                        "ddc_number": "026",
                        "components": {"base": "026"},
                        "justification": "026 is confirmed for library collections"
                    }
                }"""
            else:
                # Final synthesis
                return """{
                    "final_ddc": "026",
                    "confidence": 0.85,
                    "components": {
                        "base": "026",
                        "standard_subdivisions": [],
                        "tables": []
                    },
                    "justification": "Based on strong evidence from schedules and manuals, 026 (Libraries, archives, information centers) is the correct classification for library collections and institutions.",
                    "alternatives": [
                        {
                            "ddc": "020",
                            "reason_rejected": "Too broad - covers all library and information sciences, not specific to libraries as institutions"
                        }
                    ],
                    "cited_evidence": [
                        {
                            "ddc_number": "026",
                            "source": "Sch2",
                            "score": 0.92,
                            "role": "primary base number"
                        }
                    ]
                }"""

    return MockLLMManager()


def example_basic():
    """
    Basic classification example.
    """
    print("=" * 60)
    print("Example 1: Basic Classification")
    print("=" * 60)

    from detective_systemv3.orchestrator import classify_subject

    # Create mock LLM manager (replace with your actual manager)
    llm_manager = mock_llm_manager()

    # Classify a subject
    result = classify_subject(
        subject_text="Dictionaries of library science",
        annif_top2=["026", "020"],
        llm_manager=llm_manager,
        max_rounds=3,
        verbose=True
    )

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Final DDC: {result['final_ddc']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nJustification:")
    print(result['justification'])

    print(f"\nMetadata:")
    print(f"  Rounds executed: {result['metadata']['rounds_executed']}")
    print(f"  Elapsed: {result['metadata']['elapsed_seconds']}s")
    print(f"  Memory artifacts: {result['metadata']['memory_stats']['total_artifacts']}")


def example_advanced():
    """
    Advanced usage with direct orchestrator access.
    """
    print("\n" + "=" * 60)
    print("Example 2: Advanced Usage")
    print("=" * 60)

    from detective_systemv3.orchestrator import TwoAgentOrchestrator

    # Create orchestrator
    llm_manager = mock_llm_manager()
    orchestrator = TwoAgentOrchestrator(
        llm_manager=llm_manager,
        max_rounds=5,
        verbose=False  # Suppress output
    )

    # Classify
    result = orchestrator.classify(
        subject_text="Library catalogs and collections management",
        annif_top2=["026", "025.3"]
    )

    print("\nDetailed Results:")
    print(f"Final DDC: {result['final_ddc']}")
    print(f"Confidence: {result['confidence']:.2f}")

    print(f"\nFacets detected:")
    for facet, value in result['metadata']['facets'].items():
        print(f"  {facet}: {value}")

    print(f"\nRelevance history:")
    for i, rel in enumerate(result['metadata']['relevance_history']):
        print(f"  Round {i}: {rel:.3f}")

    if result.get('alternatives'):
        print(f"\nAlternatives considered:")
        for alt in result['alternatives']:
            print(f"  {alt['ddc']}: {alt['reason_rejected']}")


def example_retrieval_only():
    """
    Example using just the retrieval layer (no agents).
    """
    print("\n" + "=" * 60)
    print("Example 3: Retrieval Layer Only")
    print("=" * 60)

    try:
        from detective_systemv3.retrieval.loaders import load_all_sources
        from detective_systemv3.retrieval.search import DDCSearchEngine

        # Load sources
        print("Loading DDC sources...")
        sources = load_all_sources()
        print(f"Loaded {len(sources)} source types")

        # Create search engine
        engine = DDCSearchEngine(sources)

        # Search
        print("\nSearching for 'libraries'...")
        hits = engine.search(
            numbers=["026"],
            keywords=["libraries", "collections"],
            facets={},
            sources=["Sch2", "Sch3"],
            k_per_source=5,
            max_docs=10
        )

        print(f"\nTop {len(hits)} results:")
        for i, hit in enumerate(hits):
            print(f"\n{i+1}. {hit.doc.ddc_number} - {hit.doc.heading}")
            print(f"   Source: {hit.doc.source}")
            print(f"   Score: {hit.score:.3f}")
            print(f"   Top signals: {sorted(hit.signals.items(), key=lambda x: x[1], reverse=True)[:3]}")

    except FileNotFoundError:
        print("⚠️ Could not find data_processed directory")
        print("Make sure detective_system/data_processed/ exists")


if __name__ == "__main__":
    # Run examples
    example_basic()
    example_advanced()
    example_retrieval_only()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)