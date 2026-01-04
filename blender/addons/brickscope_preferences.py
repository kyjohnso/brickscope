"""
BrickScope Preferences
User settings and configuration
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty


class BrickScopePreferences(AddonPreferences):
    """Extension preferences shown in Edit → Preferences → Get Extensions → BrickScope"""
    bl_idname = __package__

    ldraw_library_path: StringProperty(
        name="LDraw Library Path",
        description="Path to LDraw parts library (download from ldraw.org)",
        default="",  # Let user set, or use auto-detect
        subtype='DIR_PATH',
    )

    output_directory: StringProperty(
        name="Output Directory",
        description="Default output directory for generated datasets",
        default="//",  # Relative to .blend file
        subtype='DIR_PATH',
    )

    default_resolution: IntProperty(
        name="Default Resolution",
        description="Default image resolution (square)",
        default=1024,
        min=256,
        max=4096,
    )

    default_samples: IntProperty(
        name="Default Render Samples",
        description="Default Cycles render samples",
        default=128,
        min=16,
        max=512,
    )

    use_gpu: BoolProperty(
        name="Use GPU for Rendering",
        description="Enable GPU acceleration for Cycles (if available)",
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Required Dependencies", icon='INFO')
        box.label(text="Install ldr_tools_blender from:")
        box.label(text="  github.com/ScanMountGoat/ldr_tools_blender")

        layout.separator()

        box = layout.box()
        box.label(text="Asset Paths", icon='FILE_FOLDER')

        # LDraw path with helper button
        row = box.row()
        row.prop(self, "ldraw_library_path")
        row.operator("brickscope.set_default_ldraw_path", text="", icon='FILE_REFRESH')

        box.prop(self, "output_directory")

        layout.separator()

        box = layout.box()
        box.label(text="Default Settings", icon='SETTINGS')
        box.prop(self, "default_resolution")
        box.prop(self, "default_samples")
        box.prop(self, "use_gpu")


def get_preferences(context=None):
    """Helper to get addon preferences"""
    if context is None:
        context = bpy.context
    return context.preferences.addons[__package__].preferences
