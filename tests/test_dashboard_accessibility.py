from html.parser import HTMLParser
from pathlib import Path
import re


DASHBOARD = Path(__file__).parents[1] / "src" / "static" / "dashboard.html"


class DashboardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.labels: set[str] = set()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag == "label" and attributes.get("for"):
            self.labels.add(str(attributes["for"]))
        if attributes.get("id"):
            self.ids.append(str(attributes["id"]))


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
            for value in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_dashboard_has_named_landmarks_and_skip_link() -> None:
    source = DASHBOARD.read_text(encoding="utf-8")
    parser = DashboardParser()
    parser.feed(source)
    tags = parser.tags

    assert sum(tag == "main" for tag, _ in tags) == 1
    assert sum(tag == "nav" for tag, _ in tags) == 1
    assert sum(tag == "h1" for tag, _ in tags) == 1
    assert len(parser.ids) == len(set(parser.ids))
    assert any(tag == "main" and attrs.get("id") == "main-content" for tag, attrs in tags)
    assert any(
        tag == "a" and attrs.get("class") == "skip-link" and attrs.get("href") == "#main-content"
        for tag, attrs in tags
    )


def test_dashboard_form_controls_are_labeled_and_errors_are_announced() -> None:
    source = DASHBOARD.read_text(encoding="utf-8")
    parser = DashboardParser()
    parser.feed(source)

    controls = [
        attrs.get("id")
        for tag, attrs in parser.tags
        if tag in {"input", "select"}
    ]
    assert controls
    assert all(control and control in parser.labels for control in controls)
    assert any(attrs.get("role") == "alert" for _, attrs in parser.tags)
    assert 'aria-live="polite"' in source


def test_dashboard_has_visible_keyboard_focus_and_reduced_motion_support() -> None:
    source = DASHBOARD.read_text(encoding="utf-8")
    assert re.search(r":focus-visible\s*\{[^}]*outline:\s*2px solid var\(--blue\)", source)
    assert "@media (prefers-reduced-motion: reduce)" in source


def test_muted_text_meets_wcag_aa_on_dashboard_surfaces() -> None:
    source = DASHBOARD.read_text(encoding="utf-8")
    soft = re.search(r"--soft:\s*(#[0-9a-fA-F]{6})", source)
    assert soft is not None
    foreground = soft.group(1)
    for background in ("#0b1016", "#121b26", "#0d141d", "#0f1720"):
        assert contrast_ratio(foreground, background) >= 4.5


def test_dashboard_remains_read_only_and_uses_safe_dom_text_updates() -> None:
    source = DASHBOARD.read_text(encoding="utf-8")
    assert "No order controls are exposed" in source
    assert "This dashboard has no broker trade controls" in source
    assert "textContent" in source
    assert "innerHTML" not in source
