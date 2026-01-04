# VisioneerLabs BrickScope - Project Brief & Decisions

**Project Lead:** Kyle  
**Date:** January 2026  
**Status:** Phase 1 - Synthetic Data Generation via Blender  
**Repository:** `visioneerlabs/brickscope`

---

## Project Overview

**VisioneerLabs BrickScope** is an AI-powered AR system that helps users find specific LEGO pieces in large, chaotic piles using computer vision and grounded object detection.

**Tagline:** "Scope out exactly what you need"

### Core Use Case
- User has massive LEGO pile (example: 3ft × 2ft × 2ft bucket, ~150k pieces)
- User wants to build specific set (e.g., Black Seas Barracuda #6285)
- System highlights only the pieces needed from that set
- Ignores 1000+ other pieces in the pile

### Key Innovation
**Selective Grounded Detection:** Among 150 visible pieces in camera frame, only detect/highlight the 10-50 pieces user actually needs based on text query.

---

## Strategic Decisions

### 1. Vision Models (Comparative Study)

**Primary Model: Grounding-DINO** ⭐  
- Purpose-built for text-grounded object detection
- Best at dense scenes with selective filtering
- Speed: 5-8 fps on RTX 3090
- Open source (Apache 2.0)
- Fine-tunable on single 3090

**Secondary Model: Florence-2 (Comparison)**  
- Vision-language foundation model
- More flexible, slower (3-5 fps)
- Research comparison potential

**MSc Research Angle:** Comparative analysis of Florence-2 vs Grounding-DINO on dense LEGO detection could be novel research contribution.

### 2. Hardware Architecture

```
┌─────────────────────────────────┐
│  Linux Workstation (3090)       │
│  - Training (Blender + ML)      │
│  - Inference Server (FastAPI)   │
└────────────┬────────────────────┘
             │ WiFi/Network
             ↓
┌─────────────────────────────────┐
│  iPad Air M1 (5th Gen)          │
│  - ARKit camera                 │
│  - Stream to server             │
│  - AR overlay rendering         │
└─────────────────────────────────┘
```

**Key Decision:** All heavy compute on Linux 3090, iPad is thin AR client.

### 3. Platform & Licensing

- **Open Source:** Apache 2.0 license
- **Repository:** `github.com/visioneerlabs/brickscope`
- **Cross-platform training data:** Works for Grounding-DINO, Florence-2, YOLO, etc.
- **No vendor lock-in:** Train once on Linux, deploy anywhere

---

## Synthetic Data Generation Strategy

### Current Phase: Blender Addon Development

**Tool:** VS Code + Claude Code for Blender addon  
**Goal:** Generate 1M+ training images with rich annotations

### Three Scene Types

**1. Single Pieces (30% - 300k images)**
```
- 1 piece per image
- Fully visible (visibility = 1.0)
- Clean training signal
- All rotations, lighting, backgrounds
- Purpose: Foundation learning
```

**2. Multiple Pieces, No Occlusion (30% - 300k images)**
```
- 5-25 pieces per image
- Grid or scattered layout
- No overlapping bboxes
- All pieces visible (visibility = 1.0)
- Purpose: Multi-object detection training
```

**3. Piles - Dense & Occluded (40% - 400k images)**
```
- 30-150 pieces per image
- Heavy occlusion (30-90% average)
- Realistic pile physics
- Partial visibility common
- Purpose: Real-world scenario
```

### Progressive Generation Plan

```
Phase 1: 10k images (validate pipeline)
Phase 2: 100k images (baseline training)
Phase 3: 500k images (competitive performance)
Phase 4: 1M+ images (only if needed)
```

**Rationale:** Validate quality before generating millions. Diminishing returns likely after 100-500k.

---

## Data Format Specification

### Rich Intermediate Format (JSON)

**Design Principle:** Output comprehensive JSON from Blender, then write lightweight converters to model-specific formats.

```
Blender → Rich JSON → Converters → Florence-2 / Grounding-DINO / YOLO
```

### Per-Image Annotation Structure

```json
{
  "format_version": "1.0",
  "generator": "VisioneerLabs BrickScope Blender Addon v0.1",
  
  "image_metadata": {
    "file_path": "images/pile_000001.png",
    "width": 1024,
    "height": 1024,
    "scene_id": "batch_001_scene_042",
    "scene_type": "pile" | "single_piece" | "multiple_no_occlusion",
    "difficulty": "easy" | "medium" | "hard",
    "render_samples": 128,
    "camera": {
      "position": [x, y, z],
      "rotation": [rx, ry, rz],
      "fov": 50,
      "lens_mm": 50
    },
    "lighting": {
      "hdri": "studio_small_08.exr",
      "intensity": 1.2
    }
  },
  
  "objects": [
    {
      // IDENTITY
      "piece_id": "3001",
      "color_id": "red",
      "color_name": "Bright Red",
      "category": "brick",
      "piece_name": "Brick 2x4",
      "part_number": "300121",
      
      // 2D SPATIAL (absolute pixels)
      "bbox": [120, 150, 220, 250],  // [x1, y1, x2, y2] in pixels
      "center_2d": [170, 200],
      "area_pixels": 10000,
      
      // 3D SPATIAL (Blender world space)
      "position_3d": [0.05, 0.02, 0.01],
      "rotation_3d": [15, 45, 90],
      "bbox_3d_corners": [[...], [...], ...],
      
      // VISIBILITY/OCCLUSION
      "visibility": 0.65,  // 0.0-1.0
      "is_fully_visible": false,
      "is_partially_occluded": true,
      "occluding_objects": ["3002_blue", "3003_black"],
      "distance_from_camera": 0.45,
      "z_order": 12,
      "in_frame": true,
      
      // TEXT DESCRIPTIONS (multiple variants)
      "captions": {
        "short": "red brick",
        "medium": "red 2x4 brick",
        "long": "red 2x4 LEGO brick part 3001",
        "natural": "a rectangular red LEGO brick measuring 2 by 4 studs",
        "attributes": "color: red, size: 2x4, type: brick, category: standard"
      },
      
      // METADATA
      "object_index": 0,
      "spatial_neighbors": ["3002_blue"],
      
      // OPTIONAL: Segmentation
      "segmentation_mask": "masks/pile_000001_obj_000.png",
      "segmentation_polygon": [[x1,y1], [x2,y2], ...]
    }
    // ... more objects
  ],
  
  "scene_metadata": {
    "total_pieces": 87,
    "visible_pieces": 52,
    "pieces_in_frame": 48,
    "avg_occlusion": 0.65,
    "avg_visibility": 0.35,
    "piece_count_by_category": {
      "brick": 45,
      "plate": 30,
      "slope": 12
    },
    "piece_count_by_color": {
      "red": 20,
      "blue": 15,
      "black": 10
    },
    "background_type": "wood_table",
    "difficulty_score": 0.75
  }
}
```

### Critical Data Format Rules

1. **Store absolute pixel coordinates** - Don't normalize in Blender
   - Different models need different normalizations
   - Easy to normalize later, impossible to denormalize
   
2. **Multiple caption variants** - Generate several text description styles
   - Test which works best for each model
   - Florence-2 might prefer longer captions
   - Grounding-DINO might prefer shorter

3. **Include visibility/occlusion metrics**
   - Essential for training on hard examples
   - Enables curriculum learning (easy→hard)
   - Important for evaluation stratification

4. **Rich metadata enables research**
   - Difficulty scores
   - Scene statistics
   - Spatial relationships

---

## Repository Structure

```
visioneerlabs/brickscope/
├── README.md
├── LICENSE (Apache 2.0)
├── PROJECT_BRIEF.md              # This document
│
├── blender/                       # Synthetic data generation
│   ├── addons/
│   │   └── brickscope/           # Main Blender addon
│   │       ├── __init__.py
│   │       ├── scene_generators/
│   │       ├── annotations/
│   │       └── utils/
│   ├── scripts/
│   │   ├── generate_dataset.py
│   │   └── batch_render.py
│   └── assets/
│       ├── hdris/
│       ├── backgrounds/
│       └── ldraw_parts/
│
├── data/                          # Dataset storage (gitignored)
│   ├── single_pieces/
│   ├── multiple_clean/
│   ├── piles/
│   ├── converted/
│   └── metadata/
│
├── training/                      # Model training code
│   ├── grounding_dino/
│   │   ├── train.py
│   │   ├── configs/
│   │   └── checkpoints/
│   ├── florence2/
│   │   ├── train.py
│   │   └── configs/
│   └── converters/
│       ├── to_grounding_dino.py
│       ├── to_florence2.py
│       └── to_coco.py
│
├── inference/                     # Production inference server
│   ├── server.py                 # FastAPI server
│   ├── models/
│   ├── api/
│   └── utils/
│
├── clients/                       # Client applications
│   ├── ios/                      # iPad ARKit app
│   │   └── BrickScope/
│   ├── android/                  # Android app (future)
│   └── web/                      # Web demo
│
├── evaluation/                    # Testing & metrics
│   ├── evaluate.py
│   ├── benchmarks/
│   └── test_images/
│
├── docs/                          # Documentation
│   ├── data_format.md
│   ├── blender_addon_guide.md
│   └── api_reference.md
│
└── scripts/                       # Utility scripts
    ├── dataset_stats.py
    ├── visualize_annotations.py
    └── sync_models.sh
```

---

## Dataset Organization

```
data/
├── single_pieces/
│   ├── images/
│   │   ├── train/      (240k images)
│   │   ├── val/        (30k images)
│   │   └── test/       (30k images)
│   └── annotations/    (JSON files)
│
├── multiple_clean/
│   ├── images/
│   │   ├── train/      (240k images)
│   │   ├── val/        (30k images)
│   │   └── test/       (30k images)
│   └── annotations/
│
├── piles/
│   ├── images/
│   │   ├── train/      (320k images)
│   │   ├── val/        (40k images)
│   │   └── test/       (40k images)
│   └── annotations/
│
├── converted/          (Generated by converter scripts)
│   ├── florence2/
│   │   ├── train.json
│   │   └── val.json
│   ├── grounding_dino/
│   │   ├── train_annotations.json
│   │   └── val_annotations.json
│   └── coco/
│       └── instances_train.json
│
├── masks/              (Optional: instance segmentation)
│   ├── train/
│   └── val/
│
└── metadata/
    ├── piece_database.json      # All LEGO pieces catalog
    ├── color_database.json      # LDraw color definitions
    ├── scene_stats.json         # Dataset statistics
    └── dataset_splits.json      # Train/val/test split info
```

---

## LEGO Asset Preparation

### LDraw Library

**Source:** https://www.ldraw.org/  
**License:** CC-BY-4.0  
**Content:** ~10,000 official LEGO part models

```bash
# Download complete library
wget https://library.ldraw.org/library/updates/complete.zip
unzip complete.zip -d ~/ldraw

# Directory structure
~/ldraw/
├── parts/          # Individual .dat files (3001.dat, 3002.dat, etc.)
├── p/              # Primitives
├── models/         # Complete models
└── LDConfig.ldr    # Official LEGO color definitions
```

### Initial Part Set

**Black Seas Barracuda (Set 6285):**
- ~900 total pieces
- ~100-150 unique part types
- Good starter set for prototyping

**Expansion Plan:**
- Phase 1: Black Seas Barracuda parts (~150 types)
- Phase 2: Common 500 pieces (80% coverage of most sets)
- Phase 3: Full catalog (~3000-4000 active parts)

---

## Blender Generation Requirements

### Scene Parameters by Type

**Single Pieces:**
```python
pieces_per_scene: 1
camera_distance: 15-30cm
rotations: Random all axes
lighting: Varied HDRIs
backgrounds: Wood, plastic, fabric textures
render_time: ~10 sec/image
```

**Multiple No-Occlusion:**
```python
pieces_per_scene: 5-25
layout: Grid (3x3, 4x4, 5x5) or scattered
min_spacing: 5-10mm between pieces
no_bbox_overlap: True
camera_angle: Overhead or 45°
render_time: ~25 sec/image
```

**Piles:**
```python
pieces_per_scene: 30-150
physics_simulation: Drop or random placement
occlusion_levels: 30-90% average
camera_angles: Overhead, 30°, 45°, 60°
render_time: ~60 sec/image
```

### Domain Randomization

**Essential variations:**
- Camera position/angle
- Lighting (multiple HDRIs)
- Backgrounds
- Piece rotations
- Color distributions
- Piece size distributions

**Goal:** Synthetic→real domain gap minimization

---

## Distribution Control System (Visual + Programmatic)

**Implementation Status:** In development (feature/distribution-control branch)

### Overview

Visual system for controlling part and color distributions with real-time preview and programmatic API for dataset generation.

### Architecture

**Three-Phase Workflow:**

```
Phase 1: Define Distribution (UI + Sliders)
    ↓
Phase 2: Preview (Geometry Nodes - Real-time)
    ↓
Phase 3: Bake (Import Real Parts - For Rendering)
```

### Phase 1: Distribution Definition (UI)

**Part Distribution:**
- UI List with weight sliders for each part type
- Add/remove parts dynamically
- Example: `Brick 2x4 (weight: 1.0)`, `Plate 2x2 (weight: 0.7)`

**Color Distribution:**
- UI List with weight sliders for each color
- Example: `Red (weight: 1.0)`, `Blue (weight: 0.5)`

**Generation Settings:**
- Total pieces count (e.g., 100 pieces)
- Random seed (for reproducibility)

**Features:**
- Normalize weights button (sum to 1.0)
- Load defaults (common parts/colors preset)
- Save/load distribution configs (JSON)
- Real-time weight statistics display

### Phase 2: Preview Mode (Geometry Nodes)

**Purpose:** Instant visual feedback without importing actual parts

**Implementation:**
- Scatter points in volume (or on surface)
- Instance parts on points using geometry nodes
- Weight-based selection (heavier weights = more instances)
- Update in real-time as user adjusts sliders

**Benefits:**
- ✅ Instant feedback (no waiting for imports)
- ✅ Interactive exploration of distributions
- ✅ Lightweight (instances, not real objects)
- ✅ See distribution before committing to import

### Phase 3: Bake Mode (Real Object Import)

**Purpose:** Create actual LEGO parts for physics simulation and rendering

**Workflow:**
1. **Sample Distribution:**
   - Use weighted random sampling
   - Generate list of (part_id, color_id) pairs
   - Example: `[(3001, 4), (3003, 1), (3001, 4), ...]` = 50x red 2x4, 30x blue 2x2, etc.

2. **Import Parts:**
   - Call `ldraw_wrapper.py` for each unique (part_id, color_id)
   - Use `part_cache.py` for efficiency (import once, instance many)
   - Apply colors via ldr_tools_blender

3. **Place Objects:**
   - Scatter placement (random positions/rotations)
   - OR prepare for physics simulation (drop from height)

4. **Result:**
   - Real Blender objects with proper materials
   - Ready for rigid body physics
   - Ready for Cycles rendering with annotations

### Multi-Distribution Mixing

**Goal:** Combine multiple distributions for complex scenarios

**Use Cases:**

**Example 1: Set-Specific + Common Parts**
```json
{
  "layers": [
    {
      "name": "Black Seas Barracuda Set",
      "source": "rebrickable:6285",
      "count": 50,
      "weight": 1.0
    },
    {
      "name": "Common Filler Bricks",
      "parts": ["3001", "3003", "3004"],
      "colors": ["4", "1", "14"],
      "count": 150,
      "weight": 0.8
    }
  ]
}
```

**Example 2: Realistic Bucket (Multiple Sets Mixed)**
```json
{
  "layers": [
    {"name": "Set A", "count": 200, "weight": 1.0},
    {"name": "Set B", "count": 100, "weight": 0.5},
    {"name": "Random Parts", "count": 500, "weight": 0.3}
  ]
}
```

### Set-Based Import (Future Feature)

**Goal:** Automatically populate distributions from LEGO set inventories

**Data Sources:**
- Rebrickable API (https://rebrickable.com/api/)
- Parse LDraw .mpd files
- Custom set inventory JSON files

**Workflow:**
1. User enters set number (e.g., "6285")
2. Fetch set inventory from API
3. Populate distribution with:
   - All unique part types
   - Correct colors
   - Piece counts matching set
4. User can adjust weights/counts before generating

**Example Sets:**
- 6285: Black Seas Barracuda (~900 pieces, ~150 unique parts)
- 10179: Millennium Falcon UCS (~5000 pieces, ~400 unique parts)

### Data Structures

**Distribution Config (JSON):**
```json
{
  "parts": [
    {"id": "3001", "name": "Brick 2x4", "weight": 1.0},
    {"id": "3003", "name": "Brick 2x2", "weight": 0.9}
  ],
  "colors": [
    {"id": "4", "name": "Red", "weight": 1.0},
    {"id": "1", "name": "Blue", "weight": 0.5}
  ],
  "total_pieces": 100,
  "seed": 12345
}
```

**Sampling Output:**
```python
# From 100 pieces with above distribution:
[
  ("3001", "4"),  # Red 2x4
  ("3003", "1"),  # Blue 2x2
  ("3001", "4"),  # Red 2x4
  ...
  # Total: 100 (part_id, color_id) pairs
]
```

### Implementation Status

**✅ Completed:**
- `distribution_manager.py` - Weighted sampling logic
- `distribution_properties.py` - Blender scene properties
- `distribution_operators.py` - Add/remove/normalize
- `distribution_ui.py` - UI lists with weight sliders
- UI panel with part/color lists
- Save/load distribution configs
- Preset distributions (common parts/colors)

**🚧 In Progress:**
- None (ready for next phase)

**📋 TODO:**
- Geometry nodes preview system
- Bake functionality (sample → import → place)
- Multi-distribution mixing
- Set-based import (Rebrickable API)
- Distribution presets library

### Key Benefits

**For Artists:**
- Visual, intuitive control
- Instant preview
- Easy experimentation

**For ML Engineers:**
- Programmatic API (JSON configs)
- Reproducible (seed-based)
- Scalable (batch generation)

**For Researchers:**
- Controlled distributions for ablation studies
- Easy to vary part/color ratios
- Dataset diversity metrics

---

## Headless/Server Usage for Production

**Critical Design:** All core functionality (distribution → simulation → rendering) runs in Blender headless mode for large-scale dataset generation.

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  Pure Python (Optional - Config Generation Only)    │
│  - Create distribution configs (no Blender needed)  │
│  - Sample distributions to preview counts           │
│  - Generate batch job configs                       │
└──────────────────┬──────────────────────────────────┘
                   │ JSON configs
                   ↓
┌─────────────────────────────────────────────────────┐
│  Blender Headless (Full Pipeline)                   │
│  1. Load distribution config                        │
│  2. Sample → (part_id, color_id) pairs              │
│  3. Import LEGO parts (ldr_tools_blender)           │
│  4. Scatter parts in scene                          │
│  5. Physics simulation (rigid body pile)            │
│  6. Randomize camera/lighting                       │
│  7. Render image (Cycles)                           │
│  8. Calculate bboxes/visibility                     │
│  9. Export annotations (JSON)                       │
│  10. Clear scene → repeat                           │
└─────────────────────────────────────────────────────┘
```

### What Each Mode Can Do

**Pure Python (No Blender Required):**
- ✅ Create/edit distribution configs
- ✅ Sample distributions (get part/color lists)
- ✅ Save/load JSON configs
- ✅ Validate distributions
- ❌ Cannot import parts (needs Blender)
- ❌ Cannot simulate physics (needs Blender)
- ❌ Cannot render (needs Blender Cycles)

**Blender Headless (`--background` flag):**
- ✅ **Everything** - Full pipeline end-to-end
- ✅ Load distribution configs
- ✅ Import LEGO parts with materials
- ✅ Physics simulation for piles
- ✅ Photorealistic rendering
- ✅ Annotation generation (bboxes, visibility)
- ✅ No GUI overhead (faster, scalable)

**Blender Interactive (UI):**
- ✅ Same as headless + visual feedback
- Use for: Development, prototyping, debugging

### Production Workflow

**Step 1: Create Distribution Configs (Optional - Can skip to Step 2)**

```python
# create_configs.py - Pure Python, no Blender needed
from distribution_manager import DistributionConfig, WeightedDistribution

# Create distribution
config = DistributionConfig()
config.part_distribution.add_item("3001", "Brick 2x4", 1.0)
config.part_distribution.add_item("3003", "Brick 2x2", 0.9)
config.color_distribution.add_item("4", "Red", 1.0)
config.color_distribution.add_item("1", "Blue", 0.5)
config.total_pieces = 100
config.seed = 12345

# Save for batch processing
config.save("configs/pile_config_001.json")

# Create 100 configs with different seeds
for i in range(100):
    config.seed = 1000 + i
    config.save(f"configs/batch_001/config_{i:03d}.json")
```

**Step 2: Generate Dataset (Blender Headless)**

```bash
# Single scene generation
blender --background --python generate_scene.py -- \
    --config configs/pile_config_001.json \
    --output data/piles/scene_001 \
    --scene-type pile

# Batch generation (1000 scenes)
for config in configs/batch_001/*.json; do
    blender --background --python generate_scene.py -- \
        --config $config \
        --output data/piles/batch_001
done

# Parallel generation (10 workers)
ls configs/batch_001/*.json | \
    parallel -j 10 blender --background --python generate_scene.py -- \
        --config {} \
        --output data/piles/batch_001
```

**Step 3: Blender Headless Script**

```python
# generate_scene.py - Full pipeline in headless Blender
import bpy
import sys
import json
from pathlib import Path

# Parse arguments
args = sys.argv[sys.argv.index("--") + 1:]
config_path = args[args.index("--config") + 1]
output_dir = Path(args[args.index("--output") + 1])
scene_type = args[args.index("--scene-type") + 1] if "--scene-type" in args else "pile"

# Import BrickScope modules (addon must be installed/available)
from distribution_manager import DistributionConfig
from ldraw_wrapper import LDrawImporter
from part_cache import get_part_cache
# from scene_generator import generate_pile_scene  # TODO
# from annotation_exporter import export_annotations  # TODO

# Load distribution config
config = DistributionConfig.load(config_path)
print(f"Loaded config: {len(config.part_distribution.items)} parts, "
      f"{len(config.color_distribution.items)} colors, "
      f"{config.total_pieces} total pieces")

# Sample distribution
pairs = config.generate_part_color_pairs()
print(f"Generated {len(pairs)} part/color pairs")

# Initialize importers
ldraw_path = "/path/to/ldraw"  # From addon preferences
importer = LDrawImporter(ldraw_path)
cache = get_part_cache()

# Import parts (with caching)
objects = []
for part_id, color_id in pairs:
    # Check cache first
    if not cache.has_part(part_id, int(color_id)):
        # Import and cache
        obj = importer.import_part(part_id, int(color_id))
        if obj:
            cache.add_part(part_id, int(color_id), obj)

    # Create instance from cache
    instance = cache.create_instance(
        part_id,
        int(color_id),
        location=(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0, 2)),
        rotation=(random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28))
    )
    objects.append(instance)

print(f"Imported {len(objects)} objects, cache has {cache.get_stats()['cached_parts']} unique parts")

# Physics simulation (pile creation)
if scene_type == "pile":
    # Enable rigid body physics
    for obj in objects:
        bpy.ops.rigidbody.object_add({'object': obj})
        obj.rigid_body.type = 'ACTIVE'

    # Add ground plane
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    ground = bpy.context.active_object
    bpy.ops.rigidbody.object_add({'object': ground})
    ground.rigid_body.type = 'PASSIVE'

    # Simulate (240 frames = 10 seconds at 24fps)
    bpy.context.scene.frame_end = 240
    bpy.context.scene.frame_set(240)
    print("Physics simulation complete")

# Randomize camera and lighting
# TODO: Implement camera/lighting randomization

# Render
output_dir.mkdir(parents=True, exist_ok=True)
image_path = output_dir / f"image_{config.seed:06d}.png"
bpy.context.scene.render.filepath = str(image_path)
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print(f"Rendered: {image_path}")

# Export annotations
# TODO: Calculate bboxes, visibility, export JSON
annotation_path = output_dir / f"annotation_{config.seed:06d}.json"
# export_annotations(objects, annotation_path)

print("Scene generation complete")
```

### Docker Container for Scale

```dockerfile
# Dockerfile
FROM ubuntu:22.04

# Install Blender
RUN apt-get update && apt-get install -y \
    blender \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip3 install numpy

# Copy BrickScope addon
COPY blender/addons /opt/brickscope/addons

# Copy scripts
COPY scripts /opt/brickscope/scripts

# Copy LDraw library
COPY ldraw /opt/ldraw

# Install BrickScope addon
RUN blender --background --python /opt/brickscope/scripts/install_addon.py

WORKDIR /workspace

ENTRYPOINT ["blender", "--background", "--python", "/opt/brickscope/scripts/generate_scene.py"]
```

```bash
# Build container
docker build -t brickscope:latest .

# Run single job
docker run -v $(pwd)/configs:/configs \
           -v $(pwd)/output:/output \
           brickscope:latest -- \
           --config /configs/pile_001.json \
           --output /output/batch_001

# Scale with Kubernetes / AWS Batch / GCP Batch
# Run 1000 containers in parallel for 1M images
```

### Cloud Deployment Examples

**AWS Batch:**
```bash
# Submit 1000 batch jobs
for i in {0..999}; do
    aws batch submit-job \
        --job-name brickscope-batch-$i \
        --job-queue brickscope-queue \
        --job-definition brickscope-job \
        --parameters config=s3://bucket/configs/config_$i.json
done
```

**Render Farm:**
```bash
# Many render farms support Blender headless
# Submit to Deadline, Royal Render, etc.
```

### Performance Considerations

**Single Machine:**
- 1 Blender instance: ~60 sec/pile image (with physics)
- 10 parallel instances: 10x throughput
- Limit: CPU cores, GPU memory

**Multi-Machine:**
- Stateless design = perfect for horizontal scaling
- 100 machines × 10 instances = 1000x throughput
- 1M images possible in days, not months

**Optimization Tips:**
- Use GPU rendering (Cycles OptiX/HIP)
- Cache parts aggressively (import once per batch)
- Lower samples for validation sets (64 vs 128)
- Use geometry nodes preview mode for development

### Reproducibility

**Every generated scene includes:**
```json
{
  "image_path": "pile_012345.png",
  "distribution_config": { ... },  // Exact config used
  "random_seed": 12345,            // Reproducible
  "render_settings": { ... },
  "timestamp": "2026-01-03T20:00:00Z"
}
```

**Benefits:**
- Can regenerate exact same scene
- Debug specific failure cases
- Ablation studies (vary one parameter)
- Version control for datasets

### Summary: Modes & Use Cases

| Mode | Use Case | Can Do |
|------|----------|--------|
| **Pure Python** | Config generation | Distributions only |
| **Blender UI** | Development, debugging | Full pipeline + visual feedback |
| **Blender Headless** | Production dataset generation | Full pipeline, scalable |
| **Docker/Cloud** | Massive scale (1M+ images) | Parallel headless Blender |

**Critical Point:** The UI is for *defining* distributions visually, but production dataset generation runs the exact same code in Blender headless mode. No functionality is lost.

---

## Render Performance Calculations

### Computational Requirements

```
Estimated render times (Cycles, 128 samples, 1024px):

Single piece:    10 sec/image × 300k = 833 hours
Multiple pieces: 25 sec/image × 300k = 2,083 hours
Piles:          60 sec/image × 400k = 6,667 hours

Total for 1M images: ~9,583 hours = 400 days (single machine)

Solutions:
1. Parallel Blender instances (10 processes = 40 days)
2. Multiple machines (10 machines = 4 days)
3. Reduce samples (64 instead of 128 = 2× faster)
4. Cloud rendering (AWS/GCP spot instances)
```

### Recommended Approach

```
Start small: 10k images in 4 days (single machine, 10 parallel)
Validate quality and train initial models
Scale based on results
```

---

## Next Steps - Phase 1

### 1. Blender Addon Development (VS Code + Claude Code)

**Priority 1: Core Infrastructure**
- [ ] LDraw import functionality
- [ ] Scene type generators (single/multiple/pile)
- [ ] Camera & lighting randomization
- [ ] JSON annotation export

**Priority 2: Quality Features**
- [ ] Visibility/occlusion calculation
- [ ] Multiple caption generation
- [ ] Bbox validation (in-frame, valid coords)
- [ ] Progress tracking & resumption

**Priority 3: Scale Features**
- [ ] Batch processing
- [ ] Parallel rendering support
- [ ] Error handling & logging
- [ ] Dataset statistics generation

### 2. Validation Dataset (10k images)

**Goal:** Prove pipeline works end-to-end

```
Generate:
├─ 3k single pieces
├─ 3k multiple clean
└─ 4k piles

Test:
├─ Annotation quality
├─ Visual inspection
├─ Converter scripts (to Florence-2/Grounding-DINO formats)
└─ Train tiny model to validate data works
```

### 3. Initial Model Training

**After 10k dataset ready:**
- Convert to Grounding-DINO format
- Train for 5-10 epochs (quick test)
- Validate on real LEGO pile photos
- Measure synthetic→real gap
- Iterate on data quality

---

## Success Criteria - Phase 1

**Data Quality:**
- [ ] All bboxes within image bounds
- [ ] No invalid/corrupt annotations
- [ ] Visibility calculations accurate (spot check)
- [ ] Caption variety (multiple styles per object)

**Pipeline Performance:**
- [ ] Generate 10k images in <1 week (single machine)
- [ ] <5% generation failures
- [ ] Consistent quality across scene types

**Model Validation:**
- [ ] Grounding-DINO trains successfully on generated data
- [ ] >60% accuracy on synthetic test set
- [ ] Model can detect pieces in real photos (even if accuracy low)

---

## Future Phases (Post-Data Generation)

### Phase 2: Model Training & Comparison
- Train Grounding-DINO on full dataset
- Train Florence-2 on same dataset
- Comparative evaluation
- Hyperparameter tuning

### Phase 3: Deployment
- FastAPI inference server on Linux
- iPad ARKit client app
- WebSocket streaming
- Real-time AR overlay

### Phase 4: Research & Publication
- MSc thesis write-up
- Conference paper submission
- Open-source release
- Dataset publication

---

## Key Resources

**Models:**
- Grounding-DINO: https://github.com/IDEA-Research/GroundingDINO
- Florence-2: https://huggingface.co/microsoft/Florence-2-large

**Data:**
- LDraw Parts: https://www.ldraw.org/
- Rebrickable API: https://rebrickable.com/api/
- HDRIs: https://polyhaven.com/hdris

**Hardware:**
- Linux Workstation: RTX 3090 (24GB)
- Client Device: iPad Air 5th Gen (M1)

**Repository:**
- GitHub: https://github.com/visioneerlabs/brickscope

---

## Notes & Decisions Log

**2026-01-03:**
- ✅ Decided on Grounding-DINO as primary model (vs Florence-2)
- ✅ Chose 3090-centric architecture (no on-device inference)
- ✅ Rich intermediate JSON format (convert to model formats later)
- ✅ Three scene types: single/multiple/piles (30/30/40 distribution)
- ✅ Start with 10k validation set before scaling to 1M
- ✅ No Facebook/Meta products (ruled out Quest headsets)
- ✅ Focus on Linux + iPad ecosystem
- ✅ Project name: BrickScope (better than BrickFinder)
- ✅ Repository: visioneerlabs/brickscope

**Key Insight:** Grounded detection (text-based filtering) is killer feature for this use case - don't need to detect all 150 pieces, just the 10-50 user actually needs. The "-scope" metaphor perfectly captures the AR viewing/filtering experience.

---

## Questions for Claude Code Session

1. Best approach for LDraw → Blender import (existing addon vs custom)?
2. Optimal Blender scene structure for parallel rendering?
3. Physics simulation vs manual placement for piles?
4. Segmentation mask generation worth the complexity?
5. HDRI licensing for commercial use?

---

**End of Brief - Ready for VS Code + Claude Code Implementation** 🔍🧱

**Repository:** `github.com/visioneerlabs/brickscope`  
**License:** Apache 2.0  
**Status:** Phase 1 - Blender Addon Development
