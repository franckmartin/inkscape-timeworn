# Development Guide

## Setting Up Development Environment

### Clone Repository

```bash
git clone https://github.com/franckmartin/inkscape-timeworn.git
cd inkscape-timeworn
```

### Install for Development

Use the sync script for quick iteration during development:

```bash
chmod +x sync.sh
```

The script automatically detects its location and copies files to Inkscape extensions directory.

## Development Workflow

### 1. Make Changes

Edit `timeworn.py` or `timeworn.inx` in your local repository.

### 2. Sync to Inkscape

```bash
./sync.sh
```

### 3. Test in Inkscape

Restart Inkscape to load the updated extension, then test your changes.

### 4. Iterate

Repeat steps 1-3 until satisfied with changes.

## Sync Script Details

The default `sync.sh` is configured for Snap version of Inkscape:

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# For Snap version
cp "$SCRIPT_DIR"/timeworn.* ~/snap/inkscape/common/extensions/

echo "Files synced to Inkscape extensions"
```

### For Regular Inkscape Installation

Modify `sync.sh` to use the standard extensions directory:

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# For regular installation
cp "$SCRIPT_DIR"/timeworn.* ~/.config/inkscape/extensions/

echo "Files synced to Inkscape extensions"
```

## Project Structure

```
inkscape-timeworn/
├── timeworn.py          # Main extension code
├── timeworn.inx         # UI definition (XML)
├── sync.sh              # Development sync script
├── README.md            # Project overview
├── LICENSE              # MIT License
├── docs/                # Documentation (MkDocs)
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   ├── parameters.md
│   ├── examples.md
│   ├── troubleshooting.md
│   └── development.md
├── mkdocs.yml           # Documentation config
└── .github/
    └── workflows/
        └── docs.yml     # GitHub Pages deployment
```

## Code Architecture

### Main Components

**`timeworn.py`**

- `Timeworn` class extends `inkex.EffectExtension`
- `add_arguments()` - Defines command-line parameters
- `effect()` - Main execution logic
- Helper methods for shape generation and distribution

**`timeworn.inx`**

- XML definition for Inkscape's extension UI
- Parameter definitions with labels and constraints
- Menu placement configuration

### Key Algorithms

**Spot Generation:**
- Organic blobs use parametric curves with random noise
- Angular fragments use random polygons
- Irregularity is normalized to maintain average size

**Distribution:**
- Clustering uses exponential distribution around random centers
- Non-clustered spots use uniform random distribution
- All points constrained to selected shape boundary

**Elongation:**
- Applied via scaling transformation matrix
- Angle variation randomizes direction per spot
- Factor variation randomizes stretch per spot

## Testing

### Manual Testing Checklist

- [ ] Install extension via sync script
- [ ] Verify menu appears: **Extensions > Render > Timeworn**
- [ ] Test with basic rectangle
- [ ] Test all shape types (organic, angular, mixed)
- [ ] Test clustering at various levels
- [ ] Test elongation parameters
- [ ] Test extreme parameter values
- [ ] Test with complex boundary shapes
- [ ] Verify output is valid SVG paths

### Edge Cases to Test

- Minimum density (10 spots)
- Maximum density (1000 spots)
- Very small boundary shape
- Very large boundary shape
- Complex concave shapes
- Zero clustering vs. maximum clustering

## Contributing

### Before Submitting PR

1. Test thoroughly with various parameters
2. Ensure code follows existing style
3. Update documentation if adding features
4. Add examples for new functionality
5. Check that sync script still works

### Commit Message Format

Follow Conventional Commits:

```
type(scope): description

Examples:
feat(params): add new blend mode parameter
fix(distribution): correct clustering calculation
docs(readme): update installation instructions
```

### Pull Request Guidelines

- Describe what your PR does and why
- Include screenshots/examples for visual changes
- Link related issues if applicable
- Keep changes focused and atomic

## Building Documentation

Documentation uses MkDocs with Material theme.

### Install Dependencies

On modern Linux systems, Python packages must be installed in a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

!!! note "Virtual Environment"
    The virtual environment must be activated each time you work on documentation. To deactivate it later, run `deactivate`.

### Preview Locally

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start development server
mkdocs serve
```

Then open http://localhost:8000

### Build Static Site

```bash
mkdocs build
```

### Deploy to GitHub Pages

Deployment is automated via GitHub Actions on push to main branch.

Manual deployment (with virtual environment activated):

```bash
mkdocs gh-deploy
```

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/franckmartin/inkscape-timeworn/blob/main/LICENSE) for details.
