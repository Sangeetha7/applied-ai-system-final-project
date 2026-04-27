"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
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

    for profile_name, user_prefs in user_profiles.items():
        print(f"\n{'='*100}")
        print(f"Top 5 recommendations for: {profile_name}")
        print(f"{'='*100}")
        
        # Simple ASCII Table Header
        print(f"{'Song Title (Artist)':<45} | {'Score':<5} | {'Reasons'}")
        print(f"{'-'*100}")
        
        recommendations = recommend_songs(user_prefs, songs, k=5)

        for rec in recommendations:
            song, score, explanation = rec
            song_info = f"{song['title']} ({song['artist']})"
            # Fixed-width formatting to create clean columns
            print(f"{song_info:<45} | {score:>.2f} | {explanation}")


if __name__ == "__main__":
    main()
