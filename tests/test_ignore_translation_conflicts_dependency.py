from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "game" / "Submods" / "MAICA_ChatSubmod" / "header.rpy"
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
DEPENDENCY_URL = (
    "https://github.com/MAS-Submod-MoyuTeam/"
    "MAS_ignore_tl_conficts_submod/archive/refs/tags/v1.0.0.zip"
)


def test_maica_declares_unrestricted_translation_conflicts_dependency():
    header = HEADER.read_text(encoding="utf-8")

    assert 'dependencies={"Ignore Translation Conflicts": (None, None)},' in header


def test_release_stages_dependency_before_creating_package():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    download_step = workflow.index("- name: Download Ignore Translation Conflicts dependency")
    package_step = workflow.index("- name: Create zip package")
    dependency_block = workflow[download_step:package_step]

    assert DEPENDENCY_URL in dependency_block
    assert "if: steps.get_version.outputs.is_development == 'false' && steps.check_release.outputs.create_release == 'true'" in dependency_block
    assert "curl" in dependency_block
    assert "--fail" in dependency_block
    assert "--location" in dependency_block
    assert "unzip" in dependency_block
    assert "game/Submods/IgnoreTranslationConflicts" in dependency_block
    assert 'zz_ignore_translation_conflicts.rpy"' in dependency_block
    assert "find" in dependency_block
    assert 'cp -R "$dependency_source" game/Submods/' in dependency_block
    assert "exit 1" in dependency_block
