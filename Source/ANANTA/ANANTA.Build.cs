using UnrealBuildTool;

public class ANANTA : ModuleRules
{
	public ANANTA(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PrivateDependencyModuleNames.Add("Json");

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"InputCore",
				"Json",
				"UMG",
				"Slate",
				"SlateCore",
				"RenderCore",
				"RHI",
				"AIModule",
				"NavigationSystem"

			});
	}
}
