
import json
import os
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from dataclasses import asdict

# Add the 'src' directory to the Python path to allow imports from errorbrain_server
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "server" / "src"))


from server.src.errorbrain_server.core.models import ErrorEvent, Source
from server.src.errorbrain_server.core.reasoning.engine import analyze

def generate_test_verdict():
    """
    Creates a sample ErrorEvent, runs it through the reasoning engine,
    and saves the resulting Verdict to a JSON file in the temp directory.
    """
    # 1. Create a sample ErrorEvent
    event = ErrorEvent(
        id=str(uuid4()),
        message="Flux reconciliation failed: Helm upgrade failed: another operation (install/upgrade/rollback) is in progress",
        severity="critical",
        source=Source(
            name="flux-cd",
            language="go",
            tags=["kubernetes", "gitops", "production"]
        ),
        timestamp=datetime.utcnow(),
        metadata={"cluster": "prod-us-east-1", "component": "helm-controller"},
        evidence=[]
    )

    # 2. Analyze the event to get a Verdict
    verdict = analyze(event)

    # 3. Serialize the Verdict to a dictionary
    verdict_dict = asdict(verdict)

    # 4. Save to a temporary JSON file
    temp_dir = os.environ.get("GEMINI_TMP_DIR")
    if not temp_dir:
        raise EnvironmentError("GEMINI_TMP_DIR is not set.")

    output_path = Path(temp_dir) / "verdict.json"
    with open(output_path, "w") as f:
        json.dump(verdict_dict, f, indent=2, default=str)

    print(f"Verdict saved to {output_path}")

if __name__ == "__main__":
    generate_test_verdict()
