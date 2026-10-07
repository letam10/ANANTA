#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "ANANTACityController.generated.h"

class AANANTACityVehicle;

UCLASS()
class ANANTA_API AANANTACityController : public APlayerController
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;
    virtual void PlayerTick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    FString GetInteractionPrompt() const;
    AActor* FindInteractionTarget() const;
    AANANTACityVehicle* GetDrivenVehicle() const { return DrivenVehicle.Get(); }
    FTransform GetSafePlayerTransform() const;
    bool CanCaptureProgress() const { return bRestoreComplete; }
    void RecoverPlayer();
    void Interact();
    void TogglePause();
    void SaveNow();

private:
    void JumpPressed();
    void JumpReleased();
    void Mantle();
    void Attack();
    void RestorePlayer(float DeltaTime);

    UPROPERTY()
    TWeakObjectPtr<AANANTACityVehicle> DrivenVehicle;

    FTransform LastOnFootTransform;
    bool bRestoreComplete = false;
    bool bRestoreRequested = false;
    float RestoreElapsed = 0;
    float AutoSaveElapsed = 0;
};
