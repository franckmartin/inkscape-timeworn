# Timeworn - Inkscape Extension

A parametric texture generator for Inkscape that creates authentic aging and weathered effects with organic, irregularly distributed spots simulating paint deterioration on ancient surfaces.

## Features

- **Shape-aware distribution**: Spots intelligently conform to any path shape, including curves and holes
- **Parametric control**: Adjust size, density, irregularity, clustering, and elongation
- **Organic shapes**: Generate smooth, natural-looking blobs or angular fragments
- **Clustering system**: Create realistic non-uniform distribution patterns
- **Elongation control**: Stretch spots along customizable axes with variation
- **Pure vector output**: All spots are individual vector paths (black fill, no stroke)
- **Real measurements**: Size parameters in millimeters for precise control

## Requirements

- Inkscape 1.4.2 or later
- Python 3.x
- Inkscape Python extensions API (inkex)

## Quick Links

- [Installation Guide](installation.md) - Get started with Timeworn
- [Usage Guide](usage.md) - Learn how to use the extension
- [Parameters Reference](parameters.md) - Detailed parameter documentation
- [Examples](examples.md) - See what you can create
- [Troubleshooting](troubleshooting.md) - Fix common issues

## Technical Details

- Shape-aware placement using ray-casting algorithm with Bézier curve flattening
- Coverage grid optimization with 5mm fixed cell size for efficient sampling
- Uses Inkscape's native unit conversion (`svg.unittouu()`) for accurate millimeter measurements
- Generates pure vector paths with Bézier curves for smooth organic shapes
- Implements exponential distribution for realistic cluster concentration
- Normalizes irregularity to maintain consistent average spot size
- Handles compound paths with holes using even-odd winding rule

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues on [GitHub](https://github.com/franckmartin/inkscape-timeworn).
