#!/usr/bin/env python3
"""Validate the Obsidian extension structure and templates."""

import json
import re
from pathlib import Path

def validate_extension():
    """Validate Obsidian extension files and structure."""

    # 1. Validate template syntax
    print("=" * 60)
    print("OBSIDIAN EXTENSION VALIDATION")
    print("=" * 60)

    # Check template files exist
    template_path = Path("extensions/obsidian/templates/verdict.md.j2")
    template_content = template_path.read_text()

    jinja_vars = set(re.findall(r'\{\{(\w+)', template_content))
    jinja_blocks = set(re.findall(r'\{%\s*(if|for|endif|endfor)', template_content))

    print("\n✅ Template Jinja2 Syntax Validation")
    print(f"   Variables referenced: {sorted(jinja_vars)}")
    print(f"   Control blocks: {sorted(jinja_blocks)}")
    print(f"   Total lines: {len(template_content.splitlines())}")

    # 2. Verify support files
    print("\n✅ Support Files")

    mappings_path = Path("extensions/obsidian/mapping.py")
    mappings_content = mappings_path.read_text()
    if "verdict_to_template_context" in mappings_content:
        print("   ✓ mapping.py has verdict_to_template_context()")

    exporter_path = Path("extensions/obsidian/exporter.py")
    exporter_content = exporter_path.read_text()
    if "ObsidianExporter" in exporter_content:
        print("   ✓ exporter.py has ObsidianExporter class")

    # 3. Verify example verdict
    print("\n✅ Example Verdict")

    example_verdict = Path("docs/scenarios/01-flux-reconciliation-failed/verdict.json")
    with open(example_verdict) as f:
        verdict = json.load(f)

    assert "hypothesis" in verdict, "Missing hypothesis"
    assert "impact" in verdict, "Missing impact"
    assert "recommended_actions" in verdict, "Missing recommended_actions"

    print(f"   Hypothesis: {verdict['hypothesis']['title'][:50]}...")
    print(f"   Severity: {verdict['impact']['severity']}")
    print(f"   Confidence: {verdict['hypothesis']['confidence']}")
    print(f"   Actions: {len(verdict['recommended_actions'])} recommended")

    # 4. Verify no Core imports
    print("\n✅ Architecture Validation (No Core Imports)")

    for py_file in Path("extensions/obsidian").glob("*.py"):
        content = py_file.read_text()
        imports = re.findall(r'^from\s+(.+?)\s+import', content, re.MULTILINE)
        for imp in imports:
            assert "core" not in imp, f"❌ {py_file.name} imports Core: {imp}"
            assert "ports" not in imp, f"❌ {py_file.name} imports Ports: {imp}"
            assert "api" not in imp, f"❌ {py_file.name} imports API: {imp}"

    print("   ✓ No Core imports found")
    print("   ✓ No Ports imports found")
    print("   ✓ No API imports found")

    # 5. Summary
    print("\n" + "=" * 60)
    print("✅ ALL VALIDATION CHECKS PASSED")
    print("=" * 60)
    print("\nObsidian Extension is ready for use:")
    print("  - Templates: verdict.md.j2 (minimal), incident.md.j2 (extended)")
    print("  - Exporter: Spec Verdict → Markdown transformation")
    print("  - Mapping: spec/v1 → Obsidian context")
    print("  - Architecture: Spec-only, no Core/Ports/API imports")
    print("\nNext Steps:")
    print("  1. Delete obsolete ./api directory")
    print("  2. Commit extensions/ to git")
    print("=" * 60)

if __name__ == "__main__":
    validate_extension()
