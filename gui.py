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
        self.window.geometry("800x600")  # Larger window for better grid visibility
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Create canvas for grid visualisation
        self.canvas = tk.Canvas(self.window, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Add scrollbars for larger grids
        x_scrollbar = ttk.Scrollbar(self.window, orient="horizontal", command=self.canvas.xview)
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        y_scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        
        # Add close button
        close_button = ttk.Button(self.window, text="Close", command=self.window.withdraw)
        close_button.grid(row=2, column=0, pady=10)
        
        # Store grid dimensions and cell size
        self.rows = 0
        self.cols = 0
        self.cell_size = 60  # Default cell size in pixels
        
        # Initially hide the window
        self.window.withdraw()
    
    def show(self):
        # Center the window
        self.window.deiconify()
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def update_visualisation(self, text):
        # This method will be replaced with draw_grid
        pass

class PathfinderGUI:
    def __init__(self, root, rows=10, cols=10):  # Modified to accept dimensions
        # Store the root window and configure basic window properties
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        
        # Initialize threading components
        self.processing = False
        self.result_queue = queue.Queue()
        
        # Create visualisation window
        self.viz_window = VisualisationWindow(root)
        
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
                
                # Update the visualisation window
                self.viz_window.update_visualisation(result['visualization'])
                
                # Show the visualisation window
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
        
        # Also clear visualisation window if it's open
        self.viz_window.update_visualisation("")

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