#include "Settings/ANANTAGraphicsSettings.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Internationalization/Culture.h"
#include "Internationalization/Internationalization.h"
#include "Misc/AutomationTest.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/ScopeExit.h"
#include "Templates/UnrealTemplate.h"
#include "UObject/UnrealType.h"
#include <limits>

namespace
{
    constexpr int32 FCityGraphicsOptions::* QualityMembers[] =
    {
        &FCityGraphicsOptions::ViewDistance,
        &FCityGraphicsOptions::AntiAliasing,
        &FCityGraphicsOptions::Shadows,
        &FCityGraphicsOptions::GlobalIllumination,
        &FCityGraphicsOptions::Reflections,
        &FCityGraphicsOptions::PostProcess,
        &FCityGraphicsOptions::Textures,
        &FCityGraphicsOptions::Effects,
        &FCityGraphicsOptions::Foliage,
        &FCityGraphicsOptions::Shading
    };
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityGraphicsDefaultsTest, "ANANTA.City.Settings.DefaultsAndEpicMaximum",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityGraphicsDefaultsTest::RunTest(const FString& Parameters)
{
    const FCityGraphicsOptions Defaults = UANANTAGraphicsSettings::MakeDefaults();
    FCityGraphicsOptions Max = Defaults;
    for (const auto Member : QualityMembers)
    {
        TestEqual(TEXT("Default quality is High"), Defaults.*Member, 2);
        Max.*Member = 4;
    }
    TestTrue(TEXT("Default TSR scale"), FMath::IsNearlyEqual(Defaults.ResolutionScale, 83.333333f));
    TestEqual(TEXT("Default FPS cap"), Defaults.FrameRateLimit, 90.0f);
    TestFalse(TEXT("Default VSync disabled"), Defaults.bVSync);
    TestFalse(TEXT("FPS display starts hidden"), Defaults.bShowFPS);
    TestEqual(TEXT("Default language Vietnamese"), Defaults.Language, FString(TEXT("vi")));
    Max.ResolutionScale = 150.0f;
    Max = UANANTAGraphicsSettings::SanitizeOptions(Max);
    for (const auto Member : QualityMembers)
    {
        TestEqual(TEXT("Cinematic reduced to actual Epic maximum"), Max.*Member, 3);
    }
    TestEqual(TEXT("Maximum uses native resolution"), Max.ResolutionScale, 100.0f);
    auto* Settings = NewObject<UANANTAGraphicsSettings>();
    Settings->SetToDefaults();
    const FCityGraphicsOptions Captured = Settings->CaptureOptions();
    for (const auto Member : QualityMembers)
    {
        TestEqual(TEXT("UGameUserSettings receives default quality"), Captured.*Member, Defaults.*Member);
    }
    TestEqual(TEXT("Default cap reaches engine settings"), Captured.FrameRateLimit, Defaults.FrameRateLimit);
    TestTrue(TEXT("Default scale reaches engine settings"),
        FMath::IsNearlyEqual(Captured.ResolutionScale, Defaults.ResolutionScale));
    TestEqual(TEXT("Language accessor"), Settings->GetLanguage(), Defaults.Language);
    TestFalse(TEXT("FPS accessor"), Settings->IsFPSVisible());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityGraphicsRangeTest, "ANANTA.City.Settings.InvalidRangesAndFiniteValues",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityGraphicsRangeTest::RunTest(const FString& Parameters)
{
    FCityGraphicsOptions Input;
    for (const auto Member : QualityMembers)
    {
        Input.*Member = MIN_int32;
    }
    Input.ResolutionScale = -1.0f;
    Input.FrameRateLimit = -10.0f;
    Input.Language = TEXT("unsupported");
    FCityGraphicsOptions Clean = UANANTAGraphicsSettings::SanitizeOptions(Input);
    for (const auto Member : QualityMembers)
    {
        TestEqual(TEXT("Negative quality becomes Low"), Clean.*Member, 0);
    }
    TestEqual(TEXT("Minimum render scale"), Clean.ResolutionScale, 50.0f);
    TestEqual(TEXT("Negative FPS cannot become unlimited"), Clean.FrameRateLimit, 30.0f);
    TestEqual(TEXT("Unsupported language falls back"), Clean.Language, FString(TEXT("vi")));
    const float InvalidValues[] =
    {
        std::numeric_limits<float>::quiet_NaN(),
        std::numeric_limits<float>::infinity(),
        -std::numeric_limits<float>::infinity()
    };
    for (const float Invalid : InvalidValues)
    {
        Input.ResolutionScale = Invalid;
        Input.FrameRateLimit = Invalid;
        Clean = UANANTAGraphicsSettings::SanitizeOptions(Input);
        TestTrue(TEXT("Invalid scale becomes finite default"),
            FMath::IsNearlyEqual(Clean.ResolutionScale, 83.333333f));
        TestEqual(TEXT("Invalid FPS becomes finite default"), Clean.FrameRateLimit, 90.0f);
    }
    Input.FrameRateLimit = 1.0f;
    TestEqual(TEXT("Nonzero FPS minimum"),
        UANANTAGraphicsSettings::SanitizeOptions(Input).FrameRateLimit, 30.0f);
    Input.FrameRateLimit = 1000.0f;
    TestEqual(TEXT("FPS maximum"), UANANTAGraphicsSettings::SanitizeOptions(Input).FrameRateLimit, 240.0f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityGraphicsValidOptionsTest, "ANANTA.City.Settings.ValidOptionsPreserved",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityGraphicsValidOptionsTest::RunTest(const FString& Parameters)
{
    FCityGraphicsOptions Input;
    for (int32 Level = 0; Level <= 3; ++Level)
    {
        for (const auto Member : QualityMembers)
        {
            Input.*Member = Level;
        }
        const FCityGraphicsOptions Clean = UANANTAGraphicsSettings::SanitizeOptions(Input);
        for (const auto Member : QualityMembers)
        {
            TestEqual(TEXT("Each playable quality level retained"), Clean.*Member, Level);
        }
    }
    Input.ResolutionScale = 71.5f;
    Input.FrameRateLimit = 0.0f;
    Input.bVSync = true;
    Input.bShowFPS = true;
    Input.Language = TEXT(" EN ");
    const FCityGraphicsOptions Clean = UANANTAGraphicsSettings::SanitizeOptions(Input);
    TestEqual(TEXT("Custom render scale preserved"), Clean.ResolutionScale, 71.5f);
    TestEqual(TEXT("Zero explicitly means unlimited"), Clean.FrameRateLimit, 0.0f);
    TestTrue(TEXT("VSync selection retained"), Clean.bVSync);
    TestTrue(TEXT("FPS selection retained"), Clean.bShowFPS);
    TestEqual(TEXT("Language normalized"), Clean.Language, FString(TEXT("en")));
    const float ValidCaps[] = {30.0f, 90.0f, 144.0f, 240.0f};
    for (const float Cap : ValidCaps)
    {
        Input.FrameRateLimit = Cap;
        TestEqual(TEXT("Valid FPS cap retained"),
            UANANTAGraphicsSettings::SanitizeOptions(Input).FrameRateLimit, Cap);
    }
    const float ValidScales[] = {50.0f, 83.333333f, 100.0f};
    for (const float Scale : ValidScales)
    {
        Input.ResolutionScale = Scale;
        TestEqual(TEXT("Valid scale and boundaries retained"),
            UANANTAGraphicsSettings::SanitizeOptions(Input).ResolutionScale, Scale);
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityGraphicsMigrationTest, "ANANTA.City.Settings.LegacyConfigMigration",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityGraphicsMigrationTest::RunTest(const FString& Parameters)
{
    const FString Directory = FPaths::ProjectSavedDir() / TEXT("QA/CitySettings");
    IFileManager::Get().MakeDirectory(*Directory, true);
    const FString Path = Directory / (FGuid::NewGuid().ToString() + TEXT(".ini"));
    const FString LegacyText = TEXT(";METADATA=(Diff=true, UseCommands=true)\n")
        TEXT("[/Script/Engine.GameUserSettings]\nFrameRateLimit=0\nbUseVSync=True\n")
        TEXT("ResolutionSizeX=2048\nResolutionSizeY=1280\nFullscreenMode=1\nVersion=5\n")
        TEXT("DesiredScreenWidth=1280\nDesiredScreenHeight=720\n")
        TEXT("LastUserConfirmedResolutionSizeX=2048\nLastUserConfirmedResolutionSizeY=1280\n")
        TEXT("[ScalabilityGroups]\nsg.ResolutionQuality=83.3332977\nsg.TextureQuality=1\n");
    if (!TestTrue(TEXT("Write isolated legacy fixture"), FFileHelper::SaveStringToFile(LegacyText, *Path)))
    {
        return false;
    }
    const FString PreviousCulture = FInternationalization::Get().GetCurrentCulture()->GetName();
    IConsoleVariable* FullscreenCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("r.FullScreenMode"));
    const int32 PreviousFullscreen = FullscreenCVar->GetInt();
    FConfigCacheIni IsolatedConfig(EConfigCacheType::Temporary);
    TGuardValue<FConfigCacheIni*> ConfigGuard(GConfig, &IsolatedConfig);
    TGuardValue<FString> SettingsNameGuard(GGameUserSettingsIni, TEXT("GameUserSettings"));
    ON_SCOPE_EXIT
    {
        IFileManager::Get().Delete(*Path);
        FInternationalization::Get().SetCurrentCulture(PreviousCulture);
        FullscreenCVar->Set(PreviousFullscreen, ECVF_SetByGameSetting);
    };
    FConfigFile Fixture;
    Fixture.Read(Path);
    IsolatedConfig.SetFile(GGameUserSettingsIni, &Fixture);
    FConfigBranch* Branch = IsolatedConfig.FindBranch(NAME_None, GGameUserSettingsIni);
    if (!TestNotNull(TEXT("Known config branch exists"), Branch))
    {
        return false;
    }
    Branch->IniPath = Path;
    FConfigFile EditorFixture;
    EditorFixture.SetFloat(TEXT("ScalabilityGroups"), TEXT("sg.ResolutionQuality"), 66.666667f);
    IsolatedConfig.SetFile(GEditorSettingsIni, &EditorFixture);
    auto* Settings = NewObject<UANANTAGraphicsSettings>();
    Settings->LoadSettings();
    Settings->ValidateSettings();
    const FCityGraphicsOptions Migrated = Settings->CaptureOptions();
    TestEqual(TEXT("Legacy unlimited FPS preserved"), Migrated.FrameRateLimit, 0.0f);
    TestTrue(TEXT("Legacy VSync preserved"), Migrated.bVSync);
    TestEqual(TEXT("Legacy output size preserved"), Settings->GetScreenResolution(), FIntPoint(2048, 1280));
    TestEqual(TEXT("Legacy window mode preserved"), Settings->GetFullscreenMode(), EWindowMode::WindowedFullscreen);
    TestTrue(TEXT("Migration uses legacy scale instead of editor scale"),
        FMath::IsNearlyEqual(Migrated.ResolutionScale, 83.3332977f));
    TestEqual(TEXT("Legacy individual quality preserved"), Migrated.Textures, 1);
    const auto* Width = FindFProperty<FIntProperty>(Settings->GetClass(), TEXT("DesiredScreenWidth"));
    const auto* Height = FindFProperty<FIntProperty>(Settings->GetClass(), TEXT("DesiredScreenHeight"));
    if (TestNotNull(TEXT("Desired width reflected"), Width) && TestNotNull(TEXT("Desired height reflected"), Height))
    {
        TestEqual(TEXT("Load and validation preserve desired width"),
            Width->GetPropertyValue_InContainer(Settings), 1280);
        TestEqual(TEXT("Load and validation preserve desired height"),
            Height->GetPropertyValue_InContainer(Settings), 720);
    }
    FString AfterLoad;
    FFileHelper::LoadFileToString(AfterLoad, *Path);
    TestEqual(TEXT("Loading never rewrites the legacy fixture"), AfterLoad, LegacyText);

    const FString CurrentText = LegacyText
        + TEXT("[/Script/ANANTA.ANANTAGraphicsSettings]\nFrameRateLimit=144\nLanguage=en\nbShowFPS=True\n");
    TestTrue(TEXT("Write isolated current fixture"), FFileHelper::SaveStringToFile(CurrentText, *Path));
    FConfigFile CurrentFixture;
    CurrentFixture.Read(Path);
    IsolatedConfig.SetFile(GGameUserSettingsIni, &CurrentFixture);
    Settings->LoadSettings();
    TestEqual(TEXT("Existing subclass takes precedence over legacy"), Settings->GetFrameRateLimit(), 144.0f);
    TestEqual(TEXT("Existing subclass language preserved"), Settings->GetLanguage(), FString(TEXT("en")));
    TestTrue(TEXT("Existing subclass FPS toggle preserved"), Settings->IsFPSVisible());
    if (GIsEditor)
    {
        TestTrue(TEXT("Current subclass still uses editor scalability"),
            FMath::IsNearlyEqual(Settings->CaptureOptions().ResolutionScale, 66.666667f));
    }
    return true;
}
#endif
