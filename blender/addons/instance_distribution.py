"""
Instance Distribution - Geometry nodes visualization of distributions
Shows parts as lightweight instances using geometry nodes
"""

import bpy
from bpy.types import Operator
import random


class BRICKSCOPE_OT_generate_instance_distribution(Operator):
    """Generate geometry nodes instance distribution"""
    bl_idname = "brickscope.generate_instance_distribution"
    bl_label = "Generate Instance Distribution"
    bl_options = {'REGISTER', 'UNDO'}

    distribution_mode: bpy.props.EnumProperty(
        name="Distribution Mode",
        items=[
            ('VOLUME', "Volume", "Distribute points in a volume"),
            ('FACES', "Faces", "Distribute points on faces of a plane"),
        ],
        default='VOLUME'
    )

    def execute(self, context):
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

        # Sample distribution to get part+color pairs
        self.report({'INFO'}, f"Sampling distribution for {props.total_pieces} pieces...")
        pairs = config.generate_part_color_pairs()

        # Initialize importer and cache
        importer = LDrawImporter(prefs.ldraw_library_path)
        cache = get_part_cache()

        if not importer.has_ldr_tools:
            self.report({'ERROR'}, "ldr_tools_blender not found. Install from github.com/ScanMountGoat/ldr_tools_blender")
            return {'CANCELLED'}

        # Import all unique part+color combinations
        # For geometry nodes, we need visible reference objects (not hidden cache)
        unique_combos = list(set(pairs))
        self.report({'INFO'}, f"Importing {len(unique_combos)} unique part+color combinations...")

        # Create a collection for geometry node reference objects (VISIBLE)
        ref_collection_name = "BrickScope_GeoNodeReferences"
        if ref_collection_name in bpy.data.collections:
            ref_collection = bpy.data.collections[ref_collection_name]
            # Clear existing objects
            for obj in list(ref_collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
        else:
            ref_collection = bpy.data.collections.new(ref_collection_name)
            context.scene.collection.children.link(ref_collection)
            # Keep collection visible (don't hide!)

        combo_to_object = {}
        for part_id, color_id in unique_combos:
            color_id_int = int(color_id)

            # Import parts (they stay visible in the reference collection)
            obj = importer.import_part(part_id, color_id_int, location=(0, 0, 0))
            if obj:
                # Move to reference collection
                for col in obj.users_collection:
                    col.objects.unlink(obj)
                ref_collection.objects.link(obj)
                obj.name = f"geonode_ref_{part_id}_color{color_id_int}"

                combo_to_object[(part_id, color_id)] = obj
            else:
                self.report({'WARNING'}, f"Failed to import {part_id} color {color_id_int}")

        # Create collection for instances
        collection_name = "BrickScope_Instances"
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
        else:
            collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(collection)

        # Create base geometry (volume or plane)
        if self.distribution_mode == 'VOLUME':
            bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
            base_obj = context.active_object
            base_obj.name = "BrickScope_InstanceVolume"
        else:  # FACES
            bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
            base_obj = context.active_object
            base_obj.name = "BrickScope_InstancePlane"

        # Link to collection
        for col in base_obj.users_collection:
            col.objects.unlink(base_obj)
        collection.objects.link(base_obj)

        # Create geometry nodes modifier
        modifier = base_obj.modifiers.new(name="InstanceDistribution", type='NODES')

        # Build geometry nodes tree
        self._build_geometry_nodes_tree(
            modifier,
            pairs,
            combo_to_object,
            self.distribution_mode
        )

        self.report({'INFO'}, f"Generated instance distribution with {len(pairs)} instances from {len(unique_combos)} unique parts")
        return {'FINISHED'}

    def _build_geometry_nodes_tree(self, modifier, pairs, combo_to_object, mode):
        """
        Build a geometry nodes tree for instancing

        Strategy: Create separate point distributions for each part+color combo,
        then join them all together. This avoids complex weighted random in geo nodes.
        """
        from collections import Counter

        # Count occurrences of each combo
        combo_counts = Counter(pairs)

        # Create node group
        node_group = bpy.data.node_groups.new(name="BrickScope_InstanceDistribution", type='GeometryNodeTree')
        modifier.node_group = node_group

        # Add input/output nodes
        nodes = node_group.nodes
        input_node = nodes.new('NodeGroupInput')
        output_node = nodes.new('NodeGroupOutput')
        input_node.location = (-800, 0)
        output_node.location = (600, 0)

        # Create group input/output sockets
        node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

        # Calculate volume/area for density calculation
        if mode == 'VOLUME':
            total_space = 8.0  # 2x2x2 cube
        else:
            total_space = 16.0  # 4x4 plane

        # Add mesh to volume conversion if in volume mode
        mesh_to_volume_node = None
        if mode == 'VOLUME':
            mesh_to_volume_node = nodes.new('GeometryNodeMeshToVolume')
            mesh_to_volume_node.location = (-600, 0)
            links = node_group.links
            links.new(input_node.outputs['Geometry'], mesh_to_volume_node.inputs['Mesh'])

        # Create a separate distribution + instance for each combo
        instance_geometries = []
        y_offset = 0

        for idx, (combo, count) in enumerate(combo_counts.items()):
            if combo not in combo_to_object:
                continue

            obj = combo_to_object[combo]

            # Create distribute points node
            if mode == 'VOLUME':
                distribute_node = nodes.new('GeometryNodeDistributePointsInVolume')
                distribute_node.inputs['Density'].default_value = count / total_space
                geometry_input_name = 'Volume'  # Volume mode uses 'Volume' input
            else:
                distribute_node = nodes.new('GeometryNodeDistributePointsOnFaces')
                distribute_node.inputs['Density'].default_value = count / total_space
                geometry_input_name = 'Mesh'  # Face mode uses 'Mesh' input

            distribute_node.location = (-400, y_offset)
            distribute_node.inputs['Seed'].default_value = idx  # Different seed per combo

            # Create instance on points node
            instance_node = nodes.new('GeometryNodeInstanceOnPoints')
            instance_node.location = (-100, y_offset)

            # Set the object to instance
            object_info_node = nodes.new('GeometryNodeObjectInfo')
            object_info_node.location = (-300, y_offset - 150)
            object_info_node.inputs['Object'].default_value = obj
            object_info_node.transform_space = 'RELATIVE'

            # Connect nodes
            links = node_group.links

            # Connect input geometry to distribute node (with mesh to volume conversion if needed)
            if mode == 'VOLUME':
                links.new(mesh_to_volume_node.outputs['Volume'], distribute_node.inputs[geometry_input_name])
            else:
                links.new(input_node.outputs['Geometry'], distribute_node.inputs[geometry_input_name])

            links.new(distribute_node.outputs['Points'], instance_node.inputs['Points'])
            links.new(object_info_node.outputs['Geometry'], instance_node.inputs['Instance'])

            instance_geometries.append((instance_node, y_offset))
            y_offset -= 300  # Stack nodes vertically

        # Join all instance geometries
        if len(instance_geometries) > 1:
            # Create join geometry nodes to merge all
            join_node = nodes.new('GeometryNodeJoinGeometry')
            join_node.location = (200, 0)

            links = node_group.links
            for instance_node, _ in instance_geometries:
                links.new(instance_node.outputs['Instances'], join_node.inputs['Geometry'])

            links.new(join_node.outputs['Geometry'], output_node.inputs['Geometry'])
        elif len(instance_geometries) == 1:
            # Only one combo, connect directly
            links = node_group.links
            links.new(instance_geometries[0][0].outputs['Instances'], output_node.inputs['Geometry'])

        return node_group
