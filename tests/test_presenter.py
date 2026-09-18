import subprocess
from pathlib import Path

from conftest import REPO_ROOT

PRESENTER = REPO_ROOT / "presenter.vim"
WORKSHOP = REPO_ROOT / "WORKSHOP.md"
TAGLINE = "teaching agents how we work"
SPACE = "\\<Space>"
BACKSPACE = "\\<BS>"


def tagline_visible_after(keys: str, tmp_path: Path) -> bool:
    probe = tmp_path / "probe.vim"
    probe.write_text(
        f'call feedkeys("{keys}", "x")\n'
        "redraw\n"
        f"let l = search('{TAGLINE}', 'nw')\n"
        "let shown = foldclosed(l) == -1 && l >= line('w0') && l <= line('w$')\n"
        "echo shown ? 'SHOWN' : 'HIDDEN'\n"
    )
    result = subprocess.run(
        [
            "nvim",
            "--headless",
            "--clean",
            "-S",
            str(PRESENTER),
            "-S",
            str(probe),
            "-c",
            "qa!",
            str(WORKSHOP),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return "SHOWN" in result.stderr + result.stdout


def test_presenter_opens_on_the_title_screen(tmp_path: Path):
    assert tagline_visible_after("", tmp_path)


def test_presenter_hides_the_title_on_the_first_section(tmp_path: Path):
    assert not tagline_visible_after(SPACE, tmp_path)


def test_presenter_goes_back_to_the_title_from_the_first_section(tmp_path: Path):
    assert tagline_visible_after(SPACE + BACKSPACE, tmp_path)
