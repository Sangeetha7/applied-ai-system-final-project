"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import logging

try:
    # Package execution path: python -m src.main
    from src.recommender import load_songs, recommend_songs
    from src.reliability import evaluate_batch
    from src.quality_gates import evaluate_quality_gates
except ImportError:
    # Direct script execution path: python src/main.py
    from recommender import load_songs, recommend_songs
    from reliability import evaluate_batch
    from quality_gates import evaluate_quality_gates


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    songs = load_songs("data/songs.csv") 

    # Define distinct user preference profiles
    user_profiles = {
        "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9},
        "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3},
        "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.85},
        
        # Adversarial / Edge Case Profiles
        "High-Energy Sad": {"genre": "classical", "mood": "sad", "energy": 0.99},
        "Zero-Energy EDM": {"genre": "edm", "mood": "intense", "energy": 0.0},
        "Aggressive Lullaby": {"genre": "lullaby", "mood": "angry", "energy": 0.1}
    }

    profile_results = {}

    for profile_name, user_prefs in user_profiles.items():
        print(f"\n{'='*100}")
        print(f"Top 5 recommendations for: {profile_name}")
        print(f"{'='*100}")
        
        # Simple ASCII Table Header
        print(f"{'Song Title (Artist)':<45} | {'Score':<5} | {'Reasons'}")
        print(f"{'-'*100}")
        
        recommendations = recommend_songs(user_prefs, songs, k=5)
        profile_results[profile_name] = recommendations

        for rec in recommendations:
            song, score, explanation = rec
            song_info = f"{song['title']} ({song['artist']})"
            # Fixed-width formatting to create clean columns
            print(f"{song_info:<45} | {score:>.2f} | {explanation}")

    per_profile_metrics, summary_metrics = evaluate_batch(user_profiles, profile_results)

    print(f"\n{'='*100}")
    print("Reliability Report")
    print(f"{'='*100}")
    print(f"{'Profile':<24} | {'GenreHit':>8} | {'MoodHit':>7} | {'AvgEnergyErr':>12} | {'LowConf':>7}")
    print(f"{'-'*100}")
    for profile_name, metrics in per_profile_metrics.items():
        print(
            f"{profile_name:<24} | "
            f"{metrics['genre_match_rate']:.2f} | "
            f"{metrics['mood_match_rate']:.2f} | "
            f"{metrics['avg_energy_error']:.3f} | "
            f"{metrics['low_confidence_rate']:.2f}"
        )

    print(f"{'-'*100}")
    print(
        "Overall                    | "
        f"{summary_metrics['overall_genre_match_rate']:.2f} | "
        f"{summary_metrics['overall_mood_match_rate']:.2f} | "
        f"{summary_metrics['overall_avg_energy_error']:.3f} | "
        f"{summary_metrics['overall_low_confidence_rate']:.2f}"
    )

    passed, failures = evaluate_quality_gates(summary_metrics)
    print(f"\nQuality Gates: {'PASS' if passed else 'FAIL'}")
    if failures:
        for failure in failures:
            print(f"- {failure}")


if __name__ == "__main__":
    main()
