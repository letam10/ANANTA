using UnrealBuildTool;

public class ANANTA : ModuleRules
{
	public ANANTA(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"InputCore",
				"UMG",
				"AIModule",
				"NavigationSystem"
			});
	}
}
