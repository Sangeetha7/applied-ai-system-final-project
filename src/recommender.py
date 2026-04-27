import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file and casts numeric fields."""
    print(f"Loading songs from {csv_path}...")
    songs_data = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                row['id'] = int(row['id'])
                row['energy'] = float(row['energy'])
                row['tempo_bpm'] = float(row['tempo_bpm'])
                row['valence'] = float(row['valence'])
                row['danceability'] = float(row['danceability'])
                row['acousticness'] = float(row['acousticness'])
                songs_data.append(row)
    except FileNotFoundError:
        print(f"Error: Could not find '{csv_path}'.")
    
    print(f"Successfully loaded {len(songs_data)} songs.")    
    return songs_data

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Calculates a song's numeric score and returns a list of matching reasons based on user preferences."""
    score = 0.0
    reasons = []

    # Get user preferences, handling both potential key names
    target_genre = user_prefs.get('preferred_genre') or user_prefs.get('genre', '')
    target_mood = user_prefs.get('preferred_mood') or user_prefs.get('mood', '')
    target_energy = user_prefs.get('target_energy') if user_prefs.get('target_energy') is not None else user_prefs.get('energy')

    # 1. Genre Match (+1.0 points - halved)
    if song.get('genre', '').lower() == target_genre.lower():
        score += 1.0
        reasons.append(f"Genre match (+1.0)")

    # 2. Mood Match (+1.0 points)
    if song.get('mood', '').lower() == target_mood.lower():
        score += 1.0
        reasons.append(f"Mood match (+1.0)")

    # 3. Energy Similarity (Up to +2.0 points - doubled)
    if target_energy is not None:
        song_energy = song.get('energy', 0.5)
        energy_score = (1.0 - abs(target_energy - song_energy)) * 2.0
        score += energy_score
        reasons.append(f"Energy proximity (+{energy_score:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Evaluates and ranks all songs to return the top k recommendations."""
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        # Combine the list of reasons into a single readable string
        explanation = ", ".join(reasons) if reasons else "No specific matches."
        scored_songs.append((song, score, explanation))
        
    # Sort the list of tuples by the score (which is at index 1), descending
    ranked_songs = sorted(scored_songs, key=lambda x: x[1], reverse=True)
    
    return ranked_songs[:k]
