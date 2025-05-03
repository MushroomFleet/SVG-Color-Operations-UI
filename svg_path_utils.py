import re
import numpy as np

try:
    from svg.path import parse_path
    SVG_PATH_AVAILABLE = True
except ImportError:
    SVG_PATH_AVAILABLE = False
    print("Warning: svg.path module not available. Install with: pip install svg.path")


def estimate_path_size(d):
    """
    Estimate the size of a path using its bounding box from the path data
    
    Args:
        d: SVG path data string
        
    Returns:
        Approximate area based on bounding box
    """
    # Extract points from path
    points = re.findall(r'[ML]\s*(-?\d+\.?\d*)[,\s](-?\d+\.?\d*)', d)
    
    if not points:
        return 0
        
    # Convert to floats
    points = [(float(x), float(y)) for x, y in points]
    
    # Calculate bounding box
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Bounding box area as an approximation
    return (max_x - min_x) * (max_y - min_y)


def calculate_path_area(d):
    """
    Calculate the approximate area of a path by sampling points and using shoelace formula
    
    Args:
        d: SVG path data string
        
    Returns:
        Approximate area of the path
    """
    # If svg.path is not available, use simpler estimation
    if not SVG_PATH_AVAILABLE:
        return estimate_path_size(d)
    
    try:
        path = parse_path(d)
        
        # Sample points along the path
        points = []
        for i in range(1000):
            t = i / 999
            point = path.point(t)
            points.append((point.real, point.imag))
        
        # If we don't have enough points or path is not closed, use bounding box
        if len(points) < 3 or np.linalg.norm(np.array(points[0]) - np.array(points[-1])) > 1e-6:
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            return (max_x - min_x) * (max_y - min_y)
        
        # Use shoelace formula for closed paths
        area = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        area = abs(area) / 2.0
        
        return area
    except Exception as e:
        print(f"Error calculating path area: {e}")
        # Fallback to bounding box estimation
        return estimate_path_size(d)


def get_path_centroid(d):
    """
    Calculate the centroid (average position) of a path
    
    Args:
        d: SVG path data string
        
    Returns:
        (x, y) tuple representing the centroid
    """
    # Extract points from path
    points = re.findall(r'[ML]\s*(-?\d+\.?\d*)[,\s](-?\d+\.?\d*)', d)
    
    if not points:
        return (0, 0)
        
    # Convert to floats
    points = [(float(x), float(y)) for x, y in points]
    
    # Calculate centroid
    avg_x = sum(p[0] for p in points) / len(points)
    avg_y = sum(p[1] for p in points) / len(points)
    
    return (avg_x, avg_y)