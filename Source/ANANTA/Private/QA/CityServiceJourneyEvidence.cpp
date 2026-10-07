#include "QA/CityServiceJourney.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACityInteractable.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/World.h"
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

FString UCityServiceJourney::EvidenceDirectory() const
{
    return FPaths::ProjectSavedDir() / TEXT("QA/CityServiceJourney");
}

const TCHAR* UCityServiceJourney::PhaseName() const
{
    static const TCHAR* Names[] = {
        TEXT("WaitReady"), TEXT("Route"), TEXT("Interact"), TEXT("Repeat"), TEXT("Save"), TEXT("Reload")
    };
    return Names[static_cast<uint8>(Phase)];
}

void UCityServiceJourney::NextPhase(const ECityServiceJourneyPhase Next, const FString& Detail)
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
        Finish(false, TEXT("Cannot persist journey phase evidence"));
    }
}

void UCityServiceJourney::Observe(const bool bPass, const FString& Detail)
{
    const auto* Hero = GetHero();
    const auto* State = GetState();
    const auto* Target = Controller.IsValid() ? Controller->FindInteractionTarget() : nullptr;
    const auto* Item = Cast<AANANTACityInteractable>(Target);
    const FString TargetName = Item ? Item->InteractionId.ToString() : GetNameSafe(Target);
    FString Entry = FString::Printf(TEXT("phase=%s venue=%s waypoint=%d result=%s wall_seconds=%.3f detail=%s\n"),
        PhaseName(), *ServiceId(Venue).ToString(), Waypoint, bPass ? TEXT("PASS") : TEXT("FAIL"),
        Now - StartTime, *Detail);
    Entry += FString::Printf(TEXT("player_transform=%s current_target=%s health=%.3f\n"),
        Hero ? *Hero->GetActorTransform().ToString() : TEXT("missing"), *TargetName, Hero ? Hero->Health : -1);
    if (Waypoints.IsValidIndex(Waypoint))
    {
        Entry += FString::Printf(TEXT("waypoint_target=%s\n"), *Waypoints[Waypoint].ToString());
    }
    if (State && State->GetProgress())
    {
        const auto& Services = State->GetServices();
        Entry += FString::Printf(TEXT("mission=%s visited_ids=%s claimed_supply_ids=%s supplies=%d\n"),
            State->GetMissionStage() == ECityMissionStage::NotStarted ? TEXT("NotStarted") : TEXT("CHANGED"),
            *SortedIds(Services.VisitedIds), *SortedIds(Services.ClaimedSupplyIds), Services.SuppliesCount);
        Entry += FString::Printf(TEXT("save_attempts=%u successful_saves=%u slot=%s\n"),
            State->GetSaveAttemptCount(), State->GetSuccessfulSaveCount(), *State->GetSaveSlotName());
    }
    Observations.Add(Entry);
    UE_LOG(LogTemp, Display, TEXT("CITY_SERVICE_JOURNEY %s"), *Entry);
}

bool UCityServiceJourney::WriteReport(const bool bComplete, const bool bPass) const
{
    IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
    FString Report = TEXT("ANANTA city service journey\n");
    Report += TEXT("input_source=PlayerController.InputKey\ncontroller_facing_set=true\n");
    Report += TEXT("teleport=false\ndirect_interaction=false\nmission_mutation=false\n");
    Report += TEXT("direct_damage=false\nhealth_injection=false\ngod_mode=false\n");
    Report += TEXT("injured_player_healing_exercised=false\nrest_heal_may_run_at_full_health=true\n");
    Report += TEXT("save_slot=ANANTA_City_QA\nbackup_slot=ANANTA_City_QA_Backup\nnormal_save_io=false\n");
    Report += TEXT("maximum_duration_seconds=360\ntransform_tolerance_cm=10\nrotation_tolerance_degrees=0.5\n");
    Report += TEXT("frame_scope=Wall frame intervals after ready during this ordinary short play; not a benchmark\n");
    Report += FString::Printf(TEXT("mode=%s process_id=%u status=%s held_keys_after_cleanup=%d\n"),
        bReload ? TEXT("Reload") : TEXT("Check"), FPlatformProcess::GetCurrentProcessId(),
        bComplete ? (bPass ? TEXT("PASSED") : TEXT("FAILED")) : TEXT("RUNNING"), HeldKeys.Num());
    Report += FString::Printf(TEXT("map=%s wall_seconds=%.3f\n"),
        GetWorld() ? *GetWorld()->GetMapName() : TEXT("missing"), Now - StartTime);
    double Total = 0;
    int32 Over33 = 0;
    int32 Over50 = 0;
    for (const double Milliseconds : FrameMilliseconds)
    {
        Total += Milliseconds;
        Over33 += Milliseconds > 33.3 ? 1 : 0;
        Over50 += Milliseconds > 50 ? 1 : 0;
    }
    TArray<double> Sorted = FrameMilliseconds;
    Sorted.Sort();
    const int32 Count = Sorted.Num();
    const double P95 = Count > 0 ? Sorted[FMath::CeilToInt(Count * 0.95) - 1] : 0;
    Report += FString::Printf(TEXT("frame_samples=%d mean_ms=%.3f p95_ms=%.3f over_33_3_ms=%d over_50_ms=%d\n\n"),
        Count, Count > 0 ? Total / Count : 0, P95, Over33, Over50);
    for (const FString& Entry : Observations)
    {
        Report += Entry + TEXT("\n");
    }
    const FString Name = bReload ? TEXT("Reload.txt") : TEXT("Report.txt");
    return FFileHelper::SaveStringToFile(Report, *(EvidenceDirectory() / Name));
}

void UCityServiceJourney::Finish(const bool bPass, const FString& Detail)
{
    if (bFinished)
    {
        return;
    }
    Observe(bPass, Detail);
    ReleaseKeys();
    bFinished = true;
    bPassed = bPass;
    if (!WriteReport(true, bPassed))
    {
        bPassed = false;
        UE_LOG(LogTemp, Error, TEXT("CITY_SERVICE_JOURNEY evidence write failed"));
    }
    if (!bPassed && !bReload)
    {
        IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Checkpoint.txt")), false);
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_SERVICE_JOURNEY_FINISH mode=%s success=%d"),
        bReload ? TEXT("Reload") : TEXT("Check"), bPassed);
}
