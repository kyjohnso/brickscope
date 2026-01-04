"""
Distribution Operators - Add/remove/manage part and color distributions
"""

import bpy
from bpy.types import Operator
from .distribution_properties import initialize_default_distributions


class BRICKSCOPE_OT_add_part(Operator):
    """Add a new part to the distribution"""
    bl_idname = "brickscope.add_part"
    bl_label = "Add Part"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.brickscope_distribution
        item = props.parts.add()
        item.part_id = "3001"
        item.part_name = "New Part"
        item.weight = 1.0
        props.parts_active_index = len(props.parts) - 1
        return {'FINISHED'}


class BRICKSCOPE_OT_remove_part(Operator):
    """Remove selected part from the distribution"""
    bl_idname = "brickscope.remove_part"
    bl_label = "Remove Part"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.scene.brickscope_distribution
        return len(props.parts) > 0

    def execute(self, context):
        props = context.scene.brickscope_distribution
        props.parts.remove(props.parts_active_index)
        props.parts_active_index = min(props.parts_active_index, len(props.parts) - 1)
        return {'FINISHED'}


class BRICKSCOPE_OT_add_color(Operator):
    """Add a new color to the distribution"""
    bl_idname = "brickscope.add_color"
    bl_label = "Add Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.brickscope_distribution
        item = props.colors.add()
        item.color_id = "4"
        item.color_name = "New Color"
        item.weight = 1.0
        props.colors_active_index = len(props.colors) - 1
        return {'FINISHED'}


class BRICKSCOPE_OT_remove_color(Operator):
    """Remove selected color from the distribution"""
    bl_idname = "brickscope.remove_color"
    bl_label = "Remove Color"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.scene.brickscope_distribution
        return len(props.colors) > 0

    def execute(self, context):
        props = context.scene.brickscope_distribution
        props.colors.remove(props.colors_active_index)
        props.colors_active_index = min(props.colors_active_index, len(props.colors) - 1)
        return {'FINISHED'}


class BRICKSCOPE_OT_initialize_defaults(Operator):
    """Initialize with common parts and colors"""
    bl_idname = "brickscope.initialize_defaults"
    bl_label = "Load Defaults"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        initialize_default_distributions(context)
        self.report({'INFO'}, "Loaded default distributions")
        return {'FINISHED'}


class BRICKSCOPE_OT_normalize_weights(Operator):
    """Normalize all weights to sum to 1.0"""
    bl_idname = "brickscope.normalize_weights"
    bl_label = "Normalize Weights"
    bl_options = {'REGISTER', 'UNDO'}

    distribution_type: bpy.props.EnumProperty(
        items=[
            ('PARTS', "Parts", "Normalize part weights"),
            ('COLORS', "Colors", "Normalize color weights"),
        ]
    )

    def execute(self, context):
        props = context.scene.brickscope_distribution

        if self.distribution_type == 'PARTS':
            items = props.parts
            name = "part"
        else:
            items = props.colors
            name = "color"

        total = sum(item.weight for item in items)

        if total == 0:
            self.report({'WARNING'}, f"Cannot normalize - all {name} weights are 0")
            return {'CANCELLED'}

        for item in items:
            item.weight = item.weight / total

        self.report({'INFO'}, f"Normalized {name} weights")
        return {'FINISHED'}


class BRICKSCOPE_OT_generate_preview(Operator):
    """Generate preview using geometry nodes"""
    bl_idname = "brickscope.generate_preview"
    bl_label = "Generate Preview"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # TODO: Implement geometry nodes preview
        self.report({'INFO'}, "Preview generation not yet implemented")
        return {'FINISHED'}


class BRICKSCOPE_OT_bake_distribution(Operator):
    """Bake geometry node instances to real objects"""
    bl_idname = "brickscope.bake_distribution"
    bl_label = "Bake to Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.brickscope_distribution

        # TODO: Implement baking
        # For now, just report the distribution stats

        total_part_weight = sum(p.weight for p in props.parts)
        total_color_weight = sum(c.weight for c in props.colors)

        self.report({'INFO'},
                   f"Will generate {props.total_pieces} pieces: "
                   f"{len(props.parts)} part types (total weight: {total_part_weight:.2f}), "
                   f"{len(props.colors)} colors (total weight: {total_color_weight:.2f})")

        return {'FINISHED'}
