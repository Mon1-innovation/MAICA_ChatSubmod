from pathlib import Path


WORKFLOW = (
    Path(__file__).resolve().parents[1] / ".github" / "workflows" / "release.yml"
)


def test_zip_and_artifact_are_created_even_when_release_is_skipped():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    package_step = workflow.index("- name: Create zip package")
    artifact_step = workflow.index("- name: Upload artifact")
    release_step = workflow.index("- name: Create Release")

    assert package_step < artifact_step < release_step
    for step_name in (
        "Create release version file",
        "Download Ignore Translation Conflicts dependency",
        "Download CertifiFixer dependency",
        "Copy documentation into submod package",
        "Create zip package",
        "Generate Release Notes",
        "Upload artifact",
    ):
        block = workflow.split("- name: " + step_name, 1)[1].split("\n    - name:", 1)[0]
        assert "\n      if:" not in block

    artifact = workflow[artifact_step:release_step]
    assert "MAICA_ChatSubmod-${{ steps.get_version.outputs.version }}.zip" in artifact
    assert "release_notes.md" in artifact
