#pragma once

#include "CoreMinimal.h"
#include "InputCoreTypes.h"
#include "Subsystems/WorldSubsystem.h"
#include "CitySettingsCheck.generated.h"

class AANANTACityController;
class SWidget;

UCLASS()
class ANANTA_API UCitySettingsCheck : public UTickableWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void Tick(float DeltaTime) override;
    virtual bool IsTickableWhenPaused() const override { return true; }
    virtual TStatId GetStatId() const override;

private:
    void RunStep();
    void SendKey(const FKey& Key, bool bSlate = false, bool bDown = true);
    bool ClickApply();
    void ScrollMenuBottom();
    void Capture(const FString& Name);
    void Finish(bool bSuccess, const FString& Detail);
    bool Check(bool bCondition, const FString& Detail);
    void RecordSettings();
    FString Directory() const;

    TWeakObjectPtr<AANANTACityController> Controller;
    TArray<FString> Evidence;
    TArray<FString> Captures;
    FVector PausedLocation = FVector::ZeroVector;
    double Start = 0;
    double StepStart = 0;
    int32 Step = 0;
    bool bReload = false;
    bool bFinished = false;
};
