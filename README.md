# BrickScope

**AI-powered AR system for finding specific LEGO pieces in large, chaotic piles**

> "Scope out exactly what you need"

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Blender](https://img.shields.io/badge/Blender-3.6%2B-orange.svg)](https://www.blender.org/)

---

![lego pile](docs/images/lego_pile.png)

## What is BrickScope?

BrickScope uses computer vision and grounded object detection to help you find specific LEGO pieces in massive piles. Point your device at a pile of 150+ pieces, tell it what you need (e.g., "red 2x4 brick from Black Seas Barracuda"), and BrickScope highlights only those pieces.

### The Problem

- You have a massive LEGO collection (example: 3ft × 2ft × 2ft bucket, ~150k pieces)
- You want to build a specific set (e.g., Black Seas Barracuda #6285)
- Finding the exact pieces you need is like finding needles in a haystack
- Sorting manually takes hours or days

### The Solution

**Selective Grounded Detection:** Among 150 visible pieces in your camera frame, BrickScope detects and highlights only the 10-50 pieces you actually need based on text queries. Ignores everything else.

---

## Key Features

- **Text-Grounded Detection**: Search by natural language ("red 2x4 brick", "blue slope piece")
- **Dense Scene Understanding**: Handles 30-150+ pieces per frame with heavy occlusion
- **AR Overlay**: Real-time highlighting via iPad ARKit
- **Synthetic Training Data**: 1M+ generated images from Blender with rich annotations
- **Model Comparison**: Grounding-DINO vs Florence-2 comparative study
- **Open Source**: Apache 2.0 license, reproducible research

---

## System Architecture

```
┌─────────────────────────────────┐
│  Linux Workstation (RTX 3090)   │
│  - Blender (synthetic data)     │
│  - Model training               │
│  - FastAPI inference server     │
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

**Design Decision:** All heavy compute on Linux 3090, iPad is a thin AR client.

---

## Project Status

**Phase 1: Synthetic Data Generation (Current)**
- Building Blender addon for generating training images
- Three scene types: single pieces, multiple clean, dense piles
- Target: 10k validation set → 100k → 500k → 1M images
- Rich JSON annotations with visibility, occlusion, multiple captions

**Phase 2: Model Training (Next)**
- Fine-tune Grounding-DINO on synthetic data
- Comparative study with Florence-2
- Evaluate on real LEGO pile photos

**Phase 3: Deployment (Future)**
- FastAPI inference server
- iPad ARKit client app
- WebSocket streaming for real-time AR

**Phase 4: Research (Future)**
- MSc thesis write-up
- Conference paper submission
- Open-source release & dataset publication

---

## Repository Structure

```
brickscope/
├── blender/                # Synthetic data generation
│   ├── addons/brickscope/  # Main Blender addon
│   ├── scripts/            # Generation & batch scripts
│   └── assets/             # HDRIs, backgrounds, LDraw parts
│
├── data/                   # Dataset storage (gitignored)
│   ├── single_pieces/      # 30% - Clean training signal
│   ├── multiple_clean/     # 30% - Multi-object, no occlusion
│   ├── piles/              # 40% - Dense, realistic scenes
│   ├── converted/          # Model-specific formats
│   └── metadata/           # Part catalogs, stats
│
├── training/               # Model training code
│   ├── grounding_dino/     # Primary model
│   ├── florence2/          # Comparison model
│   └── converters/         # JSON → model formats
│
├── inference/              # Production inference server
│   ├── server.py           # FastAPI server
│   ├── models/             # Model weights
│   └── api/                # API endpoints
│
├── clients/                # Client applications
│   ├── ios/                # iPad ARKit app
│   ├── android/            # Android app (future)
│   └── web/                # Web demo
│
├── evaluation/             # Testing & metrics
│   ├── benchmarks/
│   └── test_images/
│
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

---

## Quick Start

### Prerequisites

- **Blender 3.6+** (for data generation)
- **Python 3.9+**
- **CUDA-capable GPU** (RTX 3090 recommended for training)
- **LDraw Parts Library** (download from [ldraw.org](https://www.ldraw.org/))

### Installation

```bash
# Clone repository
git clone git@github.com:kyjohnso/brickscope.git
cd brickscope

# Install Python dependencies (coming soon)
pip install -r requirements.txt

# Install Blender addon
# 1. Open Blender
# 2. Edit → Preferences → Add-ons → Install
# 3. Select blender/addons/brickscope
# 4. Enable "BrickScope: Synthetic LEGO Dataset Generator"
```

### Generating Your First Dataset

```bash
# Generate 100 test images
cd blender/scripts
python generate_dataset.py --count 100 --scene-type single_piece --output ../../data/test

# View annotations
python ../../scripts/visualize_annotations.py ../../data/test
```

---

## Technical Details

### Data Format

BrickScope uses a **rich intermediate JSON format** that stores:
- Image metadata (camera, lighting, render settings)
- Per-object annotations (bboxes, visibility, occlusion, 3D pose)
- Multiple caption variants (short, medium, long, natural language)
- Scene statistics (piece counts, difficulty scores)

Lightweight converters transform this to model-specific formats:
```
Blender → Rich JSON → Converters → Florence-2 / Grounding-DINO / YOLO
```

See [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md) for complete data format specification.

### Models

**Primary: Grounding-DINO**
- Purpose-built for text-grounded object detection
- Best for dense scenes with selective filtering
- 5-8 fps on RTX 3090
- Apache 2.0 license

**Secondary: Florence-2** (research comparison)
- Vision-language foundation model
- More flexible, slower (3-5 fps)
- Potential MSc research contribution

### Why Synthetic Data?

Real-world LEGO datasets don't exist at scale. BrickScope generates:
- **1M+ images** with perfect annotations
- **Heavy occlusion** (30-90% average in pile scenes)
- **Domain randomization** (lighting, backgrounds, rotations)
- **Zero annotation cost**

Goal: Minimize synthetic→real domain gap through diversity.

---

## Research Goals

This project is part of an MSc research program investigating:
- Comparative performance of Florence-2 vs Grounding-DINO on dense object detection
- Synthetic data quality vs quantity tradeoffs
- Grounded detection for user-driven filtering in AR applications

---

## Roadmap

- [ ] **Phase 1.1**: Blender addon core infrastructure (LDraw import, scene generation)
- [ ] **Phase 1.2**: Annotation export (JSON with visibility/occlusion)
- [ ] **Phase 1.3**: Generate 10k validation dataset
- [ ] **Phase 2.1**: Train Grounding-DINO baseline
- [ ] **Phase 2.2**: Evaluate on real photos, measure domain gap
- [ ] **Phase 2.3**: Iterate on data quality
- [ ] **Phase 3.1**: FastAPI inference server
- [ ] **Phase 3.2**: iPad ARKit client
- [ ] **Phase 4.1**: Write MSc thesis
- [ ] **Phase 4.2**: Publish dataset & research

---

## Contributing

This is currently a personal research project. Contributions, ideas, and feedback are welcome via issues and discussions.

---

## License

Apache 2.0 - See [LICENSE](LICENSE) for details

---

## Resources

**Models:**
- [Grounding-DINO](https://github.com/IDEA-Research/GroundingDINO)
- [Florence-2](https://huggingface.co/microsoft/Florence-2-large)

**Data:**
- [LDraw Parts Library](https://www.ldraw.org/)
- [Poly Haven HDRIs](https://polyhaven.com/hdris)
- [Rebrickable API](https://rebrickable.com/api/)

**Hardware:**
- Linux Workstation: RTX 3090 (24GB VRAM)
- Client Device: iPad Air 5th Gen (M1)

---

## Acknowledgments

- LDraw community for the comprehensive LEGO parts library (CC-BY-4.0)
- Grounding-DINO and Florence-2 teams for open-source models
- Poly Haven for high-quality HDRIs (CC0)

---

**Status:** Early development - Phase 1 (Blender addon)
**Author:** Kyle Johnson
**Contact:** [GitHub Issues](https://github.com/kyjohnso/brickscope/issues)

For detailed technical decisions and specifications, see [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md).
