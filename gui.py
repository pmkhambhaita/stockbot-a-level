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

class VisualisationWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Path Visualisation")
        self.window.geometry("1000x800")  # Larger default window size
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Create canvas for grid visualisation
        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')  # Remove padding
        
        # Add scrollbars for larger grids
        x_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        y_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        
        # Add close button
        close_button = ttk.Button(self.window, text="Close", command=self.window.withdraw)
        close_button.grid(row=2, column=0, pady=5)
        
        # Store grid dimensions and cell size
        self.rows = 0
        self.cols = 0
        self.cell_size = 40  # Smaller cell size (was 60)
        
        # Prevent window from being destroyed when closed
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        
        # Initially hide the window
        self.window.withdraw()

    def draw_grid(self, rows, cols, path=None, start=None, end=None, points=None):
        # Store grid dimensions
        self.rows = rows
        self.cols = cols
        
        # Store current path and points for later reference
        self._current_path = path
        self._current_start = start
        self._current_end = end
        self._current_points = points
        
        # Clear previous drawings
        self.canvas.delete("all")
        
        # Calculate total grid size
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size
        
        # Configure canvas scrolling region
        self.canvas.configure(scrollregion=(0, 0, grid_width, grid_height))
        
        # Draw grid cells
        for i in range(rows):
            for j in range(cols):
                # Calculate cell coordinates
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Calculate position ID (1-based)
                pos_id = (i * cols) + j + 1
                
                # Default cell color
                cell_color = "white"
                
                # Check if this cell is in the path
                if path and (i, j) in path:
                    cell_color = "#CCFFCC"  # Green for path
                
                # Check if this cell is a special point
                if points and (i, j) in points:
                    cell_color = "#FFFF00"  # Yellow for intermediate points
                
                # Check if this is start or end
                if start and (i, j) == start:
                    cell_color = "#99CCFF"  # Blue for start
                
                if end and (i, j) == end:
                    cell_color = "#99CCFF"  # Blue for end
                
                # Draw cell rectangle with appropriate color
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cell_color, outline="black")
                
                # Calculate cell center
                x_center = x1 + self.cell_size // 2
                y_center = y1 + self.cell_size // 2
                
                # Draw position ID
                self.canvas.create_text(x_center, y_center, text=str(pos_id), font=("Arial", 10))
        
        # Draw path lines if available
        if path:
            for i in range(len(path) - 1):
                # Get current and next point
                current = path[i]
                next_point = path[i + 1]
                
                # Calculate centers
                x1 = current[1] * self.cell_size + self.cell_size // 2
                y1 = current[0] * self.cell_size + self.cell_size // 2
                x2 = next_point[1] * self.cell_size + self.cell_size // 2
                y2 = next_point[0] * self.cell_size + self.cell_size // 2
                
                # Draw line
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, arrow=tk.LAST)
        
        # Draw grid lines
        for i in range(rows + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, grid_width, y, fill="black")
        
        for j in range(cols + 1):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, grid_height, fill="black")
        
        # Draw cell IDs
        for i in range(rows):
            for j in range(cols):
                # Calculate position ID (1-based)
                pos_id = (i * cols) + j + 1
                
                # Calculate cell center
                x = j * self.cell_size + self.cell_size // 2
                y = i * self.cell_size + self.cell_size // 2
                
                # Draw position ID
                self.canvas.create_text(x, y, text=str(pos_id), font=("Arial", 10))

    
    def show(self):
        # Calculate the exact window size needed based on grid dimensions
        grid_width = self.cols * self.cell_size + 20  # Add a small margin
        grid_height = self.rows * self.cell_size + 50  # Add space for scrollbar and button
        
        # Set minimum sizes to prevent tiny windows
        window_width = max(grid_width, 400)
        window_height = max(grid_height, 300)
        
        # Update window size to fit the grid
        self.window.geometry(f"{window_width}x{window_height}")
        
        # Center the window
        self.window.deiconify()
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.window.winfo_screenheight() // 2) - (window_height // 2)
        self.window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Only draw the basic grid if no path is currently displayed
        # This prevents overwriting an existing path visualization
        if not hasattr(self, '_current_path') or not self._current_path:
            if self.rows > 0 and self.cols > 0:
                self.draw_grid(self.rows, self.cols)
    
    def update_visualisation(self, text):
        # Safely clear the canvas if it exists
        try:
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                self.canvas.delete("all")
        except tk.TclError:
            # Canvas might have been destroyed, recreate it
            self.canvas = tk.Canvas(self.window, bg="white")
            self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
            
            # Reconfigure scrollbars
            x_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.canvas.xview)
            x_scrollbar.grid(row=1, column=0, sticky='ew')
            
            y_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
            y_scrollbar.grid(row=0, column=1, sticky='ns')
            
            self.canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        # This method will be replaced with draw_grid
        pass

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        
        # Initialize threading components
        self.processing = False
        self.result_queue = queue.Queue()
        
        # Create visualisation window
        self.viz_window = VisualisationWindow(root)
        self.viz_window.rows = rows
        self.viz_window.cols = cols
        
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
        
        # Create main output area for displaying messages (not visualisation)
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')
        
        # Create bottom frame for control buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, pady=5)
        
        # Add buttons for path finding and clearing
        start_button = ttk.Button(button_frame, text="Find Path", command=self.find_path)
        start_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Add button to open visualisation window
        viz_button = ttk.Button(button_frame, text="Open Grid Visualisation", command=self.viz_window.show)
        viz_button.grid(row=0, column=2, padx=5)
        
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
        point_str = self.point_entry.get().strip()
        try:
            # Convert input string to single number
            index = int(point_str)
            
            # Validate index range
            if not (1 <= index <= self.grid.rows * self.grid.cols):
                self.output_text.insert(tk.END, f"Error: Position {index} out of range (1-{self.grid.rows * self.grid.cols})\n")
                return
            
            # Check stock before adding point
            quantity = self.db.get_quantity(index)
            if quantity is None:
                self.output_text.insert(tk.END, f"Error: Position {index} not found\n")
                return
            if quantity <= 0:
                self.output_text.insert(tk.END, f"Warning: Skipping position {index} - Out of stock\n")
                return
            
            # Convert to coordinates (0-based)
            x, y = spa.index_to_coordinates(index, self.grid.cols)
            
            # Validate the point
            valid, error = spa.validate_point(x, y, self.grid.rows, self.grid.cols)
            if not valid:
                self.output_text.insert(tk.END, f"Error: {error}\n")
                return
            
            self.points.append((x, y))
            self.point_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added position {index} (Stock: {quantity})\n")
            
        except ValueError:
            self.output_text.insert(tk.END, "Error: Please enter a valid number\n")

    def find_path(self):
        # Prevent multiple concurrent pathfinding operations
        if self.processing:
            self.output_text.insert(tk.END, "Already processing a path request. Please wait.\n")
            return

        # Check if there are any points to process
        if not self.points:
            self.output_text.insert(tk.END, "Error: No intermediate points added. Please add at least one point.\n")
            return

        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing path...\n")
        
        # Set processing flag
        self.processing = True
        
        # Create and start pathfinding thread
        path_thread = threading.Thread(target=self._find_path_thread)
        path_thread.daemon = True  # Thread will be terminated when main program exits
        path_thread.start()
        
        # Start checking for results
        self.root.after(100, self._check_path_results)

    def _find_path_thread(self):
        try:
            # Define start and end points of the grid
            start_node = (0, 0)
            end_node = (self.grid.rows - 1, self.grid.cols - 1)
            
            # Find path through all points
            path = self.path_finder.find_path_through_points(start_node, self.points, end_node)
            
            if path:
                # Decrement stock for each intermediate point
                for x, y in self.points:
                    item_id = spa.coordinates_to_index(x, y, self.grid.cols)
                    self.db.decrement_quantity(item_id)
                
                # Capture visualization in a string
                old_stdout = sys.stdout
                result = io.StringIO()
                sys.stdout = result
                
                # Generate the path visualisation
                self.path_visualiser.visualise_path(path, start_node, end_node, self.points)
                
                # Restore stdout and get the visualisation
                sys.stdout = old_stdout
                visualization = result.getvalue()
                
                # Put results in queue
                self.result_queue.put({
                    'success': True,
                    'visualization': visualization,
                    'path': path
                })
            else:
                self.result_queue.put({
                    'success': False,
                    'error': "No valid path found through all points"
                })
        except Exception as e:
            self.result_queue.put({
                'success': False,
                'error': str(e)
            })

    def _check_path_results(self):
        try:
            result = self.result_queue.get_nowait()
            
            if result['success']:
                # Update the main output text with basic information
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, "Path found successfully!\n")
                self.output_text.insert(tk.END, f"Total path length: {len(result['path']) - 1} steps\n")
                
                # Convert path to position numbers
                path_indices = [spa.coordinates_to_index(x, y, self.grid.cols) 
                              for x, y in result['path']]
                
                # Show path as position numbers
                path_str = " -> ".join([str(idx) for idx in path_indices])
                self.output_text.insert(tk.END, f"Path: {path_str}\n")
                self.output_text.insert(tk.END, "\nOpen Grid Visualisation to see the path map.")
                
                # Get start and end points
                start_node = (0, 0)
                end_node = (self.grid.rows - 1, self.grid.cols - 1)
                
                # Draw the grid with path
                self.viz_window.draw_grid(
                    self.grid.rows, 
                    self.grid.cols, 
                    path=result['path'],
                    start=start_node,
                    end=end_node,
                    points=self.points
                )
                
                # Show the visualisation window if it's not already visible
                if not self.viz_window.window.winfo_viewable():
                    self.viz_window.show()
                
            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, f"Error: {result['error']}\n")
            
            # Reset processing flag
            self.processing = False
            
        except queue.Empty:
            # No results yet, check again in 100ms
            self.root.after(100, self._check_path_results)

    def clear_all(self):
        # Reset all components to initial state
        self.points = []
        self.point_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Cleared all points\n")
        
        # Redraw the grid without path or special points
        try:
            if hasattr(self.viz_window, 'canvas') and self.viz_window.canvas.winfo_exists():
                # Clear the stored path
                self.viz_window._current_path = None
                self.viz_window._current_start = None
                self.viz_window._current_end = None
                self.viz_window._current_points = None
                
                # Redraw the basic grid
                self.viz_window.draw_grid(self.grid.rows, self.grid.cols)
        except tk.TclError:
            # If there's an error, just pass - the window might be closed
            pass

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
