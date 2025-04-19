# Import required libraries for GUI, file operations and system functions
import tkinter as tk
from tkinter import ttk  # Themed widgets for enhanced GUI appearance
import spa              # Custom module for pathfinding algorithms
import io              # For redirecting stdout to capture visualisation
import sys             # For system-level operations like stdout manipulation
import threading       # For multi-threading support
import queue           # For thread-safe data exchange
import config
import database

class GridVisualizer(tk.Toplevel):
    def __init__(self, parent, grid_rows, grid_cols, path=None, start=None, end=None, points=None):
        super().__init__(parent)
        self.title("Path Visualization")
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        
        # Calculate canvas size based on grid dimensions (improved size)
        cell_size = 40  # Increased from 30 for better readability
        canvas_width = grid_cols * cell_size + 1
        canvas_height = grid_rows * cell_size + 1
        
        # Create canvas for grid drawing
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)
        
        # Store references for later use
        self.cell_size = cell_size
        self.path = path
        self.start = start
        self.end = end
        self.points = points
        
        # Draw the grid with numbers
        self.draw_grid()
        
        # Draw path and points if provided
        if path and start is not None and end is not None and points is not None:
            self.visualize_path(path, start, end, points)
    
    def draw_grid(self):
        # Draw horizontal lines
        for i in range(self.grid_rows + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_cols * self.cell_size, y, fill="gray")
        
        # Draw vertical lines
        for j in range(self.grid_cols + 1):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_rows * self.cell_size, fill="gray")
            
        # Add cell numbers
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                # Calculate position number (1-based)
                pos_num = spa.coordinates_to_index(row, col, self.grid_cols)
                
                # Calculate text position (center of cell)
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                
                # Add text with improved font
                self.canvas.create_text(x, y, text=str(pos_num), font=("Arial", 10, "bold"))
    
    def visualize_path(self, path, start, end, points):
        # Draw start and end points (improved colors)
        self.draw_cell(start[0], start[1], "#4287f5")  # Bright blue for start
        self.draw_cell(end[0], end[1], "#4287f5")      # Bright blue for end
        
        # Draw intermediate points (improved color)
        for point in points:
            self.draw_cell(point[0], point[1], "#f5d742")  # Bright yellow for points
        
        # Draw path (improved color)
        for x, y in path:
            # Skip start, end, and intermediate points to avoid overwriting
            if (x, y) != start and (x, y) != end and (x, y) not in points:
                self.draw_cell(x, y, "#42f56f")  # Bright green for path
    
    def draw_cell(self, row, col, color):
        x1 = col * self.cell_size + 1
        y1 = row * self.cell_size + 1
        x2 = x1 + self.cell_size - 2
        y2 = y1 + self.cell_size - 2
        
        # Create rectangle with improved transparency to keep numbers visible
        # First draw a filled rectangle with alpha transparency
        rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        
        # Add the position number on top with contrasting color
        pos_num = spa.coordinates_to_index(row, col, self.grid_cols)
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        
        # Determine text color based on background brightness
        text_color = "black"
        if color in ["#4287f5", "#42f56f"]:  # For blue and green backgrounds
            text_color = "white"
            
        self.canvas.create_text(x, y, text=str(pos_num), font=("Arial", 10, "bold"), fill=text_color)
    
    def clear_visualization(self):
        # Clear all colored cells but keep the grid and numbers
        self.canvas.delete("all")
        self.draw_grid()

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):  # Modified to accept dimensions
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        
        # Initialize threading components
        self.processing = False
        self.result_queue = queue.Queue()
        
        # Configure grid weights to enable proper resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create and configure the top frame for input elements
        input_frame = ttk.Frame(root)
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky='ew')
        input_frame.grid_columnconfigure(0, weight=1)  # Allow input field to expand
        
        # Create text entry field for coordinates
        self.point_entry = ttk.Entry(input_frame)
        self.point_entry.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        # Add range label after point entry
        self.range_label = ttk.Label(input_frame, text=f"Enter position (1-{rows*cols})")
        self.range_label.grid(row=1, column=0, columnspan=2, pady=(5,0))
        
        # Create button to add points to the path
        add_button = ttk.Button(input_frame, text="Add Point", command=self.add_point)
        add_button.grid(row=0, column=1)
        
        # Create main output area for displaying messages (smaller now)
        self.output_text = tk.Text(root, height=5, width=50)
        self.output_text.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
        
        # Create bottom frame for control buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=5)
        
        # Add buttons for path finding and clearing
        start_button = ttk.Button(button_frame, text="Find Path", command=self.find_path)
        start_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Add button to show grid visualization
        show_grid_button = ttk.Button(button_frame, text="Show Grid", command=self.show_grid)
        show_grid_button.grid(row=0, column=2, padx=5)
        
        # Initialise the pathfinding components with configured grid size
        self.grid = spa.Grid(rows, cols)
        self.path_finder = spa.PathFinder(self.grid)
        self.path_visualiser = spa.PathVisualiser(self.grid)
        
        # Initialise empty list to store intermediate points
        self.points = []

        # Initialize database with the same dimensions as the grid
        self.db = database.InventoryDB(rows, cols)
        self.db.populate_random_data()  # Initialize with random stock levels
        
        # Create stock management frame
        stock_frame = ttk.Frame(root)
        stock_frame.grid(row=3, column=0, pady=5)
        
        # Add stock management buttons
        query_button = ttk.Button(stock_frame, text="Query Stock", command=self.query_stock)
        query_button.grid(row=0, column=0, padx=5)
        
        update_button = ttk.Button(stock_frame, text="Update Stock", command=self.update_stock)
        update_button.grid(row=0, column=1, padx=5)

    def add_point(self):
        # Get and clean the input string from the entry field
        points_str = self.point_entry.get().strip()
        if not points_str:
            self.output_text.insert(tk.END, "Error: Please enter at least one position\n")
            return
            
        # Split input by commas or spaces
        import re
        point_list = re.split(r'[,\s]+', points_str)
        
        # Process each point
        added_count = 0
        for point_str in point_list:
            if not point_str:  # Skip empty strings
                continue
                
            try:
                # Convert input string to single number
                index = int(point_str)
                
                # Validate index range
                if not (1 <= index <= self.grid.rows * self.grid.cols):
                    self.output_text.insert(tk.END, f"Error: Position {index} out of range (1-{self.grid.rows * self.grid.cols})\n")
                    continue
                
                # Check stock before adding point
                quantity = self.db.get_quantity(index)
                if quantity is None:
                    self.output_text.insert(tk.END, f"Error: Position {index} not found\n")
                    continue
                if quantity <= 0:
                    self.output_text.insert(tk.END, f"Warning: Skipping position {index} - Out of stock\n")
                    continue
                
                # Convert to coordinates (0-based)
                x, y = spa.index_to_coordinates(index, self.grid.cols)
                
                # Validate the point
                valid, error = spa.validate_point(x, y, self.grid.rows, self.grid.cols)
                if not valid:
                    self.output_text.insert(tk.END, f"Error: {error}\n")
                    continue
                    
                # Check if point already exists in the list
                if (x, y) in self.points:
                    self.output_text.insert(tk.END, f"Warning: Position {index} already added, skipping\n")
                    continue
                
                self.points.append((x, y))
                added_count += 1
                self.output_text.insert(tk.END, f"Added position {index} (Stock: {quantity})\n")
                
            except ValueError:
                self.output_text.insert(tk.END, f"Error: '{point_str}' is not a valid number\n")
        
        # Clear the entry field after processing all points
        self.point_entry.delete(0, tk.END)
        
        # Summary message
        if added_count > 0:
            self.output_text.insert(tk.END, f"Successfully added {added_count} point(s)\n")
        else:
            self.output_text.insert(tk.END, "No valid points were added\n")

    def find_path(self):
        # Check if there are any points to process
        if not self.points:
            self.output_text.insert(tk.END, "Error: No intermediate points added. Please add at least one point.\n")
            return
    
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing path...\n")
        
        try:
            # Define start and end points of the grid
            start_node = (0, 0)
            end_node = (self.grid.rows - 1, self.grid.cols - 1)
            
            # Filter out points with zero stock before pathfinding
            valid_points = []
            skipped_points = []
            
            for x, y in self.points:
                item_id = spa.coordinates_to_index(x, y, self.grid.cols)
                quantity = self.db.get_quantity(item_id)
                
                if quantity > 0:
                    valid_points.append((x, y))
                else:
                    skipped_points.append((x, y))
            
            if skipped_points:
                skipped_indices = [spa.coordinates_to_index(x, y, self.grid.cols) for x, y in skipped_points]
                self.output_text.insert(tk.END, f"Skipping positions with no stock: {', '.join(map(str, skipped_indices))}\n")
            
            # If no valid points, find direct path from start to end
            if not valid_points:
                self.output_text.insert(tk.END, "No valid points with stock available. Finding direct path from start to end.\n")
                # Use find_path_through_points with empty intermediate points list
                path = self.path_finder.find_path_through_points(start_node, [], end_node)
                valid_points = []  # Empty list for visualization
            else:
                # Find path through all valid points
                path = self.path_finder.find_path_through_points(start_node, valid_points, end_node)
            
            if path:
                # Decrement stock for each valid intermediate point
                for x, y in valid_points:
                    item_id = spa.coordinates_to_index(x, y, self.grid.cols)
                    self.db.decrement_quantity(item_id)
                
                # Display path length
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Total path length: {len(path) - 1} steps\n")
                
                # Convert path to position numbers
                path_indices = [spa.coordinates_to_index(x, y, self.grid.cols) 
                              for x, y in path]
                
                # Show path as position numbers
                path_str = " -> ".join([str(idx) for idx in path_indices])
                self.output_text.insert(tk.END, f"Path: {path_str}\n")
                
                # If visualization window doesn't exist, create it
                if not hasattr(self, 'viz_window') or not self.viz_window or not self.viz_window.winfo_exists():
                    self.viz_window = GridVisualizer(
                        self.root, 
                        self.grid.rows, 
                        self.grid.cols, 
                        path=path, 
                        start=start_node, 
                        end=end_node, 
                        points=valid_points  # Use only valid points for visualization
                    )
                else:
                    # If window exists, clear it and update with new path
                    self.viz_window.clear_visualization()
                    self.viz_window.path = path
                    self.viz_window.start = start_node
                    self.viz_window.end = end_node
                    self.viz_window.points = valid_points  # Use only valid points for visualization
                    self.viz_window.visualize_path(path, start_node, end_node, valid_points)
            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Error: No valid path found\n")
        
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")

    def clear_all(self):
        # Reset all components to initial state
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Cleared all points\n")
        
        # Clear visualization but keep window open
        if hasattr(self, 'viz_window') and self.viz_window and self.viz_window.winfo_exists():
            self.viz_window.clear_visualization()

    def query_stock(self):
        try:
            point_str = self.point_entry.get().strip()
            if not point_str:
                self.output_text.insert(tk.END, "Please enter a position to query\n")
                return
                
            index = int(point_str)
            quantity = self.db.get_quantity(index)
            
            if quantity is not None:
                pos = self.db.get_position(index)
                self.output_text.insert(tk.END, f"Position {index} (row={pos[0]}, col={pos[1]}): Stock = {quantity}\n")
            else:
                self.output_text.insert(tk.END, f"Position {index} not found\n")
                
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid number\n")

    def update_stock(self):
        try:
            point_str = self.point_entry.get().strip()
            if not point_str:
                self.output_text.insert(tk.END, "Please enter a position to update\n")
                return
                
            index = int(point_str)
            
            # Create popup for quantity input
            popup = tk.Toplevel(self.root)
            popup.title("Update Stock")
            popup.geometry("200x100")
            
            ttk.Label(popup, text="Enter new quantity:").pack(pady=5)
            qty_entry = ttk.Entry(popup)
            qty_entry.pack(pady=5)
            
            def do_update():
                try:
                    new_qty = int(qty_entry.get())
                    self.db.update_quantity(index, new_qty)
                    self.output_text.insert(tk.END, f"Updated stock for position {index} to {new_qty}\n")
                    popup.destroy()
                except ValueError:
                    self.output_text.insert(tk.END, "Error: Please enter a valid number\n")
                except Exception as e:
                    self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            
            ttk.Button(popup, text="Update", command=do_update).pack(pady=5)
            
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid position number\n")

    def show_grid(self):
        # Create or show visualization window
        if not hasattr(self, 'viz_window') or not self.viz_window or not self.viz_window.winfo_exists():
            self.viz_window = GridVisualizer(
                self.root, 
                self.grid.rows, 
                self.grid.cols
            )
        else:
            # If window exists but is minimized, restore it
            self.viz_window.deiconify()
            self.viz_window.lift()

def main():
    # Get grid dimensions from config window (will only show once)
    rows, cols = config.get_grid_config()
    if rows is None or cols is None:
        return  # User closed the config window
        
    # Create and start the main application window
    root = tk.Tk()
    app = PathfinderGUI(root, rows, cols)
    root.mainloop()

if __name__ == "__main__":
    main()