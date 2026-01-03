"""
BrickScope Operators
"""

import bpy
from bpy.types import Operator


class BRICKSCOPE_OT_hello_world(Operator):
    """Test operator to verify addon is working"""
    bl_idname = "brickscope.hello_world"
    bl_label = "Hello World"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "BrickScope addon is working! Hot-reload test successful!")
        print("BrickScope: Hello World executed!")
        return {'FINISHED'}
