"""Create the initial ANANTA content layout inside a running UE Editor.

This script is intentionally idempotent and only creates Content Browser
folders. It does not import external assets, modify source assets, or create
actors in a level.
"""

import unreal


CONTENT_FOLDERS = (
    "/Game/ANANTA",
    "/Game/ANANTA/Characters",
    "/Game/ANANTA/Combat",
    "/Game/ANANTA/Environment",
    "/Game/ANANTA/Environment/Materials",
    "/Game/ANANTA/Environment/PCG",
    "/Game/ANANTA/Environment/Props",
    "/Game/ANANTA/UI",
    "/Game/ANANTA/Audio",
    "/Game/ANANTA/Quests",
    "/Game/ANANTA/VFX",
)


def main():
    created = []
    for folder in CONTENT_FOLDERS:
        if not unreal.EditorAssetLibrary.does_directory_exist(folder):
            unreal.EditorAssetLibrary.make_directory(folder)
            created.append(folder)

    unreal.log("ANANTA foundation folders ready: {} created, {} total".format(
        len(created), len(CONTENT_FOLDERS)
    ))
    for folder in created:
        unreal.log("  created {}".format(folder))


if __name__ == "__main__":
    main()
