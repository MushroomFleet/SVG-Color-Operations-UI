# SVG Shape Analyzer and Color Editor

This tool allows you to analyze SVG files to identify large shapes and edit their colors. It's particularly useful for working with vector graphics like shoe designs, where you might want to identify and modify large color sections.

## Features

- Analyze SVG files to identify the largest shapes by color
- Edit colors of shapes within SVG files
- Apply color gradients to shapes based on position
- User-friendly GUI for visual editing
- Command-line interface for scripting and automation

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/svg-shape-analyzer.git
   cd svg-shape-analyzer
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode

To launch the graphical user interface:

```
python main.py
```

The GUI allows you to:
- Open SVG files
- View a list of the largest shapes by color
- Select shapes and view their details
- Change colors with a color picker
- Apply color gradients to shapes
- Save the modified SVG

### Command Line Interface

For command line usage:

```
python main.py --cli
```

This will guide you through a text-based interface to analyze and edit SVG files.

### Analysis Mode

To analyze an SVG file without editing it:

```
python main.py --analyze path/to/file.svg
```

This will print information about the largest shapes in the SVG file.

## File Structure

- `main.py` - Main entry point for the application
- `svg_analyzer.py` - Core functionality for analyzing SVG files
- `svg_path_utils.py` - Utilities for calculating path areas and sizes
- `svg_color_utils.py` - Utilities for handling color gradients and color manipulation
- `svg_editor_ui.py` - Tkinter-based UI for the SVG editor
- `requirements.txt` - Required Python packages

## Dependencies

- Python 3.7 or higher
- NumPy
- svg.path (optional, for better path area calculations)
- Tkinter (included in standard Python distribution)

## License

MIT License