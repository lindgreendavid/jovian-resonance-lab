from pathlib import Path

import pytest

from jovian_resonance_lab.analysis import (
    compare_trace,
    describe_reference,
    expectation_results,
    load_json,
    relative_drift,
    write_json,
)


def test_analysis_endpoints(tmp_path: Path) -> None:
    comparison = compare_trace([359, 1], [1, 359])
    assert comparison["circular_rmse_degrees"] == 2.0
    description = describe_reference([179, 180, 181])
    assert description["circular_mean_degrees"] == pytest.approx(180)
    assert description["half_peak_to_peak_degrees"] == 1
    assert description["fraction_within_two_degrees_of_180"] == 1
    metrics = {
        name: {"circular_rmse_degrees": value}
        for name, value in {"K2": 4, "G3": 3, "G4": 2, "G4J2": 1}.items()
    }
    assert all(expectation_results(metrics).values())
    assert relative_drift(-100, -99) == 0.01
    path = tmp_path / "nested/report.json"
    write_json(path, {"answer": 42})
    assert load_json(path) == {"answer": 42}


def test_bad_analysis_inputs_fail() -> None:
    with pytest.raises(ValueError):
        compare_trace([], [])
    with pytest.raises(ValueError):
        describe_reference([])
    with pytest.raises(ValueError):
        relative_drift(0, 1)
