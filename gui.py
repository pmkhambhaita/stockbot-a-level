import tkinter as tk
from tkinter import ttk
import spa
import io
import sys

class PathfinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create input frame
        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Create input elements
        self.point_entry = ttk.Entry(input_frame)
        self.point_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        add_button = ttk.Button(input_frame, text="Add Point", command=self.add_point)
        add_button.grid(row=0, column=1)
        
        # Create output text area
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
        
        # Create button frame
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=5)
        
        # Add control buttons
        start_button = ttk.Button(button_frame, text="Find Path", command=self.find_path)
        start_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Initialize pathfinding components
        self.grid = spa.Grid(10, 10)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)
        
        # Store points
        self.points = []

    def add_point(self):
        point_str = self.point_entry.get().strip()
        try:
            x, y = map(int, point_str.strip('()').replace(' ', '').split(','))
            
            if spa.validate_point(x, y, self.grid.rows, self.grid.cols):
                self.points.append((x, y))
                self.point_entry.delete(0, tk.END)
                self.output_text.insert(tk.END, f"Added point: ({x}, {y})\n")
            else:
                self.output_text.insert(tk.END, f"Error: Cannot add point ({x}, {y}). Must not be start/end point and must be within bounds.\n")
        except ValueError:
            self.output_text.insert(tk.END, "Error: Invalid input format. Please use 'x,y' format\n")

    def find_path(self):
        if not self.points:
            self.output_text.insert(tk.END, "Error: No points added\n")
            return

        start_node = (0, 0)
        end_node = (self.grid.rows - 1, self.grid.cols - 1)
        
        self.output_text.delete(1.0, tk.END)
        path = self.path_finder.find_path_through_points(start_node, self.points, end_node)
        
        if path:
            old_stdout = sys.stdout
            result = io.StringIO()
            sys.stdout = result
            
            self.path_visualiser.visualise_path(path, start_node, end_node, self.points)
            
            sys.stdout = old_stdout
            visualization = result.getvalue()
            
            self.output_text.insert(tk.END, visualization)
            self.output_text.insert(tk.END, f"\nTotal path length: {len(path) - 1} steps\n")
        else:
            self.output_text.insert(tk.END, "Error: No valid path found through all points\n")

    def clear_all(self):
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Cleared all points\n")

def main():
    root = tk.Tk()
    app = PathfinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()