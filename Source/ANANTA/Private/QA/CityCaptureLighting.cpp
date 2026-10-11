#include "QA/CityCaptureSubsystem.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"

FString UCityCaptureSubsystem::GetOutputDirectory() const
{
    if (!PlacementViews.IsEmpty())
    {
        FString Manifest;
        FParse::Value(FCommandLine::Get(), TEXT("CityPlacementViews="), Manifest);
        return FPaths::GetPath(Manifest);
    }
    const bool bBlueHour = FParse::Param(FCommandLine::Get(), TEXT("CityBlueHour"));
    if (FParse::Param(FCommandLine::Get(), TEXT("CityCivicViews")))
    {
        return FPaths::ProjectSavedDir() / (bBlueHour ? TEXT("QA/CityCivicBlueHour") : TEXT("QA/CityCivic"));
    }
    if (FParse::Param(FCommandLine::Get(), TEXT("CityFixtureViews")))
    {
        return FPaths::ProjectSavedDir() / (bBlueHour ? TEXT("QA/CityFixturesBlueHour") : TEXT("QA/CityFixtures"));
    }
    if (FParse::Param(FCommandLine::Get(), TEXT("CityFinishingViews")))
    {
        return FPaths::ProjectSavedDir() / (bBlueHour ? TEXT("QA/CityFinishingBlueHour") : TEXT("QA/CityFinishing"));
    }
    if (FParse::Param(FCommandLine::Get(), TEXT("CityDressingViews")))
    {
        return FPaths::ProjectSavedDir() / (bBlueHour ? TEXT("QA/CityDressingBlueHour") : TEXT("QA/CityDressing"));
    }
    return FPaths::ProjectSavedDir() / (bBlueHour ? TEXT("QA/CityGPUBlueHour") : TEXT("QA/CityGPU"));
}

void UCityCaptureSubsystem::ApplyReviewLighting()
{
    if (!FParse::Param(FCommandLine::Get(), TEXT("CityBlueHour")))
    {
        return;
    }
    // Bien the anh sang chi dung trong luot chup QA, khong thay doi map da luu.
    for (TActorIterator<ADirectionalLight> Light(GetWorld()); Light; ++Light)
    {
        Light->SetActorRotation(FRotator(-6, -28, 0));
        auto* Component = Cast<UDirectionalLightComponent>(Light->GetLightComponent());
        Component->SetIntensity(800);
        Component->SetLightColor(FLinearColor(0.55f, 0.67f, 1.f));
    }
    for (TActorIterator<ASkyLight> Sky(GetWorld()); Sky; ++Sky)
    {
        Sky->GetLightComponent()->SetIntensity(1.4f);
    }
}
