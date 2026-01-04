"""
Distribution Manager - Weighted random sampling for parts and colors
"""

import random
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class DistributionItem:
    """Single item in a distribution (part or color) with weight"""

    def __init__(self, id: str, name: str, weight: float = 1.0):
        self.id = id
        self.name = name
        self.weight = max(0.0, weight)  # Ensure non-negative

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DistributionItem':
        return cls(data["id"], data["name"], data.get("weight", 1.0))


class WeightedDistribution:
    """
    Weighted distribution for sampling items

    Supports:
    - Adding/removing items with weights
    - Normalizing weights
    - Sampling based on weights
    - Save/load to JSON
    """

    def __init__(self, items: Optional[List[DistributionItem]] = None):
        self.items: List[DistributionItem] = items if items else []

    def add_item(self, id: str, name: str, weight: float = 1.0):
        """Add an item to the distribution"""
        self.items.append(DistributionItem(id, name, weight))

    def remove_item(self, id: str):
        """Remove an item by ID"""
        self.items = [item for item in self.items if item.id != id]

    def get_item(self, id: str) -> Optional[DistributionItem]:
        """Get an item by ID"""
        for item in self.items:
            if item.id == id:
                return item
        return None

    def set_weight(self, id: str, weight: float):
        """Update weight for an item"""
        item = self.get_item(id)
        if item:
            item.weight = max(0.0, weight)

    def get_normalized_weights(self) -> List[float]:
        """
        Get normalized weights (sum to 1.0)
        Returns empty list if total weight is 0
        """
        total = sum(item.weight for item in self.items)
        if total == 0:
            return []
        return [item.weight / total for item in self.items]

    def sample(self, count: int = 1, seed: Optional[int] = None) -> List[DistributionItem]:
        """
        Sample items from the distribution based on weights

        Args:
            count: Number of samples to draw
            seed: Random seed for reproducibility

        Returns:
            List of sampled items (can contain duplicates)
        """
        if not self.items:
            return []

        if seed is not None:
            random.seed(seed)

        weights = self.get_normalized_weights()
        if not weights:
            # All weights are 0, sample uniformly
            return [random.choice(self.items) for _ in range(count)]

        return random.choices(self.items, weights=weights, k=count)

    def get_expected_counts(self, total: int) -> Dict[str, int]:
        """
        Calculate expected count for each item given total samples

        Args:
            total: Total number of items to distribute

        Returns:
            Dictionary mapping item ID to expected count
        """
        normalized = self.get_normalized_weights()
        if not normalized:
            return {}

        counts = {}
        for item, norm_weight in zip(self.items, normalized):
            counts[item.id] = int(round(norm_weight * total))

        return counts

    def to_dict(self) -> dict:
        """Export to dictionary"""
        return {
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeightedDistribution':
        """Import from dictionary"""
        items = [DistributionItem.from_dict(item_data) for item_data in data["items"]]
        return cls(items)

    def save(self, filepath: Path):
        """Save distribution to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'WeightedDistribution':
        """Load distribution from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class DistributionConfig:
    """
    Complete configuration for part and color distributions
    Used for synthetic data generation
    """

    def __init__(self,
                 part_distribution: Optional[WeightedDistribution] = None,
                 color_distribution: Optional[WeightedDistribution] = None,
                 total_pieces: int = 100,
                 seed: Optional[int] = None):
        self.part_distribution = part_distribution or WeightedDistribution()
        self.color_distribution = color_distribution or WeightedDistribution()
        self.total_pieces = total_pieces
        self.seed = seed

    def generate_part_color_pairs(self) -> List[Tuple[str, str]]:
        """
        Generate list of (part_id, color_id) pairs based on distributions

        Returns:
            List of tuples (part_id, color_id)
        """
        # Sample parts
        parts = self.part_distribution.sample(self.total_pieces, seed=self.seed)

        # Sample colors (use different seed if provided)
        color_seed = self.seed + 1 if self.seed is not None else None
        colors = self.color_distribution.sample(self.total_pieces, seed=color_seed)

        return [(part.id, color.id) for part, color in zip(parts, colors)]

    def to_dict(self) -> dict:
        """Export to dictionary"""
        return {
            "parts": self.part_distribution.to_dict(),
            "colors": self.color_distribution.to_dict(),
            "total_pieces": self.total_pieces,
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DistributionConfig':
        """Import from dictionary"""
        return cls(
            part_distribution=WeightedDistribution.from_dict(data["parts"]),
            color_distribution=WeightedDistribution.from_dict(data["colors"]),
            total_pieces=data.get("total_pieces", 100),
            seed=data.get("seed"),
        )

    def save(self, filepath: Path):
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'DistributionConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Preset distributions for common use cases
def get_common_parts_distribution() -> WeightedDistribution:
    """Get distribution of common LEGO parts"""
    dist = WeightedDistribution()

    # Bricks - higher weight
    dist.add_item("3001", "Brick 2x4", weight=1.0)
    dist.add_item("3002", "Brick 2x3", weight=0.8)
    dist.add_item("3003", "Brick 2x2", weight=0.9)
    dist.add_item("3004", "Brick 1x2", weight=1.0)
    dist.add_item("3005", "Brick 1x1", weight=0.7)

    # Plates - medium weight
    dist.add_item("3021", "Plate 2x3", weight=0.6)
    dist.add_item("3022", "Plate 2x2", weight=0.7)
    dist.add_item("3023", "Plate 1x2", weight=0.8)
    dist.add_item("3024", "Plate 1x1", weight=0.5)

    return dist


def get_common_colors_distribution() -> WeightedDistribution:
    """Get distribution of common LEGO colors"""
    dist = WeightedDistribution()

    # Primary colors - higher weight
    dist.add_item("4", "Red", weight=1.0)
    dist.add_item("1", "Blue", weight=1.0)
    dist.add_item("2", "Green", weight=0.8)
    dist.add_item("14", "Yellow", weight=0.9)

    # Neutral colors - medium weight
    dist.add_item("0", "Black", weight=0.7)
    dist.add_item("15", "White", weight=0.7)
    dist.add_item("72", "Dark Gray", weight=0.5)

    return dist
