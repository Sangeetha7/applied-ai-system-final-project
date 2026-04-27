"""Quality gate checks for recommender reliability metrics."""

from __future__ import annotations

from typing import Dict, List, Tuple


DEFAULT_QUALITY_GATES: Dict[str, float] = {
    "overall_genre_match_rate_min": 0.20,
    "overall_mood_match_rate_min": 0.20,
    "overall_avg_energy_error_max": 0.25,
    "overall_low_confidence_rate_max": 0.75,
}


def evaluate_quality_gates(
    summary_metrics: Dict[str, float],
    gates: Dict[str, float] | None = None,
) -> Tuple[bool, List[str]]:
    """Returns whether metrics pass and a list of failed gate messages."""
    active_gates = gates or DEFAULT_QUALITY_GATES
    failures: List[str] = []

    genre_rate = summary_metrics.get("overall_genre_match_rate", 0.0)
    if genre_rate < active_gates["overall_genre_match_rate_min"]:
        failures.append(
            "overall_genre_match_rate below minimum "
            f"({genre_rate:.3f} < {active_gates['overall_genre_match_rate_min']:.3f})"
        )

    mood_rate = summary_metrics.get("overall_mood_match_rate", 0.0)
    if mood_rate < active_gates["overall_mood_match_rate_min"]:
        failures.append(
            "overall_mood_match_rate below minimum "
            f"({mood_rate:.3f} < {active_gates['overall_mood_match_rate_min']:.3f})"
        )

    energy_error = summary_metrics.get("overall_avg_energy_error", 1.0)
    if energy_error > active_gates["overall_avg_energy_error_max"]:
        failures.append(
            "overall_avg_energy_error above maximum "
            f"({energy_error:.3f} > {active_gates['overall_avg_energy_error_max']:.3f})"
        )

    low_conf = summary_metrics.get("overall_low_confidence_rate", 1.0)
    if low_conf > active_gates["overall_low_confidence_rate_max"]:
        failures.append(
            "overall_low_confidence_rate above maximum "
            f"({low_conf:.3f} > {active_gates['overall_low_confidence_rate_max']:.3f})"
        )

    return len(failures) == 0, failures
