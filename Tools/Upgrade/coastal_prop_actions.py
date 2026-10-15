"""Đặt các prop nhỏ có thể tương tác trong cảnh coastal."""

import unreal


def place_interactive_prop(scene, label, model, position, message, yaw=0, scale=(1, 1, 1)):
    """Đặt prop tương tác loại nhỏ và trả về actor vừa tạo."""
    action_name = " ".join(str(label).replace("_", " ").split())
    actor = scene.action(
        action_name,
        position,
        message,
        kind=5,
        model=model,
        yaw=yaw,
    )
    actor.action_name = action_name
    scale_values = tuple(scale)
    if scale_values != (1, 1, 1):
        actor.mesh.set_relative_scale3d(unreal.Vector(*scale_values))
    return actor
