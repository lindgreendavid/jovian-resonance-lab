from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_site_exposes_interaction_results_and_boundaries() -> None:
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    script = (ROOT / "site/app.js").read_text(encoding="utf-8")
    styles = (ROOT / "site/styles.css").read_text(encoding="utf-8")
    assert "Watch a three-body clock emerge" in html
    assert "The expected ordering passed" in html
    assert "not numerically converged" in html
    assert "JUP365 is a fitted" in html
    assert "10,957" in html and "11.27°" in html and "8.13°" in html and "0.46°" in html
    assert 'aria-live="polite"' in html and 'aria-pressed="true"' in html
    assert "drawOrbit" in script and "drawChart" in script and "chooseModel" in script
    assert "prefers-reduced-motion" in styles and "forced-colors:active" in styles
    assert "min-height:46px" in styles


def test_no_unreviewed_remote_scripts_or_insecure_links() -> None:
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert "http://" not in html
    assert '<script src="http' not in html
    assert 'target="_blank"' not in html
