import csv
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

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
        self._last_retrieval_mode = ""
        self._last_retrieval_by_song_id: Dict[int, str] = {}
        logger.info("Recommender initialized with %d songs", len(songs))

    @staticmethod
    def _normalize_label(value: str) -> str:
        return value.strip().lower()

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(value, high))

    @staticmethod
    def _target_valence_for_mood(mood: str) -> float:
        mood_value_map = {
            "happy": 0.82,
            "uplifting": 0.80,
            "carefree": 0.78,
            "romantic": 0.68,
            "groovy": 0.74,
            "chill": 0.58,
            "relaxed": 0.60,
            "focused": 0.55,
            "moody": 0.45,
            "sad": 0.22,
            "intense": 0.48,
            "angry": 0.32,
            "energetic": 0.62,
        }
        return mood_value_map.get(Recommender._normalize_label(mood), 0.55)

    @staticmethod
    def _genre_aliases(genre: str) -> set[str]:
        canonical = Recommender._normalize_label(genre)
        alias_map = {
            "indie pop": {"indie pop", "pop"},
            "pop": {"pop", "indie pop"},
            "edm": {"edm", "electronic"},
            "hip hop": {"hip hop", "hip-hop", "rap"},
            "r&b": {"r&b", "soul"},
            "lofi": {"lofi", "chillhop"},
        }
        return alias_map.get(canonical, {canonical})

    @staticmethod
    def _mood_aliases(mood: str) -> set[str]:
        canonical = Recommender._normalize_label(mood)
        alias_map = {
            "chill": {"chill", "relaxed", "calm"},
            "relaxed": {"relaxed", "chill", "calm"},
            "happy": {"happy", "uplifting", "carefree"},
            "intense": {"intense", "energetic", "angry"},
            "focused": {"focused", "moody", "chill"},
            "sad": {"sad", "moody"},
        }
        return alias_map.get(canonical, {canonical})

    def _retrieve_candidates(self, user: UserProfile, k: int) -> List[Song]:
        """Retrieves candidate songs before scoring and ranking."""
        if not self.songs:
            logger.warning("Retrieval requested but catalog is empty")
            self._last_retrieval_mode = "empty-catalog"
            self._last_retrieval_by_song_id = {}
            return []

        genre_targets = self._genre_aliases(user.favorite_genre)
        mood_targets = self._mood_aliases(user.favorite_mood)

        strict: List[Song] = []
        for song in self.songs:
            if (
                self._normalize_label(song.genre) in genre_targets
                and self._normalize_label(song.mood) in mood_targets
                and abs(song.energy - user.target_energy) <= 0.20
            ):
                strict.append(song)

        if len(strict) >= max(1, k):
            self._last_retrieval_mode = "strict"
            self._last_retrieval_by_song_id = {
                song.id: "Retrieved by strict genre+mood+energy filter" for song in strict
            }
            logger.info("Retrieval mode=strict candidates=%d", len(strict))
            return strict

        relaxed: List[Song] = []
        for song in self.songs:
            genre_match = self._normalize_label(song.genre) in genre_targets
            mood_match = self._normalize_label(song.mood) in mood_targets
            if (genre_match or mood_match) and abs(song.energy - user.target_energy) <= 0.35:
                relaxed.append(song)

        if relaxed:
            self._last_retrieval_mode = "relaxed"
            self._last_retrieval_by_song_id = {
                song.id: "Retrieved by relaxed filter (genre or mood plus wider energy band)"
                for song in relaxed
            }
            logger.info("Retrieval mode=relaxed candidates=%d", len(relaxed))
            return relaxed

        broad_energy: List[Song] = [
            song for song in self.songs if abs(song.energy - user.target_energy) <= 0.50
        ]
        if broad_energy:
            self._last_retrieval_mode = "energy-fallback"
            self._last_retrieval_by_song_id = {
                song.id: "Retrieved by fallback energy-only filter" for song in broad_energy
            }
            logger.warning("Retrieval mode=energy-fallback candidates=%d", len(broad_energy))
            return broad_energy

        self._last_retrieval_mode = "full-catalog-fallback"
        self._last_retrieval_by_song_id = {
            song.id: "Retrieved by full-catalog fallback" for song in self.songs
        }
        logger.warning("Retrieval mode=full-catalog-fallback candidates=%d", len(self.songs))
        return self.songs

    @staticmethod
    def _score_song(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Returns a numeric score with short reason strings for one song."""
        score = 0.0
        reasons: List[str] = []

        # Genre and mood exact-match anchors.
        if song.genre.lower() == user.favorite_genre.lower():
            score += 1.0
            reasons.append("Genre match (+1.0)")

        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
            reasons.append("Mood match (+1.0)")

        # Energy proximity rewards closeness up to +2.0.
        energy_score = max(0.0, (1.0 - abs(user.target_energy - song.energy)) * 2.0)
        score += energy_score
        reasons.append(f"Energy proximity (+{energy_score:.2f})")

        # Extra feature 1: tempo should loosely track requested energy.
        expected_tempo = 60.0 + (user.target_energy * 100.0)
        tempo_score = max(0.0, 1.0 - abs(expected_tempo - song.tempo_bpm) / 100.0) * 0.6
        score += tempo_score
        reasons.append(f"Tempo alignment (+{tempo_score:.2f})")

        # Extra feature 2: valence should align with requested mood.
        target_valence = Recommender._target_valence_for_mood(user.favorite_mood)
        valence_score = max(0.0, 1.0 - abs(target_valence - song.valence)) * 0.6
        score += valence_score
        reasons.append(f"Mood-valence fit (+{valence_score:.2f})")

        # Extra feature 3: danceability is a light proxy for energy-vibe fit.
        target_danceability = Recommender._clamp(0.35 + (user.target_energy * 0.6), 0.2, 0.95)
        danceability_score = max(0.0, 1.0 - abs(target_danceability - song.danceability)) * 0.4
        score += danceability_score
        reasons.append(f"Danceability fit (+{danceability_score:.2f})")

        # Optional acoustic preference bonus/penalty.
        if user.likes_acoustic and song.acousticness >= 0.6:
            score += 0.5
            reasons.append("Acoustic preference match (+0.5)")
        elif not user.likes_acoustic and song.acousticness >= 0.8:
            score -= 0.25
            reasons.append("Very acoustic penalty (-0.25)")

        return score, reasons

    def _confidence_score(self, user: UserProfile, song: Song, score: float) -> float:
        """Computes a normalized confidence score in [0, 1]."""
        max_base_score = 1.0 + 1.0 + 2.0 + 0.6 + 0.6 + 0.4 + 0.5
        normalized = self._clamp(score / max_base_score, 0.0, 1.0)

        retrieval_mode_factor = {
            "strict": 1.00,
            "relaxed": 0.92,
            "energy-fallback": 0.82,
            "full-catalog-fallback": 0.75,
        }.get(self._last_retrieval_mode, 0.85)

        confidence = self._clamp(normalized * retrieval_mode_factor, 0.0, 1.0)
        return confidence

    @staticmethod
    def _confidence_label(confidence: float) -> str:
        if confidence >= 0.75:
            return "high"
        if confidence >= 0.50:
            return "medium"
        return "low"

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        if k <= 0:
            logger.warning("Non-positive k=%d requested; returning empty results", k)
            return []

        logger.info(
            "Recommend called with profile genre=%s mood=%s energy=%.2f k=%d",
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            k,
        )

        candidates = self._retrieve_candidates(user, k)
        if not candidates:
            logger.warning("No candidates available after retrieval")
            return []

        if len(candidates) < k:
            selected_ids = {song.id for song in candidates}
            original_count = len(candidates)
            for song in self.songs:
                if song.id not in selected_ids:
                    candidates.append(song)
                    self._last_retrieval_by_song_id[song.id] = (
                        "Backfilled from broader catalog to satisfy top-k"
                    )
            logger.info(
                "Backfilled candidates from %d to %d to satisfy k=%d",
                original_count,
                len(candidates),
                k,
            )

        scored = [(song, self._score_song(user, song)[0]) for song in candidates]
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)
        logger.info("Ranking complete for %d candidates", len(candidates))
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = self._score_song(user, song)
        retrieval_reason = self._last_retrieval_by_song_id.get(song.id)
        if retrieval_reason:
            reasons.insert(0, retrieval_reason)
        confidence = self._confidence_score(user, song, score)
        confidence_label = self._confidence_label(confidence)
        reasons.append(f"Confidence: {confidence_label} ({confidence:.2f})")
        if not reasons:
            return "No specific feature matches were found."
        return ", ".join(reasons)


def _dict_to_song(song_data: Dict) -> Song:
    """Converts a dictionary row into a Song dataclass."""
    return Song(
        id=int(song_data["id"]),
        title=str(song_data["title"]),
        artist=str(song_data["artist"]),
        genre=str(song_data["genre"]),
        mood=str(song_data["mood"]),
        energy=float(song_data["energy"]),
        tempo_bpm=float(song_data["tempo_bpm"]),
        valence=float(song_data["valence"]),
        danceability=float(song_data["danceability"]),
        acousticness=float(song_data["acousticness"]),
    )


def _prefs_to_user_profile(user_prefs: Dict) -> UserProfile:
    """Normalizes multiple possible preference keys to UserProfile."""
    if not isinstance(user_prefs, dict):
        logger.warning("Invalid user_prefs type %s; defaulting to empty profile", type(user_prefs))
        user_prefs = {}

    favorite_genre = user_prefs.get("preferred_genre") or user_prefs.get("genre", "")
    favorite_mood = user_prefs.get("preferred_mood") or user_prefs.get("mood", "")
    if not str(favorite_genre).strip():
        favorite_genre = "any"
        logger.warning("Missing genre preference; using fallback 'any'")
    if not str(favorite_mood).strip():
        favorite_mood = "any"
        logger.warning("Missing mood preference; using fallback 'any'")

    target_energy = user_prefs.get("target_energy")
    if target_energy is None:
        target_energy = user_prefs.get("energy", 0.5)

    try:
        target_energy = float(target_energy)
    except (TypeError, ValueError):
        logger.warning("Invalid target_energy '%s'; defaulting to 0.5", target_energy)
        target_energy = 0.5

    clamped_energy = Recommender._clamp(target_energy, 0.0, 1.0)
    if clamped_energy != target_energy:
        logger.warning("Clamped target_energy from %.2f to %.2f", target_energy, clamped_energy)

    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    return UserProfile(
        favorite_genre=str(favorite_genre),
        favorite_mood=str(favorite_mood),
        target_energy=clamped_energy,
        likes_acoustic=likes_acoustic,
    )

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file and casts numeric fields."""
    logger.info("Loading songs from %s", csv_path)
    songs_data = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Convert numeric fields.
                    row['id'] = int(row['id'])
                    row['energy'] = Recommender._clamp(float(row['energy']), 0.0, 1.0)
                    row['tempo_bpm'] = float(row['tempo_bpm'])
                    row['valence'] = Recommender._clamp(float(row['valence']), 0.0, 1.0)
                    row['danceability'] = Recommender._clamp(float(row['danceability']), 0.0, 1.0)
                    row['acousticness'] = Recommender._clamp(float(row['acousticness']), 0.0, 1.0)
                    songs_data.append(row)
                except (TypeError, ValueError, KeyError) as exc:
                    logger.warning("Skipping malformed song row due to %s: %s", type(exc).__name__, row)
    except FileNotFoundError:
        logger.error("Could not find song file: %s", csv_path)

    logger.info("Successfully loaded %d songs", len(songs_data))
    return songs_data

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Calculates a song's numeric score and returns a list of matching reasons based on user preferences."""
    user = _prefs_to_user_profile(user_prefs)
    song_obj = _dict_to_song(song)
    return Recommender._score_song(user, song_obj)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Evaluates and ranks all songs to return the top k recommendations."""
    if not songs:
        logger.warning("recommend_songs called with empty catalog")
        return []

    if k <= 0:
        logger.warning("recommend_songs called with non-positive k=%d", k)
        return []

    user = _prefs_to_user_profile(user_prefs)
    song_objects = [_dict_to_song(song) for song in songs]
    recommender = Recommender(song_objects)

    top_songs = recommender.recommend(user, k=k)
    song_by_id = {song["id"]: song for song in songs}

    results: List[Tuple[Dict, float, str]] = []
    for song_obj in top_songs:
        score, _ = recommender._score_song(user, song_obj)
        explanation = recommender.explain_recommendation(user, song_obj)
        results.append((song_by_id[song_obj.id], score, explanation))

    return results
