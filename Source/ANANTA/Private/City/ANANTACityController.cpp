#include "City/ANANTACityController.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityInteractable.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CombatComponent.h"
#include "Components/TraversalComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputCoreTypes.h"

void AANANTACityController::BeginPlay()
{
    Super::BeginPlay();
    SetInputMode(FInputModeGameOnly());
    bShowMouseCursor = false;
    if (PlayerCameraManager)
    {
        PlayerCameraManager->ViewPitchMin = -65;
        PlayerCameraManager->ViewPitchMax = 65;
    }
}

void AANANTACityController::SetupInputComponent()
{
    Super::SetupInputComponent();
    InputComponent->BindKey(EKeys::E, IE_Pressed, this, &AANANTACityController::Interact);
    InputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this, &AANANTACityController::JumpPressed);
    InputComponent->BindKey(EKeys::SpaceBar, IE_Released, this, &AANANTACityController::JumpReleased);
    InputComponent->BindKey(EKeys::F, IE_Pressed, this, &AANANTACityController::Mantle);
    InputComponent->BindKey(EKeys::LeftMouseButton, IE_Pressed, this, &AANANTACityController::Attack);
    InputComponent->BindKey(EKeys::F5, IE_Pressed, this, &AANANTACityController::SaveNow);
    auto& PauseBinding = InputComponent->BindKey(EKeys::Escape, IE_Pressed,
        this, &AANANTACityController::TogglePause);
    PauseBinding.bExecuteWhenPaused = true;
}

void AANANTACityController::PlayerTick(const float DeltaTime)
{
    Super::PlayerTick(DeltaTime);
    if (IsPaused())
    {
        return;
    }
    auto* Hero = Cast<AANANTACityCharacter>(GetPawn());
    if (!Hero)
    {
        return;
    }
    RestorePlayer(DeltaTime);
    if (!bRestoreComplete)
    {
        return;
    }
    float MouseX = 0;
    float MouseY = 0;
    GetInputMouseDelta(MouseX, MouseY);
    AddYawInput(MouseX * 0.8f);
    AddPitchInput(-MouseY * 0.8f);
    const float Forward = float(IsInputKeyDown(EKeys::W)) - float(IsInputKeyDown(EKeys::S));
    const float Right = float(IsInputKeyDown(EKeys::D)) - float(IsInputKeyDown(EKeys::A));
    if (AANANTACityVehicle* Car = DrivenVehicle.Get())
    {
        Car->Drive(Forward, Right, IsInputKeyDown(EKeys::SpaceBar), DeltaTime);
        Car->CameraArm->SetWorldRotation(GetControlRotation());
    }
    else
    {
        const FRotator Direction(0, GetControlRotation().Yaw, 0);
        Hero->AddMovementInput(Direction.Vector(), Forward);
        Hero->AddMovementInput(FRotationMatrix(Direction).GetUnitAxis(EAxis::Y), Right);
        if (IsInputKeyDown(EKeys::LeftShift))
        {
            Hero->TraversalComponent->StartSprint();
        }
        else
        {
            Hero->TraversalComponent->StopSprint();
        }
        if (Hero->GetCharacterMovement()->IsMovingOnGround())
        {
            LastOnFootTransform = Hero->GetActorTransform();
        }
        if (Hero->GetActorLocation().Z < -600)
        {
            RecoverPlayer();
        }
        if (GetWorld()->GetTimeSeconds() - Hero->LastDamageTime > 8)
        {
            Hero->Health = FMath::Min(100.f, Hero->Health + DeltaTime * 6);
        }
    }
    AutoSaveElapsed += DeltaTime;
    if (AutoSaveElapsed >= 20)
    {
        AutoSaveElapsed = 0;
        SaveNow();
    }
}

AActor* AANANTACityController::FindInteractionTarget() const
{
    const APawn* Hero = GetPawn();
    if (!Hero || !bRestoreComplete)
    {
        return nullptr;
    }
    AActor* Best = nullptr;
    double BestDistance = 320 * 320;
    const auto Consider = [&](AActor* Actor)
    {
        const double Distance = FVector::DistSquared(Hero->GetActorLocation(), Actor->GetActorLocation());
        if (Distance >= BestDistance)
        {
            return;
        }
        FHitResult Hit;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(CityInteract), false, Hero);
        Params.AddIgnoredActor(Actor);
        const FVector Start = Hero->GetActorLocation() + FVector(0, 0, 40);
        const FVector End = Actor->GetActorLocation() + FVector(0, 0, 40);
        if (!GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
        {
            Best = Actor;
            BestDistance = Distance;
        }
    };
    for (TActorIterator<AANANTACityInteractable> It(GetWorld()); It; ++It)
    {
        if (It->IsAvailable())
        {
            Consider(*It);
        }
    }
    for (TActorIterator<AANANTACityVehicle> It(GetWorld()); It; ++It)
    {
        if (!It->bOccupied && It->IsRestoreComplete())
        {
            Consider(*It);
        }
    }
    return Best;
}

FString AANANTACityController::GetInteractionPrompt() const
{
    if (!bRestoreComplete)
    {
        return TEXT("Loading nearby streets...");
    }
    if (DrivenVehicle.IsValid())
    {
        return DrivenVehicle->GetSpeedKmh() > 2 ? TEXT("Space: brake before exiting") : TEXT("E: leave car");
    }
    if (auto* Target = Cast<AANANTACityInteractable>(FindInteractionTarget()))
    {
        return Target->GetPrompt();
    }
    return FindInteractionTarget() ? TEXT("E: drive car") : TEXT("");
}

void AANANTACityController::Interact()
{
    auto* Hero = Cast<AANANTACityCharacter>(GetPawn());
    if (!Hero || !bRestoreComplete || IsPaused())
    {
        return;
    }
    if (AANANTACityVehicle* Car = DrivenVehicle.Get())
    {
        FVector Exit;
        if (Car->GetSpeedKmh() > 2 || !Car->FindSafeExit(Hero, Exit))
        {
            return;
        }
        Hero->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
        Hero->SetActorLocation(Exit);
        Hero->SetActorHiddenInGame(false);
        Hero->SetActorEnableCollision(true);
        Hero->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
        Car->bOccupied = false;
        DrivenVehicle.Reset();
        LastOnFootTransform = Hero->GetActorTransform();
        SetViewTargetWithBlend(Hero, 0.25f);
        SaveNow();
        return;
    }
    AActor* Target = FindInteractionTarget();
    if (auto* Car = Cast<AANANTACityVehicle>(Target))
    {
        LastOnFootTransform = Hero->GetActorTransform();
        DrivenVehicle = Car;
        Car->bOccupied = true;
        Hero->GetCharacterMovement()->DisableMovement();
        Hero->SetActorEnableCollision(false);
        Hero->SetActorHiddenInGame(true);
        Hero->AttachToActor(Car, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
        SetViewTargetWithBlend(Car, 0.35f);
        SaveNow();
    }
    else if (auto* Item = Cast<AANANTACityInteractable>(Target))
    {
        Item->Interact(Hero);
    }
}

void AANANTACityController::JumpPressed()
{
    if (auto* Hero = Cast<AANANTACityCharacter>(GetPawn()); Hero && !DrivenVehicle.IsValid())
    {
        Hero->Jump();
    }
}

void AANANTACityController::JumpReleased()
{
    if (auto* Hero = Cast<ACharacter>(GetPawn()))
    {
        Hero->StopJumping();
    }
}

void AANANTACityController::Mantle()
{
    if (auto* Hero = Cast<AANANTACityCharacter>(GetPawn()); Hero && !DrivenVehicle.IsValid())
    {
        Hero->TraversalComponent->TryMantle();
    }
}

void AANANTACityController::Attack()
{
    if (auto* Hero = Cast<AANANTACityCharacter>(GetPawn()); Hero && !DrivenVehicle.IsValid())
    {
        Hero->SetActorRotation(FRotator(0, GetControlRotation().Yaw, 0));
        Hero->CombatComponent->TryAttack();
    }
}

void AANANTACityController::TogglePause()
{
    if (!IsPaused())
    {
        SaveNow();
    }
    SetPause(!IsPaused());
}

void AANANTACityController::SaveNow()
{
    if (GetGameInstance())
    {
        if (auto* State = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>())
        {
            State->SaveProgress();
        }
    }
}

void AANANTACityController::EndPlay(const EEndPlayReason::Type Reason)
{
    SaveNow();
    Super::EndPlay(Reason);
}
