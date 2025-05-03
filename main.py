#!/usr/bin/env python3
"""
SVG Shape Analyzer and Color Editor

This tool allows users to:
1. Analyze SVG files to identify large shapes
2. Edit colors of shapes within SVG files
3. Apply color gradients to shapes based on position

Usage:
    python main.py             # Launch the GUI
    python main.py --cli       # Use command line interface
    python main.py --analyze file.svg  # Analyze and print results without editing
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET

from svg_analyzer import analyze_svg, analyze_svg_with_regex
from svg_color_utils import apply_color_range
from svg_editor_ui import run_editor


def analyze_mode(svg_file):
    """
    Analyze SVG file and print results without launching UI
    
    Args:
        svg_file: Path to the SVG file
    """
    print(f"Analyzing SVG file: {svg_file}")
    
    if not os.path.exists(svg_file):
        print(f"Error: File not found: {svg_file}")
        return 1
    
    try:
        # Analyze SVG
        shapes = analyze_svg(svg_file)
        
        # Print results
        print("\nLargest shapes by color:")
        print("-----------------------")
        
        for color, (element, size) in shapes.items():
            shape_type = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            print(f"Color: {color}")
            print(f"  Shape type: {shape_type}")
            print(f"  Size: {size:.1f}")
            
            # For paths, show a sample of the path data
            if shape_type == 'path':
                path_data = element.get('d', '')
                if len(path_data) > 50:
                    path_data = path_data[:50] + "..."
                print(f"  Path data: {path_data}")
            
            print()
        
        print(f"Total shapes found: {len(shapes)}")
        return 0
        
    except Exception as e:
        print(f"Error analyzing SVG: {e}")
        return 1


def cli_mode():
    """Command line interface mode"""
    print("SVG Shape Analyzer and Color Editor - CLI Mode")
    print("---------------------------------------------")
    
    # Get SVG file
    svg_file = input("Enter path to SVG file: ")
    if not os.path.exists(svg_file):
        print(f"Error: File not found: {svg_file}")
        return 1
    
    # Analyze SVG
    try:
        shapes = analyze_svg(svg_file)
        
        print("\nLargest shapes by color:")
        for i, (color, (element, size)) in enumerate(shapes.items()):
            shape_type = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            print(f"{i+1}. {color} {shape_type} (Size: {size:.1f})")
        
        # Ask which shape to edit
        shape_idx = int(input("\nEnter number of shape to edit (0 to exit): ")) - 1
        if shape_idx < 0 or shape_idx >= len(shapes):
            print("Exiting without changes")
            return 0
        
        color = list(shapes.keys())[shape_idx]
        
        # Choose edit type
        print("\nEdit options:")
        print("1. Change color")
        print("2. Apply color gradient")
        edit_type = int(input("Enter option number: "))
        
        if edit_type == 1:
            new_color = input("Enter new color (hex format, e.g. #ff0000): ")
            element, _ = shapes[color]
            element.set('fill', new_color)
            
            # Save modified SVG
            tree = ET.parse(svg_file)
            tree.write(svg_file + ".modified.svg")
            print(f"Saved as: {svg_file}.modified.svg")
            
        elif edit_type == 2:
            start_color = input("Enter gradient start color (hex format, e.g. #ff0000): ")
            end_color = input("Enter gradient end color (hex format, e.g. #0000ff): ")
            
            # Read SVG content
            with open(svg_file, 'r') as f:
                svg_content = f.read()
            
            # Apply gradient
            new_svg_content = apply_color_range(svg_content, color, start_color, end_color)
            
            # Save modified SVG
            with open(svg_file + ".gradient.svg", 'w') as f:
                f.write(new_svg_content)
            
            print(f"Saved as: {svg_file}.gradient.svg")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SVG Shape Analyzer and Color Editor")
    parser.add_argument("--cli", action="store_true", help="Use command line interface")
    parser.add_argument("--analyze", metavar="FILE", help="Analyze SVG file and print results")
    args = parser.parse_args()
    
    if args.analyze:
        return analyze_mode(args.analyze)
    elif args.cli:
        return cli_mode()
    else:
        # Launch GUI
        run_editor()
        return 0


if __name__ == "__main__":
    sys.exit(main())