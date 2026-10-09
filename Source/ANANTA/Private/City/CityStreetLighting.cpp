#include "City/CityStreetLighting.h"
#include "City/CityWorldBounds.h"

#include "Camera/PlayerCameraManager.h"
#include "Components/LightComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SpotLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialParameterCollection.h"
#include "Materials/MaterialParameterCollectionInstance.h"

ACityStreetLighting::ACityStreetLighting()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.5f;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    for (int32 Index = 0; Index < 8; ++Index)
    {
        const FName Name(*FString::Printf(TEXT("StreetLight%d"), Index));
        auto* Light = CreateDefaultSubobject<USpotLightComponent>(Name);
        Light->SetupAttachment(RootComponent);
        Light->SetMobility(EComponentMobility::Movable);
        Light->SetIntensityUnits(ELightUnits::Lumens);
        Light->SetIntensity(4500);
        Light->SetLightColor(FLinearColor(1.f, 0.82f, 0.62f));
        Light->SetAttenuationRadius(2200);
        Light->SetInnerConeAngle(50);
        Light->SetOuterConeAngle(75);
        Light->SetCastShadows(Index < 2);
        Light->SetIndirectLightingIntensity(0);
        Light->SetVolumetricScatteringIntensity(0);
        Light->SetVisibility(false);
        Lights.Add(Light);
    }
}

void ACityStreetLighting::BeginPlay()
{
    Super::BeginPlay();
    WindowParameters = LoadObject<UMaterialParameterCollection>(nullptr,
        TEXT("/Game/ANANTA/City/Materials/MPC_CityLighting.MPC_CityLighting"));
    for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It)
    {
        Sun = *It;
        break;
    }
}

void ACityStreetLighting::Tick(const float DeltaTime)
{
    Super::Tick(DeltaTime);
    const auto* PC = GetWorld()->GetFirstPlayerController();
    if (!PC || !PC->PlayerCameraManager)
    {
        return;
    }
    const bool bDark = Sun && Sun->GetLightComponent()->Intensity < 2000;
    const float NightAmount = bDark ? 1.f : 0.f;
    if (WindowParameters && NightAmount != PreviousNightAmount)
    {
        // Mot tham so shader chung thay cho den rieng o hang nghin cua so.
        GetWorld()->GetParameterCollectionInstance(WindowParameters)->SetScalarParameterValue(
            TEXT("NightAmount"), NightAmount);
        PreviousNightAmount = NightAmount;
    }
    const FVector Camera = PC->PlayerCameraManager->GetCameraLocation();
    if (bDark)
    {
        // Chi xet cac o gan camera; khong sort hang van den cua thanh pho.
        LampPositions.Reset();
        constexpr float Spacing = CityWorldBounds::RoadSpacing;
        const float RoadCentre = FMath::RoundToFloat(Camera.Y / Spacing) * Spacing;
        const float BlockCentre = FMath::FloorToFloat(Camera.X / Spacing) * Spacing;
        for (int32 Row = -1; Row <= 1; ++Row)
        {
            const float Road = RoadCentre + Row * Spacing;
            if (FMath::Abs(Road) > CityWorldBounds::RoadExtent)
            {
                continue;
            }
            for (int32 Column = -1; Column <= 1; ++Column)
            {
                const float Block = BlockCentre + Column * Spacing;
                if (Block < -CityWorldBounds::RoadExtent || Block >= CityWorldBounds::RoadExtent)
                {
                    continue;
                }
                if (CityWorldBounds::IsStreetCutout(Block + 6000, Road))
                {
                    continue;
                }
                for (const int32 Side : {-1, 1})
                {
                    for (const int32 Step : {-3600, 0, 3600})
                    {
                        LampPositions.Add(FVector(Block + 6000 + Step, Road + Side * 1322, 484));
                    }
                }
            }
        }
        LampPositions.Sort([Camera](const FVector& A, const FVector& B)
        {
            return FVector::DistSquared2D(A, Camera) < FVector::DistSquared2D(B, Camera);
        });
    }
    // Tai su dung 8 den gan camera; chi 2 den gan nhat tinh bong dong.
    for (int32 Index = 0; Index < Lights.Num(); ++Index)
    {
        auto* Light = Lights[Index].Get();
        const bool bNear = LampPositions.IsValidIndex(Index)
            && FVector::DistSquared2D(LampPositions[Index], Camera) < FMath::Square(6000.0);
        Light->SetVisibility(bDark && bNear);
        if (bDark && bNear)
        {
            Light->SetWorldLocation(LampPositions[Index]);
            Light->SetWorldRotation(FRotator(-90, 0, 0));
        }
    }
}
