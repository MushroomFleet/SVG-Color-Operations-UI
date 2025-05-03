import xml.etree.ElementTree as ET
import re
import numpy as np
from svg_path_utils import estimate_path_size, calculate_path_area


def analyze_svg(svg_file):
    """
    Parse SVG file and identify largest shapes by color
    
    Args:
        svg_file: Path to the SVG file
        
    Returns:
        Dictionary mapping fill colors to (element, size) tuples
    """
    # Parse the SVG file
    tree = ET.parse(svg_file)
    root = tree.getroot()
    
    # Define the SVG namespace
    namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Find all elements with fill attribute (colored shapes)
    shapes_by_color = {}
    
    # Process paths, rectangles, circles, etc.
    for shape_type in ['path', 'rect', 'circle', 'polygon']:
        for element in root.findall(f'.//svg:{shape_type}', namespaces):
            # Get fill color
            fill = element.get('fill', 'none')
            
            # Skip if no fill or if it's transparent
            if fill == 'none' or (fill.startswith('rgba') and fill.endswith(',0)')) or fill.startswith('url('):
                continue
            
            # Calculate approximate size/area
            size = calculate_shape_size(element, shape_type)
            
            # Group by color
            if fill not in shapes_by_color:
                shapes_by_color[fill] = []
            
            shapes_by_color[fill].append((element, size))
    
    # Find largest shapes by color
    largest_shapes = {}
    for color, shapes in shapes_by_color.items():
        # Sort shapes by size (descending)
        sorted_shapes = sorted(shapes, key=lambda x: x[1], reverse=True)
        largest_shapes[color] = sorted_shapes[0] if sorted_shapes else None
    
    return largest_shapes


def calculate_shape_size(element, shape_type):
    """
    Calculate approximate size of shape based on type
    
    Args:
        element: XML element representing the shape
        shape_type: Type of shape ('path', 'rect', 'circle', 'polygon')
        
    Returns:
        Approximate area of the shape
    """
    if shape_type == 'rect':
        width = float(element.get('width', 0))
        height = float(element.get('height', 0))
        return width * height
    
    elif shape_type == 'circle':
        radius = float(element.get('r', 0))
        return np.pi * radius * radius
    
    elif shape_type == 'path':
        # Calculate area for path
        d = element.get('d', '')
        return calculate_path_area(d)
    
    elif shape_type == 'polygon':
        points = element.get('points', '')
        return estimate_polygon_size(points)
    
    return 0


def estimate_polygon_size(points_str):
    """
    Estimate the size of a polygon from its points
    
    Args:
        points_str: String containing polygon points
        
    Returns:
        Approximate area of the polygon
    """
    point_pairs = re.findall(r'(-?\d+\.?\d*)[,\s](-?\d+\.?\d*)', points_str)
    
    if not point_pairs:
        return 0
        
    # Convert to floats
    points = [(float(x), float(y)) for x, y in point_pairs]
    
    # Calculate bounding box
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Bounding box area as an approximation
    return (max_x - min_x) * (max_y - min_y)


def analyze_svg_with_regex(svg_content):
    """
    Analyze SVG content directly using regex to find large shapes
    
    Args:
        svg_content: SVG file content as string
        
    Returns:
        Dictionary mapping fill colors to (path_data, size) tuples
    """
    # Find all path elements with their d attribute and fill color
    path_pattern = r'<path[^>]*fill="([^"]*)"[^>]*d="([^"]*)"[^>]*>'
    paths = re.findall(path_pattern, svg_content)
    
    largest_paths = {}
    for fill, d in paths:
        # Skip paths with no fill or with gradients/patterns
        if fill == 'none' or fill.startswith('url('):
            continue
            
        # Estimate size
        size = estimate_path_size(d)
        
        # Keep track of largest path for each fill color
        if fill not in largest_paths or size > largest_paths[fill][1]:
            largest_paths[fill] = (d, size)
    
    return largest_paths