"""Run isolated W3 authoring in an initialized rendered editor.

Use the bridge capture_scene_png action separately for each contract camera.
No Slate callback or nested screenshot request is registered here.
"""

from pathlib import Path
import runpy

TASK = Path("D:/GAME/ANANTA/Tools/Continuation_20261020")
runpy.run_path(str(TASK / "ApplyWaterW3.py"), run_name="__main__")
