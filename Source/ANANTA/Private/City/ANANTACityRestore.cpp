#include "City/ANANTACityController.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"

FTransform AANANTACityController::GetSafePlayerTransform() const
{
    if (const auto* Car = DrivenVehicle.Get())
    {
        FVector Exit;
        if (Car->FindSafeExit(GetPawn(), Exit))
        {
            return FTransform(Car->GetActorRotation(), Exit);
        }
    }
    return LastOnFootTransform;
}

void AANANTACityController::RestorePlayer(const float DeltaTime)
{
    if (bRestoreComplete)
    {
        return;
    }
    auto* Hero = Cast<AANANTACityCharacter>(GetPawn());
    if (!Hero)
    {
        return;
    }
    if (!bRestoreRequested)
    {
        const auto* Save = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>()->GetProgress();
        LastOnFootTransform = Save->bHasPlayerTransform ? Save->PlayerTransform : Hero->GetActorTransform();
        bRestoreRequested = true;
        Hero->GetCharacterMovement()->DisableMovement();
        Hero->SetActorEnableCollision(false);
        Hero->SetActorTransform(LastOnFootTransform);
        SetControlRotation(FRotator(-12, LastOnFootTransform.Rotator().Yaw, 0));
    }
    RestoreElapsed += DeltaTime;
    // Doi collision cua cell tai vi tri luu truoc khi bat lai trong luc.
    if (RestoreElapsed < 1)
    {
        return;
    }
    FVector Location = Hero->GetActorLocation();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRestore), false, Hero);
    FHitResult Floor;
    const bool bFloor = GetWorld()->LineTraceSingleByChannel(Floor, Location + FVector(0, 0, 150),
        Location - FVector(0, 0, 1000), ECC_WorldStatic, Params);
    const float HalfHeight = Hero->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    if (bFloor && Floor.ImpactNormal.Z > 0.7f)
    {
        Location.Z = Floor.ImpactPoint.Z + HalfHeight + 3;
        const float Radius = Hero->GetCapsuleComponent()->GetScaledCapsuleRadius();
        const FCollisionShape Capsule = FCollisionShape::MakeCapsule(Radius, HalfHeight);
        if (!GetWorld()->OverlapBlockingTestByChannel(Location, FQuat::Identity, ECC_Pawn, Capsule, Params))
        {
            Hero->SetActorLocation(Location);
            Hero->SetActorEnableCollision(true);
            Hero->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
            LastOnFootTransform = Hero->GetActorTransform();
            bRestoreComplete = true;
            return;
        }
    }
    if (RestoreElapsed > 12)
    {
        Hero->SetActorLocationAndRotation(FVector(-25000, 1500, 120), FRotator(0, 90, 0));
        SetControlRotation(FRotator(-12, 90, 0));
    }
}

void AANANTACityController::RecoverPlayer()
{
    if (APawn* Hero = GetPawn())
    {
        Hero->SetActorLocationAndRotation(FVector(-25000, 1500, 120), FRotator(0, 90, 0));
        SetControlRotation(FRotator(-12, 90, 0));
        if (auto* HeroCharacter = Cast<ACharacter>(Hero))
        {
            HeroCharacter->GetCharacterMovement()->DisableMovement();
        }
        Hero->SetActorEnableCollision(false);
        bRestoreComplete = false;
        bRestoreRequested = true;
        RestoreElapsed = 0;
    }
}
