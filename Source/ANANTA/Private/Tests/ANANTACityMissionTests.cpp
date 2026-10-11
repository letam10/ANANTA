#include "City/ANANTACityState.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Kismet/GameplayStatics.h"

namespace
{
    void ReachCombat(FCityMissionState& State)
    {
        State.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver);
        State.Interact(TEXT("Clue_01"), ECityInteractionKind::Clue);
        State.Interact(TEXT("Clue_02"), ECityInteractionKind::Clue);
        State.Interact(TEXT("Clue_03"), ECityInteractionKind::Clue);
    }

    void ClearEncounter(FCityMissionState& State)
    {
        State.Defeat(TEXT("Enemy_01"));
        State.Defeat(TEXT("Enemy_02"));
        State.Defeat(TEXT("Enemy_03"));
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityMissionOrderTest, "ANANTA.City.Mission.InvalidOrderAndDuplicateIds",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityMissionOrderTest::RunTest(const FString& Parameters)
{
    FCityMissionState State;
    TestTrue(TEXT("Initial state valid"), State.IsValid());
    TestFalse(TEXT("Clue before giver rejected"), State.Interact(TEXT("Clue_01"), ECityInteractionKind::Clue));
    TestFalse(TEXT("Fragment before combat rejected"),
        State.Interact(TEXT("Fragment_Anomaly"), ECityInteractionKind::Fragment));
    TestFalse(TEXT("Premature enemy death rejected"), State.Defeat(TEXT("Enemy_01")));
    TestFalse(TEXT("Wrong giver ID rejected"), State.Interact(TEXT("Cafe"), ECityInteractionKind::Giver));
    State.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver);
    State.Interact(TEXT("Clue_01"), ECityInteractionKind::Clue);
    TestFalse(TEXT("Duplicate clue rejected"), State.Interact(TEXT("Clue_01"), ECityInteractionKind::Clue));
    TestFalse(TEXT("Unknown clue rejected"), State.Interact(TEXT("Clue_04"), ECityInteractionKind::Clue));
    TestEqual(TEXT("Only one clue counted"), State.Clues.Num(), 1);
    State.Interact(TEXT("Clue_02"), ECityInteractionKind::Clue);
    TestTrue(TEXT("Two clues do not trigger combat"), State.Stage == ECityMissionStage::Investigating);
    State.Interact(TEXT("Clue_03"), ECityInteractionKind::Clue);
    TestTrue(TEXT("Three clues activate combat"), State.Stage == ECityMissionStage::Combat);
    State.Defeat(TEXT("Enemy_01"));
    TestFalse(TEXT("Duplicate enemy rejected"), State.Defeat(TEXT("Enemy_01")));
    TestFalse(TEXT("Unknown enemy rejected"), State.Defeat(TEXT("Enemy_04")));
    TestFalse(TEXT("Fragment requires all enemies"),
        State.Interact(TEXT("Fragment_Anomaly"), ECityInteractionKind::Fragment));
    TestTrue(TEXT("State still valid"), State.IsValid());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityMissionRewardTest, "ANANTA.City.Mission.RewardExactlyOnce",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityMissionRewardTest::RunTest(const FString& Parameters)
{
    FCityMissionState State;
    ReachCombat(State);
    ClearEncounter(State);
    TestFalse(TEXT("Report without fragment rejected"), State.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver));
    TestTrue(TEXT("Player recovers fragment"),
        State.Interact(TEXT("Fragment_Anomaly"), ECityInteractionKind::Fragment));
    TestEqual(TEXT("Fragment alone gives no reward"), State.RewardCount, 0);
    TestFalse(TEXT("Duplicate fragment rejected"),
        State.Interact(TEXT("Fragment_Anomaly"), ECityInteractionKind::Fragment));
    TestTrue(TEXT("Report completes mission"), State.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver));
    for (int32 Repeat = 0; Repeat < 10; ++Repeat)
    {
        TestFalse(TEXT("Repeated report rejected"), State.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver));
    }
    TestEqual(TEXT("Exactly one reward"), State.RewardCount, 1);
    TestTrue(TEXT("Completed state valid"), State.IsValid());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCitySaveTest, "ANANTA.City.Save.SerializationAndValidation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCitySaveTest::RunTest(const FString& Parameters)
{
    UANANTACitySave* Save = NewObject<UANANTACitySave>();
    ReachCombat(Save->Mission);
    ClearEncounter(Save->Mission);
    Save->Mission.Interact(TEXT("Fragment_Anomaly"), ECityInteractionKind::Fragment);
    Save->Mission.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver);
    Save->bHasPlayerTransform = true;
    Save->bHasCarTransform = true;
    Save->PlayerTransform = FTransform(FRotator(0, 70, 0), FVector(20000, 1800, 110));
    Save->CarTransform = FTransform(FRotator(0, 20, 0), FVector(21000, 400, 70));
    Save->LegacyFragments.Add(TEXT("Fragment_001"));
    TArray<uint8> Bytes;
    TestTrue(TEXT("Serialize save"), UGameplayStatics::SaveGameToMemory(Save, Bytes));
    auto* Restored = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if (!TestNotNull(TEXT("Deserialize save"), Restored))
    {
        return false;
    }
    TestTrue(TEXT("Restored state validates"), Restored->IsValidSave());
    TestEqual(TEXT("All clues restored"), Restored->Mission.Clues.Num(), 3);
    TestEqual(TEXT("All deaths restored"), Restored->Mission.DefeatedEnemies.Num(), 3);
    TestEqual(TEXT("Reward restored once"), Restored->Mission.RewardCount, 1);
    TestTrue(TEXT("Player position restored"), Restored->PlayerTransform.Equals(Save->PlayerTransform));
    TestTrue(TEXT("Car position restored"), Restored->CarTransform.Equals(Save->CarTransform));
    TestTrue(TEXT("Legacy collection restored"), Restored->LegacyFragments.Contains(TEXT("Fragment_001")));
    TestFalse(TEXT("Reload cannot duplicate reward"),
        Restored->Mission.Interact(TEXT("Giver_Cafe"), ECityInteractionKind::Giver));
    Restored->SchemaVersion = 2;
    TestFalse(TEXT("Unknown schema rejected"), Restored->IsValidSave());
    Restored->SchemaVersion = 1;
    Restored->Mission.Clues.Empty();
    TestFalse(TEXT("Impossible completed state rejected"), Restored->IsValidSave());
    Restored->Mission = Save->Mission;
    Restored->PlayerTransform.SetLocation(FVector(999999, 0, 0));
    TestFalse(TEXT("Unsafe restored position rejected"), Restored->IsValidSave());
    return true;
}
#endif
