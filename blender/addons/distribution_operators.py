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
    """Import LEGO parts based on distribution weights"""
    bl_idname = "brickscope.bake_distribution"
    bl_label = "Bake Distribution"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import random
        import math
        from .distribution_manager import DistributionConfig, WeightedDistribution, DistributionItem
        from .ldraw_wrapper import LDrawImporter
        from .part_cache import get_part_cache
        from .brickscope_preferences import get_preferences

        props = context.scene.brickscope_distribution
        prefs = get_preferences(context)

        # Validate
        if len(props.parts) == 0:
            self.report({'ERROR'}, "No parts in distribution. Click 'Load Defaults' first.")
            return {'CANCELLED'}

        if len(props.colors) == 0:
            self.report({'ERROR'}, "No colors in distribution. Click 'Load Defaults' first.")
            return {'CANCELLED'}

        if not prefs.ldraw_library_path:
            self.report({'ERROR'}, "LDraw library path not set")
            return {'CANCELLED'}

        # Convert Blender properties to DistributionConfig
        part_dist = WeightedDistribution()
        for item in props.parts:
            part_dist.items.append(DistributionItem(item.part_id, item.part_name, item.weight))

        color_dist = WeightedDistribution()
        for item in props.colors:
            color_dist.items.append(DistributionItem(item.color_id, item.color_name, item.weight))

        config = DistributionConfig(
            part_distribution=part_dist,
            color_distribution=color_dist,
            total_pieces=props.total_pieces,
            seed=props.random_seed if props.random_seed > 0 else None
        )

        # Sample distribution
        self.report({'INFO'}, f"Sampling distribution for {props.total_pieces} pieces...")
        pairs = config.generate_part_color_pairs()

        # Initialize importer and cache
        importer = LDrawImporter(prefs.ldraw_library_path)
        cache = get_part_cache()

        if not importer.has_ldr_tools:
            self.report({'ERROR'}, "ldr_tools_blender not found. Install from github.com/ScanMountGoat/ldr_tools_blender")
            return {'CANCELLED'}

        # Import parts (with progress)
        self.report({'INFO'}, f"Importing {len(pairs)} parts...")

        imported_objects = []

        # Create mappings for unique part IDs and colors to positions
        unique_part_ids = list(set(part_id for part_id, _ in pairs))
        unique_colors = list(set(color_id for _, color_id in pairs))

        part_id_to_x = {part_id: idx for idx, part_id in enumerate(unique_part_ids)}
        color_id_to_y = {color_id: idx for idx, color_id in enumerate(unique_colors)}

        print(f"Part ID mapping: {part_id_to_x}")
        print(f"Color ID mapping: {color_id_to_y}")

        # Track count of each (part_id, color_id) combination for Z stacking
        part_color_count = {}
        z_spacing = 0.5  # Blender units between stacked parts

        for idx, (part_id, color_id) in enumerate(pairs):
            # Report progress every 10 parts
            if idx % 10 == 0:
                self.report({'INFO'}, f"Importing part {idx+1}/{len(pairs)}...")

            color_id_int = int(color_id)

            # Track how many times we've seen this part+color combination
            combo_key = (part_id, color_id)
            if combo_key not in part_color_count:
                part_color_count[combo_key] = 0
            else:
                part_color_count[combo_key] += 1

            # Calculate position based on part type (X), color (Y), and repetition (Z)
            x_pos = part_id_to_x[part_id] * 1.0  # 1 Blender unit per part type
            y_pos = color_id_to_y[color_id] * 1.0  # 1 Blender unit per color
            z_pos = part_color_count[combo_key] * z_spacing  # Stack duplicates in Z

            print(f"=== IMPORTING Part {idx}: {part_id} color {color_id} (instance #{part_color_count[combo_key]}) -> X={x_pos}, Y={y_pos}, Z={z_pos} ===")

            # Import part and translate it during import
            obj = importer.import_part(part_id, color_id_int, location=(x_pos, y_pos, z_pos))

            if obj:
                print(f"=== RESULT: {obj.name} final location = {obj.location} ===")
                imported_objects.append(obj)
            else:
                print(f"=== FAILED to import part {part_id} color {color_id} ===")

        # Report results
        cache_stats = cache.get_stats()
        self.report({'INFO'},
                   f"Successfully imported {len(imported_objects)} parts! "
                   f"Cache: {cache_stats['cached_parts']} unique parts, "
                   f"{cache_stats['unique_part_ids']} part IDs, "
                   f"{cache_stats['unique_colors']} colors")

        return {'FINISHED'}
