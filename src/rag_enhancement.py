"""RAG enhancement evaluation utilities.

Compares baseline retrieval (built-in aliases only) vs enhanced retrieval
(built-in aliases + custom retrieval documents).
"""

from __future__ import annotations

from typing import Dict, List

from src.recommender import Recommender, UserProfile, _dict_to_song, load_retrieval_documents


def _synonym_profiles() -> List[Dict]:
    return [
        {"genre": "electronic", "mood": "calm", "energy": 0.35},
        {"genre": "rap", "mood": "upbeat", "energy": 0.72},
        {"genre": "soul", "mood": "melancholic", "energy": 0.58},
    ]


def _profile_to_user(profile: Dict) -> UserProfile:
    return UserProfile(
        favorite_genre=str(profile["genre"]),
        favorite_mood=str(profile["mood"]),
        target_energy=float(profile["energy"]),
        likes_acoustic=False,
    )


def _semantic_hit_rate(recommender: Recommender, profiles: List[Dict], k: int = 5) -> float:
    """Fraction of profiles where top-k includes at least one semantically aligned song.

    In a tiny catalog, requiring both genre and mood simultaneously can be too strict,
    so this metric counts a hit when either semantic dimension aligns.
    """
    if not profiles:
        return 0.0

    hits = 0
    for profile in profiles:
        user = _profile_to_user(profile)
        genre_targets = recommender._genre_aliases(user.favorite_genre)
        mood_targets = recommender._mood_aliases(user.favorite_mood)
        genre_targets.update(
            recommender._external_aliases(
                "genre_aliases", recommender._normalize_label(user.favorite_genre), recommender.retrieval_documents
            )
        )
        mood_targets.update(
            recommender._external_aliases(
                "mood_aliases", recommender._normalize_label(user.favorite_mood), recommender.retrieval_documents
            )
        )

        recs = recommender.recommend(user, k=k)
        aligned = any(
            recommender._normalize_label(song.genre) in genre_targets
            or recommender._normalize_label(song.mood) in mood_targets
            for song in recs
        )
        if aligned:
            hits += 1

    return hits / len(profiles)


def evaluate_rag_enhancement(songs: List[Dict], k: int = 5) -> Dict[str, float]:
    """Returns baseline vs enhanced retrieval quality on synonym-heavy profiles."""
    song_objects = [_dict_to_song(song) for song in songs]
    profiles = _synonym_profiles()

    baseline = Recommender(song_objects, retrieval_documents={})
    enhanced = Recommender(song_objects, retrieval_documents=load_retrieval_documents())

    baseline_hit_rate = _semantic_hit_rate(baseline, profiles, k=k)
    enhanced_hit_rate = _semantic_hit_rate(enhanced, profiles, k=k)

    return {
        "profiles_evaluated": float(len(profiles)),
        "baseline_semantic_hit_rate": baseline_hit_rate,
        "enhanced_semantic_hit_rate": enhanced_hit_rate,
        "absolute_improvement": enhanced_hit_rate - baseline_hit_rate,
    }
