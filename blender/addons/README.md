# BrickScope Blender Extension

Synthetic LEGO dataset generator for training grounded object detection models.

## Dependencies

### Required: ldr_tools_blender

BrickScope uses **ldr_tools_blender** for importing LDraw LEGO parts with photorealistic materials.

**Installation:**

1. Download from: https://github.com/ScanMountGoat/ldr_tools_blender
2. In Blender: Edit → Preferences → Get Extensions → Install from Disk
3. Install the ldr_tools_blender .zip file
4. Enable the extension

**Why ldr_tools_blender:**
- 10x faster than alternatives (7s vs 68-100s for large models)
- Auto-instancing by part + color (memory efficient)
- Photorealistic Cycles materials with procedural detail
- Modern codebase for Blender 4.1+

### LDraw Parts Library

Download the official LDraw parts library:

```bash
# Download complete library (~50MB)
wget https://library.ldraw.org/library/updates/complete.zip
unzip complete.zip -d ~/ldraw

# Or visit: https://www.ldraw.org/
```

**Configure path in BrickScope:**
- Edit → Preferences → Get Extensions → BrickScope
- Set "LDraw Library Path" to your ldraw directory

## Development Setup

See main repository README for VS Code development workflow.

### Project Structure

```
blender/addons/
├── __init__.py                    # Main extension entry point
├── blender_manifest.toml          # Blender 5.0 extension metadata
├── auto_load.py                   # Auto-registration system
│
├── brickscope_panel.py           # UI panel
├── brickscope_operators.py       # Main operators
│
├── ldraw_wrapper.py              # Wrapper for ldr_tools_blender (TODO)
├── part_cache.py                 # Part instancing cache (TODO)
├── scene_generator.py            # Scene generation logic (TODO)
└── annotation_exporter.py        # JSON export (TODO)
```

## Current Status

**✅ Completed:**
- Extension structure and registration
- Hot-reload workflow with VS Code
- Basic UI panel

**🚧 In Progress:**
- LDraw integration
- Scene generation
- Annotation export

## License

Apache 2.0 - See repository LICENSE file
