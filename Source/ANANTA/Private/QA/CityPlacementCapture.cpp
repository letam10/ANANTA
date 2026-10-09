#include "QA/CityCaptureSubsystem.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

bool UCityCaptureSubsystem::InitializePlacementViews()
{
    FString Path;
    if (!FParse::Value(FCommandLine::Get(), TEXT("CityPlacementViews="), Path))
    {
        return true;
    }
    FString Contents;
    TSharedPtr<FJsonObject> Document;
    if (!FFileHelper::LoadFileToString(Contents, *Path)
        || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Contents), Document)
        || !Document.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("CITY_PLACEMENT_INVALID manifest=%s"), *Path);
        return false;
    }
    const TArray<TSharedPtr<FJsonValue>>* Views;
    if (!Document->TryGetArrayField(TEXT("views"), Views) || Views->IsEmpty() || Views->Num() > 200)
    {
        return false;
    }
    for (const auto& Value : *Views)
    {
        const TSharedPtr<FJsonObject> Item = Value->AsObject();
        const TArray<TSharedPtr<FJsonValue>>* Location;
        const TArray<TSharedPtr<FJsonValue>>* Rotation;
        if (!Item.IsValid() || !Item->TryGetArrayField(TEXT("location"), Location)
            || !Item->TryGetArrayField(TEXT("rotation"), Rotation)
            || Location->Num() != 3 || Rotation->Num() != 3)
        {
            return false;
        }
        const FVector Position((*Location)[0]->AsNumber(), (*Location)[1]->AsNumber(), (*Location)[2]->AsNumber());
        const FRotator Angles((*Rotation)[0]->AsNumber(), (*Rotation)[1]->AsNumber(), (*Rotation)[2]->AsNumber());
        if (Position.ContainsNaN() || Angles.ContainsNaN())
        {
            return false;
        }
        PlacementViews.Emplace(Angles, Position);
    }
    CaptureCount = PlacementViews.Num();
    MoveReviewCamera(PlacementViews[0].GetLocation(), PlacementViews[0].Rotator());
    UE_LOG(LogTemp, Display, TEXT("CITY_PLACEMENT_VIEWS_READY count=%d manifest=%s"), CaptureCount, *Path);
    return true;
}

void UCityCaptureSubsystem::MoveReviewCamera(const FVector& Location, const FRotator& Rotation)
{
    if (!ReviewCamera)
    {
        ReviewCamera = GetWorld()->SpawnActor<ACameraActor>();
        ReviewCamera->GetCameraComponent()->SetFieldOfView(75);
        auto* Source = NewObject<UWorldPartitionStreamingSourceComponent>(ReviewCamera);
        Source->RegisterComponent();
    }
    ReviewCamera->SetActorLocationAndRotation(Location, Rotation);
    GetWorld()->GetFirstPlayerController()->SetViewTarget(ReviewCamera);
}
