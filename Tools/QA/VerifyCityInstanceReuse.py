"""Audit shared mesh/material signatures without opening Unreal."""

import argparse
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "Saved" / "QA" / "CityExpansionLayout.json"
DEFAULT_OUTPUT = ROOT / "Saved" / "QA" / "CityInstanceReuse.json"


def _signature(group):
    return (
        group.get("mesh"),
        group.get("material"),
        bool(group.get("collision", True)),
        bool(group.get("hidden", False)),
    )


def analyze(payload):
    groups = payload.get("groups")
    if not isinstance(groups, list):
        written_groups = payload.get("writtenGroups", payload.get("layout", {}).get("groups"))
        written_instances = payload.get(
            "writtenInstances",
            payload.get("layout", {}).get("instances"),
        )
        return {
            "status": "PARTIAL",
            "verificationLevel": "aggregate-summary",
            "groupCount": int(written_groups or 0),
            "instanceCount": int(written_instances or 0),
            "uniqueSignatures": None,
            "reusableInstances": None,
            "reuseRatio": None,
            "message": "Input has counts but no per-group mesh/material signatures.",
        }

    signature_groups = defaultdict(int)
    instance_count = 0
    invalid_groups = []
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            invalid_groups.append(index)
            continue
        instances = group.get("instances")
        if not isinstance(instances, list):
            invalid_groups.append(index)
            continue
        signature = _signature(group)
        signature_groups[signature] += len(instances)
        instance_count += len(instances)

    unique_signatures = len(signature_groups)
    reusable_instances = max(0, instance_count - unique_signatures)
    reuse_ratio = (
        round(instance_count / unique_signatures, 3)
        if unique_signatures
        else 0.0
    )
    status = "PASS" if not invalid_groups and instance_count >= unique_signatures else "FAIL"
    return {
        "status": status,
        "verificationLevel": "group-signature",
        "groupCount": len(groups),
        "instanceCount": instance_count,
        "uniqueSignatures": unique_signatures,
        "reusableInstances": reusable_instances,
        "reuseRatio": reuse_ratio,
        "invalidGroups": invalid_groups,
        "topSignatures": [
            {
                "mesh": key[0],
                "material": key[1],
                "collision": key[2],
                "hidden": key[3],
                "instances": count,
            }
            for key, count in sorted(
                signature_groups.items(),
                key=lambda item: (-item[1], str(item[0])),
            )[:20]
        ],
    }


def _self_test():
    return {
        "groups": [
            {
                "mesh": "Window",
                "material": "Glass",
                "collision": False,
                "hidden": False,
                "instances": [
                    {"location": [0, 0, 0]},
                    {"location": [100, 0, 0]},
                ],
            },
            {
                "mesh": "Window",
                "material": "Glass",
                "collision": False,
                "hidden": False,
                "instances": [{"location": [200, 0, 0]}],
            },
            {
                "mesh": "Chair",
                "material": "Fabric",
                "collision": True,
                "hidden": False,
                "instances": [{"location": [0, 100, 0]}],
            },
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    if args.self_test:
        payload = _self_test()
    else:
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    report = analyze(payload)
    report["input"] = "self-test" if args.self_test else input_path.relative_to(ROOT).as_posix()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    if report["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
