"""Calculate a published layout independently, without replacing the working tree."""

import argparse
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, check=True, stdout=subprocess.PIPE).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", required=True)
    ref = parser.parse_args().ref
    names = git("ls-tree", "-r", "--name-only", ref, "Assets/City").decode().splitlines()
    manifests = [name for name in names if name.endswith("manifest.json")]
    archive = git("archive", ref, "Tools/Editor", *manifests)
    with tempfile.TemporaryDirectory(prefix="ANANTA_layout_snapshot_") as temporary:
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(temporary, filter="data")
        program = (
            "import sys, json; sys.path.insert(0, sys.argv[1]); "
            "from CityExpansionLayout import generate; data=generate(); "
            "print(json.dumps(data['audit']))"
        )
        result = subprocess.run(["python", "-c", program, str(Path(temporary) / "Tools/Editor")],
                                cwd=temporary, check=True, capture_output=True, text=True)
        print(result.stdout.strip())


if __name__ == "__main__":
    main()
