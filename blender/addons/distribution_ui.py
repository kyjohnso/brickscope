"""
Distribution UI - UILists for parts and colors with weight sliders
"""

import bpy
from bpy.types import UIList


class BRICKSCOPE_UL_parts(UIList):
    """UIList for part distribution"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Part ID and name
            row = layout.row(align=True)
            row.prop(item, "part_id", text="", emboss=False)
            row.label(text=item.part_name)

            # Weight slider
            row = layout.row(align=True)
            row.prop(item, "weight", text="", slider=True)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.part_id)


class BRICKSCOPE_UL_colors(UIList):
    """UIList for color distribution"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Color ID and name
            row = layout.row(align=True)
            row.prop(item, "color_id", text="", emboss=False)
            row.label(text=item.color_name)

            # Weight slider
            row = layout.row(align=True)
            row.prop(item, "weight", text="", slider=True)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.color_name)


class BRICKSCOPE_PT_distribution_panel(bpy.types.Panel):
    """Distribution control panel"""
    bl_label = "Distribution Control"
    bl_idname = "BRICKSCOPE_PT_distribution_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BrickScope'
    bl_order = 1  # Show after main panel

    def draw(self, context):
        layout = self.layout
        props = context.scene.brickscope_distribution

        # Quick actions
        box = layout.box()
        box.label(text="Quick Actions", icon='PREFERENCES')
        box.operator("brickscope.initialize_defaults", icon='FILE_REFRESH')

        # Part Distribution
        box = layout.box()
        box.label(text="Part Distribution", icon='MESH_CUBE')

        row = box.row()
        row.template_list(
            "BRICKSCOPE_UL_parts", "",
            props, "parts",
            props, "parts_active_index",
            rows=4
        )

        col = row.column(align=True)
        col.operator("brickscope.add_part", icon='ADD', text="")
        col.operator("brickscope.remove_part", icon='REMOVE', text="")
        col.separator()
        col.operator("brickscope.normalize_weights", icon='NORMALIZE_FCURVES', text="").distribution_type = 'PARTS'

        # Show stats
        if len(props.parts) > 0:
            total_weight = sum(p.weight for p in props.parts)
            box.label(text=f"Parts: {len(props.parts)}, Total Weight: {total_weight:.2f}")

        # Color Distribution
        box = layout.box()
        box.label(text="Color Distribution", icon='COLOR')

        row = box.row()
        row.template_list(
            "BRICKSCOPE_UL_colors", "",
            props, "colors",
            props, "colors_active_index",
            rows=4
        )

        col = row.column(align=True)
        col.operator("brickscope.add_color", icon='ADD', text="")
        col.operator("brickscope.remove_color", icon='REMOVE', text="")
        col.separator()
        col.operator("brickscope.normalize_weights", icon='NORMALIZE_FCURVES', text="").distribution_type = 'COLORS'

        # Show stats
        if len(props.colors) > 0:
            total_weight = sum(c.weight for c in props.colors)
            box.label(text=f"Colors: {len(props.colors)}, Total Weight: {total_weight:.2f}")

        # Generation Settings
        box = layout.box()
        box.label(text="Generation Settings", icon='SETTINGS')
        box.prop(props, "total_pieces")
        box.prop(props, "random_seed")

        # Actions
        layout.separator()
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("brickscope.generate_instance_distribution", icon='PARTICLES', text="Generate Instances")
        col.operator("brickscope.bake_distribution", icon='MESH_DATA', text="Bake to Real Objects")
