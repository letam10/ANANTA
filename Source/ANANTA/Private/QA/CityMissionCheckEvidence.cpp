#include "QA/CityMissionCheckSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{
    FString SortedIds(const TSet<FName>& Ids)
    {
        TArray<FString> Names;
        for (const FName Id : Ids)
        {
            Names.Add(Id.ToString());
        }
        Names.Sort();
        return FString::Join(Names, TEXT(","));
    }
}

FString UCityMissionCheckSubsystem::EvidenceDirectory() const
{
    return FPaths::ProjectSavedDir() / TEXT("QA/CityMissionCheck");
}

const TCHAR* UCityMissionCheckSubsystem::PhaseName() const
{
    static const TCHAR* Names[] = {
        TEXT("WaitReady"), TEXT("Route"), TEXT("Interact"), TEXT("Fight"), TEXT("Repeat"), TEXT("Save")
    };
    return Names[static_cast<uint8>(Phase)];
}

float UCityMissionCheckSubsystem::PhaseTimeout() const
{
    switch (Phase)
    {
    case ECityMissionCheckPhase::WaitReady:
        return 60;
    case ECityMissionCheckPhase::Route:
        return Objective == 5 ? 240 : 180;
    case ECityMissionCheckPhase::Fight:
        return 90;
    default:
        return 15;
    }
}

void UCityMissionCheckSubsystem::NextPhase(const ECityMissionCheckPhase Next, const FString& Detail)
{
    ReleaseKeys();
    Phase = Next;
    PhaseStartTime = Now;
    PhaseElapsed = 0;
    bInputSent = false;
    MotionOrigin = GetHero() ? GetHero()->GetActorLocation() : FVector::ZeroVector;
    MotionTime = Now;
    Observe(true, Detail);
    if (!WriteReport(false, false))
    {
        Finish(false, TEXT("Could not persist phase evidence"));
    }
}

void UCityMissionCheckSubsystem::Observe(const bool bPass, const FString& Detail)
{
    const auto* Hero = GetHero();
    const auto* State = GetState();
    FString Entry = FString::Printf(TEXT("phase=%s objective=%s result=%s elapsed=%.3f detail=%s\n"),
        PhaseName(), *ObjectiveId().ToString(), bPass ? TEXT("PASS") : TEXT("FAIL"), Now - StartTime, *Detail);
    Entry += FString::Printf(TEXT("player_transform=%s\ncar_transform=%s\nhealth=%.3f\n"),
        Hero ? *Hero->GetActorTransform().ToString() : TEXT("missing"),
        Car.IsValid() ? *Car->GetActorTransform().ToString() : TEXT("missing"), Hero ? Hero->Health : -1);
    if (State)
    {
        const auto* Save = State->GetProgress();
        const auto& Mission = Save->Mission;
        Entry += FString::Printf(TEXT("stage=%d reward=%d clues=%s defeated=%s fragment=%s\n"),
            static_cast<int32>(Mission.Stage), Mission.RewardCount, *SortedIds(Mission.Clues),
            *SortedIds(Mission.DefeatedEnemies), Mission.bFragmentCollected ? TEXT("Fragment_Anomaly") : TEXT("none"));
        Entry += FString::Printf(TEXT("saved_player_transform=%s\nsaved_car_transform=%s\n"),
            *Save->PlayerTransform.ToString(), *Save->CarTransform.ToString());
        Entry += FString::Printf(TEXT("save_attempts=%u successful_saves=%u slot=%s\n"),
            State->GetSaveAttemptCount(), State->GetSuccessfulSaveCount(), *State->GetSaveSlotName());
    }
    Observations.Add(Entry);
    UE_LOG(LogTemp, Display, TEXT("CITY_MISSION_CHECK %s"), *Entry);
}

bool UCityMissionCheckSubsystem::WriteReport(const bool bComplete, const bool bPass) const
{
    IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
    FString Report = TEXT("ANANTA complete city mission functional check\n");
    Report += TEXT("input_source=engine-injected PlayerController.InputKey\ncontroller_facing_set=true\n");
    Report += TEXT("teleport=false\nmission_mutation=false\ndirect_damage=false\ngod_mode=false\n");
    Report += TEXT("save_slot=ANANTA_City_QA\nbackup_slot=ANANTA_City_QA_Backup\nnormal_save_io=false\n");
    Report += TEXT("maximum_duration_seconds=900\ntransform_tolerance_cm=10\nrotation_tolerance_degrees=0.5\n");
    Report += TEXT("scope=One walking mission or one new process reload; no desktop input or performance evidence\n");
    Report += FString::Printf(TEXT("mode=%s process_id=%u status=%s held_keys_after_cleanup=%d\n\n"),
        bReload ? TEXT("Reload") : TEXT("Check"), FPlatformProcess::GetCurrentProcessId(),
        bComplete ? (bPass ? TEXT("PASSED") : TEXT("FAILED")) : TEXT("RUNNING"), HeldKeys.Num());
    for (const FString& Entry : Observations)
    {
        Report += Entry + TEXT("\n");
    }
    const FString Name = bReload ? TEXT("ReloadReport.txt") : TEXT("MissionReport.txt");
    return FFileHelper::SaveStringToFile(Report, *(EvidenceDirectory() / Name));
}

void UCityMissionCheckSubsystem::Finish(const bool bPass, const FString& Detail)
{
    Observe(bPass, Detail);
    ReleaseKeys();
    bFinished = true;
    bPassed = bPass && WriteReport(true, bPass);
    if (!bPass)
    {
        WriteReport(true, false);
    }
    if (!bPassed && !bReload)
    {
        IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Checkpoint.txt")), false);
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_MISSION_CHECK_FINISH mode=%s success=%d"),
        bReload ? TEXT("Reload") : TEXT("Check"), bPassed);
}
