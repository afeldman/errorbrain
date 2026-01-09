"""Obsidian Exporter: Verdict → Markdown Note.

Minimal, spec-conformant Obsidian exporter.

No business logic. No reasoning. No Core imports.
Only: spec/v1 Verdict → Markdown Note

This module is a pure adapter layer:
1. Load template
2. Map verdict to context
3. Render
4. Write to file
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import ValidationError

from extensions.obsidian.mapping import verdict_to_template_context


class ObsidianExporter:
    """Export spec/v1 Verdicts to Obsidian Markdown notes."""

    def __init__(self, vault_path: str | Path, template_dir: str | Path | None = None) -> None:
        """Initialize exporter.

        Args:
            vault_path: Path to Obsidian vault root (where notes will be written).
            template_dir: Path to Jinja2 templates directory.
                If None, uses extensions/obsidian/templates relative to this file.
        """
        self.vault_path = Path(vault_path).expanduser().resolve()
        self.vault_path.mkdir(parents=True, exist_ok=True)

        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        else:
            template_dir = Path(template_dir).expanduser().resolve()

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def export_verdict(
        self,
        verdict: dict | Any,
        template_name: str = "verdict.md.j2",
        filename: str | None = None,
    ) -> Path:
        """Export a single verdict to a Markdown note.

        Args:
            verdict: Verdict dict (spec/v1) or SpecVerdict model.
            template_name: Name of Jinja2 template to use.
            filename: Output filename. If None, uses 'incident-{event_id}.md'.

        Returns:
            Path to the written file.

        Raises:
            ValueError: If verdict is invalid or template not found.
        """
        # Validate and map verdict
        try:
            context = verdict_to_template_context(verdict)
        except ValidationError as exc:
            raise ValueError(f"Invalid verdict: {exc}") from exc

        # Generate filename if not provided
        if filename is None:
            filename = f"incident-{context['event_id']}.md"

        # Load and render template
        try:
            template = self.env.get_template(template_name)
        except FileNotFoundError as exc:
            raise ValueError(f"Template not found: {template_name}") from exc

        rendered_content = template.render(**context)

        # Write to file
        output_path = self.vault_path / filename
        output_path.write_text(rendered_content, encoding="utf-8")

        return output_path

    def export_from_file(
        self,
        verdict_json_path: str | Path,
        template_name: str = "verdict.md.j2",
        filename: str | None = None,
    ) -> Path:
        """Export a verdict from a JSON file.

        Args:
            verdict_json_path: Path to verdict.json file.
            template_name: Name of Jinja2 template to use.
            filename: Output filename. If None, auto-generated.

        Returns:
            Path to the written file.

        Raises:
            FileNotFoundError: If verdict file not found.
            ValueError: If verdict is invalid.
        """
        verdict_path = Path(verdict_json_path).expanduser().resolve()
        if not verdict_path.exists():
            raise FileNotFoundError(f"Verdict file not found: {verdict_path}")

        with verdict_path.open("r", encoding="utf-8") as f:
            verdict = json.load(f)

        return self.export_verdict(verdict, template_name=template_name, filename=filename)


def export_verdict_cli(
    verdict_json_path: str,
    vault_path: str,
    template: str = "verdict.md.j2",
) -> None:
    """CLI entry point for exporting a verdict.

    Args:
        verdict_json_path: Path to verdict.json.
        vault_path: Path to Obsidian vault.
        template: Template name (default: verdict.md.j2).
    """
    exporter = ObsidianExporter(vault_path)
    output_path = exporter.export_from_file(verdict_json_path, template_name=template)
    print(f"✓ Exported to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export an ErrorBrain verdict to an Obsidian note.")
    parser.add_argument("verdict_json_path", type=str, help="Path to the verdict.json file.")
    parser.add_argument("--vault-path", type=str, required=True, help="Path to the Obsidian vault directory.")
    parser.add_argument("--template", type=str, default="verdict.md.j2", help="Name of the template file to use.")

    args = parser.parse_args()

    export_verdict_cli(
        verdict_json_path=args.verdict_json_path,
        vault_path=args.vault_path,
        template=args.template,
    )
