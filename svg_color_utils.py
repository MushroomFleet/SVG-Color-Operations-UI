import re
import xml.etree.ElementTree as ET


def parse_color(color_str):
    """
    Parse color string (hex, rgb, or named) to RGB tuple
    
    Args:
        color_str: Color string in various formats
        
    Returns:
        (r, g, b) tuple with values 0-255
    """
    # Handle hex colors
    if color_str.startswith('#'):
        if len(color_str) == 4:  # Short hex #RGB
            r = int(color_str[1] + color_str[1], 16)
            g = int(color_str[2] + color_str[2], 16)
            b = int(color_str[3] + color_str[3], 16)
        else:  # Full hex #RRGGBB
            r = int(color_str[1:3], 16)
            g = int(color_str[3:5], 16)
            b = int(color_str[5:7], 16)
        return (r, g, b)
    
    # Handle rgb colors
    if color_str.startswith('rgb'):
        matches = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
        if matches:
            r = int(matches.group(1))
            g = int(matches.group(2))
            b = int(matches.group(3))
            return (r, g, b)
    
    # Handle named colors (simplified version - add more as needed)
    named_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 128, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'purple': (128, 0, 128),
        'gray': (128, 128, 128),
        'orange': (255, 165, 0)
    }
    
    return named_colors.get(color_str.lower(), (0, 0, 0))


def rgb_to_hex(rgb):
    """
    Convert RGB tuple to hex color string
    
    Args:
        rgb: (r, g, b) tuple with values 0-255
        
    Returns:
        Hex color string (#RRGGBB)
    """
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'


def generate_color_gradient(start_hex, end_hex, steps):
    """
    Generate a gradient of colors between two hex values
    
    Args:
        start_hex: Starting hex color (e.g. '#ff0000')
        end_hex: Ending hex color (e.g. '#0000ff')
        steps: Number of steps in the gradient
        
    Returns:
        List of hex color strings
    """
    # Convert hex to RGB
    start_rgb = parse_color(start_hex)
    end_rgb = parse_color(end_hex)
    
    # Generate steps
    colors = []
    for step in range(steps):
        ratio = step / (steps - 1) if steps > 1 else 0
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        hex_color = rgb_to_hex((r, g, b))
        colors.append(hex_color)
    
    return colors


def apply_color_range(svg_content, target_color, start_hex, end_hex):
    """
    Replace all instances of a color with a gradient based on Y position
    
    Args:
        svg_content: SVG content as string
        target_color: Color to replace
        start_hex: Starting gradient color
        end_hex: Ending gradient color
        
    Returns:
        Modified SVG content as string
    """
    tree = ET.fromstring(svg_content)
    
    # Find all elements with the target fill
    elements = []
    for elem in tree.iter():
        if elem.get('fill') == target_color:
            elements.append(elem)
    
    if not elements:
        return svg_content
        
    # Get bounding box of all these elements
    all_y_values = []
    for elem in elements:
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            points = re.findall(r'[ML]\s*(-?\d+\.?\d*)[,\s](-?\d+\.?\d*)', d)
            all_y_values.extend([float(y) for _, y in points])
        elif elem.tag.endswith('rect'):
            y = float(elem.get('y', 0))
            height = float(elem.get('height', 0))
            all_y_values.extend([y, y + height])
    
    min_y = min(all_y_values) if all_y_values else 0
    max_y = max(all_y_values) if all_y_values else 0
    y_range = max_y - min_y
    
    # Generate a gradient
    colors = generate_color_gradient(start_hex, end_hex, 100)
    
    # Apply gradient based on average y position
    for elem in elements:
        # Determine average y position of the element
        avg_y = None
        if elem.tag.endswith('path'):
            d = elem.get('d', '')
            points = re.findall(r'[ML]\s*(-?\d+\.?\d*)[,\s](-?\d+\.?\d*)', d)
            avg_y = sum(float(y) for _, y in points) / len(points) if points else None
        elif elem.tag.endswith('rect'):
            y = float(elem.get('y', 0))
            height = float(elem.get('height', 0))
            avg_y = y + height/2
        
        if avg_y is not None:
            # Map y position to color index
            relative_pos = (avg_y - min_y) / y_range if y_range > 0 else 0
            color_idx = min(int(relative_pos * 99), 99)
            elem.set('fill', colors[color_idx])
    
    return ET.tostring(tree, encoding='unicode')