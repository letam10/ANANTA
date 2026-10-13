#include "CoastalHUD.h"

#include "CoastalCharacter.h"
#include "CoastalInteractable.h"
#include "CoastalVehicle.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"

void ACoastalHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !PlayerOwner)
    {
        return;
    }
    DrawRect(FLinearColor(0.025f, 0.045f, 0.06f, 0.8f), 20, 20, 630, 91);
    DrawText(TEXT("NOVA COAST | Coastal City"), FLinearColor(0.65f, 0.9f, 0.95f), 34, 30);
    DrawText(TEXT("WASD move | Mouse look | Shift run | Space jump | E interact"),
        FLinearColor::White, 34, 59);
    if (ACoastalVehicle* Vehicle = Cast<ACoastalVehicle>(PlayerOwner->GetPawn()))
    {
        DrawText(FString::Printf(TEXT("%s | %.0f km/h | E park and exit"),
            *Vehicle->VehicleName, FMath::Abs(Vehicle->GetSpeed()) * 0.036f),
            FLinearColor::White, 34, 83);
        return;
    }
    ACoastalCharacter* Character = Cast<ACoastalCharacter>(PlayerOwner->GetPawn());
    if (!Character)
    {
        return;
    }
    const double Time = GetWorld()->GetTimeSeconds();
    if (Time > NextQuery)
    {
        Prompt.Empty();
        if (ACoastalInteractable* Item = Cast<ACoastalInteractable>(Character->FindAction()))
        {
            Prompt = TEXT("E: ") + Item->ActionName;
        }
        else if (ACoastalVehicle* Vehicle = Cast<ACoastalVehicle>(Character->FindAction()))
        {
            Prompt = TEXT("E: Board ") + Vehicle->VehicleName;
        }
        NextQuery = Time + 0.2;
    }
    DrawText(Prompt, FLinearColor(1, 0.85f, 0.5f), 34, 83);
    if (Time < Character->StatusUntil)
    {
        DrawRect(FLinearColor(0.02f, 0.035f, 0.045f, 0.85f), 20, Canvas->SizeY - 90, 850, 55);
        DrawText(Character->StatusMessage, FLinearColor::White, 35, Canvas->SizeY - 70);
    }
}
