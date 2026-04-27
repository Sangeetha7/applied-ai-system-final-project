from src.reliability import evaluate_recommendations, evaluate_batch


def test_evaluate_recommendations_returns_expected_bounds():
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    recs = [
        (
            {
                "id": 1,
                "title": "Song A",
                "artist": "Artist",
                "genre": "pop",
                "mood": "happy",
                "energy": 0.75,
            },
            5.0,
            "Confidence: high (0.80)",
        ),
        (
            {
                "id": 2,
                "title": "Song B",
                "artist": "Artist",
                "genre": "rock",
                "mood": "happy",
                "energy": 0.65,
            },
            3.0,
            "Confidence: low (0.42)",
        ),
    ]

    metrics = evaluate_recommendations(user_prefs, recs)

    assert metrics["count"] == 2.0
    assert 0.0 <= metrics["genre_match_rate"] <= 1.0
    assert 0.0 <= metrics["mood_match_rate"] <= 1.0
    assert 0.0 <= metrics["avg_energy_error"] <= 1.0
    assert metrics["avg_score"] > 0.0
    assert 0.0 <= metrics["low_confidence_rate"] <= 1.0


def test_evaluate_batch_aggregates_profiles():
    user_profiles = {
        "p1": {"genre": "pop", "mood": "happy", "energy": 0.8},
        "p2": {"genre": "lofi", "mood": "chill", "energy": 0.3},
    }
    profile_results = {
        "p1": [
            (
                {
                    "id": 1,
                    "title": "Song A",
                    "artist": "Artist",
                    "genre": "pop",
                    "mood": "happy",
                    "energy": 0.8,
                },
                4.0,
                "Confidence: medium (0.60)",
            )
        ],
        "p2": [
            (
                {
                    "id": 2,
                    "title": "Song B",
                    "artist": "Artist",
                    "genre": "lofi",
                    "mood": "chill",
                    "energy": 0.3,
                },
                4.2,
                "Confidence: high (0.78)",
            )
        ],
    }

    per_profile, summary = evaluate_batch(user_profiles, profile_results)

    assert len(per_profile) == 2
    assert summary["profiles_evaluated"] == 2.0
    assert 0.0 <= summary["overall_genre_match_rate"] <= 1.0
    assert 0.0 <= summary["overall_mood_match_rate"] <= 1.0
    assert 0.0 <= summary["overall_avg_energy_error"] <= 1.0
    assert summary["overall_avg_score"] > 0.0
    assert 0.0 <= summary["overall_low_confidence_rate"] <= 1.0
