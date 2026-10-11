#include "QA/CityRoofPoolCheck.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"

void UCityRoofPoolCheck::SetForward(const bool bDown)
{
    if (!Controller.IsValid() || bForward == bDown)
    {
        return;
    }
    Controller->InputKey(FInputKeyEventArgs(nullptr, INPUTDEVICEID_NONE, EKeys::W,
        bDown ? IE_Pressed : IE_Released, bDown ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
    bForward = bDown;
}

void UCityRoofPoolCheck::MoveToward(const FVector& Target)
{
    const FVector Position = Hero()->GetActorLocation();
    const FVector Direction(Target.X - Position.X, Target.Y - Position.Y, 0);
    Controller->SetControlRotation(FRotator(-12, Direction.Rotation().Yaw, 0));
    SetForward(true);
    const double Now = FPlatformTime::Seconds();
    if (FVector::Dist2D(Position, ProgressOrigin) >= 30)
    {
        ProgressOrigin = Position;
        ProgressAt = Now;
    }
    if (Now - ProgressAt > 4)
    {
        FHitResult Hit;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(CityRoofPoolBlocker), false, Hero());
        const FCollisionResponseParams Responses(Hero()->GetCapsuleComponent()->GetCollisionResponseToChannels());
        GetWorld()->SweepSingleByChannel(Hit, Position, Position + Direction.GetSafeNormal() * 100,
            FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(38.f, 92.f), Params, Responses);
        Blocker = GetNameSafe(Hit.GetActor());
        Finish(false, TEXT("W input made less than 30 cm progress for four seconds"));
    }
}

void UCityRoofPoolCheck::RunPhase()
{
    const FVector Position = Hero()->GetActorLocation();
    switch (Phase)
    {
    case ECityRoofPoolPhase::Ascent:
        if (Position.Y >= 199800)
        {
            if (Ascent.End.Y - Ascent.Start.Y < 4100 || FMath::Abs(FloorZ - 840) > 3
                || Ascent.Steps.Num() != 41 || Ascent.InputSamples < 41)
            {
                Finish(false, TEXT("Ascent lacks 4100 cm travel, 41 sampled treads or rooftop floor height"));
                return;
            }
            StairTop = Position;
            Advance(ECityRoofPoolPhase::Landing, TEXT("W traversed all 41 authored treads to roof height"));
        }
        else
        {
            MoveToward(FVector(98350, 200000, 0));
        }
        break;
    case ECityRoofPoolPhase::Landing:
        if (FMath::Abs(FloorZ - 840) > 3 || FMath::Abs(Position.Y - 199800) > 200)
        {
            Finish(false, TEXT("Landing crossing left supported roof elevation or landing corridor"));
        }
        else if (Position.X >= 98800)
        {
            Advance(ECityRoofPoolPhase::Roof, TEXT("W crossed landing onto roof beyond X=98800"));
        }
        else
        {
            MoveToward(FVector(99100, Position.Y, 0));
        }
        break;
    case ECityRoofPoolPhase::Roof:
        SetForward(false);
        if (FMath::Abs(FloorZ - 840) > 3 || Position.X < 98800)
        {
            Finish(false, TEXT("Character did not remain on authored roof deck"));
            return;
        }
        ++RoofSamples;
        RoofZ = FloorZ;
        if (PhaseSeconds >= 1 && Hero()->GetVelocity().Size2D() <= 1)
        {
            bRoof = RoofSamples >= 2 && LandingInputSamples >= 2;
            Advance(ECityRoofPoolPhase::ReturnLanding, TEXT("Full capsule stood clear on Z=840 roof for one second"));
        }
        break;
    case ECityRoofPoolPhase::ReturnLanding:
        if (FMath::Abs(FloorZ - 840) > 3 || FMath::Abs(Position.Y - 199800) > 200)
        {
            Finish(false, TEXT("Return landing crossing lost supported roof or landing corridor"));
        }
        else if (FVector::Dist2D(Position, StairTop) <= 18)
        {
            Advance(ECityRoofPoolPhase::Descent, TEXT("W returned across landing to stair head"));
        }
        else
        {
            MoveToward(StairTop);
        }
        break;
    case ECityRoofPoolPhase::Descent:
        if (Position.Y <= 195600)
        {
            if (Descent.Start.Y - Descent.End.Y < 4100 || FMath::Abs(FloorZ - 20) > 3
                || Descent.Steps.Num() != 41 || Descent.InputSamples < 41)
            {
                Finish(false, TEXT("Descent lacks 4100 cm travel, 41 sampled treads or courtyard floor"));
                return;
            }
            Advance(ECityRoofPoolPhase::Ground, TEXT("W descended every tread and returned to courtyard"));
        }
        else
        {
            MoveToward(FVector(98350, 195400, 0));
        }
        break;
    case ECityRoofPoolPhase::Ground:
        SetForward(false);
        if (FMath::Abs(FloorZ - 20) > 3 || FMath::Abs(Position.X - 98350) > 180)
        {
            Finish(false, TEXT("Character did not remain safely on courtyard after descent"));
        }
        else if (PhaseSeconds >= 1 && Hero()->GetVelocity().Size2D() <= 1)
        {
            bReturned = true;
            Finish(true, TEXT("Actual-map W ascent, roof landing and descent verified with normal capsule"));
        }
        break;
    default:
        break;
    }
}
