"""
Part Cache - Efficient instancing of LEGO parts
Imports each unique part+color combination once, then instances
"""

import bpy
from typing import Dict, Tuple, Optional


class PartCache:
    """
    Caches imported LEGO parts for efficient instancing

    Key concept: Import each unique (part_id, color_id) combination once,
    then create linked duplicates for subsequent uses.
    """

    def __init__(self):
        """Initialize empty cache"""
        self._cache: Dict[Tuple[str, int], bpy.types.Object] = {}
        self._cache_collection = None
        self._ensure_cache_collection()

    def _ensure_cache_collection(self):
        """Create collection to store cached parts (will be hidden when parts are added)"""
        collection_name = "BrickScope_PartCache"

        if collection_name in bpy.data.collections:
            self._cache_collection = bpy.data.collections[collection_name]
        else:
            self._cache_collection = bpy.data.collections.new(collection_name)
            # Only link if not already linked
            if self._cache_collection.name not in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.link(self._cache_collection)

    def _get_cache_key(self, part_id: str, color_id: int) -> Tuple[str, int]:
        """Generate cache key from part_id and color_id"""
        return (part_id, color_id)

    def has_part(self, part_id: str, color_id: int) -> bool:
        """Check if part+color is already cached"""
        key = self._get_cache_key(part_id, color_id)
        return key in self._cache

    def add_part(self, part_id: str, color_id: int, obj: bpy.types.Object):
        """
        Add a part to the cache

        Args:
            part_id: LDraw part number
            color_id: LDraw color ID
            obj: The imported Blender object
        """
        key = self._get_cache_key(part_id, color_id)

        # Move to cache collection
        if obj.name not in self._cache_collection.objects:
            # Unlink from all collections first
            for col in obj.users_collection:
                col.objects.unlink(obj)
            # Link to cache collection
            self._cache_collection.objects.link(obj)

        # Hide cache collection from viewport and render (safe to do here, not in draw context)
        self._cache_collection.hide_viewport = True
        self._cache_collection.hide_render = True

        # Store in cache
        self._cache[key] = obj

        # Rename for clarity
        obj.name = f"cached_{part_id}_color{color_id}"

    def get_part(self, part_id: str, color_id: int) -> Optional[bpy.types.Object]:
        """
        Get cached part (returns the original, not an instance)

        Args:
            part_id: LDraw part number
            color_id: LDraw color ID

        Returns:
            Cached object or None
        """
        key = self._get_cache_key(part_id, color_id)
        return self._cache.get(key)

    def create_instance(self, part_id: str, color_id: int,
                       location=(0, 0, 0), rotation=(0, 0, 0),
                       collection=None) -> Optional[bpy.types.Object]:
        """
        Create a linked duplicate instance of a cached part

        Args:
            part_id: LDraw part number
            color_id: LDraw color ID
            location: (x, y, z) world position
            rotation: (rx, ry, rz) euler rotation
            collection: Collection to add instance to (default: scene collection)

        Returns:
            New instance object or None
        """
        if not self.has_part(part_id, color_id):
            print(f"Part not in cache: {part_id} color {color_id}")
            return None

        cached_obj = self.get_part(part_id, color_id)

        # Create linked duplicate (shares mesh data)
        instance = cached_obj.copy()
        instance.data = cached_obj.data  # Share mesh data

        # Set transform
        instance.location = location
        instance.rotation_euler = rotation

        # Add to scene collection
        if collection is None:
            collection = bpy.context.scene.collection
        collection.objects.link(instance)

        # Generate unique name
        instance.name = f"{part_id}_color{color_id}_instance"

        return instance

    def clear(self):
        """Clear the entire cache"""
        # Remove all cached objects
        for obj in self._cache.values():
            bpy.data.objects.remove(obj, do_unlink=True)

        self._cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "cached_parts": len(self._cache),
            "unique_part_ids": len(set(k[0] for k in self._cache.keys())),
            "unique_colors": len(set(k[1] for k in self._cache.keys())),
        }


# Global cache instance (one per Blender session)
_global_cache = None


def get_part_cache() -> PartCache:
    """Get the global part cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = PartCache()
    return _global_cache
