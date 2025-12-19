# Troubleshooting

## Extension Not Appearing in Menu

### Verify Installation Location

Check that files are in the correct extensions directory:

**For Snap version:**
```bash
ls -l ~/snap/inkscape/common/extensions/timeworn.*
```

**For regular installation:**
```bash
ls -l ~/.config/inkscape/extensions/timeworn.*
```

### Check File Permissions

The Python script must be executable:

```bash
# For Snap
chmod +x ~/snap/inkscape/common/extensions/timeworn.py

# For regular installation
chmod +x ~/.config/inkscape/extensions/timeworn.py
```

### Restart Inkscape

Extensions are loaded at startup. Make sure to completely close and restart Inkscape after installation.

### Check for Errors

View Inkscape errors in the terminal:

```bash
inkscape 2>&1 | grep timeworn
```

### Clear Cache

Sometimes clearing Inkscape's cache helps:

```bash
rm -rf ~/.cache/inkscape/
```

---

## Invalid XML Error

This error typically occurs with Snap versions when symbolic links are used.

**Solution:** Files must be direct copies, not symbolic links.

```bash
# Remove any symbolic links
rm ~/snap/inkscape/common/extensions/timeworn.*

# Copy files directly
cd /path/to/inkscape-timeworn
cp timeworn.* ~/snap/inkscape/common/extensions/
chmod +x ~/snap/inkscape/common/extensions/timeworn.py
```

---

## Extension Runs but No Output

### Check Selection

The extension requires a **closed path** to be selected:

- Rectangle, circle, ellipse, or closed polygon work
- Open paths or text objects won't work
- Make sure something is selected before running the extension

### Verify Parameters

- Density must be > 0
- Size values must be positive
- Check that minimum size < maximum size

---

## Spots Appear Outside Boundary

This is expected behavior. The extension uses the selected shape as a general boundary, but spots may slightly overlap the edges due to their size and positioning algorithm.

**Workaround:** Make your boundary shape slightly larger than needed, then trim after generation.

---

## Performance Issues

### Large Density Values

Generating 1000+ spots can take time:

- Start with lower density (200-400) to preview
- Increase gradually once satisfied with parameters
- Consider breaking large areas into multiple applications

### Complex Shapes

Using very complex boundary shapes may slow down generation:

- Simplify your boundary path if possible
- Use basic shapes (rectangle, circle) for faster results

---

## Python or Import Errors

### Missing Dependencies

The extension requires Inkscape's Python environment with `inkex` module.

**For system Inkscape:** Usually included by default

**For Snap Inkscape:** All dependencies are bundled

If you see import errors, verify your Inkscape installation is complete and up to date.

---

## Still Having Issues?

If none of these solutions work:

1. Check the [GitHub Issues](https://github.com/franckmartin/inkscape-timeworn/issues) for similar problems
2. Open a new issue with:
   - Your Inkscape version (`Help > About Inkscape`)
   - Installation method (Snap/regular)
   - Operating system
   - Full error message if available
   - Steps to reproduce the problem
