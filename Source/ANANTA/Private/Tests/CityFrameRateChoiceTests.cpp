#if WITH_DEV_AUTOMATION_TESTS
#include "Settings/SCitySettingsPanel.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCityFrameRateChoiceTest, "ANANTA.City.Settings.CustomFrameRateChoice",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCityFrameRateChoiceTest::RunTest(const FString& Parameters)
{
    const TArray<int32> Legacy = { 0, 30, 60, 90, 120, 144, 165, 180, 240 };
    TestEqual(TEXT("Legacy menu has no selected item for valid cap 200"), Legacy.IndexOfByKey(200), INDEX_NONE);
    for (const float Current : {200.0f, 200.5f, 90.0f, 0.0f})
    {
        FCityGraphicsOptions Input;
        Input.FrameRateLimit = Current;
        const float Accepted = UANANTAGraphicsSettings::SanitizeOptions(Input).FrameRateLimit;
        TestEqual(TEXT("Backend accepts the precise current cap"), Accepted, Current);
        const TArray<float> Choices = SCitySettingsPanel::FrameRateChoices(Accepted);
        const int32 Selected = Choices.IndexOfByKey(Current);
        if (TestTrue(TEXT("Menu can select the precise persisted cap"), Choices.IsValidIndex(Selected)))
        {
            TestEqual(TEXT("Selection restores the exact cap without integer rounding"), Choices[Selected], Current);
        }
        for (const int32 Common : Legacy)
        {
            TestTrue(TEXT("Existing frame rate presets remain selectable"), Choices.Contains(float(Common)));
        }
        for (int32 Index = 1; Index < Choices.Num(); ++Index)
        {
            TestTrue(TEXT("Menu choices are sorted and unique"), Choices[Index - 1] < Choices[Index]);
        }
    }
    return true;
}
#endif
