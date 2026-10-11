#if WITH_DEV_AUTOMATION_TESTS
#include "City/Mobility/CityMobilityData.h"
#include "Engine/StaticMesh.h"
#include "Dom/JsonObject.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityFleetImportedBoundsTest, "ANANTA.City.Fleet.ImportedBounds",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityFleetImportedBoundsTest::RunTest(const FString& Parameters)
{
    // Doi chieu mesh Unreal voi nguon FBX cua ca bo cu va bo metro moi.
    TMap<FString, FVector> Expected;
    for (const TCHAR* File : {TEXT("mobility_manifest.json"), TEXT("metro_manifest.json")})
    {
        FString Contents;
        TSharedPtr<FJsonObject> Document;
        const FString Path = FPaths::ProjectDir() / TEXT("Assets/City") / File;
        if (!TestTrue(Path + TEXT(" readable"), FFileHelper::LoadFileToString(Contents, *Path))
            || !TestTrue(Path + TEXT(" valid JSON"),
                FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Contents), Document)))
        {
            return false;
        }
        for (const auto& Value : Document->GetArrayField(TEXT("meshes")))
        {
            const auto Item = Value->AsObject();
            const auto& Size = Item->GetObjectField(TEXT("boundsCm"))->GetArrayField(TEXT("size"));
            Expected.Add(Item->GetStringField(TEXT("id")),
                FVector(Size[0]->AsNumber(), Size[1]->AsNumber(), Size[2]->AsNumber()));
        }
    }
    for (int32 Index = 0; Index < static_cast<int32>(ECityTransportKind::Count); ++Index)
    {
        const auto Kind = static_cast<ECityTransportKind>(Index);
        const FString Name = CityMobility::MeshName(Kind);
        if (!TestTrue(Name + TEXT(" present in source manifest"), Expected.Contains(Name)))
        {
            continue;
        }
        const FString Path = FString::Printf(TEXT("/Game/ANANTA/City/Meshes/SM_%s.SM_%s"), *Name, *Name);
        UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *Path);
        if (!TestNotNull(Name + TEXT(" imported mesh exists"), Mesh))
        {
            continue;
        }
        const FBox Bounds = Mesh->GetBoundingBox();
        TestTrue(Name + TEXT(" finite valid bounds"), Bounds.IsValid && !Bounds.GetSize().ContainsNaN());
        TestTrue(Name + TEXT(" authored XYZ centimetre bounds preserved"),
            Bounds.GetSize().Equals(Expected[Name], 2));
        TestTrue(Name + TEXT(" visible mesh has a material slot"), Mesh->GetStaticMaterials().Num() > 0);
        if (Kind == ECityTransportKind::CargoShip || Kind == ECityTransportKind::Motorboat
            || Kind == ECityTransportKind::Sailboat)
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
