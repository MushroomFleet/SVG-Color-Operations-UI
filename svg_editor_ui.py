import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
import xml.etree.ElementTree as ET
import os

from svg_analyzer import analyze_svg
from svg_color_utils import generate_color_gradient, apply_color_range


class SVGEditor:
    def __init__(self, root):
        """
        Initialize the SVG Editor UI
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("SVG Shape Color Editor")
        self.root.geometry("800x600")
        
        self.svg_file = None
        self.svg_tree = None
        self.largest_shapes = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open SVG", command=self.open_file)
        file_menu.add_command(label="Save SVG", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Shape list
        left_frame = ttk.LabelFrame(main_frame, text="Shapes by Color", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Shape list
        self.shape_listbox = tk.Listbox(left_frame, height=20, width=40)
        self.shape_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.shape_listbox.bind('<<ListboxSelect>>', self.on_shape_select)
        
        # Buttons under the listbox
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.change_color_btn = ttk.Button(
            button_frame, text="Change Color", command=self.change_color)
        self.change_color_btn.pack(side=tk.LEFT, padx=5)
        
        self.apply_gradient_btn = ttk.Button(
            button_frame, text="Apply Gradient", command=self.apply_gradient)
        self.apply_gradient_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Preview and details
        right_frame = ttk.LabelFrame(main_frame, text="Shape Details", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Shape details
        detail_frame = ttk.Frame(right_frame)
        detail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="Color:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.color_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.color_var, state='readonly').grid(
            row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        ttk.Label(detail_frame, text="Size:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.size_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.size_var, state='readonly').grid(
            row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        ttk.Label(detail_frame, text="Type:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.type_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.type_var, state='readonly').grid(
            row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        # Preview placeholder (could be replaced with actual SVG rendering)
        self.preview_label = ttk.Label(right_frame, text="[SVG Preview would appear here]")
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Open an SVG file to begin.")
        self.statusbar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initially disable buttons
        self.change_color_btn.config(state=tk.DISABLED)
        self.apply_gradient_btn.config(state=tk.DISABLED)
    
    def open_file(self):
        """Open an SVG file and analyze it"""
        svg_file = filedialog.askopenfilename(
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")])
        
        if not svg_file:
            return
            
        try:
            self.svg_file = svg_file
            self.svg_tree = ET.parse(svg_file)
            self.largest_shapes = analyze_svg(svg_file)
            self.update_shape_list()
            
            filename = os.path.basename(svg_file)
            self.status_var.set(f"Loaded {filename}")
            self.change_color_btn.config(state=tk.NORMAL)
            self.apply_gradient_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open SVG file: {e}")
    
    def update_shape_list(self):
        """Update the listbox with shapes from the loaded SVG"""
        self.shape_listbox.delete(0, tk.END)
        
        if not self.largest_shapes:
            return
            
        for i, (color, (element, size)) in enumerate(self.largest_shapes.items()):
            shape_type = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            self.shape_listbox.insert(i, f"{color} {shape_type} (Size: {size:.1f})")
    
    def on_shape_select(self, event):
        """Handle shape selection in the listbox"""
        selection = self.shape_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        color = list(self.largest_shapes.keys())[index]
        element, size = self.largest_shapes[color]
        
        # Update info display
        shape_type = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        self.color_var.set(color)
        self.size_var.set(f"{size:.1f}")
        self.type_var.set(shape_type)
        
        # Update preview (placeholder)
        self.preview_label.config(text=f"Preview of {shape_type} with color {color}")
        
        # In a more advanced version, render the actual SVG shape here
    
    def change_color(self):
        """Change the color of the selected shape"""
        selection = self.shape_listbox.curselection()
        if not selection or not self.largest_shapes:
            return
            
        index = selection[0]
        color = list(self.largest_shapes.keys())[index]
        element, size = self.largest_shapes[color]
        
        # Open color chooser
        new_color_tuple = colorchooser.askcolor(color)
        if not new_color_tuple:
            return
            
        new_color = new_color_tuple[1]  # Get hex value
        
        # Update element color
        element.set('fill', new_color)
        
        # Update data structures
        self.largest_shapes[new_color] = self.largest_shapes.pop(color)
        
        # Update UI
        self.update_shape_list()
        self.shape_listbox.selection_set(index)
        self.on_shape_select(None)
        
        self.status_var.set(f"Changed color from {color} to {new_color}")
    
    def apply_gradient(self):
        """Apply a color gradient to the selected shape"""
        selection = self.shape_listbox.curselection()
        if not selection or not self.largest_shapes:
            return
            
        index = selection[0]
        color = list(self.largest_shapes.keys())[index]
        
        # Get start and end colors for gradient
        start_color_tuple = colorchooser.askcolor(title="Select Gradient Start Color")
        if not start_color_tuple:
            return
            
        end_color_tuple = colorchooser.askcolor(title="Select Gradient End Color")
        if not end_color_tuple:
            return
            
        start_color = start_color_tuple[1]
        end_color = end_color_tuple[1]
        
        # Convert SVG to string
        svg_content = ET.tostring(self.svg_tree.getroot(), encoding='unicode')
        
        # Apply gradient
        try:
            new_svg_content = apply_color_range(svg_content, color, start_color, end_color)
            
            # Parse the modified SVG
            self.svg_tree = ET.ElementTree(ET.fromstring(new_svg_content))
            
            # Re-analyze shapes
            with open("temp_gradient.svg", "w") as f:
                f.write(new_svg_content)
            
            self.largest_shapes = analyze_svg("temp_gradient.svg")
            os.remove("temp_gradient.svg")
            
            # Update UI
            self.update_shape_list()
            self.status_var.set(f"Applied gradient from {start_color} to {end_color}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply gradient: {e}")
    
    def save_file(self):
        """Save the modified SVG"""
        if not self.svg_file or not self.svg_tree:
            self.save_file_as()
            return
            
        try:
            self.svg_tree.write(self.svg_file)
            self.status_var.set(f"Saved to {self.svg_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def save_file_as(self):
        """Save the modified SVG with a new filename"""
        if not self.svg_tree:
            messagebox.showinfo("Info", "No SVG loaded to save")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")])
        
        if not save_path:
            return
            
        try:
            self.svg_tree.write(save_path)
            self.svg_file = save_path
            self.status_var.set(f"Saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


def run_editor():
    """Launch the SVG Editor application"""
    root = tk.Tk()
    app = SVGEditor(root)
    root.mainloop()


if __name__ == "__main__":
    run_editor()