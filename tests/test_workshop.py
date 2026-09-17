from conftest import REPO_ROOT

V1_SKILL = (
    REPO_ROOT / "skill-source" / "v1" / "garmin-weekly-performance-report" / "SKILL.md"
)
WORKSHOP = REPO_ROOT / "WORKSHOP.md"


def test_workshop_shows_the_v1_skill_exactly_as_installed():
    section = WORKSHOP.read_text().split("[04] BUILD ONE BY HAND")[1].split("[05]")[0]
    shown = [
        block for block in section.split("```\n") if block.startswith("---\nname:")
    ]

    assert shown == [V1_SKILL.read_text()]
