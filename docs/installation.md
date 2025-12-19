# Installation

## For Snap Version of Inkscape

!!! warning "Snap Security Restrictions"
    Snap has security restrictions that prevent symbolic links from working. Files must be copied directly.

```bash
# Clone or download to your preferred location
git clone https://github.com/franckmartin/inkscape-timeworn.git
cd inkscape-timeworn

# Copy files to Inkscape extensions directory
cp timeworn.* ~/snap/inkscape/common/extensions/
chmod +x ~/snap/inkscape/common/extensions/timeworn.py
```

## For Regular Inkscape Installation

```bash
# Clone or download
git clone https://github.com/franckmartin/inkscape-timeworn.git
cd inkscape-timeworn

# Copy files to extensions directory
cp timeworn.* ~/.config/inkscape/extensions/
chmod +x ~/.config/inkscape/extensions/timeworn.py
```

## Verify Installation

After installation, restart Inkscape. The extension should appear in:

**Extensions > Render > Timeworn**

If you don't see it, check the [Troubleshooting](troubleshooting.md) page.
