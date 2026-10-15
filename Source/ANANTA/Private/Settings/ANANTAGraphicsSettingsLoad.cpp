#include "Settings/ANANTAGraphicsSettings.h"

#include "Internationalization/Internationalization.h"
#include "Misc/ConfigCacheIni.h"

void UANANTAGraphicsSettings::LoadSettings(bool bForceReload)
{
    Language = MakeDefaults().Language;
    bShowFPS = MakeDefaults().bShowFPS;
    Super::LoadSettings(bForceReload);

    // File đã lưu có thể còn dùng tên lớp UE cũ; chỉ di chuyển khi chưa có lớp mới.
    FConfigFile SavedConfig;
    const FConfigBranch* Branch = GConfig->FindBranch(NAME_None, GGameUserSettingsIni);
    if (Branch && !Branch->IniPath.IsEmpty())
    {
        // UE 5.8 dùng tên nhánh cho GGameUserSettingsIni, không phải đường dẫn trên đĩa.
        SavedConfig.Read(Branch->IniPath);
    }
    const TCHAR* LegacySection = TEXT("/Script/Engine.GameUserSettings");
    const bool bMigratingLegacy = SavedConfig.FindSection(LegacySection)
        && !SavedConfig.FindSection(GetClass()->GetPathName());
    if (bMigratingLegacy)
    {
        LoadConfig(UGameUserSettings::StaticClass(), *GGameUserSettingsIni);
        FLoadConfigParams SavedOverrides;
        SavedOverrides.ConfigClass = UGameUserSettings::StaticClass();
        SavedOverrides.OverrideFile = &SavedConfig;
        LoadConfig(SavedOverrides);
    }

    FCityGraphicsOptions Options = CaptureOptions();
    const FCityGraphicsOptions Defaults = MakeDefaults();
    const TCHAR* Section = TEXT("ScalabilityGroups");
    const FString& Ini = GIsEditor && !bMigratingLegacy ? GEditorSettingsIni : GGameUserSettingsIni;
    Options.ViewDistance = Defaults.ViewDistance;
    Options.AntiAliasing = Defaults.AntiAliasing;
    Options.Shadows = Defaults.Shadows;
    Options.GlobalIllumination = Defaults.GlobalIllumination;
    Options.Reflections = Defaults.Reflections;
    Options.PostProcess = Defaults.PostProcess;
    Options.Textures = Defaults.Textures;
    Options.Effects = Defaults.Effects;
    Options.Foliage = Defaults.Foliage;
    Options.Shading = Defaults.Shading;
    Options.ResolutionScale = Defaults.ResolutionScale;
    GConfig->GetInt(Section, TEXT("sg.ViewDistanceQuality"), Options.ViewDistance, Ini);
    GConfig->GetInt(Section, TEXT("sg.AntiAliasingQuality"), Options.AntiAliasing, Ini);
    GConfig->GetInt(Section, TEXT("sg.ShadowQuality"), Options.Shadows, Ini);
    GConfig->GetInt(Section, TEXT("sg.GlobalIlluminationQuality"), Options.GlobalIllumination, Ini);
    GConfig->GetInt(Section, TEXT("sg.ReflectionQuality"), Options.Reflections, Ini);
    GConfig->GetInt(Section, TEXT("sg.PostProcessQuality"), Options.PostProcess, Ini);
    GConfig->GetInt(Section, TEXT("sg.TextureQuality"), Options.Textures, Ini);
    GConfig->GetInt(Section, TEXT("sg.EffectsQuality"), Options.Effects, Ini);
    GConfig->GetInt(Section, TEXT("sg.FoliageQuality"), Options.Foliage, Ini);
    GConfig->GetInt(Section, TEXT("sg.ShadingQuality"), Options.Shading, Ini);
    GConfig->GetFloat(Section, TEXT("sg.ResolutionQuality"), Options.ResolutionScale, Ini);
    StoreOptions(SanitizeOptions(Options), false);
    FInternationalization::Get().SetCurrentCulture(Language);
}
