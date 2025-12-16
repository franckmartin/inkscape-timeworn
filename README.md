# Fresco Texture - Inkscape Extension

A parametric texture generator for Inkscape that creates weathered fresco effects with organic, irregularly distributed spots simulating paint deterioration on ancient frescoes.

## Features

- **Parametric control**: Adjust size, density, irregularity, clustering, and elongation
- **Organic shapes**: Generate smooth, natural-looking blobs or angular fragments
- **Clustering system**: Create realistic non-uniform distribution patterns
- **Elongation control**: Stretch spots along customizable axes with variation
- **Pure vector output**: All spots are individual vector paths (black fill, no stroke)
- **Real measurements**: Size parameters in millimeters for precise control

## Installation

### Method 1: Symbolic Links (Recommended for Development)

```bash
# Clone or download to your preferred location
cd ~/Code/Inkscape
git clone [your-repo-url] fresco-texture

# Create symbolic links to Inkscape extensions directory
# For Snap version of Inkscape:
ln -s ~/Code/Inkscape/fresco-texture/fresco_texture.inx ~/snap/inkscape/common/extensions/fresco_texture.inx
ln -s ~/Code/Inkscape/fresco-texture/fresco_texture.py ~/snap/inkscape/common/extensions/fresco_texture.py

# For regular Inkscape installation:
ln -s ~/Code/Inkscape/fresco-texture/fresco_texture.inx ~/.config/inkscape/extensions/fresco_texture.inx
ln -s ~/Code/Inkscape/fresco-texture/fresco_texture.py ~/.config/inkscape/extensions/fresco_texture.py
```

### Method 2: Direct Copy

Copy both `fresco_texture.inx` and `fresco_texture.py` to your Inkscape extensions directory:

**Snap version:**

```bash
cp fresco_texture.* ~/snap/inkscape/common/extensions/
chmod +x ~/snap/inkscape/common/extensions/fresco_texture.py
```

**Regular installation:**

```bash
cp fresco_texture.* ~/.config/inkscape/extensions/
chmod +x ~/.config/inkscape/extensions/fresco_texture.py
```

Restart Inkscape after installation.

## Usage

1. Create or select a closed path (rectangle, circle, or any shape)
2. Go to **Extensions > Render > Fresco Texture**
3. Adjust parameters to achieve desired effect
4. Click **Apply**

The extension generates a group of black spots as separate objects. You can then:

- Ungroup and use **Path > Union** to merge all spots
- Use **Path > Difference** to subtract from your base shape

## Parameters

### Object Parameters

- **Minimum/Maximum size (mm)**: Size range for individual spots
- **Shape type**:
  - Organic blobs: Smooth, rounded shapes
  - Angular fragments: Sharp-edged fragments
  - Mixed: Random combination of both
- **Irregularity (%)**: Border variation (0 = regular, 100 = very irregular)

### Distribution Parameters

- **Density**: Total number of spots to generate (10-1000)
- **Clustering (%)**: Tendency to group spots together (0 = uniform, 100 = strong clusters)
- **Number of clusters**: How many cluster centers to create (1-20)

### Elongation Parameters

- **Factor**: Stretch ratio (1.0 = circular, 5.0 = very elongated)
- **Factor variation (%)**: Random variation in elongation per spot
- **Angle (°)**: Main elongation direction (0° = horizontal, 90° = vertical)
- **Angle variation (%)**: Random variation in direction per spot

## Requirements

- Inkscape 1.4.2 or later
- Python 3.x
- Inkscape Python extensions API (inkex)

## Technical Details

- Uses Inkscape's native unit conversion (`svg.unittouu()`) for accurate millimeter measurements
- Generates pure vector paths with Bézier curves for smooth organic shapes
- Implements exponential distribution for realistic cluster concentration
- Normalizes irregularity to maintain consistent average spot size

## Examples

**Weathered fresco effect:**

- Size: 0.5-2.5mm
- Density: 500-1000
- Clustering: 60-80%
- Elongation: 2.0-3.0

**Fine grain texture:**

- Size: 0.3-1.0mm
- Density: 1000
- Clustering: 30%
- Irregularity: 30%
