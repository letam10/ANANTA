using UnrealBuildTool;

public class ANANTAEditorTarget : TargetRules
{
    public ANANTAEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("ANANTA");
    }
}
