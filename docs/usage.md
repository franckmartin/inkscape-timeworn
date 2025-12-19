# Usage Guide

## Basic Workflow

1. **Create or select a closed path** (rectangle, circle, or any shape)
2. Go to **Extensions > Render > Timeworn**
3. **Adjust parameters** to achieve desired effect
4. Click **Apply**

The extension generates a group of black spots as separate objects within the selected shape.

## Shape-Aware Distribution

Timeworn uses intelligent shape-aware distribution to ensure all spots stay within your selected path boundaries:

- **Respects actual shape**: Spots are confined to the exact shape, not just the bounding box
- **Handles complex paths**: Works with circles, curves, and complex organic shapes
- **Supports compound paths**: Correctly handles shapes with holes (like donuts or rings)
- **Preserves clustering**: Natural clustering behavior is maintained while respecting boundaries
- **Exact density**: The specified number of spots will be placed within the shape

This means you can use any closed path as a boundary - circles, stars, custom shapes, or even shapes with cutouts - and the texture will conform perfectly to your design.

## Working with the Output

### Merging Spots

To create a single unified shape from all spots:

1. Select the generated group
2. Go to **Object > Ungroup** (or press `Ctrl+Shift+G`)
3. With all spots selected, go to **Path > Union** (or press `Ctrl++`)

### Creating Cutouts

To subtract the texture from your base shape:

1. Ensure your base shape is below the spots
2. Select both the base shape and the texture group
3. Go to **Path > Difference** (or press `Ctrl+-`)

### Layering Effects

For more complex effects:

- Apply the extension multiple times with different parameters
- Use different shapes as boundaries for varied distribution
- Combine with Inkscape's blur and opacity settings

## Tips

!!! tip "Start Simple"
    Begin with moderate density (200-300) and clustering (40-60%) to see how parameters affect the result.

!!! tip "Experiment with Elongation"
    Setting elongation angle to match natural wear patterns (e.g., vertical for rain damage) creates more realistic effects.

!!! tip "Size Variation"
    A wider gap between minimum and maximum size creates more organic, natural-looking textures.
