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
        
        # Generate cluster centers
        clusters = []
        for _ in range(num_clusters):
            cx = x_min + random.uniform(0, width)
            cy = y_min + random.uniform(0, height)
            # Smaller, more concentrated clusters at high clustering values
            cluster_radius = min(width, height) * random.uniform(0.05, 0.15) * (1.5 - clustering)
            # Each cluster gets a weight/density
            cluster_weight = random.uniform(0.5, 2.0)
            clusters.append((cx, cy, cluster_radius, cluster_weight))
        
        # Generate spots
        for i in range(density):
            # Determine if this spot is clustered based on clustering parameter
            use_cluster = random.random() < (clustering ** 0.5)  # Non-linear for stronger effect
            
            if use_cluster and clusters:
                # Choose cluster with weighted probability
                weights = [c[3] for c in clusters]
                cluster = random.choices(clusters, weights=weights)[0]
                
                # Position within cluster using exponential distribution (more concentrated at center)
                dist_factor = random.expovariate(2.0)  # Exponential distribution
                dist = min(cluster[2] * dist_factor, cluster[2])
                angle = random.uniform(0, 2 * math.pi)
                
                x = cluster[0] + dist * math.cos(angle)
                y = cluster[1] + dist * math.sin(angle)
                
                # Clamp to bounding box
                x = max(x_min, min(x_min + width, x))
                y = max(y_min, min(y_min + height, y))
            else:
                # Random uniform position
                x = x_min + random.uniform(0, width)
                y = y_min + random.uniform(0, height)
            
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