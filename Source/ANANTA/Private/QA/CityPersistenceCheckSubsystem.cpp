#include "QA/CityPersistenceCheckSubsystem.h"

#include "City/ANANTACityState.h"
#include "City/ANANTACitySubsystem.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"

namespace
{
    FString SortedSet(const TSet<FName>& Values)
    {
        TArray<FString> Names;
        for (const FName Value : Values)
        {
            Names.Add(Value.ToString());
        }
        Names.Sort();
        return FString::Join(Names, TEXT(","));
    }

    FString SortedIntMap(const TMap<FName, int32>& Values)
    {
        TArray<FString> Entries;
        for (const TPair<FName, int32>& Value : Values)
        {
            Entries.Add(FString::Printf(TEXT("%s:%d"), *Value.Key.ToString(), Value.Value));
        }
        Entries.Sort();
        return FString::Join(Entries, TEXT(","));
    }

    FString SortedFloatMap(const TMap<FName, float>& Values)
    {
        TArray<FString> Entries;
        for (const TPair<FName, float>& Value : Values)
        {
            Entries.Add(FString::Printf(TEXT("%s:%.4f"), *Value.Key.ToString(), Value.Value));
        }
        Entries.Sort();
        return FString::Join(Entries, TEXT(","));
    }

    FString SortedByteMap(const TMap<FName, uint8>& Values)
    {
        TArray<FString> Entries;
        for (const TPair<FName, uint8>& Value : Values)
        {
            Entries.Add(FString::Printf(TEXT("%s:%d"), *Value.Key.ToString(), Value.Value));
        }
        Entries.Sort();
        return FString::Join(Entries, TEXT(","));
    }

    FString SortedTransformMap(const TMap<FName, FTransform>& Values)
    {
        TArray<FString> Entries;
        for (const TPair<FName, FTransform>& Value : Values)
        {
            Entries.Add(FString::Printf(TEXT("%s:%s"), *Value.Key.ToString(),
                *Value.Value.ToString()));
        }
        Entries.Sort();
        return FString::Join(Entries, TEXT(","));
    }
}

bool UCityPersistenceCheckSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
#if UE_BUILD_SHIPPING
    return false;
#else
    const UWorld* World = Cast<UWorld>(Outer);
    return World && World->IsGameWorld()
        && (FParse::Param(FCommandLine::Get(), TEXT("CityPersistenceCheck"))
            || FParse::Param(FCommandLine::Get(), TEXT("CityPersistenceReload")));
#endif
}

TStatId UCityPersistenceCheckSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(UCityPersistenceCheckSubsystem, STATGROUP_Tickables);
}

UANANTACitySubsystem* UCityPersistenceCheckSubsystem::State() const
{
    return GetWorld() && GetWorld()->GetGameInstance()
        ? GetWorld()->GetGameInstance()->GetSubsystem<UANANTACitySubsystem>() : nullptr;
}

FString UCityPersistenceCheckSubsystem::EvidenceDirectory() const
{
    return FPaths::ProjectSavedDir() / TEXT("QA/CityPersistence");
}

FString UCityPersistenceCheckSubsystem::Snapshot(const UANANTACitySave* Save) const
{
    if (!Save)
    {
        return TEXT("missing");
    }
    return FString::Printf(
        TEXT("schema=%d|doors=%s|props=%s|districts=%s|npc=%s|active=%s|vehicles=%s|routes=%s|boarded=%s|signals=%s|inventory=%s|tokens=%d|day=%d|hours=%.4f|layer=%s|mission=%d|visits=%s|claims=%s|supplies=%d"),
        Save->SchemaVersion,
        *SortedSet(Save->InteractionState.OpenedDoorIds),
        *SortedSet(Save->InteractionState.UsedPropIds),
        *SortedSet(Save->InteractionState.VisitedDistrictIds),
        *SortedFloatMap(Save->NpcSchedule.PhaseByNpcId),
        *SortedSet(Save->NpcSchedule.ActiveNpcIds),
        *SortedTransformMap(Save->VehicleTransit.VehicleTransforms),
        *SortedIntMap(Save->VehicleTransit.RouteStopById),
        *SortedSet(Save->VehicleTransit.BoardedTransitIds),
        *SortedByteMap(Save->VehicleTransit.SignalStateById),
        *SortedIntMap(Save->Economy.Inventory),
        Save->Economy.CityTokens,
        Save->DayNight.DayIndex,
        Save->DayNight.TimeHours,
        *Save->DayNight.LightingLayer.ToString(),
        static_cast<int32>(Save->Mission.Stage),
        *SortedSet(Save->Services.VisitedIds),
        *SortedSet(Save->Services.ClaimedSupplyIds),
        Save->Services.SuppliesCount);
}

bool UCityPersistenceCheckSubsystem::StartRun()
{
    if (bStarted)
    {
        return true;
    }
    bStarted = true;
    StartedAt = FPlatformTime::Seconds();
    bReload = FParse::Param(FCommandLine::Get(), TEXT("CityPersistenceReload"));
    const bool bCheck = FParse::Param(FCommandLine::Get(), TEXT("CityPersistenceCheck"));
    if (bReload == bCheck || !FParse::Param(FCommandLine::Get(), TEXT("CityQASlot"))
        || !GetWorld() || !GetWorld()->GetMapName().Contains(TEXT("ANANTA_City")))
    {
        Finish(false, TEXT("Require exactly one persistence mode, CityQASlot and ANANTA_City map"));
        return false;
    }
    IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
    if (!bReload)
    {
        IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Checkpoint.txt")), false);
        IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Report.txt")), false);
        IFileManager::Get().Delete(*(EvidenceDirectory() / TEXT("Reload.txt")), false);
    }
    if (bReload && !ReadCheckpoint())
    {
        Finish(false, TEXT("Reload requires a checkpoint from a different process"));
        return false;
    }
    return true;
}

bool UCityPersistenceCheckSubsystem::ReadSlotSnapshot(const FString& Slot, FString& OutSnapshot) const
{
    if (!UGameplayStatics::DoesSaveGameExist(Slot, 0))
    {
        return false;
    }
    auto* Save = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromSlot(Slot, 0));
    if (!Save || !Save->MigrateToCurrentSchema() || !Save->IsValidSave())
    {
        return false;
    }
    OutSnapshot = Snapshot(Save);
    return true;
}

bool UCityPersistenceCheckSubsystem::ExecuteCheck()
{
    auto* CityState = State();
    if (!CityState || !CityState->IsUsingQASlot() || !CityState->GetProgress()
        || CityState->GetProgress()->SchemaVersion != UANANTACitySave::GetCurrentSchemaVersion())
    {
        Finish(false, TEXT("Fresh QA state or schema two was not established"));
        return false;
    }
    const FTransform VehicleTransform(FRotator(0, 35, 0), FVector(2400, -1800, 90));
    ExpectedVehicleTransform = VehicleTransform;
    const bool bDoor = CityState->MarkDoorOpened(TEXT("Fixture_Door_Main"));
    const bool bProp = CityState->MarkPropUsed(TEXT("Fixture_Prop_Lamp"));
    const bool bVehicle = CityState->UpdateVehicleTransit(TEXT("PlayerCar"), VehicleTransform, 4, true);
    const bool bDistrict = CityState->MarkDistrictVisited(TEXT("District_Coastal"));
    const bool bService = CityState->TryUseService(TEXT("Market_Supplies"), ECityServiceKind::Supplies,
        TEXT("P4C fixture supply claim"));
    const bool bNpc = CityState->UpdateNpcSchedule(TEXT("Npc_Fixture_01"), 1.25f, true);
    const bool bSignal = CityState->UpdateTransitSignal(TEXT("Signal_Fixture_Main"), 2);
    const bool bInventory = CityState->AddInventory(TEXT("Item_Coffee"), 2);
    const bool bTokens = CityState->SetCityTokens(17);
    const bool bDayNight = CityState->SetDayNight(4, 19.5f, TEXT("BlueHour"));
    const bool bAllActions = bDoor && bProp && bVehicle && bDistrict && bService && bNpc && bSignal
        && bInventory && bTokens && bDayNight && CityState->SaveProgress();
    if (!bAllActions)
    {
        Finish(false, TEXT("One or more bounded persistence fixture mutations failed"));
        return false;
    }
    const UANANTACitySave* Save = CityState->GetProgress();
    ExpectedSnapshot = Snapshot(Save);
    FString PrimarySnapshot;
    FString BackupSnapshot;
    const bool bPrimary = ReadSlotSnapshot(CityState->GetSaveSlotName(), PrimarySnapshot);
    const bool bBackup = ReadSlotSnapshot(TEXT("ANANTA_City_QA_Backup"), BackupSnapshot);
    const bool bSlotsMatch = bPrimary && bBackup && PrimarySnapshot == ExpectedSnapshot
        && BackupSnapshot == ExpectedSnapshot;
    if (!bSlotsMatch || !WriteCheckpoint(Save))
    {
        Finish(false, TEXT("Primary and backup snapshots did not match the in memory fixture"));
        return false;
    }
    Finish(true, TEXT("Saved door prop vehicle district service NPC transit economy and day night fixture"));
    return true;
}

bool UCityPersistenceCheckSubsystem::ExecuteReload()
{
    auto* CityState = State();
    const UANANTACitySave* Save = CityState ? CityState->GetProgress() : nullptr;
    FString PrimarySnapshot;
    FString BackupSnapshot;
    const bool bSlotsMatch = CityState && Save && Save->IsValidSave()
        && Snapshot(Save) == ExpectedSnapshot
        && Save->VehicleTransit.VehicleTransforms.Contains(TEXT("PlayerCar"))
        && Save->VehicleTransit.VehicleTransforms.FindChecked(TEXT("PlayerCar")).Equals(ExpectedVehicleTransform)
        && ReadSlotSnapshot(CityState->GetSaveSlotName(), PrimarySnapshot)
        && ReadSlotSnapshot(TEXT("ANANTA_City_QA_Backup"), BackupSnapshot)
        && PrimarySnapshot == ExpectedSnapshot && BackupSnapshot == ExpectedSnapshot;
    if (!bSlotsMatch)
    {
        Finish(false, TEXT("Reloaded save did not retain all state groups or slot snapshots"));
        return false;
    }
    Finish(true, TEXT("Separate process reload retained all schema two persistence state"));
    return true;
}

bool UCityPersistenceCheckSubsystem::ReadCheckpoint()
{
    TArray<FString> Lines;
    if (!FFileHelper::LoadFileToStringArray(Lines, *(EvidenceDirectory() / TEXT("Checkpoint.txt")))
        || Lines.Num() != 4 || Lines[0] != TEXT("ANANTA_CITY_PERSISTENCE_CHECKPOINT_V1")
        || !Lines[1].IsNumeric() || !ExpectedVehicleTransform.InitFromString(Lines[3]))
    {
        return false;
    }
    PreviousProcessId = FCString::Strtoui64(*Lines[1], nullptr, 10);
    ExpectedSnapshot = Lines[2];
    return PreviousProcessId != 0 && PreviousProcessId != FPlatformProcess::GetCurrentProcessId()
        && !ExpectedSnapshot.IsEmpty();
}

bool UCityPersistenceCheckSubsystem::WriteCheckpoint(const UANANTACitySave* Save) const
{
    const TArray<FString> Lines = {
        TEXT("ANANTA_CITY_PERSISTENCE_CHECKPOINT_V1"),
        FString::Printf(TEXT("%u"), FPlatformProcess::GetCurrentProcessId()),
        Snapshot(Save),
        ExpectedVehicleTransform.ToString()
    };
    return FFileHelper::SaveStringArrayToFile(Lines, *(EvidenceDirectory() / TEXT("Checkpoint.txt")));
}

bool UCityPersistenceCheckSubsystem::WriteEvidence(const FString& FileName, const FString& Body) const
{
    IFileManager::Get().MakeDirectory(*EvidenceDirectory(), true);
    return FFileHelper::SaveStringToFile(Body, *(EvidenceDirectory() / FileName));
}

void UCityPersistenceCheckSubsystem::Finish(const bool bSuccess, const FString& Detail)
{
    if (bFinished)
    {
        return;
    }
    bFinished = true;
    bPassed = bSuccess;
    const auto* CityState = State();
    const FString Body = FString::Printf(
        TEXT("ANANTA P4C persistence quick runtime\nfixture_mode=true\nbackend_economy=fixture_only\n"
             "native_coastal_actor_hooks=false\nmode=%s\nstatus=%s\nprocess_id=%u\nwall_seconds=%.3f\n"
             "schema=%d\nsave_slot=%s\nbackup_slot=ANANTA_City_QA_Backup\n"
             "detail=%s\nsnapshot=%s\n"),
        bReload ? TEXT("Reload") : TEXT("Check"), bSuccess ? TEXT("PASSED") : TEXT("FAILED"),
        FPlatformProcess::GetCurrentProcessId(), FPlatformTime::Seconds() - StartedAt,
        CityState && CityState->GetProgress() ? CityState->GetProgress()->SchemaVersion : -1,
        CityState ? *CityState->GetSaveSlotName() : TEXT("missing"), *Detail,
        CityState ? *Snapshot(CityState->GetProgress()) : TEXT("missing"));
    WriteEvidence(bReload ? TEXT("Reload.txt") : TEXT("Report.txt"), Body);
    UE_LOG(LogTemp, Display, TEXT("CITY_PERSISTENCE_FINISH success=%d detail=%s"), bPassed, *Detail);
}

void UCityPersistenceCheckSubsystem::Tick(const float DeltaTime)
{
    if (bFinished)
    {
        if (++ExitFrames == 3)
        {
            FPlatformMisc::RequestExitWithStatus(false, bPassed ? 0 : 1);
        }
        return;
    }
    if (!GetWorld() || !GetWorld()->HasBegunPlay())
    {
        return;
    }
    if (!StartRun())
    {
        return;
    }
    if (FPlatformTime::Seconds() - StartedAt < 1.0)
    {
        return;
    }
    if (bReload)
    {
        ExecuteReload();
    }
    else
    {
        ExecuteCheck();
    }
}

void UCityPersistenceCheckSubsystem::Deinitialize()
{
    if (!bFinished && bStarted)
    {
        Finish(false, TEXT("World ended before bounded persistence check completed"));
    }
    Super::Deinitialize();
}
