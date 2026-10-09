from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "game" / "Submods" / "MAICA_ChatSubmod" / "header.rpy"
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
DEPENDENCY_REPO = "MAS-Submod-MoyuTeam/mas_certifi_fixer"


def test_maica_declares_certifi_fixer_dependency_without_vendoring_it():
    header = HEADER.read_text(encoding="utf-8")

    assert '"CertifiFixer": (None, None)' in header
    assert not any(
        path.is_file()
        for path in (ROOT / "game" / "Submods" / "CertifiFixer").rglob("*")
    )


def test_release_stages_certifi_fixer_before_creating_package():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    download_step = workflow.index("- name: Download CertifiFixer dependency")
    package_step = workflow.index("- name: Create zip package")
    dependency_block = workflow[download_step:package_step]

    assert DEPENDENCY_REPO in dependency_block
    assert 'gh release download' in dependency_block
    assert '--pattern "CertifiFixer-*.zip"' in dependency_block
    assert "if: steps.get_version.outputs.is_development == 'false' && steps.check_release.outputs.create_release == 'true'" in dependency_block
    assert "unzip -q" in dependency_block
    assert "game/Submods/CertifiFixer" in dependency_block
    for filename in ("certifi_fixer.rpy", "core.py", "__init__.py", "cacert.pem"):
        assert filename in dependency_block
    assert 'cp -R "$dependency_source" game/Submods/' in dependency_block
    assert "exit 1" in dependency_block
