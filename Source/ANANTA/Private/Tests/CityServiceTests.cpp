#include "City/ANANTACityState.h"
#include "City/CityServiceState.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Kismet/GameplayStatics.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityServiceClaimsTest, "ANANTA.City.Services.ClaimsExactlyOnce",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityServiceClaimsTest::RunTest(const FString& Parameters)
{
    FCityServiceState State;
    TestTrue(TEXT("Default service state valid"), State.IsValid());
    TestTrue(TEXT("First market claim"), State.ClaimSupply(TEXT("Market_Supplies")));
    TestTrue(TEXT("Additional authored supply"), State.ClaimSupply(TEXT("Supply_Rooftop")));
    TestTrue(TEXT("First bookshop discovery"), State.Discover(TEXT("Bookshop_Read")));
    for (int32 Repeat = 0; Repeat < 10; ++Repeat)
    {
        TestFalse(TEXT("Market repeat gives nothing"), State.ClaimSupply(TEXT("Market_Supplies")));
        TestFalse(TEXT("Optional supply repeat gives nothing"), State.ClaimSupply(TEXT("Supply_Rooftop")));
        TestFalse(TEXT("Bookshop repeat adds no discovery"), State.Discover(TEXT("Bookshop_Read")));
    }
    TestEqual(TEXT("Two supplies from two IDs"), State.SuppliesCount, 2);
    TestEqual(TEXT("One location discovered"), State.VisitedIds.Num(), 1);
    TestTrue(TEXT("Claims remain valid"), State.IsValid());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityServiceValidationTest, "ANANTA.City.Services.InvalidIdsAndCounts",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityServiceValidationTest::RunTest(const FString& Parameters)
{
    FCityServiceState State;
    TestFalse(TEXT("None claim rejected"), State.ClaimSupply(NAME_None));
    TestFalse(TEXT("None discovery rejected"), State.Discover(NAME_None));
    TestFalse(TEXT("Unknown supply rejected"), State.ClaimSupply(TEXT("Unknown")));
    TestFalse(TEXT("Empty supply suffix rejected"), State.ClaimSupply(TEXT("Supply_")));
    TestFalse(TEXT("Mission ID rejected"), State.Discover(TEXT("Clue_01")));
    TestFalse(TEXT("Wrong service kind rejected"), State.ClaimSupply(TEXT("Bookshop_Read")));
    TestFalse(TEXT("Unknown enum rejected"),
        FCityServiceState::IsServiceId(TEXT("Clinic_Heal"), static_cast<ECityServiceKind>(255)));
    TestTrue(TEXT("Rest cafe recognized"), FCityServiceState::IsServiceId(TEXT("Cafe_Rest"), ECityServiceKind::Rest));
    TestTrue(TEXT("Rest apartment recognized"),
        FCityServiceState::IsServiceId(TEXT("Apartment_Rest"), ECityServiceKind::Rest));
    TestTrue(TEXT("Clinic recognized"), FCityServiceState::IsServiceId(TEXT("Clinic_Heal"), ECityServiceKind::Heal));
    State.SuppliesCount = -1;
    TestFalse(TEXT("Negative count rejected"), State.IsValid());
    State.SuppliesCount = MAX_int32;
    TestFalse(TEXT("Impossible large count rejected"), State.IsValid());
    TestFalse(TEXT("Corrupt state cannot accept claims"), State.ClaimSupply(TEXT("Market_Supplies")));
    State.SuppliesCount = 0;
    State.ClaimedSupplyIds.Add(TEXT("Market_Supplies"));
    TestFalse(TEXT("Missing inventory unit rejected"), State.IsValid());
    State.SuppliesCount = 1;
    TestTrue(TEXT("Matching claim and inventory valid"), State.IsValid());
    State.VisitedIds.Add(NAME_None);
    TestFalse(TEXT("None in loaded discoveries rejected"), State.IsValid());
    State.VisitedIds.Empty();
    State.ClaimedSupplyIds.Empty();
    State.ClaimedSupplyIds.Add(NAME_None);
    TestFalse(TEXT("None in loaded claims rejected"), State.IsValid());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityServiceSaveTest, "ANANTA.City.Services.AdditiveSaveAndMissionIsolation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityServiceSaveTest::RunTest(const FString& Parameters)
{
    auto* Save = NewObject<UANANTACitySave>();
    TestEqual(TEXT("Existing schema retained"), Save->SchemaVersion, 1);
    TestTrue(TEXT("Empty additive fields valid"), Save->IsValidSave());
    Save->Mission.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver);
    Save->Mission.Interact(TEXT("Clue_01"), ECityInteractionKind::Clue);
    Save->Services.ClaimSupply(TEXT("Market_Supplies"));
    Save->Services.Discover(TEXT("Bookshop_Read"));
    Save->Services.Discover(TEXT("Gallery_Read"));
    Save->Services.Discover(TEXT("Workshop_Read"));
    Save->Services.Discover(TEXT("Transit_Read"));
    Save->Services.Discover(TEXT("Cafe_Rest"));
    Save->Services.Discover(TEXT("Apartment_Rest"));
    Save->Services.Discover(TEXT("Clinic_Heal"));
    Save->Services.Discover(TEXT("Market_Supplies"));
    TArray<uint8> Bytes;
    TestTrue(TEXT("Serialize additive save in memory"), UGameplayStatics::SaveGameToMemory(Save, Bytes));
    auto* Restored = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if (!TestNotNull(TEXT("Deserialize additive save"), Restored))
    {
        return false;
    }
    TestTrue(TEXT("Restored save valid"), Restored->IsValidSave());
    TestEqual(TEXT("Inventory restored"), Restored->Services.SuppliesCount, 1);
    TestEqual(TEXT("All eight services restored"), Restored->Services.VisitedIds.Num(), 8);
    TestFalse(TEXT("Reload does not replenish supply"), Restored->Services.ClaimSupply(TEXT("Market_Supplies")));
    TestFalse(TEXT("Reload does not duplicate discovery"), Restored->Services.Discover(TEXT("Gallery_Read")));
    TestTrue(TEXT("Mission stage unchanged"), Restored->Mission.Stage == ECityMissionStage::Investigating);
    TestTrue(TEXT("Mission clue preserved"), Restored->Mission.Clues.Contains(TEXT("Clue_01")));
    TestEqual(TEXT("Mission clue count unchanged"), Restored->Mission.Clues.Num(), 1);
    TestEqual(TEXT("Services give no mission reward"), Restored->Mission.RewardCount, 0);
    TestTrue(TEXT("Mission proceeds normally"),
        Restored->Mission.Interact(TEXT("Clue_02"), ECityInteractionKind::Clue));
    Restored->Services.SuppliesCount = 2;
    TestFalse(TEXT("Invalid services reject entire save"), Restored->IsValidSave());
    return true;
}
#endif
