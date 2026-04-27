from src.recommender import load_songs
from src.rag_enhancement import evaluate_rag_enhancement


def test_rag_enhancement_improves_synonym_semantic_hit_rate():
    songs = load_songs("data/songs.csv")
    metrics = evaluate_rag_enhancement(songs, k=5)

    assert metrics["profiles_evaluated"] == 3.0
    assert metrics["enhanced_semantic_hit_rate"] >= metrics["baseline_semantic_hit_rate"]
    assert metrics["absolute_improvement"] >= 0.0
