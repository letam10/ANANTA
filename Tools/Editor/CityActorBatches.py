"""Yield persisted actors in bounded loads; release references between batches."""

import unreal


def batches(descriptors, size=1000):
    library = unreal.WorldPartitionBlueprintLibrary
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    guids = [item.guid for item in descriptors if item.native_class.get_name() != "WorldPartitionHLOD"]
    library.unload_actors(guids)
    for offset in range(0, len(guids), size):
        selected = guids[offset:offset + size]
        library.load_actors(selected)
        wanted = {unreal.GuidLibrary.conv_guid_to_string(guid) for guid in selected}
        loaded = [actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
                  if unreal.GuidLibrary.conv_guid_to_string(actor.get_editor_property("actor_guid")) in wanted]
        actual = {unreal.GuidLibrary.conv_guid_to_string(actor.get_editor_property("actor_guid"))
                  for actor in loaded}
        unknown = wanted - actual
        missing = [f"{d.label}:{d.native_class.get_name()}" for d in descriptors
                   if unreal.GuidLibrary.conv_guid_to_string(d.guid) in unknown] if unknown else []
        assert not missing, f"Missing actors at {offset}: {missing}"
        yield loaded
        del loaded
        library.unload_actors(selected)
        unreal.SystemLibrary.collect_garbage()
        unreal.log(f"CITY_READBACK_BATCH {offset + len(selected)}/{len(guids)}")
