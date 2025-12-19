# Python Coding Conventions

## Constants

- Use **SCREAMING_SNAKE_CASE** for constants (not camelCase)
- Place constants at the **top of the module** after imports
- Group constants by theme with comments
- Extract hardcoded values that are configuration/tuning parameters

### Examples

**Good:**
```python
#!/usr/bin/env python3
import inkex

# Grid configuration
GRID_CELL_SIZE_MM = 5.0
GRID_SAMPLES_PER_CELL = 12

# Geometry configuration
BEZIER_FLATTEN_SEGMENTS = 8

class MyExtension(inkex.EffectExtension):
    def my_method(self):
        cell_size = self.svg.unittouu(f"{GRID_CELL_SIZE_MM}mm")
```

**Bad:**
```python
def my_method(self):
    cell_size_mm = 5.0  # Magic number buried in code
    samples = 12
```

## Function Parameters

Keep default arguments when they are **logical function parameters** (behavior options), not configuration constants:

```python
# ✅ Good - behavioral parameter
def generate_spots(self, density, use_clustering=True):
    pass

# ❌ Bad - should be a module constant
def create_grid(self, bbox, cell_size_mm=5.0):
    pass
```

## Type Hints

Use type hints for all function signatures to improve code clarity and IDE support:

```python
def point_in_path(self, x: float, y: float, path_element) -> bool:
    """Test if point is inside path"""
    pass

def create_grid(
    self,
    bbox,
    path_element,
    cell_size_mm: float = GRID_CELL_SIZE_MM
) -> tuple[list[list[int]], int, int, float, float]:
    """Create coverage grid"""
    pass
```

## Docstrings

Use Google-style docstrings for all public methods:

```python
def generate_valid_point(
    self,
    x_min: float,
    y_min: float,
    grid: list[list[int]],
    elem
) -> tuple[float | None, float | None]:
    """Generate a point inside the shape using grid-guided sampling.

    Args:
        x_min: Left boundary of bounding box
        y_min: Top boundary of bounding box
        grid: Coverage grid with cell classifications (0=empty, 1=partial, 2=full)
        elem: SVG path element to test points against

    Returns:
        Tuple of (x, y) coordinates if successful, (None, None) if failed

    Note:
        Attempts up to MAX_POINT_GENERATION_RETRIES times before giving up.
    """
```

## Early Returns (Guard Clauses)

Use early returns to reduce nesting and improve readability:

```python
# ✅ Good
def process_data(data):
    if not data:
        return None

    if not validate(data):
        return None

    # Main logic here (less indentation)
    return result

# ❌ Bad
def process_data(data):
    if data:
        if validate(data):
            # Main logic here (deeply nested)
            return result
        else:
            return None
    else:
        return None
```

## Descriptive Naming

Always use descriptive variable names, even for loop indices:

```python
# ✅ Good - Clear intent
for spot_index in range(density):
    for segment_index in range(len(flattened) - 1):
        for row_index in range(grid_rows):
            for col_index in range(grid_cols):

# ❌ Bad - Single letters
for i in range(density):
    for j in range(len(flattened) - 1):
        for r in range(grid_rows):
            for c in range(grid_cols):

# Exception: Short mathematical operations where convention is clear
for t in range(segments + 1):  # t is standard for parametric curves
    angle = (t / segments) * 2 * math.pi  # OK in this narrow context
```

**Naming conventions:**
- Coordinates: `point_x`, `point_y` (not `x`, `y`)
- Cluster positions: `cluster_x`, `cluster_y` (not `cx`, `cy`)
- Grid positions: `row_index`, `col_index` (not `row`, `col` or `r`, `c`)
- Loop indices: `spot_index`, `segment_index`, `attempt_number` (not `i`, `j`, `k`)
- Only exception: parametric values like `t` in mathematical contexts

## Style Guide

Follow [PEP 8](https://pep8.org/) Python style guide:
- 4 spaces for indentation
- Maximum line length: 100 characters (flexible)
- Type hints for all functions
- Google-style docstrings for all public methods
- Descriptive variable names (no single-letter variables except mathematical parameters)
