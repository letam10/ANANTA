#include "QA/CityServiceJourney.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACitySubsystem.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformProcess.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"

namespace
{
    const FString CheckpointSchema = TEXT("ANANTA_CITY_SERVICE_CHECKPOINT_V1");
    const FString CompletedServices = TEXT("NotStarted|8|Market_Supplies|1");

    bool SameTransform(const FTransform& A, const FTransform& B)
    {
        return A.GetLocation().Equals(B.GetLocation(), 10)
            && A.GetRotation().AngularDistance(B.GetRotation()) <= FMath::DegreesToRadians(0.5)
            && A.GetScale3D().Equals(B.GetScale3D(), 0.001);
    }
}

bool UCityServiceJourney::VerifySavedProgress() const
{
    const auto* State = GetState();
    const auto* Hero = GetHero();
    if (!State || !State->IsUsingQASlot() || State->GetSaveSlotName() != TEXT("ANANTA_City_QA")
        || !Hero || !Hero->GetCharacterMovement()->IsMovingOnGround()
        || !Hero->GetActorEnableCollision() || Hero->GetAttachParentActor() || Hero->IsHidden()
        || Hero->GetVelocity().Size() > 1 || !MatchesProgress(State->GetProgress(), 8))
    {
        return false;
    }
    // Chi doc save thanh doi tuong rieng; khong goi LoadProgress hay thay doi trang thai dang choi.
    for (const FString& Slot : { FString(TEXT("ANANTA_City_QA")), FString(TEXT("ANANTA_City_QA_Backup")) })
    {
        const auto* Save = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromSlot(Slot, 0));
        if (!MatchesProgress(Save, 8) || !Save->bHasPlayerTransform
            || !SameTransform(Save->PlayerTransform, Hero->GetActorTransform())
            || !SameTransform(Save->PlayerTransform, State->GetProgress()->PlayerTransform))
        {
            return false;
        }
    }
    return true;
}

bool UCityServiceJourney::WriteCheckpoint() const
{
    const auto* Save = GetState()->GetProgress();
    const TArray<FString> Lines = {
        CheckpointSchema, FString::Printf(TEXT("%u"), FPlatformProcess::GetCurrentProcessId()),
        Save->PlayerTransform.ToString(), CompletedServices
    };
    return FFileHelper::SaveStringArrayToFile(Lines, *(EvidenceDirectory() / TEXT("Checkpoint.txt")));
}

bool UCityServiceJourney::ReadCheckpoint()
{
    TArray<FString> Lines;
    if (!FFileHelper::LoadFileToStringArray(Lines, *(EvidenceDirectory() / TEXT("Checkpoint.txt")))
        || Lines.Num() != 4 || Lines[0] != CheckpointSchema || Lines[3] != CompletedServices
        || !Lines[1].IsNumeric())
    {
        return false;
    }
    const uint32 PreviousPid = static_cast<uint32>(FCString::Strtoui64(*Lines[1], nullptr, 10));
    return PreviousPid != 0 && PreviousPid != FPlatformProcess::GetCurrentProcessId()
        && ExpectedPlayer.InitFromString(Lines[2]) && !ExpectedPlayer.ContainsNaN();
}

bool UCityServiceJourney::VerifyRestoredProgress() const
{
    const auto* Save = GetState()->GetProgress();
    return MatchesProgress(Save, 8) && Save->bHasPlayerTransform
        && SameTransform(ExpectedPlayer, Save->PlayerTransform)
        && SameTransform(ExpectedPlayer, GetHero()->GetActorTransform()) && VerifySavedProgress();
}

void UCityServiceJourney::RunSave()
{
    if (!bInputSent && PhaseElapsed >= 1)
    {
        SaveAttemptsBefore = GetState()->GetSaveAttemptCount();
        SavesBefore = GetState()->GetSuccessfulSaveCount();
        TapKey(EKeys::F5);
        bInputSent = true;
    }
    else if (bInputSent && PhaseElapsed >= 1.6)
    {
        const bool bSaved = GetState()->GetSaveAttemptCount() > SaveAttemptsBefore
            && GetState()->GetSuccessfulSaveCount() > SavesBefore && VerifySavedProgress();
        if (!bSaved)
        {
            Finish(false, TEXT("F5 or primary/backup service save verification failed"));
            return;
        }
        if (!WriteCheckpoint())
        {
            Finish(false, TEXT("Could not write verified service checkpoint"));
            return;
        }
        Finish(true, TEXT("Eight services, repeat Market E and F5 verified; separate reload gate remains"));
    }
}
