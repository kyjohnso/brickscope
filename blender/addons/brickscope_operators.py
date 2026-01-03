"""
BrickScope Operators
"""

import bpy
from bpy.types import Operator
from .ldraw_wrapper import LDrawImporter
from .part_cache import get_part_cache
from .brickscope_preferences import get_preferences


class BRICKSCOPE_OT_hello_world(Operator):
    """Test operator to verify addon is working"""
    bl_idname = "brickscope.hello_world"
    bl_label = "Hello World"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "BrickScope addon is working! Hot-reload test successful!")
        print("BrickScope: Hello World executed!")
        return {'FINISHED'}


class BRICKSCOPE_OT_test_ldraw_import(Operator):
    """Test LDraw import and caching system"""
    bl_idname = "brickscope.test_ldraw_import"
    bl_label = "Test LDraw Import"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = get_preferences(context)

        if not prefs.ldraw_library_path:
            self.report({'ERROR'}, "LDraw library path not set. Configure in preferences.")
            return {'CANCELLED'}

        # Initialize importer
        importer = LDrawImporter(prefs.ldraw_library_path)

        if not importer.has_ldr_tools:
            self.report({'WARNING'},
                       "ldr_tools_blender not installed. Install from github.com/ScanMountGoat/ldr_tools_blender")
            return {'CANCELLED'}

        # Test import a simple brick
        self.report({'INFO'}, f"Testing import from: {prefs.ldraw_library_path}")

        obj = importer.import_part("3001")  # 2x4 brick
        if obj:
            self.report({'INFO'}, f"Successfully imported test part: {obj.name}")
        else:
            self.report({'WARNING'}, "Import returned None (may be placeholder)")

        return {'FINISHED'}


class BRICKSCOPE_OT_clear_scene(Operator):
    """Clear scene (remove all mesh objects)"""
    bl_idname = "brickscope.clear_scene"
    bl_label = "Clear Scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Select all mesh objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in context.scene.objects:
            if obj.type == 'MESH':
                obj.select_set(True)

        # Delete selected
        bpy.ops.object.delete()

        self.report({'INFO'}, "Scene cleared")
        return {'FINISHED'}


class BRICKSCOPE_OT_clear_cache(Operator):
    """Clear part cache"""
    bl_idname = "brickscope.clear_cache"
    bl_label = "Clear Part Cache"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cache = get_part_cache()
        stats = cache.get_stats()
        cache.clear()

        self.report({'INFO'},
                   f"Cleared cache: {stats['cached_parts']} parts "
                   f"({stats['unique_part_ids']} unique part IDs)")
        return {'FINISHED'}
