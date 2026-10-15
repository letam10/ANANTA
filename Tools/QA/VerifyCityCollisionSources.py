"""Static collision safeguards. Engine tests and live doorway walks remain required."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source/ANANTA"


def read(relative):
    return (SOURCE / relative).read_text(encoding="utf-8")


def main():
    vehicle = read("Private/City/ANANTACityVehicle.cpp")
    traversal = read("Private/Components/TraversalComponent.cpp")
    tests = read("Private/Tests/CityCollisionTests.cpp")
    runtime = read("Private/QA/CityCollisionCheck.cpp")
    checks = {
        "drive uses shared expanded bounds": (
            "59000" not in vehicle and vehicle.count("CityWorldBounds::RoadExtent") == 2
        ),
        "steering does not ignore standing player": "Params.AddIgnoredActor(PC->GetPawn())" not in vehicle,
        "exit sweeps actual full capsule": (
            "GetScaledCapsuleRadius" in vehicle
            and "GetScaledCapsuleHalfHeight" in vehicle
            and "MakeSphere(38)" not in vehicle
            and "Capsule, Params" in vehicle
        ),
        "exit cannot choose overhead roof": "Floor.ImpactPoint.Z > DoorFloor" in vehicle,
        "mantle requires pawn support and walkability": (
            "ECC_Visibility" not in traversal and "Movement->IsWalkable(TopHit)" in traversal
        ),
        "restore cannot mantle while movement disabled": "Movement->MovementMode == MOVE_None" in traversal,
        "regressions use physical collision scene": (
            "UWorld::CreateWorld" in tests
            and "ExitChecksEntireCapsule" in tests
            and "MantleRequiresPawnSupport" in tests
            and "Head-only obstacles" in tests
        ),
        "runtime check isolated from normal save": (
            'TEXT("CityQASlot")' in runtime and 'TEXT("CityCollisionCheck")' in runtime
        ),
        "runtime walks both doorways in both directions": (
            runtime.count("FVector(-25080, 2400, 110)") == 2
            and runtime.count("FVector(1600, 2500, 110)") == 2
            and "Hero->AddMovementInput" in runtime
            and "Movement->IsMovingOnGround()" in runtime
        ),
    }
    for label, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {label}")
    if not all(checks.values()):
        raise SystemExit(1)
    print(f"{len(checks)}/{len(checks)} static safeguards passed; runtime acceptance not measured here.")


if __name__ == "__main__":
    main()
