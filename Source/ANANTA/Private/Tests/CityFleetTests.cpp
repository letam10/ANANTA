#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityMobilityData.h"
#include "Engine/StaticMesh.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityFleetImportedBoundsTest, "ANANTA.City.Fleet.ImportedBounds",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityFleetImportedBoundsTest::RunTest(const FString& Parameters)
{
    // Kich thuoc cm cua 11 mesh trong mobility_manifest, bat loi FBX doi truc/doi don vi.
    const FVector Expected[] = {
        FVector(1175, 317, 364.158), FVector(1055, 317, 336.158), FVector(471, 249, 188.970),
        FVector(853, 289, 301.866), FVector(853, 289, 297.866), FVector(855.7, 289, 325.366),
        FVector(471, 249, 189.970), FVector(603, 289, 301.930), FVector(2606.936, 616.981, 1026.354),
        FVector(693.5, 241.924, 229.881), FVector(866.936, 276.937, 1221.5)
    };
    TestEqual(TEXT("Manifest covers all requested types"),
        static_cast<int32>(UE_ARRAY_COUNT(Expected)), static_cast<int32>(ECityTransportKind::Count));
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Expected); ++Index)
    {
        const auto Kind = static_cast<ECityTransportKind>(Index);
        const FString Name = CityMobility::MeshName(Kind);
        const FString Path = FString::Printf(TEXT("/Game/ANANTA/City/Meshes/SM_%s.SM_%s"), *Name, *Name);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        if (!TestNotNull(Name + TEXT(" imported mesh exists"), Mesh))
        {
            continue;
        }
        const FBox Bounds = Mesh->GetBoundingBox();
        TestTrue(Name + TEXT(" finite valid bounds"), Bounds.IsValid && !Bounds.GetSize().ContainsNaN());
        TestTrue(Name + TEXT(" authored XYZ centimetre bounds preserved"),
            Bounds.GetSize().Equals(Expected[Index], 2));
        TestTrue(Name + TEXT(" visible mesh has a material slot"), Mesh->GetStaticMaterials().Num() > 0);
        if (Kind >= ECityTransportKind::CargoShip)
        {
            TestTrue(Name + TEXT(" keel below waterline origin"), Bounds.Min.Z < -30 && Bounds.Max.Z > 100);
        }
        else
        {
            TestTrue(Name + TEXT(" wheels above road origin"), Bounds.Min.Z >= -1 && Bounds.Min.Z <= 10);
        }
    }
    return true;
}
#endif
