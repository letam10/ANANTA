#include "Settings/ANANTAGraphicsSettings.h"

#include "Internationalization/Internationalization.h"
#include "Templates/UnrealTemplate.h"

UANANTAGraphicsSettings::UANANTAGraphicsSettings(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    SetToDefaults();
}

UANANTAGraphicsSettings* UANANTAGraphicsSettings::Get()
{
    return Cast<UANANTAGraphicsSettings>(UGameUserSettings::GetGameUserSettings());
}

FCityGraphicsOptions UANANTAGraphicsSettings::MakeDefaults()
{
    return FCityGraphicsOptions();
}

FCityGraphicsOptions UANANTAGraphicsSettings::SanitizeOptions(const FCityGraphicsOptions& Options)
{
    FCityGraphicsOptions Clean = Options;
    Clean.ViewDistance = FMath::Clamp(Clean.ViewDistance, 0, 3);
    Clean.AntiAliasing = FMath::Clamp(Clean.AntiAliasing, 0, 3);
    Clean.Shadows = FMath::Clamp(Clean.Shadows, 0, 3);
    Clean.GlobalIllumination = FMath::Clamp(Clean.GlobalIllumination, 0, 3);
    Clean.Reflections = FMath::Clamp(Clean.Reflections, 0, 3);
    Clean.PostProcess = FMath::Clamp(Clean.PostProcess, 0, 3);
    Clean.Textures = FMath::Clamp(Clean.Textures, 0, 3);
    Clean.Effects = FMath::Clamp(Clean.Effects, 0, 3);
    Clean.Foliage = FMath::Clamp(Clean.Foliage, 0, 3);
    Clean.Shading = FMath::Clamp(Clean.Shading, 0, 3);
    Clean.ResolutionScale = FMath::IsFinite(Clean.ResolutionScale)
        ? FMath::Clamp(Clean.ResolutionScale, 50.0f, 100.0f) : MakeDefaults().ResolutionScale;
    if (!FMath::IsFinite(Clean.FrameRateLimit))
    {
        Clean.FrameRateLimit = MakeDefaults().FrameRateLimit;
    }
    else if (Clean.FrameRateLimit != 0.0f)
    {
        Clean.FrameRateLimit = FMath::Clamp(Clean.FrameRateLimit, 30.0f, 240.0f);
    }
    Clean.Language.TrimStartAndEndInline();
    Clean.Language.ToLowerInline();
    if (Clean.Language != TEXT("vi") && Clean.Language != TEXT("en"))
    {
        Clean.Language = MakeDefaults().Language;
    }
    return Clean;
}

FCityGraphicsOptions UANANTAGraphicsSettings::CaptureOptions() const
{
    FCityGraphicsOptions Options;
    Options.ViewDistance = GetViewDistanceQuality();
    Options.AntiAliasing = GetAntiAliasingQuality();
    Options.Shadows = GetShadowQuality();
    Options.GlobalIllumination = GetGlobalIlluminationQuality();
    Options.Reflections = GetReflectionQuality();
    Options.PostProcess = GetPostProcessingQuality();
    Options.Textures = GetTextureQuality();
    Options.Effects = GetVisualEffectQuality();
    Options.Foliage = GetFoliageQuality();
    Options.Shading = GetShadingQuality();
    Options.ResolutionScale = ScalabilityQuality.ResolutionQuality;
    Options.FrameRateLimit = GetFrameRateLimit();
    Options.bVSync = IsVSyncEnabled();
    Options.bShowFPS = bShowFPS;
    Options.Language = Language;
    return Options;
}

void UANANTAGraphicsSettings::StoreOptions(const FCityGraphicsOptions& Options, bool bUpdateDesiredResolution)
{
    SetViewDistanceQuality(Options.ViewDistance);
    SetAntiAliasingQuality(Options.AntiAliasing);
    SetShadowQuality(Options.Shadows);
    SetGlobalIlluminationQuality(Options.GlobalIllumination);
    SetReflectionQuality(Options.Reflections);
    SetPostProcessingQuality(Options.PostProcess);
    SetTextureQuality(Options.Textures);
    SetVisualEffectQuality(Options.Effects);
    SetFoliageQuality(Options.Foliage);
    SetShadingQuality(Options.Shading);
    if (bUpdateDesiredResolution)
    {
        SetResolutionScaleValueEx(Options.ResolutionScale);
    }
    else
    {
        // Nạp/kiểm tra không được tính lại kích thước render mà người dùng đã lưu.
        ScalabilityQuality.ResolutionQuality = Options.ResolutionScale;
    }
    SetFrameRateLimit(Options.FrameRateLimit);
    SetVSyncEnabled(Options.bVSync);
    Language = Options.Language;
    bShowFPS = Options.bShowFPS;
}

void UANANTAGraphicsSettings::ApplyOptions(const FCityGraphicsOptions& Options, bool bSave)
{
    StoreOptions(SanitizeOptions(Options));
    FInternationalization::Get().SetCurrentCulture(Language);
    // ApplySettings luôn gọi SaveSettings; chặn đường lưu đó khi chỉ áp dụng tạm.
    TGuardValue<bool> SuppressSave(bSuppressSaving, !bSave);
    ApplySettings(false);
}

FString UANANTAGraphicsSettings::GetLanguage() const
{
    return Language;
}

bool UANANTAGraphicsSettings::IsFPSVisible() const
{
    return bShowFPS;
}

void UANANTAGraphicsSettings::SetToDefaults()
{
    Super::SetToDefaults();
    StoreOptions(MakeDefaults());
    UpdateVersion();
}

void UANANTAGraphicsSettings::ValidateSettings()
{
    // Dữ liệu đồ họa được chuẩn hóa ở đây; tránh UE xóa file khi đổi lớp settings.
    UpdateVersion();
    Super::ValidateSettings();
    StoreOptions(SanitizeOptions(CaptureOptions()), false);
}

void UANANTAGraphicsSettings::SaveSettings()
{
    if (!bSuppressSaving)
    {
        Super::SaveSettings();
    }
}
