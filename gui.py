import tkinter as tk
from tkinter import ttk

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

    def add_point(self):
        pass

    def find_path(self):
        pass

    def clear_all(self):
        pass

def main():
    root = tk.Tk()
    app = PathfinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()