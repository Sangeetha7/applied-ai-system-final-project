"""Reliability metrics for recommender outputs."""

from __future__ import annotations

from typing import Dict, List, Tuple

Recommendation = Tuple[Dict, float, str]


def _safe_lower(value: object) -> str:
    return str(value).strip().lower()


def evaluate_recommendations(user_prefs: Dict, recommendations: List[Recommendation]) -> Dict[str, float]:
    """Computes simple reliability metrics for one profile's top-k results."""
    if not recommendations:
        return {
            "count": 0.0,
            "genre_match_rate": 0.0,
            "mood_match_rate": 0.0,
            "avg_energy_error": 1.0,
            "avg_score": 0.0,
            "low_confidence_rate": 1.0,
        }

    target_genre = _safe_lower(user_prefs.get("preferred_genre") or user_prefs.get("genre", ""))
    target_mood = _safe_lower(user_prefs.get("preferred_mood") or user_prefs.get("mood", ""))
    target_energy = user_prefs.get("target_energy")
    if target_energy is None:
        target_energy = user_prefs.get("energy", 0.5)

    try:
        target_energy = float(target_energy)
    except (TypeError, ValueError):
        target_energy = 0.5

    target_energy = max(0.0, min(1.0, target_energy))

    genre_matches = 0
    mood_matches = 0
    low_confidence = 0
    total_energy_error = 0.0
    total_score = 0.0

    for song, score, explanation in recommendations:
        if _safe_lower(song.get("genre", "")) == target_genre:
            genre_matches += 1
        if _safe_lower(song.get("mood", "")) == target_mood:
            mood_matches += 1

        song_energy = float(song.get("energy", 0.5))
        total_energy_error += abs(target_energy - song_energy)
        total_score += float(score)

        if "confidence: low" in _safe_lower(explanation):
            low_confidence += 1

    count = float(len(recommendations))
    return {
        "count": count,
        "genre_match_rate": genre_matches / count,
        "mood_match_rate": mood_matches / count,
        "avg_energy_error": total_energy_error / count,
        "avg_score": total_score / count,
        "low_confidence_rate": low_confidence / count,
    }


def evaluate_batch(
    user_profiles: Dict[str, Dict],
    profile_results: Dict[str, List[Recommendation]],
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, float]]:
    """Evaluates all profiles and returns per-profile and aggregate metrics."""
    per_profile: Dict[str, Dict[str, float]] = {}

    for profile_name, user_prefs in user_profiles.items():
        recs = profile_results.get(profile_name, [])
        per_profile[profile_name] = evaluate_recommendations(user_prefs, recs)

    if not per_profile:
        return per_profile, {
            "profiles_evaluated": 0.0,
            "overall_genre_match_rate": 0.0,
            "overall_mood_match_rate": 0.0,
            "overall_avg_energy_error": 1.0,
            "overall_avg_score": 0.0,
            "overall_low_confidence_rate": 1.0,
        }

    profile_count = float(len(per_profile))
    summary = {
        "profiles_evaluated": profile_count,
        "overall_genre_match_rate": sum(m["genre_match_rate"] for m in per_profile.values()) / profile_count,
        "overall_mood_match_rate": sum(m["mood_match_rate"] for m in per_profile.values()) / profile_count,
        "overall_avg_energy_error": sum(m["avg_energy_error"] for m in per_profile.values()) / profile_count,
        "overall_avg_score": sum(m["avg_score"] for m in per_profile.values()) / profile_count,
        "overall_low_confidence_rate": sum(m["low_confidence_rate"] for m in per_profile.values()) / profile_count,
    }

    return per_profile, summary
