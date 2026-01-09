"""
Test the Obsidian exporter with a real Verdict from scenarios.
Demonstrates that the extension works without importing Core.
"""

import json
import tempfile
from pathlib import Path
from extensions.obsidian.exporter import ObsidianExporter


def test_exporter_with_flux_scenario():
    """
    Integration test: Load the flux-reconciliation-failed verdict,
    export to Obsidian markdown, verify output is human-readable.
    """
    # Load real scenario verdict
    scenario_verdict_path = Path(
        "docs/scenarios/01-flux-reconciliation-failed/verdict.json"
    )
    with open(scenario_verdict_path) as f:
        verdict_dict = json.load(f)

    # Create temporary vault
    with tempfile.TemporaryDirectory() as temp_vault:
        vault_path = Path(temp_vault)

        # Export using minimal template
        exporter = ObsidianExporter(vault_path=vault_path, template_name="verdict")
        output_file = exporter.export_verdict_to_file(verdict_dict)

        # Verify file was created
        assert output_file.exists(), f"Output file not created at {output_file}"

        # Verify content is readable
        content = output_file.read_text()
        assert len(content) > 100, "Generated markdown is too short"
        assert verdict_dict["hypothesis"]["title"] in content, "Hypothesis not in output"
        assert str(verdict_dict["hypothesis"]["confidence"]) in content, "Confidence not in output"
        assert verdict_dict["impact"]["severity"] in content, "Severity not in output"

        print(f"✅ Export successful: {output_file.name}")
        print(f"   Length: {len(content)} bytes")
        print(f"   Content preview:\n{content[:300]}...")


if __name__ == "__main__":
    test_exporter_with_flux_scenario()
    print("\n✅ All tests passed!")
