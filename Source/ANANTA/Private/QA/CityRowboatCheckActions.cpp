#include "QA/CityRowboatCheck.h"

#include "City/ANANTACityController.h"
#include "City/Mobility/CityRowboat.h"
#include "GameFramework/Character.h"
#include "HAL/PlatformTime.h"
#include "InputKeyEventArgs.h"

void UCityRowboatCheck::SetKey(const FKey& Key, const bool bDown)
{
    if (!Controller.IsValid() || HeldKeys.Contains(Key) == bDown)
    {
        return;
    }
    Controller->InputKey(FInputKeyEventArgs(nullptr, INPUTDEVICEID_NONE, Key,
        bDown ? IE_Pressed : IE_Released, bDown ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
    if (bDown)
    {
        HeldKeys.Add(Key);
    }
    else
    {
        HeldKeys.Remove(Key);
    }
}

void UCityRowboatCheck::ReleaseKeys()
{
    for (const FKey& Key : HeldKeys.Array())
    {
        SetKey(Key, false);
    }
    HeldKeys.Empty();
}

void UCityRowboatCheck::RunPhase()
{
    switch (Phase)
    {
    case ECityRowboatPhase::Settle:
    {
        if (PhaseSeconds < 0.5)
        {
            return;
        }
        bool bClear = false;
        bool bDry = false;
        if (!CheckDryDock(bClear, bDry))
        {
            Finish(false, TEXT("Hero did not settle naturally on the authored timber dock"));
            return;
        }
        BoardPrompt = Controller->GetInteractionPrompt();
        if (Controller->FindInteractionTarget() != Boat.Get() || BoardPrompt != TEXT("E: row boat"))
        {
            Finish(false, TEXT("Authored rowboat is not the normal visible E interaction target"));
            return;
        }
        Advance(ECityRowboatPhase::Board, TEXT("Unmodified capsule settled on real timber dock with boat prompt"));
        SetKey(EKeys::E, true);
        break;
    }
    case ECityRowboatPhase::Board:
        // Giu E qua nhieu frame de input binding xu ly; chi do W sau khi da len thuyen.
        if (PhaseSeconds >= 0.15)
        {
            SetKey(EKeys::E, false);
        }
        if (PhaseSeconds >= 0.5)
        {
            bBoard = IsBoarded();
            if (!bBoard)
            {
                Finish(false, TEXT("E did not occupy boat and hide/attach the original hero"));
                return;
            }
            RowOrigin = Boat->GetActorLocation();
            PreviousBoatPosition = RowOrigin;
            Advance(ECityRowboatPhase::Row, TEXT("E boarded through the normal controller binding"));
            SetKey(EKeys::W, true);
        }
        break;
    case ECityRowboatPhase::Row:
        bRowInput |= Controller->IsInputKeyDown(EKeys::W);
        if (PhaseSeconds >= 1)
        {
            RowSeconds = PhaseSeconds;
            BrakeStartSpeedKmh = Boat->GetSpeedKmh();
            if (!bRowInput || MeasuredTravelCm <= 20 || RowDisplacementCm <= 20 || BrakeStartSpeedKmh <= 0.05)
            {
                Finish(false, TEXT("Held W did not produce more than 20 cm of real rowboat displacement"));
                return;
            }
            Advance(ECityRowboatPhase::Brake, TEXT("Held W for about one game second with measured travel"));
            SetKey(EKeys::SpaceBar, true);
        }
        break;
    case ECityRowboatPhase::Brake:
        bBrakeInput |= Controller->IsInputKeyDown(EKeys::SpaceBar) && !Controller->IsInputKeyDown(EKeys::W);
        if (PhaseSeconds >= 0.2 && Boat->GetSpeedKmh() <= 0.05f)
        {
            StoppedSpeedKmh = Boat->GetSpeedKmh();
            bBrake = bBrakeInput && StoppedSpeedKmh < BrakeStartSpeedKmh;
            AlightPrompt = Controller->GetInteractionPrompt();
            if (!bBrake || AlightPrompt != TEXT("E: leave boat"))
            {
                Finish(false, TEXT("Space braking or stopped-boat exit prompt was not observed"));
                return;
            }
            Advance(ECityRowboatPhase::Alight, TEXT("Released W and held Space until observed speed reached zero"));
            SetKey(EKeys::E, true);
        }
        break;
    case ECityRowboatPhase::Alight:
        if (PhaseSeconds >= 0.15)
        {
            SetKey(EKeys::E, false);
        }
        if (PhaseSeconds >= 0.6)
        {
            bAlight = !Boat->bOccupied && !Controller->GetDrivenVehicle()
                && CheckDryDock(bCapsuleClear, bDryFloor);
            if (!bAlight)
            {
                Finish(false, TEXT("E did not restore visible walking hero with clear capsule on timber dock"));
                return;
            }
            Advance(ECityRowboatPhase::OpenSea, TEXT("E alighted onto dry authored dock with no capsule overlap"));
        }
        break;
    case ECityRowboatPhase::OpenSea:
        // Setup rieng sau luot gameplay: chi doi thuyen, giu hero tren ben va dong bang so do.
        if (!bOpenSeaSetup)
        {
            const FVector Destination(150000, -130000, -120);
            Boat->SetActorLocation(Destination, false, nullptr, ETeleportType::TeleportPhysics);
            bOpenSeaSetup = Boat->GetActorLocation().Equals(Destination, 2);
            if (!bOpenSeaSetup)
            {
                Finish(false, TEXT("Separate open-sea boat setup relocation failed"));
                return;
            }
            PhaseSeconds = 0;
            UE_LOG(LogTemp, Display, TEXT("CITY_ROWBOAT_OPEN_SEA_SETUP relocation excluded from measuredTravelCm"));
            return;
        }
        if (PhaseSeconds >= 0.3)
        {
            FVector Exit;
            bOpenSeaExitRejected = !Boat->FindSafeExit(Hero(), Exit);
            bool bClear = false;
            bool bDry = false;
            const bool bHeroStillOnDock = CheckDryDock(bClear, bDry);
            Finish(bOpenSeaExitRejected && bHeroStillOnDock,
                bOpenSeaExitRejected && bHeroStillOnDock
                    ? TEXT("Real E/W/Space/E dock journey passed; separate open-sea FindSafeExit rejected")
                    : TEXT("Separate open-sea exit was accepted or dock hero changed during setup"));
        }
        break;
    default:
        break;
    }
}
