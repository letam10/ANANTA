#include "QA/CityMissionCheckSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformProcess.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"

namespace
{
    const FString CheckpointSchema = TEXT("ANANTA_CITY_MISSION_CHECKPOINT_V1");
    const FString CompletedIds = TEXT("Completed|1|Clue_01,Clue_02,Clue_03|")
        TEXT("Enemy_01,Enemy_02,Enemy_03|Fragment_Anomaly");

    bool SameTransform(const FTransform& A, const FTransform& B)
    {
        return A.GetLocation().Equals(B.GetLocation(), 10)
            && A.GetRotation().AngularDistance(B.GetRotation()) <= FMath::DegreesToRadians(0.5)
            && A.GetScale3D().Equals(B.GetScale3D(), 0.001);
    }
}

bool UCityMissionCheckSubsystem::IsComplete(const UANANTACitySave* Save) const
{
    if (!Save || !Save->IsValidSave() || !Save->LegacyFragments.IsEmpty())
    {
        return false;
    }
    const auto& Mission = Save->Mission;
    return Mission.Stage == ECityMissionStage::Completed && Mission.RewardCount == 1
        && Mission.bFragmentCollected && Mission.Clues.Num() == 3 && Mission.DefeatedEnemies.Num() == 3
        && Mission.Clues.Contains(TEXT("Clue_01")) && Mission.Clues.Contains(TEXT("Clue_02"))
        && Mission.Clues.Contains(TEXT("Clue_03")) && Mission.DefeatedEnemies.Contains(TEXT("Enemy_01"))
        && Mission.DefeatedEnemies.Contains(TEXT("Enemy_02")) && Mission.DefeatedEnemies.Contains(TEXT("Enemy_03"));
}

bool UCityMissionCheckSubsystem::IsSafelyGrounded() const
{
    const auto* Hero = GetHero();
    if (!Hero || Hero->IsHidden() || !Hero->GetActorEnableCollision() || Hero->GetAttachParentActor()
        || !Hero->GetCharacterMovement()->IsMovingOnGround())
    {
        return false;
    }
    const auto* Capsule = Hero->GetCapsuleComponent();
    const float HalfHeight = Capsule->GetScaledCapsuleHalfHeight();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityMissionGround), false, Hero);
    if (GetWorld()->OverlapBlockingTestByChannel(Hero->GetActorLocation(), FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius() - 1, HalfHeight - 1), Params))
    {
        return false;
    }
    FHitResult Floor;
    const FVector Start = Hero->GetActorLocation();
    return GetWorld()->LineTraceSingleByChannel(Floor, Start, Start - FVector(0, 0, HalfHeight + 30),
        ECC_WorldStatic, Params) && Floor.ImpactNormal.Z > 0.7f
        && FMath::Abs(Start.Z - HalfHeight - Floor.ImpactPoint.Z) < 15;
}

bool UCityMissionCheckSubsystem::VerifySavedProgress() const
{
    const auto* State = GetState();
    if (!State || !State->IsUsingQASlot() || State->GetSaveSlotName() != TEXT("ANANTA_City_QA")
        || !IsComplete(State->GetProgress()) || !IsSafelyGrounded())
    {
        return false;
    }
    // Chi doc hai slot QA; khong goi nap hay ghi save thuong.
    for (const FString& Slot : { FString(TEXT("ANANTA_City_QA")), FString(TEXT("ANANTA_City_QA_Backup")) })
    {
        const auto* Save = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromSlot(Slot, 0));
        if (!IsComplete(Save) || !Save->bHasPlayerTransform || !Save->bHasCarTransform
            || !SameTransform(Save->PlayerTransform, GetHero()->GetActorTransform())
            || !SameTransform(Save->CarTransform, Car->GetActorTransform())
            || !SameTransform(Save->PlayerTransform, State->GetProgress()->PlayerTransform)
            || !SameTransform(Save->CarTransform, State->GetProgress()->CarTransform))
        {
            return false;
        }
    }
    return true;
}

bool UCityMissionCheckSubsystem::WriteCheckpoint() const
{
    const auto* Save = GetState()->GetProgress();
    const TArray<FString> Lines = {
        CheckpointSchema, FString::Printf(TEXT("%u"), FPlatformProcess::GetCurrentProcessId()),
        Save->PlayerTransform.ToString(), Save->CarTransform.ToString(), CompletedIds
    };
    return FFileHelper::SaveStringArrayToFile(Lines, *(EvidenceDirectory() / TEXT("Checkpoint.txt")));
}

bool UCityMissionCheckSubsystem::ReadCheckpoint()
{
    TArray<FString> Lines;
    if (!FFileHelper::LoadFileToStringArray(Lines, *(EvidenceDirectory() / TEXT("Checkpoint.txt")))
        || Lines.Num() != 5 || Lines[0] != CheckpointSchema || Lines[4] != CompletedIds || !Lines[1].IsNumeric())
    {
        return false;
    }
    const uint32 PreviousPid = static_cast<uint32>(FCString::Strtoui64(*Lines[1], nullptr, 10));
    return PreviousPid != 0 && PreviousPid != FPlatformProcess::GetCurrentProcessId()
        && ExpectedPlayer.InitFromString(Lines[2]) && ExpectedCar.InitFromString(Lines[3])
        && !ExpectedPlayer.ContainsNaN() && !ExpectedCar.ContainsNaN();
}

bool UCityMissionCheckSubsystem::VerifyRestoredProgress() const
{
    const auto* Save = GetState()->GetProgress();
    return IsComplete(Save) && Save->bHasPlayerTransform && Save->bHasCarTransform
        && SameTransform(ExpectedPlayer, Save->PlayerTransform) && SameTransform(ExpectedCar, Save->CarTransform)
        && SameTransform(ExpectedPlayer, GetHero()->GetActorTransform())
        && SameTransform(ExpectedCar, Car->GetActorTransform()) && VerifySavedProgress();
}

void UCityMissionCheckSubsystem::RunSave()
{
    if (!bInputSent && PhaseElapsed > 1)
    {
        SaveAttemptsBefore = GetState()->GetSaveAttemptCount();
        SavesBefore = GetState()->GetSuccessfulSaveCount();
        TapKey(EKeys::F5);
        bInputSent = true;
    }
    else if (bInputSent && PhaseElapsed > 1.6f)
    {
        const bool bSaved = GetState()->GetSaveAttemptCount() > SaveAttemptsBefore
            && GetState()->GetSuccessfulSaveCount() > SavesBefore && VerifySavedProgress();
        if (!bSaved)
        {
            Finish(false, TEXT("F5 or QA primary/backup verification failed"));
            return;
        }
        if (!bReload && !WriteCheckpoint())
        {
            Finish(false, TEXT("Could not record completion checkpoint for the new process reload"));
            return;
        }
        Finish(true, bReload ? TEXT("Reload, repeat E and F5 retained full completion and one reward")
            : TEXT("One full mission, repeat E and F5 verified; separate process reload is the next gate"));
    }
}
