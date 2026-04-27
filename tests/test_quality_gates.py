from src.quality_gates import evaluate_quality_gates


def test_quality_gates_pass_for_reasonable_metrics():
    summary = {
        "overall_genre_match_rate": 0.30,
        "overall_mood_match_rate": 0.25,
        "overall_avg_energy_error": 0.20,
        "overall_low_confidence_rate": 0.60,
    }

    passed, failures = evaluate_quality_gates(summary)

    assert passed is True
    assert failures == []


def test_quality_gates_fail_with_clear_messages():
    summary = {
        "overall_genre_match_rate": 0.10,
        "overall_mood_match_rate": 0.10,
        "overall_avg_energy_error": 0.40,
        "overall_low_confidence_rate": 0.90,
    }

    passed, failures = evaluate_quality_gates(summary)

    assert passed is False
    assert len(failures) == 4
    assert any("overall_genre_match_rate" in item for item in failures)
    assert any("overall_mood_match_rate" in item for item in failures)
    assert any("overall_avg_energy_error" in item for item in failures)
    assert any("overall_low_confidence_rate" in item for item in failures)
