"""
LDraw Wrapper - Interface to ldr_tools_blender
Provides programmatic import with caching
"""

import bpy
import math
import tempfile
import os
from pathlib import Path
from mathutils import Euler


class LDrawImporter:
    """
    Wrapper for ldr_tools_blender that provides:
    - Programmatic import (not just UI)
    - Part caching/instancing
    - Error handling
    """

    def __init__(self, ldraw_path=None):
        """
        Initialize LDraw importer

        Args:
            ldraw_path: Path to LDraw library (e.g., ~/ldraw)
        """
        import os
        # Expand ~ to home directory
        if ldraw_path:
            expanded = os.path.expanduser(ldraw_path)
            self.ldraw_path = Path(expanded)
        else:
            self.ldraw_path = None
        self.ldr_tools_py = None
        self.color_table = None
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if ldr_tools_blender is installed and import it"""
        try:
            # Import ldr_tools_py from the ldr_tools_blender addon
            import ldr_tools_blender.ldr_tools_py as ldr_tools_py
            self.ldr_tools_py = ldr_tools_py
            self.has_ldr_tools = True

            # Load color table if ldraw_path is set
            if self.ldraw_path and self.ldraw_path.exists():
                try:
                    self.color_table = self.ldr_tools_py.load_color_table(str(self.ldraw_path))
                except Exception as e:
                    print(f"WARNING: Could not load LDraw color table: {e}")

        except ImportError as e:
            self.has_ldr_tools = False
            print("WARNING: ldr_tools_blender not found. Install from:")
            print("  https://github.com/ScanMountGoat/ldr_tools_blender")
            print(f"Error: {e}")

    def import_part(self, part_id, color_id=4, location=(0, 0, 0)):
        """
        Import a single LDraw part with specified color

        Args:
            part_id: LDraw part number (e.g., "3001" for 2x4 brick)
            color_id: LDraw color ID (default 4 = red)

        Returns:
            Blender object, or None if import failed
        """
        if not self.has_ldr_tools:
            print(f"Cannot import part {part_id}: ldr_tools_blender not installed")
            return None

        if not self.ldraw_path or not self.ldraw_path.exists():
            print(f"LDraw library path not set or doesn't exist: {self.ldraw_path}")
            return None

        part_file = self.ldraw_path / "parts" / f"{part_id}.dat"
        if not part_file.exists():
            print(f"Part file not found: {part_file}")
            return None

        try:
            # Create a temporary .ldr file that references the part with the color
            # LDR format: 1 <color> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part.dat>
            # Identity matrix at origin: 1 0 0  0 1 0  0 0 1
            temp_ldr_content = f"0 BrickScope temp part\n1 {color_id} 0 0 0 1 0 0 0 1 0 0 0 1 {part_id}.dat\n"

            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ldr', delete=False) as temp_file:
                temp_file.write(temp_ldr_content)
                temp_ldr_path = temp_file.name

            try:
                # Get all objects before import
                objects_before = set(bpy.data.objects)

                # Call the import operator with the temp .ldr file
                bpy.ops.import_scene.importldr(
                    filepath=temp_ldr_path,
                    ldraw_path=str(self.ldraw_path),
                    instance_type='LinkedDuplicates',
                    stud_type='Logo4',
                    primitive_resolution='High',
                    add_gap_between_parts=False,
                    scene_scale=0.01
                )

                # Find newly imported objects by comparing before/after
                objects_after = set(bpy.data.objects)
                new_objects = list(objects_after - objects_before)

                print(f"DEBUG: Found {len(new_objects)} new objects after import")
                print(f"DEBUG: Target location = {location}")

                # Translate all new objects by directly modifying their location
                if new_objects:
                    for obj in new_objects:
                        old_loc = obj.location.copy()
                        obj.location.x += location[0]
                        obj.location.y += location[1]
                        obj.location.z += location[2]
                        print(f"DEBUG: Moved {obj.name} from {old_loc} to {obj.location}")

                # Find the top-level parent (empty with no parent)
                obj = None
                for o in new_objects:
                    if o.parent is None:
                        obj = o
                        break

                # Fallback to first object if no parent-less object found
                if obj is None and new_objects:
                    obj = new_objects[0]

                if obj:
                    obj.name = f"part_{part_id}_color{color_id}"
                    print(f"Successfully imported part {part_id} with color {color_id} - parent at {obj.location}")

                return obj

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_ldr_path)
                except:
                    pass

        except Exception as e:
            print(f"Error importing part {part_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_part_instance(self, part_id, location=(0, 0, 0), rotation=(0, 0, 0), color_id=4):
        """
        Import or instance a part at specified location/rotation

        This will cache parts and create instances for efficiency

        Args:
            part_id: LDraw part number
            location: (x, y, z) position
            rotation: (rx, ry, rz) rotation in radians
            color_id: LDraw color ID (default 4 = red)

        Returns:
            Blender object instance
        """
        # Import the part (will use caching via part_cache.py separately)
        obj = self.import_part(part_id, color_id)
        if obj:
            obj.location = location
            obj.rotation_euler = rotation

        return obj

    def get_ldraw_colors(self):
        """
        Get list of available LDraw colors from LDConfig.ldr

        Returns:
            List of color dictionaries with id, name, rgb
        """
        # TODO: Parse LDConfig.ldr
        # For now, return common colors
        return [
            {"id": 0, "name": "Black", "rgb": (0.05, 0.05, 0.05)},
            {"id": 1, "name": "Blue", "rgb": (0.0, 0.2, 0.7)},
            {"id": 2, "name": "Green", "rgb": (0.0, 0.5, 0.2)},
            {"id": 4, "name": "Red", "rgb": (0.8, 0.0, 0.0)},
            {"id": 14, "name": "Yellow", "rgb": (0.95, 0.8, 0.0)},
            {"id": 15, "name": "White", "rgb": (0.9, 0.9, 0.9)},
        ]

    def get_common_parts(self):
        """
        Get list of common LEGO parts for quick access

        Returns:
            List of part dictionaries with id, name, category
        """
        # TODO: Load from database or file
        return [
            {"id": "3001", "name": "Brick 2x4", "category": "brick"},
            {"id": "3002", "name": "Brick 2x3", "category": "brick"},
            {"id": "3003", "name": "Brick 2x2", "category": "brick"},
            {"id": "3004", "name": "Brick 1x2", "category": "brick"},
            {"id": "3005", "name": "Brick 1x1", "category": "brick"},
            {"id": "3021", "name": "Plate 2x3", "category": "plate"},
            {"id": "3022", "name": "Plate 2x2", "category": "plate"},
            {"id": "3023", "name": "Plate 1x2", "category": "plate"},
            {"id": "3024", "name": "Plate 1x1", "category": "plate"},
        ]
