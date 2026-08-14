import json
import sys
from pathlib import Path

from jovian_resonance_lab.cli import main


def test_cli_help(monkeypatch: object, capsys: object) -> None:
    monkeypatch.setattr(sys, "argv", ["jovian-resonance"])  # type: ignore[attr-defined]
    assert main() == 0
    assert "Inspect Jovian" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_cli_report(tmp_path: Path, monkeypatch: object, capsys: object) -> None:
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"schema_version": "0.1.0", "product_version": "0.1.0"}))
    monkeypatch.setattr(sys, "argv", ["jovian-resonance", str(path)])  # type: ignore[attr-defined]
    assert main() == 0
    assert "schema=0.1.0 product=0.1.0" in capsys.readouterr().out  # type: ignore[attr-defined]
