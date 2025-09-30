"""
Orchestrator for two-agent loop: Analyzer ↔ Querier.
"""
import time
from typing import Dict, List, Any, Optional
from .agents.analyzer import Analyzer
from .agents.querier import Querier


class TwoAgentOrchestrator:
    """
    Orchestrates the interaction between Analyzer and Querier agents.

    Workflow:
    1. Initialize Analyzer with subject text and Annif top-2
    2. Analyzer plans initial round of Querier requests
    3. Loop:
       - Execute Querier requests in parallel (or series)
       - Integrate responses into Analyzer memory
       - Analyzer decides next requests or stop
    4. Final synthesis from Analyzer
    """

    def __init__(self, llm_manager, max_rounds: int = 5, verbose: bool = True):
        """
        Initialize orchestrator.

        Args:
            llm_manager: LLM manager for Analyzer
            max_rounds: maximum rounds
            verbose: whether to print progress
        """
        self.llm_manager = llm_manager
        self.max_rounds = max_rounds
        self.verbose = verbose

        self.analyzer = Analyzer(llm_manager, max_rounds=max_rounds, verbose=verbose)
        self.querier = Querier()

        self.execution_log = []

    def classify(
        self,
        subject_text: str,
        annif_top2: List[str]
    ) -> Dict[str, Any]:
        """
        Execute the two-agent classification loop.

        Args:
            subject_text: the subject to classify
            annif_top2: Annif's top 2 DDC suggestions

        Returns:
            Dict with final classification result and metadata
        """
        start_time = time.time()

        self._log(f"Starting two-agent classification for: {subject_text}")
        self._log(f"Annif top-2: {annif_top2}")

        # Initialize Analyzer
        self.analyzer.initialize(subject_text, annif_top2)

        # Plan initial round
        self._log("\n=== Round 0: Initial Planning ===")
        initial_requests = self.analyzer.plan_initial_round()
        self._log(f"Analyzer planned {len(initial_requests)} initial request(s)")

        # Execute initial requests
        for i, request in enumerate(initial_requests):
            self._log(f"\nExecuting request {i+1}/{len(initial_requests)}")
            self._log(f"  Numbers: {request.numbers}")
            self._log(f"  Keywords: {request.keywords}")
            self._log(f"  Sources: {request.sources}")

            response = self.querier.execute(request)
            self._log(f"  -> Got {len(response.hits)} hits")

            self.analyzer.integrate_response(response)

        # Main loop
        round_num = 1
        while round_num <= self.max_rounds:
            self._log(f"\n=== Round {round_num} ===")

            # Get last facet candidates (if any)
            facet_candidates = {}  # Could be extracted from last response

            # Plan next round
            next_requests = self.analyzer.plan_next_round(facet_candidates)

            if not next_requests:
                self._log("Analyzer decided to stop")
                break

            self._log(f"Analyzer planned {len(next_requests)} request(s)")

            # Execute requests
            for i, request in enumerate(next_requests):
                self._log(f"\nExecuting request {i+1}/{len(next_requests)}")
                self._log(f"  Numbers: {request.numbers}")
                self._log(f"  Keywords: {request.keywords}")
                self._log(f"  Sources: {request.sources}")

                response = self.querier.execute(request)
                self._log(f"  -> Got {len(response.hits)} hits")

                self.analyzer.integrate_response(response)

            round_num += 1

        # Final synthesis
        self._log("\n=== Final Synthesis ===")
        final_result = self.analyzer.synthesize_final()

        elapsed = time.time() - start_time

        # Build complete result
        result = {
            "final_ddc": final_result.get("final_ddc", annif_top2[0]),
            "confidence": final_result.get("confidence", 0.0),
            "justification": final_result.get("justification", ""),
            "components": final_result.get("components", {}),
            "alternatives": final_result.get("alternatives", []),
            "cited_evidence": final_result.get("cited_evidence", []),
            "metadata": {
                "subject_text": subject_text,
                "annif_top2": annif_top2,
                "rounds_executed": round_num,
                "elapsed_seconds": round(elapsed, 2),
                "memory_stats": self.analyzer.get_memory_stats(),
                "querier_stats": self.querier.get_stats(),
                "relevance_history": self.analyzer.state.relevance_history,
                "facets": self.analyzer.state.facets
            }
        }

        self._log(f"\n=== Result ===")
        self._log(f"Final DDC: {result['final_ddc']}")
        self._log(f"Confidence: {result['confidence']:.2f}")
        self._log(f"Elapsed: {elapsed:.2f}s")

        return result

    def _log(self, message: str):
        """
        Log a message if verbose is enabled.
        """
        if self.verbose:
            print(message)

        self.execution_log.append({
            "timestamp": time.time(),
            "message": message
        })

    def get_execution_log(self) -> List[Dict]:
        """
        Get the execution log.
        """
        return self.execution_log


# Convenience function for easy usage
def classify_subject(
    subject_text: str,
    annif_top2: List[str],
    llm_manager,
    max_rounds: int = 5,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to classify a subject using the two-agent system.

    Args:
        subject_text: the subject to classify
        annif_top2: Annif's top 2 DDC suggestions
        llm_manager: LLM manager instance
        max_rounds: maximum rounds
        verbose: whether to print progress

    Returns:
        Classification result dict
    """
    orchestrator = TwoAgentOrchestrator(
        llm_manager=llm_manager,
        max_rounds=max_rounds,
        verbose=verbose
    )

    return orchestrator.classify(subject_text, annif_top2)