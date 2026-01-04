"""
Preferences Operators - Helper operators for preferences
"""

import bpy
import os
from pathlib import Path
from bpy.types import Operator


class BRICKSCOPE_OT_set_default_ldraw_path(Operator):
    """Set LDraw path to project default location"""
    bl_idname = "brickscope.set_default_ldraw_path"
    bl_label = "Set Default LDraw Path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences

        # Get home directory (cross-platform)
        home = Path.home()
        default_path = home / "projects" / "brickscope" / "data" / "ldraw"

        # Set the path (as string, fully expanded)
        prefs.ldraw_library_path = str(default_path)

        # Check if it exists
        if default_path.exists():
            self.report({'INFO'}, f"Set LDraw path to: {default_path}")
        else:
            self.report({'WARNING'},
                       f"Set LDraw path to: {default_path} (directory does not exist yet)")

        return {'FINISHED'}
