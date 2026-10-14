"""Capture saved editor geometry only. Never start PIE, Simulate or a game world."""

import json
from datetime import datetime, timezone
from pathlib import Path

import unreal


def main():
    root = Path(unreal.Paths.project_dir())
    layout = json.loads((root / "Saved/Upgrade/city-layout.json").read_text(encoding="utf-8"))
    output = root / "Saved/Upgrade/EditorViews" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output.mkdir(parents=True, exist_ok=True)
    assert unreal.EditorLoadingAndSavingUtils.load_map(layout["map"])
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actor = subsystem.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 400))
    component = actor.get_component_by_class(unreal.SceneCaptureComponent2D)
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    component.set_editor_property("always_persist_rendering_state", True)
    component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)
    component.set_editor_property("fov_angle", 90)
    target = unreal.RenderingLibrary.create_render_target2d(
        world, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    component.set_editor_property("texture_target", target)
    settings = component.get_editor_property("post_process_settings")
    settings.override_auto_exposure_min_brightness = True
    settings.override_auto_exposure_max_brightness = True
    settings.auto_exposure_min_brightness = 4
    settings.auto_exposure_max_brightness = 4
    component.set_editor_property("post_process_settings", settings)
    component.set_editor_property("post_process_blend_weight", 1)
    views = layout["review_views"]
    # Một lượt ngắn cho mỗi ảnh; không có input, tick gameplay hay đo FPS.
    for view in views:
        position = unreal.Vector(*(value * 100 for value in view["position_m"]))
        target_position = unreal.Vector(*(value * 100 for value in view["target_m"]))
        actor.set_actor_location(position, False, False)
        actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(position, target_position), False)
        for sample in range(4):
            component.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, target, str(output), view["name"] + ".png")
        assert (output / (view["name"] + ".png")).is_file(), view["name"]
    subsystem.destroy_actor(actor)
    report = {"map": layout["map"], "mode": "editor_base_color_no_gameplay",
              "visual_acceptance": "pending ComposeEditorReviews and human image inspection",
              "views": views, "folder": str(output)}
    (output / "coverage.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (root / "Saved/Upgrade/latest-editor-views.txt").write_text(str(output), encoding="utf-8")
    unreal.log(f"COASTAL_EDITOR_EXPORTED {len(views)} images; pixel validation is still required")


if __name__ == "__main__":
    main()
