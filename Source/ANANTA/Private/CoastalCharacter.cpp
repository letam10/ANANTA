#include "CoastalCharacter.h"

#include "Camera/CameraComponent.h"
#include "CoastalInteractable.h"
#include "CoastalVehicle.h"
#include "Components/CapsuleComponent.h"
#include "Components/TraversalComponent.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerInput.h"
#include "GameFramework/SpringArmComponent.h"
#include "UObject/ConstructorHelpers.h"

ACoastalCharacter::ACoastalCharacter()
{
    // Engine mapping được AddUnique, không sửa DefaultInput hay input của map gốc.
    UPlayerInput::AddEngineDefinedAxisMapping(FInputAxisKeyMapping(TEXT("CoastForward"), EKeys::W, 1));
    UPlayerInput::AddEngineDefinedAxisMapping(FInputAxisKeyMapping(TEXT("CoastForward"), EKeys::S, -1));
    UPlayerInput::AddEngineDefinedAxisMapping(FInputAxisKeyMapping(TEXT("CoastRight"), EKeys::D, 1));
    UPlayerInput::AddEngineDefinedAxisMapping(FInputAxisKeyMapping(TEXT("CoastRight"), EKeys::A, -1));
    UPlayerInput::AddEngineDefinedAxisMapping(FInputAxisKeyMapping(TEXT("CoastLookYaw"), EKeys::MouseX, 1));
    UPlayerInput::AddEngineDefinedAxisMapping(FInputAxisKeyMapping(TEXT("CoastLookPitch"), EKeys::MouseY, 1));
    CameraArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraArm"));
    CameraArm->SetupAttachment(RootComponent);
    CameraArm->TargetArmLength = 380;
    CameraArm->bUsePawnControlRotation = true;
    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(CameraArm);
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0, 540, 0);
    GetCharacterMovement()->JumpZVelocity = 560;
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> CharacterMesh(
        TEXT("/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple"));
    if (CharacterMesh.Succeeded())
    {
        GetMesh()->SetSkeletalMesh(CharacterMesh.Object);
        GetMesh()->SetRelativeLocation(FVector(0, 0, -90));
        GetMesh()->SetRelativeRotation(FRotator(0, -90, 0));
    }
    static ConstructorHelpers::FClassFinder<UAnimInstance> Animation(
        TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"));
    if (Animation.Succeeded())
    {
        GetMesh()->SetAnimInstanceClass(Animation.Class);
    }
}

void ACoastalCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis(TEXT("CoastForward"), this, &ACoastalCharacter::Forward);
    Input->BindAxis(TEXT("CoastRight"), this, &ACoastalCharacter::Right);
    // AxisConfig chỉ đặt độ nhạy; BindAxis cần mapping có tên riêng ở constructor.
    Input->BindAxis(TEXT("CoastLookYaw"), this, &ACoastalCharacter::LookYaw);
    Input->BindAxis(TEXT("CoastLookPitch"), this, &ACoastalCharacter::LookPitch);
    Input->BindKey(EKeys::SpaceBar, IE_Pressed, this, &ACharacter::Jump);
    Input->BindKey(EKeys::SpaceBar, IE_Released, this, &ACharacter::StopJumping);
    Input->BindKey(EKeys::LeftShift, IE_Pressed, this, &ACoastalCharacter::Sprint);
    Input->BindKey(EKeys::LeftShift, IE_Released, this, &ACoastalCharacter::Walk);
    Input->BindKey(EKeys::E, IE_Pressed, this, &ACoastalCharacter::Interact);
}

void ACoastalCharacter::Move(float ForwardValue, float RightValue)
{
    if (Controller)
    {
        const FRotator Heading(0, Controller->GetControlRotation().Yaw, 0);
        AddMovementInput(Heading.Vector(), ForwardValue);
        AddMovementInput(FRotationMatrix(Heading).GetUnitAxis(EAxis::Y), RightValue);
    }
}

void ACoastalCharacter::Forward(float Value) { Move(Value, 0); }
void ACoastalCharacter::Right(float Value) { Move(0, Value); }
void ACoastalCharacter::LookYaw(float Value) { AddControllerYawInput(Value); }
void ACoastalCharacter::LookPitch(float Value) { AddControllerPitchInput(-Value); }
void ACoastalCharacter::Sprint() { TraversalComponent->StartSprint(); }
void ACoastalCharacter::Walk() { TraversalComponent->StopSprint(); }

AActor* ACoastalCharacter::FindAction() const
{
    AActor* Closest = nullptr;
    float Distance = 320;
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        if (!It->IsA<ACoastalInteractable>() && !It->IsA<ACoastalVehicle>())
        {
            continue;
        }
        const ACoastalInteractable* Item = Cast<ACoastalInteractable>(*It);
        if (Item && Item->Kind == 3 && Item->bUsed)
        {
            continue;
        }
        // Tính cả độ cao để không chọn nhầm bảng thang máy ở tầng khác.
        const float Candidate = FVector::Dist(GetActorLocation(), It->GetActorLocation());
        if (Candidate < Distance)
        {
            FHitResult Hit;
            FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalInteraction), false, this);
            const FVector Start = GetActorLocation() + FVector(0, 0, 40);
            const FVector End = It->GetActorLocation() + FVector(0, 0, 100);
            const bool Blocked = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Query);
            if (!Blocked || Hit.GetActor() == *It)
            {
                Closest = *It;
                Distance = Candidate;
            }
        }
    }
    return Closest;
}

void ACoastalCharacter::Interact()
{
    AActor* Target = FindAction();
    if (ACoastalInteractable* Item = Cast<ACoastalInteractable>(Target))
    {
        if (Item->Kind == 4)
        {
            FCollisionQueryParams Query(SCENE_QUERY_STAT(CoastalElevator), false, this);
            Query.AddIgnoredActor(Item);
            if (GetWorld()->OverlapBlockingTestByChannel(Item->Destination, FQuat::Identity, ECC_Pawn,
                FCollisionShape::MakeCapsule(34, 90), Query))
            {
                Notify(TEXT("Elevator landing obstructed"));
                return;
            }
            SetActorLocation(Item->Destination);
        }
        Notify(Item->Use());
    }
    else if (ACoastalVehicle* Vehicle = Cast<ACoastalVehicle>(Target))
    {
        Vehicle->Board(this);
    }
}

void ACoastalCharacter::Notify(const FString& Message)
{
    StatusMessage = Message;
    StatusUntil = GetWorld()->GetTimeSeconds() + 6;
}

void ACoastalCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    // Mép biển giữ người ở bãi cát; thuyền có giới hạn riêng ngoài khơi.
    if (GetActorLocation().Z < -300)
    {
        SetActorLocation(FVector(0, -900, 320));
        Notify(TEXT("Returned to the coastal promenade"));
    }
}
