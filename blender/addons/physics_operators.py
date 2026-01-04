"""
Physics Operators - Setup rigid body physics for LEGO parts
"""

import bpy
from bpy.types import Operator


class BRICKSCOPE_OT_setup_physics(Operator):
    """Setup rigid body physics for realistic brick piles"""
    bl_idname = "brickscope.setup_physics"
    bl_label = "Setup Physics Simulation"
    bl_options = {'REGISTER', 'UNDO'}

    use_mesh_collision: bpy.props.BoolProperty(
        name="Use Mesh Collision",
        description="Use accurate mesh collision (slower but more accurate for complex shapes)",
        default=True
    )

    bounciness: bpy.props.FloatProperty(
        name="Bounciness",
        description="How bouncy the bricks are (0 = no bounce, 1 = perfectly elastic)",
        default=0.4,
        min=0.0,
        max=1.0
    )

    friction: bpy.props.FloatProperty(
        name="Friction",
        description="Surface friction (0 = slippery, 1 = sticky)",
        default=0.5,
        min=0.0,
        max=1.0
    )

    mass: bpy.props.FloatProperty(
        name="Mass",
        description="Mass of each brick in kg",
        default=0.01,
        min=0.001,
        max=10.0
    )

    def execute(self, context):
        # Get selected objects or all objects in BrickScope_Instances collection
        # IMPORTANT: Only add rigid body to MESH objects, not empties
        target_objects = []

        if context.selected_objects:
            target_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        else:
            # Try to find BrickScope_Instances collection
            if "BrickScope_Instances" in bpy.data.collections:
                collection = bpy.data.collections["BrickScope_Instances"]
                target_objects = [obj for obj in collection.all_objects if obj.type == 'MESH']

        if not target_objects:
            self.report({'ERROR'}, "No mesh objects found. Select mesh objects or use baked distribution.")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Found {len(target_objects)} mesh objects to add physics to...")

        # Create ground plane if it doesn't exist
        ground_plane = self._setup_ground_plane(context)

        # Setup rigid body physics on all target objects
        physics_count = 0
        for obj in target_objects:
            if self._setup_rigid_body(obj):
                physics_count += 1

        self.report({'INFO'}, f"Setup physics on {physics_count} objects with ground plane")
        return {'FINISHED'}

    def _setup_ground_plane(self, context):
        """Create or update ground plane with passive rigid body"""
        plane_name = "BrickScope_GroundPlane"

        # Check if ground plane already exists
        if plane_name in bpy.data.objects:
            plane = bpy.data.objects[plane_name]
            print(f"Using existing ground plane: {plane_name}")
        else:
            # Create new ground plane
            bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
            plane = context.active_object
            plane.name = plane_name
            print(f"Created ground plane: {plane_name}")

        # Ensure rigid body world exists
        if context.scene.rigidbody_world is None:
            bpy.ops.rigidbody.world_add()

        # Add passive rigid body if not already present
        if plane.rigid_body is None:
            # Deselect all and select only the plane
            bpy.ops.object.select_all(action='DESELECT')
            plane.select_set(True)
            context.view_layer.objects.active = plane
            bpy.ops.rigidbody.object_add()

            plane.rigid_body.type = 'PASSIVE'
            plane.rigid_body.collision_shape = 'MESH'
            plane.rigid_body.friction = self.friction
            plane.rigid_body.restitution = self.bounciness

        return plane

    def _setup_rigid_body(self, obj):
        """Setup rigid body physics on an object"""
        # Get or create rigid body world
        if bpy.context.scene.rigidbody_world is None:
            bpy.ops.rigidbody.world_add()

        # Add rigid body if not already present
        if obj.rigid_body is None:
            # Try using the operator with proper context
            try:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_add()
            except RuntimeError as e:
                print(f"Failed to add rigid body via operator: {e}")
                # Fallback: manually add rigid body constraint collection
                if bpy.context.scene.rigidbody_world:
                    bpy.context.scene.rigidbody_world.collection.objects.link(obj)
                return False

        # Configure rigid body settings optimized for LEGO parts
        rb = obj.rigid_body
        if rb is None:
            print(f"Warning: rigid body not created for {obj.name}")
            return False

        rb.type = 'ACTIVE'

        # Collision shape
        if self.use_mesh_collision:
            rb.collision_shape = 'MESH'  # Accurate but slower
        else:
            rb.collision_shape = 'CONVEX_HULL'  # Faster approximation

        # Physics properties
        rb.mass = self.mass
        rb.friction = self.friction
        rb.restitution = self.bounciness

        # Damping - lower values for small objects
        rb.linear_damping = 0.04
        rb.angular_damping = 0.1

        # Collision margins
        rb.use_margin = True
        rb.collision_margin = 0.001  # Small margin for small parts

        # Enable deactivation to improve performance
        rb.use_deactivation = True
        rb.deactivate_linear_velocity = 0.01
        rb.deactivate_angular_velocity = 0.01

        return True


class BRICKSCOPE_OT_bake_physics(Operator):
    """Bake physics simulation to keyframes"""
    bl_idname = "brickscope.bake_physics"
    bl_label = "Bake Physics"
    bl_options = {'REGISTER', 'UNDO'}

    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        description="First frame to bake",
        default=1,
        min=1
    )

    frame_end: bpy.props.IntProperty(
        name="End Frame",
        description="Last frame to bake",
        default=250,
        min=1
    )

    def execute(self, context):
        # Get all objects with rigid body physics
        rb_objects = [obj for obj in bpy.data.objects if obj.rigid_body and obj.rigid_body.type == 'ACTIVE']

        if not rb_objects:
            self.report({'ERROR'}, "No objects with active rigid body physics found")
            return {'CANCELLED'}

        # Set frame range
        context.scene.frame_start = self.frame_start
        context.scene.frame_end = self.frame_end

        # Bake physics simulation
        self.report({'INFO'}, f"Baking physics for {len(rb_objects)} objects from frame {self.frame_start} to {self.frame_end}...")

        # Point cache bake
        bpy.ops.ptcache.bake_all(bake=True)

        self.report({'INFO'}, f"Physics baked successfully!")
        return {'FINISHED'}


class BRICKSCOPE_OT_clear_physics(Operator):
    """Remove rigid body physics from selected objects"""
    bl_idname = "brickscope.clear_physics"
    bl_label = "Clear Physics"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get selected objects or all with rigid body
        if context.selected_objects:
            target_objects = [obj for obj in context.selected_objects if obj.rigid_body]
        else:
            target_objects = [obj for obj in bpy.data.objects if obj.rigid_body]

        if not target_objects:
            self.report({'WARNING'}, "No objects with rigid body physics found")
            return {'CANCELLED'}

        # Remove rigid body from each object
        for obj in target_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_remove()

        self.report({'INFO'}, f"Cleared physics from {len(target_objects)} objects")
        return {'FINISHED'}
