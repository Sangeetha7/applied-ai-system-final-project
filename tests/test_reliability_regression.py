from src.recommender import load_songs, recommend_songs
from src.reliability import evaluate_batch
from src.quality_gates import evaluate_quality_gates


def _profiles() -> dict:
    return {
        "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
        "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3},
        "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.85},
        "High-Energy Sad": {"genre": "classical", "mood": "sad", "energy": 0.99},
        "Zero-Energy EDM": {"genre": "edm", "mood": "intense", "energy": 0.0},
        "Aggressive Lullaby": {"genre": "lullaby", "mood": "angry", "energy": 0.1},
    }


def test_recommendations_are_deterministic_for_fixed_inputs():
    songs = load_songs("data/songs.csv")
    profiles = _profiles()

    for _, prefs in profiles.items():
        first = recommend_songs(prefs, songs, k=5)
        second = recommend_songs(prefs, songs, k=5)

        first_ids = [item[0]["id"] for item in first]
        second_ids = [item[0]["id"] for item in second]
        assert first_ids == second_ids


def test_batch_reliability_meets_minimum_quality_gates():
    songs = load_songs("data/songs.csv")
    profiles = _profiles()

    profile_results = {
        profile_name: recommend_songs(prefs, songs, k=5)
        for profile_name, prefs in profiles.items()
    }

    _, summary = evaluate_batch(profiles, profile_results)
    passed, failures = evaluate_quality_gates(summary)

    assert summary["profiles_evaluated"] == 6.0
    assert passed, "Quality gate failures: " + "; ".join(failures)
