#include "City/ANANTACityHUD.h"

#include "City/ANANTACityCharacter.h"
#include "City/ANANTACityController.h"
#include "City/ANANTACitySubsystem.h"
#include "City/ANANTACityVehicle.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
#include "Settings/CityText.h"

void AANANTACityHUD::DrawHUD()
{
    Super::DrawHUD();
    auto* PC = Cast<AANANTACityController>(PlayerOwner);
    auto* Player = PC ? Cast<AANANTACityCharacter>(PC->GetPawn()) : nullptr;
    if (!Canvas || !Player)
    {
        return;
    }
    const auto* State = GetGameInstance()->GetSubsystem<UANANTACitySubsystem>();
    const float Scale = FMath::Clamp(Canvas->ClipY / 1080.f, 0.7f, 2.f);
    const float Left = 32 * Scale;
    DrawRect(FLinearColor(0.015f, 0.025f, 0.05f, 0.88f), Left - 12, 25 * Scale, 630 * Scale, 132 * Scale);
    DrawText(CityTranslate(TEXT("ANANTA  |  ANOMALY CASE")), FLinearColor(0.3f, 0.85f, 1), Left, 36 * Scale,
        nullptr, 1.6f * Scale);
    DrawText(CityTranslate(State->GetObjectiveText()), FLinearColor::White, Left, 72 * Scale, nullptr, 1.35f * Scale);

    FVector Goal(-25000, 2400, 110);
    FString Destination(TEXT("Cafe contact"));
    const auto& Mission = State->GetMission();
    if (Mission.Stage == ECityMissionStage::Investigating)
    {
        const FVector Clues[] = { FVector(-12000, 1800, 100), FVector(1000, 1800, 100), FVector(24500, 2400, 100) };
        for (int32 Index = 0; Index < 3; ++Index)
        {
            if (!Mission.Clues.Contains(FName(*FString::Printf(TEXT("Clue_%02d"), Index + 1))))
            {
                Goal = Clues[Index];
                Destination = FString::Printf(TEXT("%s %d"), *CityText(TEXT("Trace"), TEXT("Dấu vết")), Index + 1);
                break;
            }
        }
    }
    else if (Mission.Stage == ECityMissionStage::Combat)
    {
        Goal = FVector(26000, 4500, 100);
        Destination = TEXT("Anomaly site");
    }
    if (Mission.Stage != ECityMissionStage::Completed)
    {
        const FVector Direction = Goal - Player->GetActorLocation();
        const float Bearing = FMath::FindDeltaAngleDegrees(PC->GetControlRotation().Yaw, Direction.Rotation().Yaw);
        const FString Turn = FMath::Abs(Bearing) < 15 ? CityText(TEXT("ahead"), TEXT("phía trước"))
            : (Bearing > 0 ? CityText(TEXT("right"), TEXT("phải")) : CityText(TEXT("left"), TEXT("trái")));
        const FString Guidance = FString::Printf(TEXT("%s  %.0f m  |  %s %.0f deg"), *CityTranslate(Destination),
            Direction.Size2D() / 100, *Turn, FMath::Abs(Bearing));
        DrawText(Guidance, FLinearColor(0.6f, 0.9f, 1), Left, 108 * Scale, nullptr, 1.2f * Scale);
    }
    const float Bottom = Canvas->ClipY - 115 * Scale;
    DrawRect(FLinearColor(0.015f, 0.025f, 0.05f, 0.88f), Left - 12, Bottom - 12, 685 * Scale, 106 * Scale);
    DrawRect(FLinearColor(0.25f, 0.1f, 0.12f), Left, Bottom, 200 * Scale, 12 * Scale);
    DrawRect(FLinearColor(0.25f, 0.85f, 0.65f), Left, Bottom, 2 * Player->Health * Scale, 12 * Scale);
    DrawText(FString::Printf(TEXT("%s %.0f"), *CityText(TEXT("Health"), TEXT("Máu")), Player->Health),
        FLinearColor::White,
        Left + 220 * Scale, Bottom - 3, nullptr, 1.1f * Scale);
    if (auto* Car = PC->GetDrivenVehicle())
    {
        DrawText(FString::Printf(TEXT("%.0f km/h"), Car->GetSpeedKmh()), FLinearColor::White,
            Left + 360 * Scale, Bottom - 3, nullptr, 1.3f * Scale);
    }
    DrawText(CityText(TEXT("WASD Move/Drive   Mouse Look   Shift Sprint   Space Jump/Brake"),
        TEXT("WASD Di chuyển   Chuột Nhìn   Shift Chạy   Space Nhảy/Phanh")), FLinearColor::White,
        Left, Bottom + 25 * Scale, nullptr, 1.05f * Scale);
    DrawText(CityText(TEXT("E Interact   LMB Attack   F Mantle   F5 Save   Esc Settings"),
        TEXT("E Tương tác   Chuột trái Đánh   F Leo   F5 Lưu   Esc Cài đặt")), FLinearColor::White,
        Left, Bottom + 49 * Scale, nullptr, 1.05f * Scale);
    DrawText(CityTranslate(State->SaveStatus), FLinearColor(0.75f, 0.8f, 0.85f),
        Left, Bottom - 42 * Scale, nullptr, Scale);
    FString ServiceText = State->GetServiceSummary();
    float ServiceWidth = 0;
    float ServiceHeight = 0;
    const float MaxServiceWidth = FMath::Max(100.f, Canvas->ClipX - 2 * Left);
    GetTextSize(ServiceText, ServiceWidth, ServiceHeight, nullptr, Scale);
    while (ServiceWidth > MaxServiceWidth && ServiceText.Len() > 4)
    {
        ServiceText.LeftChopInline(4);
        ServiceText += TEXT("...");
        GetTextSize(ServiceText, ServiceWidth, ServiceHeight, nullptr, Scale);
    }
    DrawText(ServiceText, FLinearColor(0.65f, 0.95f, 0.8f), Left, Bottom - 67 * Scale, nullptr, Scale);
    const FString Prompt = CityTranslate(PC->GetInteractionPrompt());
    if (!Prompt.IsEmpty())
    {
        float Width = 0;
        float Height = 0;
        GetTextSize(Prompt, Width, Height, nullptr, 1.5f * Scale);
        const float X = (Canvas->ClipX - Width) / 2;
        const float Y = Canvas->ClipY * 0.72f;
        DrawRect(FLinearColor(0, 0, 0, 0.75f), X - 18, Y - 10, Width + 36, Height + 20);
        DrawText(Prompt, FLinearColor::White, X, Y, nullptr, 1.5f * Scale);
    }
    if (PC->IsPaused() && !PC->IsSettingsOpen())
    {
        DrawRect(FLinearColor(0, 0, 0, 0.7f), 0, 0, Canvas->ClipX, Canvas->ClipY);
        DrawText(TEXT("PAUSED  |  Esc to continue"), FLinearColor::White,
            Canvas->ClipX * 0.35f, Canvas->ClipY * 0.45f, nullptr, 2 * Scale);
    }
}
