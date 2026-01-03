"""
BrickScope UI Panel
"""

import bpy
from bpy.types import Panel


class BRICKSCOPE_PT_main_panel(Panel):
    """Main BrickScope panel in 3D viewport sidebar"""
    bl_label = "Dataset Generator"
    bl_idname = "BRICKSCOPE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BrickScope'  # This creates the "BrickScope" tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Header
        box = layout.box()
        box.label(text="Synthetic LEGO Data Generator", icon='RENDERLAYERS')

        # Quick test section
        box = layout.box()
        box.label(text="Quick Test", icon='PLAY')
        box.operator("brickscope.hello_world", icon='WORLD', text="Test Button")

        # Info
        layout.separator()
        layout.label(text="Extension loaded successfully!", icon='CHECKMARK')
