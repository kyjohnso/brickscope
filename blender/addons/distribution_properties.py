"""
Distribution Properties - Blender properties for part/color distributions
"""

import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
    IntProperty,
    CollectionProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup


class PartDistributionItem(PropertyGroup):
    """Single part in the distribution with weight"""

    part_id: StringProperty(
        name="Part ID",
        description="LDraw part number (e.g., 3001 for 2x4 brick)",
        default="3001"
    )

    part_name: StringProperty(
        name="Part Name",
        description="Human-readable name",
        default="Brick 2x4"
    )

    weight: FloatProperty(
        name="Weight",
        description="Relative probability of this part appearing",
        default=1.0,
        min=0.0,
        max=10.0,
        soft_max=2.0,
    )


class ColorDistributionItem(PropertyGroup):
    """Single color in the distribution with weight"""

    color_id: StringProperty(
        name="Color ID",
        description="LDraw color code (e.g., 4 for red)",
        default="4"
    )

    color_name: StringProperty(
        name="Color Name",
        description="Human-readable color name",
        default="Red"
    )

    weight: FloatProperty(
        name="Weight",
        description="Relative probability of this color appearing",
        default=1.0,
        min=0.0,
        max=10.0,
        soft_max=2.0,
    )


class DistributionProperties(PropertyGroup):
    """Distribution configuration stored in scene"""

    # Part distribution
    parts: CollectionProperty(
        type=PartDistributionItem,
        name="Parts",
        description="List of parts with weights"
    )

    parts_active_index: IntProperty(
        name="Active Part Index",
        description="Index of selected part in list",
        default=0
    )

    # Color distribution
    colors: CollectionProperty(
        type=ColorDistributionItem,
        name="Colors",
        description="List of colors with weights"
    )

    colors_active_index: IntProperty(
        name="Active Color Index",
        description="Index of selected color in list",
        default=0
    )

    # Generation settings
    total_pieces: IntProperty(
        name="Total Pieces",
        description="Number of pieces to generate in the scene",
        default=100,
        min=1,
        max=1000,
        soft_max=200,
    )

    random_seed: IntProperty(
        name="Random Seed",
        description="Seed for reproducible generation (0 = random)",
        default=0,
        min=0,
    )

    # Preview mode
    preview_enabled: bpy.props.BoolProperty(
        name="Preview Mode",
        description="Show real-time preview using geometry nodes",
        default=False
    )


def initialize_default_distributions(context):
    """Initialize with common parts and colors"""
    props = context.scene.brickscope_distribution

    # Clear existing
    props.parts.clear()
    props.colors.clear()

    # Add common parts
    common_parts = [
        ("3001", "Brick 2x4", 1.0),
        ("3002", "Brick 2x3", 0.8),
        ("3003", "Brick 2x2", 0.9),
        ("3004", "Brick 1x2", 1.0),
        ("3005", "Brick 1x1", 0.7),
        ("3021", "Plate 2x3", 0.6),
        ("3022", "Plate 2x2", 0.7),
        ("3023", "Plate 1x2", 0.8),
        ("3024", "Plate 1x1", 0.5),
    ]

    for part_id, name, weight in common_parts:
        item = props.parts.add()
        item.part_id = part_id
        item.part_name = name
        item.weight = weight

    # Add common colors
    common_colors = [
        ("4", "Red", 1.0),
        ("1", "Blue", 1.0),
        ("2", "Green", 0.8),
        ("14", "Yellow", 0.9),
        ("0", "Black", 0.7),
        ("15", "White", 0.7),
        ("72", "Dark Gray", 0.5),
    ]

    for color_id, name, weight in common_colors:
        item = props.colors.add()
        item.color_id = color_id
        item.color_name = name
        item.weight = weight


# Note: Registration is handled by auto_load.py
# Scene property is registered in __init__.py after all classes are registered
