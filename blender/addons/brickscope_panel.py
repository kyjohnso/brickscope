"""
BrickScope UI Panel
"""

import bpy
from bpy.types import Panel
from .part_cache import get_part_cache
from .brickscope_preferences import get_preferences


class BRICKSCOPE_PT_main_panel(Panel):
    """Main BrickScope panel in 3D viewport sidebar"""
    bl_label = "Dataset Generator"
    bl_idname = "BRICKSCOPE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BrickScope'  # This creates the "BrickScope" tab

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences(context)

        # Header
        box = layout.box()
        box.label(text="Synthetic LEGO Data Generator", icon='RENDERLAYERS')

        # Setup section
        box = layout.box()
        box.label(text="Setup", icon='SETTINGS')

        # Direct path configuration in panel
        box.prop(prefs, "ldraw_library_path", text="LDraw Library")

        if not prefs.ldraw_library_path:
            box.label(text="⚠ Download from ldraw.org", icon='INFO')
        else:
            box.label(text="✓ LDraw path configured", icon='CHECKMARK')

        # Testing section
        box = layout.box()
        box.label(text="Testing", icon='EXPERIMENTAL')
        box.operator("brickscope.test_ldraw_import", icon='IMPORT')
        box.operator("brickscope.hello_world", icon='WORLD', text="Test Extension")

        # Part cache section
        box = layout.box()
        box.label(text="Part Cache", icon='COMMUNITY')

        cache = get_part_cache()
        stats = cache.get_stats()

        row = box.row()
        row.label(text=f"Cached parts: {stats['cached_parts']}")
        row = box.row()
        row.label(text=f"Unique IDs: {stats['unique_part_ids']}")

        box.operator("brickscope.clear_cache", icon='TRASH')

        # Utilities
        layout.separator()
        box = layout.box()
        box.label(text="Utilities", icon='TOOL_SETTINGS')
        box.operator("brickscope.clear_scene", icon='TRASH')
