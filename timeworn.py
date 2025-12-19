#!/usr/bin/env python3
import inkex
import random
import math

# Grid configuration
GRID_CELL_SIZE_MM = 5.0
GRID_SAMPLES_PER_CELL = 12
FULL_CELL_COVERAGE_THRESHOLD = 0.9

# Geometry configuration
BEZIER_FLATTEN_SEGMENTS = 8

# Distribution configuration
MAX_POINT_GENERATION_RETRIES = 50
MAX_CLUSTER_POINT_ATTEMPTS = 50

class Timeworn(inkex.EffectExtension):
    
    def add_arguments(self, pars):
        pars.add_argument("--tabs", default="objects")
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

    def flatten_bezier(
        self,
        p0: tuple[float, float],
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
        segments: int = BEZIER_FLATTEN_SEGMENTS
    ) -> list[tuple[float, float]]:
        """Flatten a cubic Bézier curve into line segments.

        Args:
            p0: Start point (x, y)
            p1: First control point (x, y)
            p2: Second control point (x, y)
            p3: End point (x, y)
            segments: Number of segments to subdivide the curve into

        Returns:
            List of points forming the flattened curve

        Note:
            Uses standard cubic Bézier formula for interpolation.
        """
        points = []
        for segment_index in range(segments + 1):
            t = segment_index / segments
            # Cubic Bézier formula
            t2 = t * t
            t3 = t2 * t
            mt = 1 - t
            mt2 = mt * mt
            mt3 = mt2 * mt

            point_x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
            point_y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
            points.append((point_x, point_y))
        return points

    def point_in_path(
        self,
        test_x: float,
        test_y: float,
        path_element
    ) -> bool:
        """Test if point is inside the path using ray-casting algorithm.

        Args:
            test_x: X coordinate of point to test
            test_y: Y coordinate of point to test
            path_element: SVG path element to test against

        Returns:
            True if point is inside path, False otherwise

        Note:
            Uses even-odd rule: casts horizontal ray and counts intersections.
            Odd count = inside, even count = outside.
        """
        # Get path as superpath for predictable format
        path = path_element.path.to_superpath()

        # Flatten path to line segments
        line_segments = []
        for subpath in path:
            for point_index in range(len(subpath)):
                # Each segment in superpath is ((x,y), (cp1_x, cp1_y), (cp2_x, cp2_y))
                current_point = subpath[point_index]
                next_point_index = (point_index + 1) % len(subpath)

                # Close path - connect last to first
                if next_point_index == 0 and point_index == len(subpath) - 1:
                    next_point = subpath[0]
                else:
                    next_point = subpath[next_point_index]

                # Extract Bézier control points
                bezier_p0 = (current_point[1][0], current_point[1][1])  # current point
                bezier_p1 = (current_point[2][0], current_point[2][1])  # control point 1
                bezier_p2 = (next_point[0][0], next_point[0][1])  # control point 2
                bezier_p3 = (next_point[1][0], next_point[1][1])  # next point

                # Flatten Bézier curve to line segments
                flattened_points = self.flatten_bezier(bezier_p0, bezier_p1, bezier_p2, bezier_p3)
                for segment_index in range(len(flattened_points) - 1):
                    line_segments.append((
                        flattened_points[segment_index],
                        flattened_points[segment_index + 1]
                    ))

        # Ray casting: count intersections with horizontal ray from point
        intersection_count = 0
        for segment_start, segment_end in line_segments:
            start_x, start_y = segment_start
            end_x, end_y = segment_end

            # Skip horizontal segments
            if start_y == end_y:
                continue

            # Check if ray intersects segment's y range
            if not (min(start_y, end_y) < test_y <= max(start_y, end_y)):
                continue

            # Calculate x coordinate of intersection
            intersect_x = start_x + (test_y - start_y) * (end_x - start_x) / (end_y - start_y)

            # Count if intersection is to the right of test point
            if intersect_x > test_x:
                intersection_count += 1

        # Odd number of intersections = inside (even-odd rule)
        return intersection_count % 2 == 1

    def create_coverage_grid(
        self,
        bbox,
        path_element,
        cell_size_mm: float = GRID_CELL_SIZE_MM
    ) -> tuple[list[list[int]], int, int, float, float]:
        """Create coverage grid with fixed cell size.

        Args:
            bbox: Bounding box of the shape
            path_element: SVG path element to test
            cell_size_mm: Cell size in millimeters

        Returns:
            Tuple of (grid, grid_cols, grid_rows, cell_width, cell_height)
            Grid values: 0=empty, 1=partial, 2=full

        Note:
            Samples GRID_SAMPLES_PER_CELL points per cell to classify coverage.
            Cells with >=90% coverage are marked as full.
        """
        bbox_x_min, bbox_y_min = bbox.left, bbox.top
        bbox_width, bbox_height = bbox.width, bbox.height

        # Convert cell size to user units
        cell_size = self.svg.unittouu(f"{cell_size_mm}mm")

        # Calculate grid dimensions
        grid_cols = max(1, int(bbox_width / cell_size))
        grid_rows = max(1, int(bbox_height / cell_size))

        # Actual cell dimensions
        cell_width = bbox_width / grid_cols
        cell_height = bbox_height / grid_rows

        # Initialize grid
        grid = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]

        # Sample each cell to determine coverage
        samples_per_cell = GRID_SAMPLES_PER_CELL
        for row_index in range(grid_rows):
            for col_index in range(grid_cols):
                # Cell bounds
                cell_x_min = bbox_x_min + col_index * cell_width
                cell_y_min = bbox_y_min + row_index * cell_height

                # Sample points in cell
                inside_count = 0
                for sample_index in range(samples_per_cell):
                    sample_x = cell_x_min + random.uniform(0, cell_width)
                    sample_y = cell_y_min + random.uniform(0, cell_height)

                    if self.point_in_path(sample_x, sample_y, path_element):
                        inside_count += 1

                # Classify cell
                coverage = inside_count / samples_per_cell
                if coverage == 0:
                    grid[row_index][col_index] = 0  # empty
                elif coverage >= FULL_CELL_COVERAGE_THRESHOLD:
                    grid[row_index][col_index] = 2  # full
                else:
                    grid[row_index][col_index] = 1  # partial

        return grid, grid_cols, grid_rows, cell_width, cell_height

    def generate_valid_point(
        self,
        bbox_x_min: float,
        bbox_y_min: float,
        grid: list[list[int]],
        grid_cols: int,
        grid_rows: int,
        cell_width: float,
        cell_height: float,
        path_element,
        max_retries: int = MAX_POINT_GENERATION_RETRIES
    ) -> tuple[float | None, float | None]:
        """Generate a point inside the shape using grid-guided sampling.

        Args:
            bbox_x_min: Left boundary of bounding box
            bbox_y_min: Top boundary of bounding box
            grid: Coverage grid with cell classifications (0=empty, 1=partial, 2=full)
            grid_cols: Number of grid columns
            grid_rows: Number of grid rows
            cell_width: Width of each grid cell
            cell_height: Height of each grid cell
            path_element: SVG path element to test points against
            max_retries: Maximum number of attempts before giving up

        Returns:
            Tuple of (x, y) coordinates if successful, (None, None) if failed

        Note:
            Full cells (2) are weighted 3x more heavily than partial cells (1).
            Full cells skip the point-in-path test for efficiency.
        """
        # Build list of cells weighted by coverage
        weighted_cells = []
        for row_index in range(grid_rows):
            for col_index in range(grid_cols):
                if grid[row_index][col_index] == 2:  # full cell
                    # Add multiple times for higher probability
                    weighted_cells.extend([(row_index, col_index)] * 3)
                elif grid[row_index][col_index] == 1:  # partial cell
                    weighted_cells.append((row_index, col_index))

        # Early return if no valid cells
        if not weighted_cells:
            return None, None

        for attempt_number in range(max_retries):
            # Pick random cell from weighted list
            cell_row, cell_col = random.choice(weighted_cells)

            # Generate random point within cell
            point_x = bbox_x_min + cell_col * cell_width + random.uniform(0, cell_width)
            point_y = bbox_y_min + cell_row * cell_height + random.uniform(0, cell_height)

            # Test if in path (skip test for full cells for efficiency)
            if grid[cell_row][cell_col] == 2 or self.point_in_path(point_x, point_y, path_element):
                return point_x, point_y

        # Failed to find valid point after all retries
        return None, None

    def effect(self) -> None:
        """Main extension execution - generates weathered texture spots.

        Processes the selected SVG path and generates texture spots within its boundaries
        using shape-aware distribution with optional clustering and elongation.

        Returns:
            None

        Note:
            Creates a new group containing all generated spots as separate path elements.
            Uses coverage grid for efficient shape-aware placement.
        """
        # Early return: Check if path is selected
        if not self.svg.selected:
            inkex.errormsg("Please select a path first")
            return

        selected_element = list(self.svg.selected.values())[0]

        # Early return: Check if bounding box can be calculated
        bbox = selected_element.bounding_box()
        if bbox is None:
            inkex.errormsg("Could not get path bounding box")
            return

        bbox_x_min, bbox_y_min = bbox.left, bbox.top
        bbox_width, bbox_height = bbox.width, bbox.height

        # Create coverage grid for shape-aware distribution
        grid, grid_cols, grid_rows, cell_width, cell_height = self.create_coverage_grid(
            bbox, selected_element
        )

        # Convert spot size parameters from mm to user units
        spot_size_min = self.svg.unittouu(f"{self.options.size_min}mm")
        spot_size_max = self.svg.unittouu(f"{self.options.size_max}mm")

        # Extract and normalize parameters
        spot_density = self.options.density
        irregularity = self.options.irregularity / 100.0
        shape_type = self.options.shape_type
        clustering_factor = self.options.clustering / 100.0
        num_clusters = self.options.num_clusters
        elongation_base = self.options.elongation
        elongation_variation = self.options.elongation_variation / 100.0
        elongation_angle_base = math.radians(self.options.elongation_angle)
        angle_variation = self.options.angle_variation / 100.0

        # Create group to contain all generated spots
        spots_group = selected_element.getparent().add(inkex.Group())

        # Generate cluster centers (only in non-empty cells)
        clusters = []
        non_empty_cells = []
        for row_index in range(grid_rows):
            for col_index in range(grid_cols):
                if grid[row_index][col_index] > 0:  # partial or full cell
                    non_empty_cells.append((row_index, col_index))

        if non_empty_cells:
            for cluster_index in range(num_clusters):
                # Pick random non-empty cell for cluster center
                cell_row, cell_col = random.choice(non_empty_cells)

                # Place cluster center randomly within chosen cell
                cluster_center_x = (
                    bbox_x_min + cell_col * cell_width + random.uniform(0, cell_width)
                )
                cluster_center_y = (
                    bbox_y_min + cell_row * cell_height + random.uniform(0, cell_height)
                )

                # Calculate cluster radius (smaller at high clustering values for tighter groups)
                cluster_radius = (
                    min(bbox_width, bbox_height)
                    * random.uniform(0.05, 0.15)
                    * (1.5 - clustering_factor)
                )

                # Assign random weight for cluster selection probability
                cluster_weight = random.uniform(0.5, 2.0)

                clusters.append((cluster_center_x, cluster_center_y, cluster_radius, cluster_weight))

        # Generate individual spots
        for spot_index in range(spot_density):
            # Determine if this spot should use clustering (non-linear for stronger effect)
            use_clustering = random.random() < (clustering_factor ** 0.5)

            spot_x, spot_y = None, None
            max_cluster_attempts = MAX_CLUSTER_POINT_ATTEMPTS

            # Try clustered distribution if enabled
            if use_clustering and clusters:
                for attempt_number in range(max_cluster_attempts):
                    # Choose cluster with weighted probability
                    cluster_weights = [cluster[3] for cluster in clusters]
                    selected_cluster = random.choices(clusters, weights=cluster_weights)[0]

                    # Position within cluster using exponential distribution (more concentrated at center)
                    distance_factor = random.expovariate(2.0)
                    distance = min(selected_cluster[2] * distance_factor, selected_cluster[2])
                    polar_angle = random.uniform(0, 2 * math.pi)

                    test_x = selected_cluster[0] + distance * math.cos(polar_angle)
                    test_y = selected_cluster[1] + distance * math.sin(polar_angle)

                    # Clamp to bounding box
                    test_x = max(bbox_x_min, min(bbox_x_min + bbox_width, test_x))
                    test_y = max(bbox_y_min, min(bbox_y_min + bbox_height, test_y))

                    # Check if point is inside shape
                    if self.point_in_path(test_x, test_y, selected_element):
                        spot_x, spot_y = test_x, test_y
                        break

            # Fallback to uniform distribution if clustering failed or not using clustering
            if spot_x is None:
                spot_x, spot_y = self.generate_valid_point(
                    bbox_x_min, bbox_y_min, grid, grid_cols, grid_rows,
                    cell_width, cell_height, selected_element
                )

            # Skip this spot if no valid position found
            if spot_x is None or spot_y is None:
                continue

            # Generate random spot size
            spot_size = random.uniform(spot_size_min, spot_size_max)

            # Calculate individual elongation with random variation
            spot_elongation = elongation_base * (
                1 + random.uniform(-elongation_variation, elongation_variation)
            )
            spot_elongation = max(1.0, spot_elongation)  # Minimum 1.0 (no negative elongation)

            # Calculate individual elongation angle with random variation
            angle_variation_radians = random.uniform(-angle_variation, angle_variation) * math.pi
            spot_elongation_angle = elongation_angle_base + angle_variation_radians

            # Generate shape based on type selection
            if shape_type == "organic" or (shape_type == "mixed" and random.random() > 0.5):
                path_data = self.generate_organic_blob(
                    spot_x, spot_y, spot_size, irregularity, spot_elongation, spot_elongation_angle
                )
            else:
                path_data = self.generate_angular_fragment(
                    spot_x, spot_y, spot_size, irregularity, spot_elongation, spot_elongation_angle
                )

            # Create SVG path element for this spot
            spot_path_element = spots_group.add(inkex.PathElement())
            spot_path_element.style = {
                'fill': '#000000',
                'fill-opacity': '1',
                'stroke': 'none'
            }
            spot_path_element.path = path_data
    
    def generate_organic_blob(
        self,
        center_x: float,
        center_y: float,
        size: float,
        irregularity: float,
        elongation: float,
        elongation_angle: float
    ) -> str:
        """Generate organic blob shape with elongation.

        Args:
            center_x: X coordinate of blob center
            center_y: Y coordinate of blob center
            size: Diameter of blob
            irregularity: Amount of border variation (0-1)
            elongation: Elongation factor along axis
            elongation_angle: Angle of elongation axis in radians

        Returns:
            SVG path data string for the organic blob

        Note:
            Uses 6-12 random points with normalized irregularity to maintain
            consistent average size. Creates smooth curves with Bézier control points.
        """
        num_points = random.randint(6, 12)
        blob_points = []

        # Pre-calculate irregularity variations (normalized to keep average radius constant)
        radius_variations = []
        for point_index in range(num_points):
            variation = 1 + random.uniform(-irregularity, irregularity)
            radius_variations.append(variation)

        # Normalize to keep average = 1.0
        avg_variation = sum(radius_variations) / len(radius_variations)
        radius_variations = [v / avg_variation for v in radius_variations]

        # Generate points around circle with elongation
        for point_index in range(num_points):
            point_angle = (point_index / num_points) * 2 * math.pi
            radius = (size / 2) * radius_variations[point_index]

            # Apply elongation transformation
            cos_angle = math.cos(point_angle - elongation_angle)
            sin_angle = math.sin(point_angle - elongation_angle)

            # Elongate along the specified axis
            stretched_x = cos_angle * elongation
            stretched_y = sin_angle

            # Rotate back to original orientation
            final_x = stretched_x * math.cos(elongation_angle) - stretched_y * math.sin(elongation_angle)
            final_y = stretched_x * math.sin(elongation_angle) + stretched_y * math.cos(elongation_angle)

            point_x = center_x + radius * final_x
            point_y = center_y + radius * final_y
            blob_points.append((point_x, point_y))

        # Create smooth path with Bézier curves
        path = f"M {blob_points[0][0]},{blob_points[0][1]} "

        for point_index in range(len(blob_points)):
            next_point_index = (point_index + 1) % len(blob_points)
            prev_point_index = (point_index - 1) % len(blob_points)

            # Calculate Bézier control points for smooth curves
            control_point_1_x = blob_points[point_index][0] + (blob_points[next_point_index][0] - blob_points[prev_point_index][0]) * 0.25
            control_point_1_y = blob_points[point_index][1] + (blob_points[next_point_index][1] - blob_points[prev_point_index][1]) * 0.25
            control_point_2_x = blob_points[next_point_index][0] - (blob_points[next_point_index][0] - blob_points[point_index][0]) * 0.25
            control_point_2_y = blob_points[next_point_index][1] - (blob_points[next_point_index][1] - blob_points[point_index][1]) * 0.25

            path += f"C {control_point_1_x},{control_point_1_y} {control_point_2_x},{control_point_2_y} {blob_points[next_point_index][0]},{blob_points[next_point_index][1]} "

        path += "Z"
        return path
    
    def generate_angular_fragment(
        self,
        center_x: float,
        center_y: float,
        size: float,
        irregularity: float,
        elongation: float,
        elongation_angle: float
    ) -> str:
        """Generate angular fragment shape with elongation.

        Args:
            center_x: X coordinate of fragment center
            center_y: Y coordinate of fragment center
            size: Diameter of fragment
            irregularity: Amount of border variation (0-1), amplified by 1.5x
            elongation: Elongation factor along axis
            elongation_angle: Angle of elongation axis in radians

        Returns:
            SVG path data string for the angular fragment

        Note:
            Uses 3-8 random points with enhanced irregularity (1.5x) and angle jitter
            to create sharp, crystalline shapes. Connects points with straight lines.
        """
        num_points = random.randint(3, 8)

        # Pre-calculate irregularity variations (normalized, enhanced for angular look)
        radius_variations = []
        for point_index in range(num_points):
            variation = 1 + random.uniform(-irregularity * 1.5, irregularity * 1.5)
            radius_variations.append(variation)

        # Normalize to keep average = 1.0
        avg_variation = sum(radius_variations) / len(radius_variations)
        radius_variations = [v / avg_variation for v in radius_variations]

        # Generate angular points with jitter
        fragment_points = []
        for point_index in range(num_points):
            # Add angular jitter for more chaotic look
            point_angle = (point_index / num_points) * 2 * math.pi + random.uniform(-0.3, 0.3)
            radius = (size / 2) * radius_variations[point_index]

            # Apply elongation transformation
            cos_angle = math.cos(point_angle - elongation_angle)
            sin_angle = math.sin(point_angle - elongation_angle)

            stretched_x = cos_angle * elongation
            stretched_y = sin_angle

            final_x = stretched_x * math.cos(elongation_angle) - stretched_y * math.sin(elongation_angle)
            final_y = stretched_x * math.sin(elongation_angle) + stretched_y * math.cos(elongation_angle)

            point_x = center_x + radius * final_x
            point_y = center_y + radius * final_y
            fragment_points.append((point_x, point_y))

        # Create path with straight lines (angular, not curved)
        path = f"M {fragment_points[0][0]},{fragment_points[0][1]} "
        for point_index in range(1, len(fragment_points)):
            path += f"L {fragment_points[point_index][0]},{fragment_points[point_index][1]} "
        path += "Z"

        return path

if __name__ == '__main__':
    Timeworn().run()