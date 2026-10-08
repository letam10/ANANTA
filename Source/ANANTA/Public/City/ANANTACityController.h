#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "ANANTACityController.generated.h"

class AANANTACityVehicle;
class SCitySettingsPanel;
class SWidget;

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
    void ToggleSettings();
    void CloseSettings(bool bResumeGame = true);
    void ToggleFPS();
    bool IsSettingsOpen() const { return SettingsPanel.IsValid(); }
    TSharedPtr<SCitySettingsPanel> GetSettingsPanel() const { return SettingsPanel; }
    double GetMeasuredFPS() const { return MeasuredFPS; }
    double GetMeasuredFrameMs() const { return MeasuredFrameMs; }

private:
    void JumpPressed();
    void JumpReleased();
    void Mantle();
    void Attack();
    void RestorePlayer(float DeltaTime);
    void InitializeSettingsUI();
    void UpdateFrameMeter();
    void ShowMenuCursor();
    void HideMenuCursor();

    TSharedPtr<SCitySettingsPanel> SettingsPanel;
    TSharedPtr<SWidget> SettingsOverlay;
    bool bPausedBeforeSettings = false;
    double FrameMeterStart = 0;
    int32 FrameMeterCount = 0;
    double MeasuredFPS = 0;
    double MeasuredFrameMs = 0;

    UPROPERTY()
    TWeakObjectPtr<AANANTACityVehicle> DrivenVehicle;

    FTransform LastOnFootTransform;
    bool bRestoreComplete = false;
    bool bRestoreRequested = false;
    float RestoreElapsed = 0;
    float AutoSaveElapsed = 0;
};
