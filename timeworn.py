#!/usr/bin/env python3
import inkex
import random
import math

class Timeworn(inkex.EffectExtension):
    
    def add_arguments(self, pars):
        pars.add_argument("--density", type=int, default=200)
        pars.add_argument("--size_min", type=float, default=0.5)
        pars.add_argument("--size_max", type=float, default=3.0)
        pars.add_argument("--irregularity", type=int, default=50)
        pars.add_argument("--shape_type", default="organic")
        pars.add_argument("--clustering", type=int, default=30)
        pars.add_argument("--num_clusters", type=int, default=5)
        pars.add_argument("--elongation", type=float, default=1.5)
        pars.add_argument("--elongation_variation", type=int, default=30)
        pars.add_argument("--elongation_angle", type=float, default=45.0)
        pars.add_argument("--angle_variation", type=int, default=30)

    def flatten_bezier(self, p0, p1, p2, p3, segments=8):
        """Flatten a cubic Bézier curve into line segments"""
        points = []
        for i in range(segments + 1):
            t = i / segments
            # Cubic Bézier formula
            t2 = t * t
            t3 = t2 * t
            mt = 1 - t
            mt2 = mt * mt
            mt3 = mt2 * mt

            x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
            y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
            points.append((x, y))
        return points

    def point_in_path(self, x, y, path_element):
        """Test if point (x,y) is inside the path using ray-casting algorithm"""
        # Get path as superpath for predictable format
        path = path_element.path.to_superpath()

        # Flatten path to line segments
        segments = []
        for subpath in path:
            for i in range(len(subpath)):
                # Each segment in superpath is ((x,y), (cp1_x, cp1_y), (cp2_x, cp2_y))
                # Next point is at index (i+1) % len
                current = subpath[i]
                next_idx = (i + 1) % len(subpath)
                if next_idx == 0 and i == len(subpath) - 1:
                    # Close path - connect last to first
                    next_point = subpath[0]
                else:
                    next_point = subpath[next_idx]

                # Current point, control points, next point
                p0 = (current[1][0], current[1][1])  # current point
                p1 = (current[2][0], current[2][1])  # control point 1
                p2 = (next_point[0][0], next_point[0][1])  # control point 2
                p3 = (next_point[1][0], next_point[1][1])  # next point

                # Flatten bezier to line segments
                flattened = self.flatten_bezier(p0, p1, p2, p3, segments=8)
                for j in range(len(flattened) - 1):
                    segments.append((flattened[j], flattened[j + 1]))

        # Ray casting: count intersections with horizontal ray from point
        intersections = 0
        for seg_start, seg_end in segments:
            x1, y1 = seg_start
            x2, y2 = seg_end

            # Check if segment crosses the horizontal ray from (x, y) to the right
            if y1 == y2:  # Horizontal segment, skip
                continue

            # Check if ray is within segment's y range
            if not (min(y1, y2) < y <= max(y1, y2)):
                continue

            # Calculate x coordinate of intersection
            x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)

            # Count if intersection is to the right of point
            if x_intersect > x:
                intersections += 1

        # Odd number of intersections = inside (even-odd rule)
        return intersections % 2 == 1

    def create_coverage_grid(self, bbox, path_element, cell_size_mm=5.0):
        """
        Create coverage grid with fixed cell size.
        Returns: (grid, grid_cols, grid_rows, cell_width, cell_height)
        Grid values: 0=empty, 1=partial, 2=full
        """
        x_min, y_min = bbox.left, bbox.top
        width, height = bbox.width, bbox.height

        # Convert cell size to user units
        cell_size = self.svg.unittouu(f"{cell_size_mm}mm")

        # Calculate grid dimensions
        grid_cols = max(1, int(width / cell_size))
        grid_rows = max(1, int(height / cell_size))

        # Actual cell dimensions
        cell_width = width / grid_cols
        cell_height = height / grid_rows

        # Initialize grid
        grid = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]

        # Sample each cell to determine coverage
        samples_per_cell = 12
        for row in range(grid_rows):
            for col in range(grid_cols):
                # Cell bounds
                cell_x_min = x_min + col * cell_width
                cell_y_min = y_min + row * cell_height

                # Sample points in cell
                inside_count = 0
                for _ in range(samples_per_cell):
                    sample_x = cell_x_min + random.uniform(0, cell_width)
                    sample_y = cell_y_min + random.uniform(0, cell_height)

                    if self.point_in_path(sample_x, sample_y, path_element):
                        inside_count += 1

                # Classify cell
                coverage = inside_count / samples_per_cell
                if coverage == 0:
                    grid[row][col] = 0  # empty
                elif coverage >= 0.9:
                    grid[row][col] = 2  # full
                else:
                    grid[row][col] = 1  # partial

        return grid, grid_cols, grid_rows, cell_width, cell_height

    def generate_valid_point(self, x_min, y_min, grid, grid_cols, grid_rows, cell_width, cell_height, elem, max_retries=50):
        """Generate a point inside the shape using grid-guided sampling"""
        # Build list of cells weighted by coverage
        weighted_cells = []
        for row in range(grid_rows):
            for col in range(grid_cols):
                if grid[row][col] == 2:  # full cell
                    # Add multiple times for higher probability
                    weighted_cells.extend([(row, col)] * 3)
                elif grid[row][col] == 1:  # partial cell
                    weighted_cells.append((row, col))

        if not weighted_cells:
            # Fallback to random (shouldn't happen)
            return None, None

        for attempt in range(max_retries):
            # Pick cell
            row, col = random.choice(weighted_cells)

            # Generate point in cell
            x = x_min + col * cell_width + random.uniform(0, cell_width)
            y = y_min + row * cell_height + random.uniform(0, cell_height)

            # Test if in path (always test partial cells, skip test for full cells)
            if grid[row][col] == 2 or self.point_in_path(x, y, elem):
                return x, y

        # Failed to find valid point
        return None, None

    def effect(self):
        # Get selected path
        if not self.svg.selected:
            inkex.errormsg("Please select a path first")
            return
        
        elem = list(self.svg.selected.values())[0]
        
        # Get path bounding box
        bbox = elem.bounding_box()
        if bbox is None:
            inkex.errormsg("Could not get path bounding box")
            return
        
        x_min, y_min = bbox.left, bbox.top
        width, height = bbox.width, bbox.height

        # Create coverage grid for shape-aware distribution
        grid, grid_cols, grid_rows, cell_width, cell_height = self.create_coverage_grid(bbox, elem)

        # Convert mm to user units using Inkscape's unit conversion
        size_min = self.svg.unittouu(f"{self.options.size_min}mm")
        size_max = self.svg.unittouu(f"{self.options.size_max}mm")
        
        # Parameters
        density = self.options.density
        irregularity = self.options.irregularity / 100.0
        shape_type = self.options.shape_type
        clustering = self.options.clustering / 100.0
        num_clusters = self.options.num_clusters
        elongation_base = self.options.elongation
        elongation_variation = self.options.elongation_variation / 100.0
        elongation_angle_base = math.radians(self.options.elongation_angle)
        angle_variation = self.options.angle_variation / 100.0
        
        # Create group for all spots
        group = elem.getparent().add(inkex.Group())
        
        # Generate cluster centers (only in non-empty cells)
        clusters = []
        # Find non-empty cells for cluster placement
        non_empty_cells = []
        for row in range(grid_rows):
            for col in range(grid_cols):
                if grid[row][col] > 0:  # partial or full
                    non_empty_cells.append((row, col))

        if non_empty_cells:
            for _ in range(num_clusters):
                # Pick random non-empty cell
                row, col = random.choice(non_empty_cells)
                # Place cluster center in cell
                cx = x_min + col * cell_width + random.uniform(0, cell_width)
                cy = y_min + row * cell_height + random.uniform(0, cell_height)
                # Smaller, more concentrated clusters at high clustering values
                cluster_radius = min(width, height) * random.uniform(0.05, 0.15) * (1.5 - clustering)
                # Each cluster gets a weight/density
                cluster_weight = random.uniform(0.5, 2.0)
                clusters.append((cx, cy, cluster_radius, cluster_weight))
        
        # Generate spots
        for i in range(density):
            # Determine if this spot is clustered based on clustering parameter
            use_cluster = random.random() < (clustering ** 0.5)  # Non-linear for stronger effect

            x, y = None, None
            max_attempts = 50

            if use_cluster and clusters:
                # Try clustered distribution with shape constraint
                for attempt in range(max_attempts):
                    # Choose cluster with weighted probability
                    weights = [c[3] for c in clusters]
                    cluster = random.choices(clusters, weights=weights)[0]

                    # Position within cluster using exponential distribution
                    dist_factor = random.expovariate(2.0)
                    dist = min(cluster[2] * dist_factor, cluster[2])
                    angle = random.uniform(0, 2 * math.pi)

                    test_x = cluster[0] + dist * math.cos(angle)
                    test_y = cluster[1] + dist * math.sin(angle)

                    # Clamp to bounding box
                    test_x = max(x_min, min(x_min + width, test_x))
                    test_y = max(y_min, min(y_min + height, test_y))

                    # Check if point is in shape
                    if self.point_in_path(test_x, test_y, elem):
                        x, y = test_x, test_y
                        break

            # Fallback to uniform distribution if clustering failed or not clustering
            if x is None:
                x, y = self.generate_valid_point(x_min, y_min, grid, grid_cols, grid_rows,
                                                   cell_width, cell_height, elem)

            # Skip this spot if we couldn't find a valid position
            if x is None or y is None:
                continue
            
            # Random size
            size = random.uniform(size_min, size_max)
            
            # Calculate individual elongation with variation
            elongation_factor = elongation_base * (1 + random.uniform(-elongation_variation, elongation_variation))
            elongation_factor = max(1.0, elongation_factor)  # Minimum 1.0
            
            # Calculate individual elongation angle with variation
            angle_var = random.uniform(-angle_variation, angle_variation) * math.pi
            spot_angle = elongation_angle_base + angle_var
            
            # Generate shape based on type
            if shape_type == "organic" or (shape_type == "mixed" and random.random() > 0.5):
                path_data = self.generate_organic_blob(x, y, size, irregularity, elongation_factor, spot_angle)
            else:
                path_data = self.generate_angular_fragment(x, y, size, irregularity, elongation_factor, spot_angle)
            
            # Create path element
            path_elem = group.add(inkex.PathElement())
            path_elem.style = {
                'fill': '#000000',
                'fill-opacity': '1',
                'stroke': 'none'
            }
            path_elem.path = path_data
    
    def generate_organic_blob(self, cx, cy, size, irregularity, elongation, angle):
        """Generate organic blob shape with elongation"""
        num_points = random.randint(6, 12)
        points = []
        
        # Pre-calculate irregularity variations (normalized to keep average radius constant)
        radius_variations = []
        for i in range(num_points):
            variation = 1 + random.uniform(-irregularity, irregularity)
            radius_variations.append(variation)
        
        # Normalize to keep average = 1.0
        avg_variation = sum(radius_variations) / len(radius_variations)
        radius_variations = [v / avg_variation for v in radius_variations]
        
        for i in range(num_points):
            point_angle = (i / num_points) * 2 * math.pi
            radius = (size / 2) * radius_variations[i]
            
            # Apply elongation
            cos_angle = math.cos(point_angle - angle)
            sin_angle = math.sin(point_angle - angle)
            
            # Elongate along the specified axis
            stretched_x = cos_angle * elongation
            stretched_y = sin_angle
            
            # Rotate back
            final_x = stretched_x * math.cos(angle) - stretched_y * math.sin(angle)
            final_y = stretched_x * math.sin(angle) + stretched_y * math.cos(angle)
            
            x = cx + radius * final_x
            y = cy + radius * final_y
            points.append((x, y))
        
        # Create smooth path with Bézier curves
        path = f"M {points[0][0]},{points[0][1]} "
        
        for i in range(len(points)):
            next_i = (i + 1) % len(points)
            prev_i = (i - 1) % len(points)
            
            # Smoother control points
            cp1_x = points[i][0] + (points[next_i][0] - points[prev_i][0]) * 0.25
            cp1_y = points[i][1] + (points[next_i][1] - points[prev_i][1]) * 0.25
            cp2_x = points[next_i][0] - (points[next_i][0] - points[i][0]) * 0.25
            cp2_y = points[next_i][1] - (points[next_i][1] - points[i][1]) * 0.25
            
            path += f"C {cp1_x},{cp1_y} {cp2_x},{cp2_y} {points[next_i][0]},{points[next_i][1]} "
        
        path += "Z"
        return path
    
    def generate_angular_fragment(self, cx, cy, size, irregularity, elongation, angle):
        """Generate angular fragment shape with elongation"""
        num_points = random.randint(3, 8)
        
        # Pre-calculate irregularity variations (normalized)
        radius_variations = []
        for i in range(num_points):
            variation = 1 + random.uniform(-irregularity * 1.5, irregularity * 1.5)
            radius_variations.append(variation)
        
        # Normalize to keep average = 1.0
        avg_variation = sum(radius_variations) / len(radius_variations)
        radius_variations = [v / avg_variation for v in radius_variations]
        
        points = []
        for i in range(num_points):
            point_angle = (i / num_points) * 2 * math.pi + random.uniform(-0.3, 0.3)
            radius = (size / 2) * radius_variations[i]
            
            # Apply elongation
            cos_angle = math.cos(point_angle - angle)
            sin_angle = math.sin(point_angle - angle)
            
            stretched_x = cos_angle * elongation
            stretched_y = sin_angle
            
            final_x = stretched_x * math.cos(angle) - stretched_y * math.sin(angle)
            final_y = stretched_x * math.sin(angle) + stretched_y * math.cos(angle)
            
            x = cx + radius * final_x
            y = cy + radius * final_y
            points.append((x, y))
        
        # Create path with straight lines
        path = f"M {points[0][0]},{points[0][1]} "
        for i in range(1, len(points)):
            path += f"L {points[i][0]},{points[i][1]} "
        path += "Z"
        
        return path

if __name__ == '__main__':
    Timeworn().run()