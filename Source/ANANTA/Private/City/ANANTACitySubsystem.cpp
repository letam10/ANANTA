#include "City/ANANTACitySubsystem.h"

#include "City/ANANTACityController.h"
#include "City/ANANTACityVehicle.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Settings/CityText.h"

void UANANTACitySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    Progress = NewObject<UANANTACitySave>(this);
#if !UE_BUILD_SHIPPING
    const bool bInputSmoke = FParse::Param(FCommandLine::Get(), TEXT("CityInputSmoke"));
    const bool bMissionCheck = FParse::Param(FCommandLine::Get(), TEXT("CityMissionCheck"));
    const bool bMissionReload = FParse::Param(FCommandLine::Get(), TEXT("CityMissionReload"));
    const bool bServiceCheck = FParse::Param(FCommandLine::Get(), TEXT("CityServiceCheck"));
    const bool bServiceReload = FParse::Param(FCommandLine::Get(), TEXT("CityServiceReload"));
    const bool bStreamingCheck = FParse::Param(FCommandLine::Get(), TEXT("CityStreamingCheck"));
    const bool bMobilityCheck = FParse::Param(FCommandLine::Get(), TEXT("CityCollisionCheck"))
        || FParse::Param(FCommandLine::Get(), TEXT("CityTransitCheck"));
    bUseQASlot = bInputSmoke || bMissionCheck || bMissionReload || bServiceCheck || bServiceReload
        || bStreamingCheck || FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"));
    if (bUseQASlot)
    {
        SaveSlot = TEXT("ANANTA_City_QA");
        BackupSlot = TEXT("ANANTA_City_QA_Backup");
    }
    // Smoke luon bat dau moi; moi IO chi dung slot QA, khong nap hoac di chuyen save thuong.
    if (bInputSmoke || bMissionCheck || bServiceCheck || bStreamingCheck || bMobilityCheck)
    {
        SaveStatus = TEXT("New isolated QA journey");
        return;
    }
#endif
    LoadProgress();
}

FString UANANTACitySubsystem::GetObjectiveText() const
{
    const FCityMissionState& Mission = Progress->Mission;
    switch (Mission.Stage)
    {
    case ECityMissionStage::NotStarted:
        return TEXT("Meet the cafe contact [E]");
    case ECityMissionStage::Investigating:
        return FString::Printf(TEXT("%s %d / 3 [E]"),
            *CityText(TEXT("Investigate boulevard clues:"), TEXT("Điều tra manh mối:")), Mission.Clues.Num());
    case ECityMissionStage::Combat:
        return Mission.DefeatedEnemies.Num() == 3 ? TEXT("Recover the anomaly fragment [E]")
            : FString::Printf(TEXT("%s %d / 3 [LMB]"),
                *CityText(TEXT("Defeat anomaly guards:"), TEXT("Đánh bại lính dị thường:")),
                Mission.DefeatedEnemies.Num());
    case ECityMissionStage::ReturnToGiver:
        return TEXT("Return the fragment to the cafe contact [E]");
    case ECityMissionStage::Completed:
        return TEXT("Case closed. Reward received: 1 city token");
    default:
        return TEXT("");
    }
}

bool UANANTACitySubsystem::TryInteract(const FName Id, const ECityInteractionKind Kind)
{
    if (!Progress->Mission.Interact(Id, Kind))
    {
        return false;
    }
    SaveProgress();
    return true;
}

bool UANANTACitySubsystem::RegisterEnemyDefeated(const FName Id)
{
    if (!Progress->Mission.Defeat(Id))
    {
        return false;
    }
    SaveProgress();
    return true;
}

bool UANANTACitySubsystem::RegisterLegacyFragment(const FName Id)
{
    if (Id.IsNone() || Progress->LegacyFragments.Contains(Id))
    {
        return false;
    }
    Progress->LegacyFragments.Add(Id);
    SaveProgress();
    return true;
}

bool UANANTACitySubsystem::HasLegacyFragment(const FName Id) const
{
    return !Id.IsNone() && Progress->LegacyFragments.Contains(Id);
}

bool UANANTACitySubsystem::TryUseService(const FName Id, const ECityServiceKind Kind,
    const FString& Description)
{
    if (!Progress || !Progress->Services.IsValid() || !FCityServiceState::IsServiceId(Id, Kind))
    {
        return false;
    }
    const FCityServiceState Before = Progress->Services;
    bool bNeedsSave = false;
    switch (Kind)
    {
    case ECityServiceKind::Rest:
        bNeedsSave = true;
        ServiceMessage = TEXT("Rested: health restored and progress saved");
        break;
    case ECityServiceKind::Heal:
        ServiceMessage = TEXT("Clinic: health restored");
        break;
    case ECityServiceKind::Supplies:
        if (!Progress->Services.ClaimSupply(Id))
        {
            ServiceMessage = TEXT("Supplies already collected here");
            return false;
        }
        bNeedsSave = true;
        ServiceMessage = TEXT("Collected 1 supply");
        break;
    case ECityServiceKind::Read:
        bNeedsSave = Progress->Services.Discover(Id);
        ServiceMessage = Description.IsEmpty() ? TEXT("Location discovered") : Description;
        ServiceMessage.ReplaceInline(TEXT("\r"), TEXT(" "));
        ServiceMessage.ReplaceInline(TEXT("\n"), TEXT(" "));
        break;
    default:
        return false;
    }
    bNeedsSave = Progress->Services.Discover(Id) || bNeedsSave;
    if (bNeedsSave && !SaveProgress())
    {
        // Chi giu lan nhan moi khi save thanh cong; nguoi choi co the thu lai.
        Progress->Services = Before;
        ServiceMessage = TEXT("Service could not save progress; please try again");
        return false;
    }
    return true;
}

FString UANANTACitySubsystem::GetServiceSummary() const
{
    return FString::Printf(TEXT("%s %d  |  %s %d  |  %s"),
        *CityText(TEXT("Supplies"), TEXT("Tiếp tế")), Progress->Services.SuppliesCount,
        *CityText(TEXT("Locations"), TEXT("Địa điểm")), Progress->Services.VisitedIds.Num(),
        *CityTranslate(ServiceMessage));
}

bool UANANTACitySubsystem::SaveProgress()
{
    ++SaveAttemptCount;
    UWorld* World = GetWorld();
    if (World)
    {
        if (const auto* PC = Cast<AANANTACityController>(World->GetFirstPlayerController()))
        {
            if (PC->CanCaptureProgress() && PC->GetPawn())
            {
                Progress->PlayerTransform = PC->GetSafePlayerTransform();
                Progress->bHasPlayerTransform = true;
            }
        }
        for (TActorIterator<AANANTACityVehicle> It(World); It; ++It)
        {
            if (It->VehicleId == TEXT("PlayerCar") && It->IsRestoreComplete())
            {
                Progress->CarTransform = It->GetActorTransform();
                Progress->bHasCarTransform = true;
                break;
            }
        }
    }
    if (!Progress->IsValidSave())
    {
        SaveStatus = TEXT("Save rejected: invalid state");
        return false;
    }
    // Ghi ban du phong truoc; file chinh hong van nap duoc tien do da xac nhan.
    if (!UGameplayStatics::SaveGameToSlot(Progress, BackupSlot, 0))
    {
        SaveStatus = TEXT("Save failed - check free disk space");
        return false;
    }
    auto* Verified = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromSlot(BackupSlot, 0));
    if (!Verified || !Verified->IsValidSave())
    {
        SaveStatus = TEXT("Save verification failed");
        return false;
    }
    const bool bSaved = UGameplayStatics::SaveGameToSlot(Progress, SaveSlot, 0);
    SaveStatus = bSaved ? TEXT("Progress saved") : TEXT("Progress saved to recovery slot");
    if (bSaved)
    {
        ++SuccessfulSaveCount;
    }
    return true;
}

bool UANANTACitySubsystem::LoadProgress()
{
    // Backup duoc ghi truoc va luon la ban moi nhat da commit.
    for (const FString& Slot : { BackupSlot, SaveSlot })
    {
        auto* Loaded = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromSlot(Slot, 0));
        if (Loaded && Loaded->IsValidSave())
        {
            Progress = Loaded;
            SaveStatus = TEXT("Progress restored");
            return true;
        }
    }
    SaveStatus = TEXT("New city journey");
    return false;
}
