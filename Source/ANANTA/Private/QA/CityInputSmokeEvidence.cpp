#include "QA/CityInputSmokeSubsystem.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

const TCHAR* UCityInputSmokeSubsystem::PhaseName() const
{
    static const TCHAR* Names[] = {
        TEXT("WaitReady"), TEXT("WalkToGiver"), TEXT("StartMission"), TEXT("LeaveCafe"),
        TEXT("WalkToCar"), TEXT("EnterCar"), TEXT("Drive"), TEXT("Brake"), TEXT("ExitCar"),
        TEXT("Save"), TEXT("Done")
    };
    return Names[static_cast<uint8>(Phase)];
}

float UCityInputSmokeSubsystem::PhaseTimeout() const
{
    switch (Phase)
    {
    case ECityInputSmokePhase::WaitReady:
        return 30;
    case ECityInputSmokePhase::WalkToGiver:
        return 15;
    case ECityInputSmokePhase::LeaveCafe:
        return 25;
    case ECityInputSmokePhase::WalkToCar:
        return 12;
    case ECityInputSmokePhase::Drive:
        return 10;
    default:
        return 5;
    }
}

bool UCityInputSmokeSubsystem::CheckCamera(const bool bVehicle) const
{
    const AANANTACityCharacter* Hero = GetHero();
    if (!Hero || !Controller.IsValid() || (bVehicle && !Car.IsValid()))
    {
        return false;
    }
    const UCameraComponent* Camera = bVehicle ? Car->Camera.Get() : Hero->Camera.Get();
    const USpringArmComponent* Arm = bVehicle ? Car->CameraArm.Get() : Hero->CameraArm.Get();
    if (!Camera || !Arm || Camera->GetAttachParent() != Arm
        || Camera->GetAttachSocketName() != USpringArmComponent::SocketName)
    {
        return false;
    }
    FVector ViewLocation;
    FRotator ViewRotation;
    Controller->GetPlayerViewPoint(ViewLocation, ViewRotation);
    const FVector Subject = bVehicle ? Car->GetActorLocation() : Hero->GetActorLocation();
    const float MinimumSeparation = bVehicle ? 300.f : 160.f;
    return FVector::Dist(ViewLocation, Subject) > MinimumSeparation
        && FVector::Dist(Camera->GetComponentLocation(), Subject) > MinimumSeparation;
}

bool UCityInputSmokeSubsystem::CheckSafeExit() const
{
    const AANANTACityCharacter* Hero = GetHero();
    if (!Hero || Hero->IsHidden() || !Hero->GetActorEnableCollision() || Hero->GetAttachParentActor()
        || !Hero->GetCharacterMovement()->IsMovingOnGround())
    {
        return false;
    }
    const auto* Capsule = Hero->GetCapsuleComponent();
    const float HalfHeight = Capsule->GetScaledCapsuleHalfHeight();
    const float Radius = Capsule->GetScaledCapsuleRadius();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CitySmokeExit), false, Hero);
    if (GetWorld()->OverlapBlockingTestByChannel(Hero->GetActorLocation(), FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(Radius - 1, HalfHeight - 1), Params))
    {
        return false;
    }
    FHitResult Ground;
    const FVector Start = Hero->GetActorLocation();
    return GetWorld()->LineTraceSingleByChannel(Ground, Start, Start - FVector(0, 0, HalfHeight + 30),
        ECC_WorldStatic, Params) && Ground.ImpactNormal.Z > 0.7f
        && FMath::Abs(Start.Z - HalfHeight - Ground.ImpactPoint.Z) < 15;
}

bool UCityInputSmokeSubsystem::VerifySavedProgress() const
{
    const auto* State = GetState();
    if (!State || !State->IsUsingQASlot() || State->GetSaveSlotName() != TEXT("ANANTA_City_QA"))
    {
        return false;
    }
    const auto* Save = Cast<UANANTACitySave>(UGameplayStatics::LoadGameFromSlot(State->GetSaveSlotName(), 0));
    return Save && Save->IsValidSave() && Save->Mission.Stage == ECityMissionStage::Investigating
        && Save->LegacyFragments.IsEmpty() && Save->bHasPlayerTransform && Save->bHasCarTransform
        && Save->PlayerTransform.GetLocation().Equals(GetHero()->GetActorLocation(), 10)
        && Save->CarTransform.GetLocation().Equals(Car->GetActorLocation(), 10);
}

void UCityInputSmokeSubsystem::NextPhase(const ECityInputSmokePhase Next, const FString& Detail)
{
    Observe(true, Detail);
    ReleaseKeys();
    Phase = Next;
    PhaseStartTime = Now;
    PhaseElapsed = 0;
    bInputSent = false;
    WriteReport(false, false);
}

void UCityInputSmokeSubsystem::Observe(const bool bPass, const FString& Detail)
{
    FVector ViewLocation = FVector::ZeroVector;
    FRotator ViewRotation = FRotator::ZeroRotator;
    if (Controller.IsValid())
    {
        Controller->GetPlayerViewPoint(ViewLocation, ViewRotation);
    }
    const auto* Hero = GetHero();
    const FString HeroTransform = Hero ? Hero->GetActorTransform().ToString() : TEXT("missing");
    const FString CarTransform = Car.IsValid() ? Car->GetActorTransform().ToString() : TEXT("missing");
    const int32 MissionStage = GetState() ? static_cast<int32>(GetState()->GetMissionStage()) : -1;
    FString Entry = FString::Printf(TEXT("phase=%s result=%s elapsed=%.3f detail=%s\n"),
        PhaseName(), bPass ? TEXT("PASS") : TEXT("FAIL"), Now - StartTime, *Detail);
    Entry += FString::Printf(TEXT("player_transform=%s\ncar_transform=%s\n"), *HeroTransform, *CarTransform);
    Entry += FString::Printf(TEXT("camera_location=%s camera_rotation=%s mission_stage=%d\n"),
        *ViewLocation.ToString(), *ViewRotation.ToString(), MissionStage);
    Entry += FString::Printf(TEXT("player_camera_distance_cm=%.3f car_camera_distance_cm=%.3f speed_kmh=%.3f\n"),
        Hero ? FVector::Dist(ViewLocation, Hero->GetActorLocation()) : -1,
        Car.IsValid() ? FVector::Dist(ViewLocation, Car->GetActorLocation()) : -1,
        Car.IsValid() ? Car->GetSpeedKmh() : -1);
    Observations.Add(Entry);
    UE_LOG(LogTemp, Display, TEXT("CITY_INPUT_SMOKE %s"), *Entry);
}

bool UCityInputSmokeSubsystem::WriteReport(const bool bComplete, const bool bPass) const
{
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CityInputSmoke");
    IFileManager::Get().MakeDirectory(*Directory, true);
    FString Report = TEXT("ANANTA city focused input smoke\ninput_source=engine-injected PlayerController.InputKey\n");
    Report += TEXT("controller_facing_set=true\nteleport=false\nmission_mutation=false\ngod_mode=false\n");
    Report += TEXT("save_slot=ANANTA_City_QA\nnormal_save_io=false\nmaximum_duration_seconds=120\n");
    Report += TEXT("scope=Giver interaction and short vehicle path; not full mission or desktop keyboard acceptance\n");
    Report += FString::Printf(TEXT("status=%s\nheld_keys_after_cleanup=%d\n\n"),
        bComplete ? (bPass ? TEXT("PASSED") : TEXT("FAILED")) : TEXT("RUNNING"), HeldKeys.Num());
    for (const FString& Entry : Observations)
    {
        Report += Entry + TEXT("\n");
    }
    return FFileHelper::SaveStringToFile(Report, *(Directory / TEXT("Report.txt")));
}

void UCityInputSmokeSubsystem::Finish(const bool bPass, const FString& Detail)
{
    Observe(bPass, Detail);
    ReleaseKeys();
    bFinished = true;
    bPassed = bPass;
    if (!WriteReport(true, bPassed))
    {
        bPassed = false;
        UE_LOG(LogTemp, Error, TEXT("CITY_INPUT_SMOKE evidence could not be written"));
    }
    UE_LOG(LogTemp, Display, TEXT("CITY_INPUT_SMOKE_FINISH success=%d"), bPassed);
}
