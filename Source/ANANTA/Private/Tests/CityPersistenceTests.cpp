#include "City/ANANTACityState.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Kismet/GameplayStatics.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{
    template <typename ElementType>
    bool SameSet(const TSet<ElementType>& Left, const TSet<ElementType>& Right)
    {
        if (Left.Num() != Right.Num())
        {
            return false;
        }
        for (const ElementType& Value : Left)
        {
            if (!Right.Contains(Value))
            {
                return false;
            }
        }
        return true;
    }

    template <typename KeyType, typename ValueType>
    bool SameMap(const TMap<KeyType, ValueType>& Left, const TMap<KeyType, ValueType>& Right)
    {
        if (Left.Num() != Right.Num())
        {
            return false;
        }
        for (const TPair<KeyType, ValueType>& Pair : Left)
        {
            const ValueType* RightValue = Right.Find(Pair.Key);
            if (RightValue == nullptr || !(*RightValue == Pair.Value))
            {
                return false;
            }
        }
        return true;
    }

    bool SameTransformMap(const TMap<FName, FTransform>& Left, const TMap<FName, FTransform>& Right)
    {
        if (Left.Num() != Right.Num())
        {
            return false;
        }
        for (const TPair<FName, FTransform>& Pair : Left)
        {
            const FTransform* RightValue = Right.Find(Pair.Key);
            if (RightValue == nullptr || !RightValue->Equals(Pair.Value))
            {
                return false;
            }
        }
        return true;
    }

    UANANTACitySave* MakeSchemaTwoSave()
    {
        UANANTACitySave* Save = NewObject<UANANTACitySave>();
        Save->SchemaVersion = UANANTACitySave::GetCurrentSchemaVersion();

        Save->InteractionState.OpenedDoorIds.Add(TEXT("Door_Main"));
        Save->InteractionState.UsedPropIds.Add(TEXT("Prop_Generator"));
        Save->InteractionState.VisitedDistrictIds.Add(TEXT("District_Central"));

        Save->NpcSchedule.PhaseByNpcId.Add(TEXT("Npc_001"), 0.25f);
        Save->NpcSchedule.ActiveNpcIds.Add(TEXT("Npc_001"));

        Save->VehicleTransit.VehicleTransforms.Add(
            TEXT("Vehicle_Bus_01"), FTransform(FRotator(0.0f, 20.0f, 0.0f), FVector(120.0f, 240.0f, 80.0f)));
        Save->VehicleTransit.RouteStopById.Add(TEXT("Vehicle_Bus_01"), 2);
        Save->VehicleTransit.BoardedTransitIds.Add(TEXT("Npc_001"));
        Save->VehicleTransit.SignalStateById.Add(TEXT("Signal_Main"), 1);

        Save->Economy.Inventory.Add(TEXT("Item_Ticket"), 2);
        Save->Economy.CityTokens = 42;

        Save->DayNight.DayIndex = 3;
        Save->DayNight.TimeHours = 14.5f;
        Save->DayNight.LightingLayer = TEXT("Day");
        return Save;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityPersistenceLegacyMigrationTest,
    "ANANTA.City.Persistence.LegacyFixtureMigratesToSchemaTwo",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityPersistenceLegacyMigrationTest::RunTest(const FString& Parameters)
{
    TArray<uint8> Bytes;
    const FString Fixture = FPaths::ProjectDir() / TEXT("Tools/QA/Fixtures/CityBeforeServices.sav");
    if (!TestTrue(TEXT("Read pre-services fixture"), FFileHelper::LoadFileToArray(Bytes, *Fixture)))
    {
        return false;
    }

    UANANTACitySave* Save = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if (!TestNotNull(TEXT("Deserialize pre-services fixture"), Save))
    {
        return false;
    }

    TestEqual(TEXT("Fixture starts at schema one"), Save->SchemaVersion, 1);
    const ECityMissionStage MissionStage = Save->Mission.Stage;
    const TSet<FName> MissionClues = Save->Mission.Clues;
    const TSet<FName> MissionDefeatedEnemies = Save->Mission.DefeatedEnemies;
    const bool bFragmentCollected = Save->Mission.bFragmentCollected;
    const int32 RewardCount = Save->Mission.RewardCount;
    const TSet<FName> VisitedServiceIds = Save->Services.VisitedIds;
    const TSet<FName> ClaimedSupplyIds = Save->Services.ClaimedSupplyIds;
    const int32 SuppliesCount = Save->Services.SuppliesCount;
    const FTransform PlayerTransform = Save->PlayerTransform;
    const FTransform CarTransform = Save->CarTransform;
    const bool bHasPlayerTransform = Save->bHasPlayerTransform;
    const bool bHasCarTransform = Save->bHasCarTransform;

    Save->MigrateToCurrentSchema();

    TestEqual(TEXT("Migration reaches current schema"), Save->SchemaVersion,
        UANANTACitySave::GetCurrentSchemaVersion());
    TestEqual(TEXT("Migration preserves mission stage"), Save->Mission.Stage, MissionStage);
    TestTrue(TEXT("Migration preserves mission clues"), SameSet(Save->Mission.Clues, MissionClues));
    TestTrue(TEXT("Migration preserves defeated enemies"),
        SameSet(Save->Mission.DefeatedEnemies, MissionDefeatedEnemies));
    TestEqual(TEXT("Migration preserves fragment state"), Save->Mission.bFragmentCollected, bFragmentCollected);
    TestEqual(TEXT("Migration preserves reward count"), Save->Mission.RewardCount, RewardCount);
    TestTrue(TEXT("Migration preserves service visits"), SameSet(Save->Services.VisitedIds, VisitedServiceIds));
    TestTrue(TEXT("Migration preserves service claims"), SameSet(Save->Services.ClaimedSupplyIds, ClaimedSupplyIds));
    TestEqual(TEXT("Migration preserves service count"), Save->Services.SuppliesCount, SuppliesCount);
    TestTrue(TEXT("Migration preserves player transform"), Save->PlayerTransform.Equals(PlayerTransform));
    TestTrue(TEXT("Migration preserves car transform"), Save->CarTransform.Equals(CarTransform));
    TestEqual(TEXT("Migration preserves player transform flag"), Save->bHasPlayerTransform, bHasPlayerTransform);
    TestEqual(TEXT("Migration preserves car transform flag"), Save->bHasCarTransform, bHasCarTransform);
    TestTrue(TEXT("Migrated fixture remains valid"), Save->IsValidSave());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityPersistenceSchemaRoundTripTest,
    "ANANTA.City.Persistence.SchemaTwoRoundTripAllState",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityPersistenceSchemaRoundTripTest::RunTest(const FString& Parameters)
{
    UANANTACitySave* Save = MakeSchemaTwoSave();
    TestTrue(TEXT("Schema two sample is valid"), Save->IsValidSave());

    TArray<uint8> Bytes;
    TestTrue(TEXT("Serialize schema two sample"), UGameplayStatics::SaveGameToMemory(Save, Bytes));
    UANANTACitySave* Restored = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if (!TestNotNull(TEXT("Deserialize schema two sample"), Restored))
    {
        return false;
    }

    TestTrue(TEXT("Restored schema two sample is valid"), Restored->IsValidSave());
    TestEqual(TEXT("Schema version round-trips"), Restored->SchemaVersion, Save->SchemaVersion);
    TestTrue(TEXT("Interaction state round-trips"),
        SameSet(Restored->InteractionState.OpenedDoorIds, Save->InteractionState.OpenedDoorIds)
        && SameSet(Restored->InteractionState.UsedPropIds, Save->InteractionState.UsedPropIds)
        && SameSet(Restored->InteractionState.VisitedDistrictIds, Save->InteractionState.VisitedDistrictIds));
    TestTrue(TEXT("NPC schedule round-trips"),
        SameMap(Restored->NpcSchedule.PhaseByNpcId, Save->NpcSchedule.PhaseByNpcId)
        && SameSet(Restored->NpcSchedule.ActiveNpcIds, Save->NpcSchedule.ActiveNpcIds));
    TestTrue(TEXT("Vehicle transforms round-trip"),
        SameTransformMap(Restored->VehicleTransit.VehicleTransforms, Save->VehicleTransit.VehicleTransforms));
    TestTrue(TEXT("Vehicle route stops round-trip"),
        SameMap(Restored->VehicleTransit.RouteStopById, Save->VehicleTransit.RouteStopById));
    TestTrue(TEXT("Vehicle boarded IDs round-trip"),
        SameSet(Restored->VehicleTransit.BoardedTransitIds, Save->VehicleTransit.BoardedTransitIds));
    TestTrue(TEXT("Vehicle signals round-trip"),
        SameMap(Restored->VehicleTransit.SignalStateById, Save->VehicleTransit.SignalStateById));
    TestTrue(TEXT("Economy inventory round-trips"), SameMap(Restored->Economy.Inventory, Save->Economy.Inventory));
    TestEqual(TEXT("Economy tokens round-trip"), Restored->Economy.CityTokens, Save->Economy.CityTokens);
    TestEqual(TEXT("Day index round-trips"), Restored->DayNight.DayIndex, Save->DayNight.DayIndex);
    TestTrue(TEXT("Time of day round-trips"),
        FMath::IsNearlyEqual(Restored->DayNight.TimeHours, Save->DayNight.TimeHours));
    TestEqual(TEXT("Lighting layer round-trips"), Restored->DayNight.LightingLayer, Save->DayNight.LightingLayer);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityPersistenceMissingDefaultsTest,
    "ANANTA.City.Persistence.SchemaTwoMissingFieldsUseDefaults",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityPersistenceMissingDefaultsTest::RunTest(const FString& Parameters)
{
    UANANTACitySave* Save = NewObject<UANANTACitySave>();
    Save->SchemaVersion = UANANTACitySave::GetCurrentSchemaVersion();
    TestTrue(TEXT("Schema two defaults are valid"), Save->IsValidSave());

    TArray<uint8> Bytes;
    TestTrue(TEXT("Serialize schema two defaults"), UGameplayStatics::SaveGameToMemory(Save, Bytes));
    UANANTACitySave* Restored = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if (!TestNotNull(TEXT("Deserialize schema two defaults"), Restored))
    {
        return false;
    }

    TestTrue(TEXT("Deserialized defaults remain valid"), Restored->IsValidSave());
    TestTrue(TEXT("Opened doors default empty"), Restored->InteractionState.OpenedDoorIds.IsEmpty());
    TestTrue(TEXT("Used props default empty"), Restored->InteractionState.UsedPropIds.IsEmpty());
    TestTrue(TEXT("Visited districts default empty"), Restored->InteractionState.VisitedDistrictIds.IsEmpty());
    TestTrue(TEXT("NPC phases default empty"), Restored->NpcSchedule.PhaseByNpcId.IsEmpty());
    TestTrue(TEXT("Active NPCs default empty"), Restored->NpcSchedule.ActiveNpcIds.IsEmpty());
    TestTrue(TEXT("Vehicle transforms default empty"), Restored->VehicleTransit.VehicleTransforms.IsEmpty());
    TestTrue(TEXT("Vehicle routes default empty"), Restored->VehicleTransit.RouteStopById.IsEmpty());
    TestTrue(TEXT("Boarded transit default empty"), Restored->VehicleTransit.BoardedTransitIds.IsEmpty());
    TestTrue(TEXT("Signal state default empty"), Restored->VehicleTransit.SignalStateById.IsEmpty());
    TestTrue(TEXT("Inventory defaults empty"), Restored->Economy.Inventory.IsEmpty());
    TestEqual(TEXT("City tokens default zero"), Restored->Economy.CityTokens, 0);
    TestEqual(TEXT("Day index defaults zero"), Restored->DayNight.DayIndex, 0);
    TestTrue(TEXT("Time defaults to midday"), FMath::IsNearlyEqual(Restored->DayNight.TimeHours, 12.f));
    TestEqual(TEXT("Lighting layer defaults to day"), Restored->DayNight.LightingLayer, FName(TEXT("Day")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityPersistenceCorruptSchemaTest,
    "ANANTA.City.Persistence.CorruptAndUnknownSchemaRejected",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityPersistenceCorruptSchemaTest::RunTest(const FString& Parameters)
{
    UANANTACitySave* UnknownSchemaSave = MakeSchemaTwoSave();
    UnknownSchemaSave->SchemaVersion = UANANTACitySave::GetCurrentSchemaVersion() + 100;
    const int32 OriginalTokens = UnknownSchemaSave->Economy.CityTokens;
    UnknownSchemaSave->MigrateToCurrentSchema();
    TestEqual(TEXT("Unknown schema is not overwritten by migration"), UnknownSchemaSave->SchemaVersion,
        UANANTACitySave::GetCurrentSchemaVersion() + 100);
    TestEqual(TEXT("Unknown schema preserves data while rejected"),
        UnknownSchemaSave->Economy.CityTokens, OriginalTokens);
    TestFalse(TEXT("Unknown schema is invalid"), UnknownSchemaSave->IsValidSave());

    TArray<uint8> ValidBytes;
    UANANTACitySave* ValidSave = MakeSchemaTwoSave();
    TestTrue(TEXT("Serialize source for corruption check"),
        UGameplayStatics::SaveGameToMemory(ValidSave, ValidBytes));
    TArray<uint8> CorruptBytes = ValidBytes;
    CorruptBytes.SetNum(2, EAllowShrinking::No);
    UANANTACitySave* Corrupt = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(CorruptBytes));
    TestNull(TEXT("Truncated corrupt bytes are rejected"), Corrupt);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityPersistenceValidationTest,
    "ANANTA.City.Persistence.InvalidIdsCountsAndTransformsRejected",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityPersistenceValidationTest::RunTest(const FString& Parameters)
{
    UANANTACitySave* InvalidIdSave = MakeSchemaTwoSave();
    InvalidIdSave->InteractionState.OpenedDoorIds.Add(NAME_None);
    TestFalse(TEXT("None interaction ID is rejected"), InvalidIdSave->IsValidSave());

    UANANTACitySave* InvalidCountSave = MakeSchemaTwoSave();
    InvalidCountSave->Economy.CityTokens = -1;
    TestFalse(TEXT("Negative economy count is rejected"), InvalidCountSave->IsValidSave());

    UANANTACitySave* InvalidTransformSave = MakeSchemaTwoSave();
    InvalidTransformSave->VehicleTransit.VehicleTransforms.Add(
        TEXT("Vehicle_Invalid"), FTransform(FVector(999999.0f, 0.0f, 0.0f)));
    TestFalse(TEXT("Out-of-bounds vehicle transform is rejected"), InvalidTransformSave->IsValidSave());

    UANANTACitySave* InvalidPhaseSave = MakeSchemaTwoSave();
    InvalidPhaseSave->NpcSchedule.PhaseByNpcId.Add(TEXT("Npc_Invalid"), -1.0f);
    TestFalse(TEXT("Negative NPC phase is rejected"), InvalidPhaseSave->IsValidSave());
    return true;
}
#endif
