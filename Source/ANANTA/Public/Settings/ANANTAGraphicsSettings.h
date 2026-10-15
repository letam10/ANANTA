#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "ANANTAGraphicsSettings.generated.h"

struct ANANTA_API FCityGraphicsOptions
{
    int32 ViewDistance = 2;
    int32 AntiAliasing = 2;
    int32 Shadows = 2;
    int32 GlobalIllumination = 2;
    int32 Reflections = 2;
    int32 PostProcess = 2;
    int32 Textures = 2;
    int32 Effects = 2;
    int32 Foliage = 2;
    int32 Shading = 2;
    float ResolutionScale = 83.333333f;
    float FrameRateLimit = 90.0f;
    bool bVSync = false;
    bool bShowFPS = false;
    FString Language = TEXT("vi");
};

UCLASS(Config=GameUserSettings)
class ANANTA_API UANANTAGraphicsSettings : public UGameUserSettings
{
    GENERATED_BODY()

public:
    UANANTAGraphicsSettings(const FObjectInitializer& ObjectInitializer);

    static UANANTAGraphicsSettings* Get();
    static FCityGraphicsOptions MakeDefaults();
    static FCityGraphicsOptions SanitizeOptions(const FCityGraphicsOptions& Options);
    FCityGraphicsOptions CaptureOptions() const;
    void ApplyOptions(const FCityGraphicsOptions& Options, bool bSave = true);
    FString GetLanguage() const;
    bool IsFPSVisible() const;

    virtual void SetToDefaults() override;
    virtual void ValidateSettings() override;
    virtual void LoadSettings(bool bForceReload = false) override;
    virtual void SaveSettings() override;

private:
    void StoreOptions(const FCityGraphicsOptions& Options, bool bUpdateDesiredResolution = true);

    UPROPERTY(Config)
    FString Language = TEXT("vi");

    UPROPERTY(Config)
    bool bShowFPS = false;

    bool bSuppressSaving = false;
};
