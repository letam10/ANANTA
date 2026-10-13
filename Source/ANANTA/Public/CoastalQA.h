#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoastalQA.generated.h"

class ACameraActor;
class ACoastalCharacter;
class ACoastalVehicle;

struct FCoastalReviewView
{
    FString Name;
    FVector Position;
    FVector Target;
    bool bMeasure = false;
};

UCLASS()
class ANANTA_API ACoastalQA : public AActor
{
    GENERATED_BODY()

public:
    ACoastalQA();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

private:
    UPROPERTY()
    TObjectPtr<ACameraActor> ReviewCamera;

    UPROPERTY()
    TObjectPtr<ACoastalCharacter> Player;

    UPROPERTY()
    TObjectPtr<ACoastalVehicle> TestVehicle;

    TArray<FCoastalReviewView> Views;
    FString Folder;
    FString Frames = TEXT("view,frame_ms,gpu_ms\n");
    FString Checks = TEXT("check,passed\n");
    int32 ViewIndex = -1;
    int32 Failures = 0;
    int32 Phase = 0;
    double PhaseStarted = 0;
    double ViewStarted = 0;
    double PreviousFrame = 0;
    FVector StartVehiclePosition;
    FTransform SavedVehicleTransform;
    bool bScreenshotRequested = false;
    void ReadViews();
    void NextView();
    void Finish();
    void Check(const TCHAR* Name, bool Passed);
    void TestInteractions();
    bool AdvanceGameplayTests();
    void Key(const FKey& KeyName, bool Pressed);
};
