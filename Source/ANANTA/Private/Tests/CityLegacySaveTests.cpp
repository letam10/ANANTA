#if WITH_DEV_AUTOMATION_TESTS
#include "City/ANANTACityState.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityLegacySaveTest, "ANANTA.City.Save.PreServicesFileCompatibility",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityLegacySaveTest::RunTest(const FString& Parameters)
{
    // File QA that duoc luu truoc khi them Services; khong cham vao slot cua nguoi choi.
    TArray<uint8> Bytes;
    const FString Fixture = FPaths::ProjectDir() / TEXT("Tools/QA/Fixtures/CityBeforeServices.sav");
    if (!TestTrue(TEXT("Read original pre-services fixture"), FFileHelper::LoadFileToArray(Bytes, *Fixture)))
    {
        return false;
    }
    auto* Save = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Bytes));
    if (!TestNotNull(TEXT("Deserialize original save"), Save))
    {
        return false;
    }
    TestTrue(TEXT("Original save remains valid"), Save->IsValidSave());
    TestEqual(TEXT("Schema remains one"), Save->SchemaVersion, 1);
    TestTrue(TEXT("Completed mission retained"), Save->Mission.Stage == ECityMissionStage::Completed);
    TestEqual(TEXT("Three clues retained"), Save->Mission.Clues.Num(), 3);
    TestEqual(TEXT("Three enemy defeats retained"), Save->Mission.DefeatedEnemies.Num(), 3);
    TestEqual(TEXT("Single reward retained"), Save->Mission.RewardCount, 1);
    TestTrue(TEXT("Player transform retained"), Save->bHasPlayerTransform);
    TestTrue(TEXT("Vehicle transform retained"), Save->bHasCarTransform);
    TestEqual(TEXT("New visits start empty"), Save->Services.VisitedIds.Num(), 0);
    TestEqual(TEXT("New claims start empty"), Save->Services.ClaimedSupplyIds.Num(), 0);
    TestEqual(TEXT("New supply count starts zero"), Save->Services.SuppliesCount, 0);
    const FTransform Player = Save->PlayerTransform;
    const FTransform Vehicle = Save->CarTransform;
    TestTrue(TEXT("Existing player can claim new service"), Save->Services.ClaimSupply(TEXT("Market_Supplies")));
    TArray<uint8> Updated;
    TestTrue(TEXT("Serialize upgraded content in memory"), UGameplayStatics::SaveGameToMemory(Save, Updated));
    auto* Reloaded = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromMemory(Updated));
    if (!TestNotNull(TEXT("Reload upgraded content"), Reloaded))
    {
        return false;
    }
    TestTrue(TEXT("Upgraded state validates"), Reloaded->IsValidSave());
    TestTrue(TEXT("Upgrade preserves player transform"), Reloaded->PlayerTransform.Equals(Player));
    TestTrue(TEXT("Upgrade preserves car transform"), Reloaded->CarTransform.Equals(Vehicle));
    TestEqual(TEXT("Upgrade preserves reward"), Reloaded->Mission.RewardCount, 1);
    TestEqual(TEXT("Upgrade preserves service claim"), Reloaded->Services.SuppliesCount, 1);
    return true;
}
#endif
