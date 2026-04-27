from src.recommender import Song, UserProfile, Recommender, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_recommend_uses_retrieval_before_scoring():
    songs = [
        Song(
            id=1,
            title="Genre Match Far Energy",
            artist="A",
            genre="pop",
            mood="happy",
            energy=0.05,
            tempo_bpm=100,
            valence=0.5,
            danceability=0.5,
            acousticness=0.1,
        ),
        Song(
            id=2,
            title="Mood Match Near Energy",
            artist="B",
            genre="rock",
            mood="happy",
            energy=0.86,
            tempo_bpm=120,
            valence=0.6,
            danceability=0.6,
            acousticness=0.2,
        ),
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.9,
        likes_acoustic=False,
    )

    results = rec.recommend(user, k=1)

    assert results[0].title == "Mood Match Near Energy"
    explanation = rec.explain_recommendation(user, results[0])
    assert "Retrieved by" in explanation


def test_explanation_contains_confidence_and_feature_signals():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    top_song = rec.recommend(user, k=1)[0]
    explanation = rec.explain_recommendation(user, top_song)

    assert "Confidence:" in explanation
    assert "Tempo alignment" in explanation
    assert "Mood-valence fit" in explanation


def test_recommend_songs_clamps_invalid_energy_and_handles_missing_labels():
    songs = [
        {
            "id": 1,
            "title": "Calm Track",
            "artist": "A",
            "genre": "ambient",
            "mood": "chill",
            "energy": 0.2,
            "tempo_bpm": 70.0,
            "valence": 0.5,
            "danceability": 0.4,
            "acousticness": 0.7,
        }
    ]
    user_prefs = {"genre": "", "mood": "", "energy": "not-a-number"}

    results = recommend_songs(user_prefs, songs, k=1)

    assert len(results) == 1
    assert isinstance(results[0][1], float)


def test_recommend_songs_returns_empty_for_invalid_k_or_empty_catalog():
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    songs = []

    assert recommend_songs(user_prefs, songs, k=3) == []
    assert recommend_songs(user_prefs, songs=[{
        "id": 1,
        "title": "Track",
        "artist": "Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120.0,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.2,
    }], k=0) == []
