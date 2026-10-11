#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "CityCaptureSubsystem.generated.h"

class ACameraActor;

UCLASS()
class ANANTA_API UCityCaptureSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;

private:
    void CaptureView(int32 Index);
    void FinishCapture();
    void ApplyReviewLighting();
    FString GetOutputDirectory() const;
    bool InitializePlacementViews();
    void MoveReviewCamera(const FVector& Location, const FRotator& Rotation);

    float Elapsed = 0;
    double WallStart = 0;
    int32 ViewIndex = 0;
    int32 CaptureCount = 8;
    TArray<FTransform> PlacementViews;
    TArray<FString> OutputFiles;
    double FrameSeconds = 0;
    float MaximumFrameSeconds = 0;
    int32 FrameSamples = 0;

    UPROPERTY()
    TObjectPtr<ACameraActor> ReviewCamera;
};
