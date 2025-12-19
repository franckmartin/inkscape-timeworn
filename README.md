# Timeworn - Inkscape Extension

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://franckmartin.github.io/inkscape-timeworn/)

A parametric texture generator for Inkscape that creates authentic weathered and aged effects with organic spot patterns simulating paint deterioration on ancient surfaces.

## Features

- **Parametric control** - Adjust size, density, irregularity, clustering, and elongation
- **Organic shapes** - Generate smooth blobs or angular fragments
- **Realistic clustering** - Non-uniform distribution patterns
- **Pure vector output** - Individual SVG paths with precise millimeter measurements
- **Real-time preview** - Iterate quickly with Inkscape's live preview

## Quick Start

```bash
# Clone repository
git clone https://github.com/franckmartin/inkscape-timeworn.git
cd inkscape-timeworn

# Install (Snap version)
cp timeworn.* ~/snap/inkscape/common/extensions/
chmod +x ~/snap/inkscape/common/extensions/timeworn.py

# Install (Regular version)
cp timeworn.* ~/.config/inkscape/extensions/
chmod +x ~/.config/inkscape/extensions/timeworn.py
```

Restart Inkscape and find the extension at **Extensions > Render > Timeworn**

## Documentation

Full documentation is available at **[franckmartin.github.io/inkscape-timeworn](https://franckmartin.github.io/inkscape-timeworn/)**

- [Installation Guide](https://franckmartin.github.io/inkscape-timeworn/installation/)
- [Usage Guide](https://franckmartin.github.io/inkscape-timeworn/usage/)
- [Parameters Reference](https://franckmartin.github.io/inkscape-timeworn/parameters/)
- [Examples](https://franckmartin.github.io/inkscape-timeworn/examples/)
- [Troubleshooting](https://franckmartin.github.io/inkscape-timeworn/troubleshooting/)
- [Development Guide](https://franckmartin.github.io/inkscape-timeworn/development/)

## Requirements

- Inkscape 1.4.2 or later
- Python 3.x (bundled with Inkscape)

## Contributing

Contributions are welcome! Please see the [Development Guide](https://franckmartin.github.io/inkscape-timeworn/development/) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
