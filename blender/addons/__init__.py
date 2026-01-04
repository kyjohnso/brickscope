# Copyright 2026 Kyle Johnson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# BrickScope: https://github.com/kyjohnso/brickscope

bl_info = {
    "name": "BrickScope Synthetic Data Generator",
    "author": "Kyle Johnson",
    "description": "Generate synthetic LEGO datasets for AI training",
    "blender": (4, 2, 0),
    "version": (0, 1, 0),
    "location": "View3D > Sidebar > BrickScope",
    "warning": "",
    "category": "3D View",
}

import bpy
from bpy.props import PointerProperty
from . import auto_load

auto_load.init()


def register():
    auto_load.register()

    # Register scene properties after all classes are registered
    from .distribution_properties import DistributionProperties
    bpy.types.Scene.brickscope_distribution = PointerProperty(type=DistributionProperties)


def unregister():
    # Remove scene properties before unregistering classes
    del bpy.types.Scene.brickscope_distribution

    auto_load.unregister()
