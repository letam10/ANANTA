#include "CoastalQA.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "CoastalCharacter.h"
#include "Dom/JsonObject.h"
#include "DynamicRHI.h"
#include "Engine/Engine.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

ACoastalQA::ACoastalQA()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickGroup = TG_PostUpdateWork;
}

void ACoastalQA::BeginPlay()
{
    Super::BeginPlay();
    Folder = FPaths::ProjectSavedDir() / TEXT("Upgrade/Runtime") / FDateTime::UtcNow().ToString();
    IFileManager::Get().MakeDirectory(*Folder, true);
    Player = Cast<ACoastalCharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
    Check(TEXT("coastal_player_spawned"), Player != nullptr);
    ReviewCamera = GetWorld()->SpawnActor<ACameraActor>();
    ReviewCamera->GetCameraComponent()->FieldOfView = 90;
    ReadViews();
    PhaseStarted = GetWorld()->GetTimeSeconds();
    PreviousFrame = FPlatformTime::Seconds();
    FString Metadata = FString::Printf(TEXT("utc=%s\nresolution=1920x1080\nprofile=High TSR 900p\n"),
        *FDateTime::UtcNow().ToIso8601());
    FFileHelper::SaveStringToFile(Metadata, *(Folder / TEXT("metadata.txt")));
}

void ACoastalQA::ReadViews()
{
    FString Source;
    TSharedPtr<FJsonObject> Layout;
    FFileHelper::LoadFileToString(Source, *(FPaths::ProjectSavedDir() / TEXT("Upgrade/city-layout.json")));
    const auto Reader = TJsonReaderFactory<>::Create(Source);
    if (!FJsonSerializer::Deserialize(Reader, Layout) || !Layout)
    {
        Check(TEXT("layout_read"), false);
        return;
    }
    for (const auto& Value : Layout->GetArrayField(TEXT("buildings")))
    {
        const auto Data = Value->AsObject();
        const auto Center = Data->GetArrayField(TEXT("center_m"));
        const double X = Center[0]->AsNumber() * 100;
        const double Y = Center[1]->AsNumber() * 100;
        const double Z = Data->GetNumberField(TEXT("ground_m")) * 100;
        const double Front = Y - Data->GetNumberField(TEXT("depth_m")) * 50;
        const FString Name = Data->GetStringField(TEXT("name"));
        const FVector Positions[] = {FVector(X, Front - 650, Z + 170),
            FVector(X - 800, Y - 800, Z + 170), FVector(X + 800, Y - 800, Z + 170),
            FVector(X - 800, Y + 800, Z + 170), FVector(X + 800, Y + 800, Z + 170)};
        for (int32 Index = 0; Index < 5; ++Index)
        {
            Views.Add({FString::Printf(TEXT("%s_%d"), *Name, Index), Positions[Index],
                FVector(X, Y, Z + 110), false});
        }
    }
    Views.Add({TEXT("measure_downtown"), FVector(-2500, -3300, 370), FVector(-1600, -1600, 450), true});
    Views.Add({TEXT("measure_interior"), FVector(-7100, -8100, 370), FVector(-8000, -7200, 330), true});
    Views.Add({TEXT("measure_coast"), FVector(17900, -11600, 410), FVector(27000, -11400, 0), true});
    Views.Add({TEXT("measure_station"), FVector(2800, 18000, 440), FVector(0, 19300, 400), true});
    Views.Add({TEXT("measure_airport"), FVector(-18400, -5500, 500), FVector(-19900, -2200, 350), true});
    Views.Add({TEXT("hotel_roof_pool"), FVector(5000, -8300, 2850), FVector(4800, -7700, 2600), false});
    Views.Add({TEXT("city_overview"), FVector(19000, -28000, 21000), FVector(-1600, -1600, 1000), false});
}

void ACoastalQA::Check(const TCHAR* Name, bool Passed)
{
    Checks += FString::Printf(TEXT("%s,%d\n"), Name, Passed ? 1 : 0);
    Failures += Passed ? 0 : 1;
    UE_LOG(LogTemp, Display, TEXT("COASTAL_CHECK %s %s"), Name, Passed ? TEXT("PASS") : TEXT("FAIL"));
}

void ACoastalQA::NextView()
{
    ++ViewIndex;
    if (ViewIndex >= Views.Num())
    {
        Finish();
        return;
    }
    const auto& View = Views[ViewIndex];
    ReviewCamera->SetActorLocation(View.Position);
    ReviewCamera->SetActorRotation((View.Target - View.Position).Rotation());
    GetWorld()->GetFirstPlayerController()->SetViewTarget(ReviewCamera);
    ViewStarted = GetWorld()->GetTimeSeconds();
    bScreenshotRequested = false;
}

void ACoastalQA::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const double Now = FPlatformTime::Seconds();
    const double FrameMs = (Now - PreviousFrame) * 1000;
    PreviousFrame = Now;
    if (Phase < 10)
    {
        if (!Player)
        {
            Finish();
            return;
        }
        if (AdvanceGameplayTests())
        {
            Phase = 10;
            Player->SetActorHiddenInGame(true);
            GetWorld()->GetFirstPlayerController()->GetHUD()->bShowHUD = false;
            NextView();
        }
        return;
    }
    if (ViewIndex < 0 || ViewIndex >= Views.Num())
    {
        return;
    }
    const auto& View = Views[ViewIndex];
    const double Age = GetWorld()->GetTimeSeconds() - ViewStarted;
    const double Warmup = View.bMeasure ? 4 : 0.8;
    if (Age > Warmup && !bScreenshotRequested)
    {
        FScreenshotRequest::RequestScreenshot(Folder / (View.Name + TEXT(".png")), false, false);
        bScreenshotRequested = true;
    }
    if (View.bMeasure && Age > Warmup && Age < Warmup + 4)
    {
        Frames += FString::Printf(TEXT("%s,%.4f,%.4f\n"), *View.Name, FrameMs,
            FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles()));
    }
    if (Age > (View.bMeasure ? Warmup + 4 : 1.1))
    {
        NextView();
    }
}

void ACoastalQA::Finish()
{
    SetActorTickEnabled(false);
    FFileHelper::SaveStringToFile(Frames, *(Folder / TEXT("frames.csv")));
    FFileHelper::SaveStringToFile(Checks, *(Folder / TEXT("checks.csv")));
    FFileHelper::SaveStringToFile(Folder, *(FPaths::ProjectSavedDir() / TEXT("Upgrade/latest-runtime.txt")));
    UE_LOG(LogTemp, Display, TEXT("COASTAL_QA_COMPLETE failures=%d views=%d folder=%s"),
        Failures, Views.Num(), *Folder);
    FPlatformMisc::RequestExitWithStatus(true, Failures ? 1 : 0);
}
