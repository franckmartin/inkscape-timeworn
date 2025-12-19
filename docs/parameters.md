# Parameters Reference

## Object Parameters

### Size

**Minimum size (mm)** and **Maximum size (mm)**

Defines the size range for individual spots in millimeters.

- Smaller values (0.3-1.0mm) create fine, detailed textures
- Larger values (2.0-5.0mm) create bold, dramatic effects
- Wider ranges create more organic variation

!!! example
    For weathered fresco: min=0.5mm, max=2.5mm

### Shape Type

Controls the visual style of generated spots:

- **Organic blobs**: Smooth, rounded shapes with natural curves
- **Angular fragments**: Sharp-edged fragments with irregular polygonal shapes
- **Mixed**: Random combination of both types for varied texture

### Irregularity

**Irregularity (%)**

Controls border variation and shape complexity.

- `0%` - Regular, smooth shapes
- `50%` - Moderate organic variation
- `100%` - Highly irregular, chaotic borders

The algorithm normalizes irregularity to maintain consistent average spot size regardless of this parameter.

---

## Distribution Parameters

### Density

**Total number of spots** to generate across the selected area.

- **Range**: 10-1000 spots
- Lower density (10-100): Sparse, minimal texture
- Medium density (200-500): Balanced coverage
- High density (500-1000): Dense, intense weathering

### Clustering

**Clustering (%)**

Controls the tendency for spots to group together.

- `0%` - Uniform, even distribution
- `50%` - Moderate clustering with some concentration areas
- `100%` - Strong clusters with high concentration zones

Uses exponential distribution to create realistic non-uniform patterns.

### Number of Clusters

**Number of cluster centers** to create when clustering is enabled.

- **Range**: 1-20 clusters
- More clusters create multiple concentration zones
- Fewer clusters create distinct, separated groupings

!!! note
    This parameter only affects distribution when Clustering % > 0

---

## Elongation Parameters

### Factor

**Elongation ratio** for stretching spots.

- `1.0` - Circular/non-elongated (default)
- `2.0` - Moderately stretched
- `5.0` - Highly elongated

### Factor Variation

**Factor variation (%)**

Random variation in elongation per spot.

- `0%` - All spots use same elongation factor
- `50%` - Moderate variation
- `100%` - High variation, each spot stretched differently

### Angle

**Main elongation direction** in degrees.

- `0°` - Horizontal elongation
- `90°` - Vertical elongation
- Custom angles for directional weathering effects

### Angle Variation

**Angle variation (%)**

Random variation in elongation direction per spot.

- `0%` - All spots aligned to same angle
- `50%` - Moderate directional variation
- `100%` - Each spot can point in any direction

!!! tip "Realistic Weathering"
    For rain damage patterns, use: angle=90°, factor=2.5, angle variation=20%
