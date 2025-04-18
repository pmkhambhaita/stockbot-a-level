import tkinter as tk
from tkinter import ttk, messagebox

class ConfigWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StockBot Setup")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Initialize result variables
        self.rows = None
        self.cols = None
        self.current_page = 0
        
        # Configure root grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)
        
        # Create content frame (will hold different pages)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=1, column=0, sticky="se", pady=(20, 0))
        
        # Create navigation buttons
        self.back_button = ttk.Button(self.button_frame, text="Back", command=self.go_back, state=tk.DISABLED)
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.go_next)
        self.finish_button = ttk.Button(self.button_frame, text="Finish", command=self.finish, state=tk.DISABLED)
        
        # Grid buttons (right-aligned)
        self.back_button.grid(row=0, column=0, padx=5)
        self.next_button.grid(row=0, column=1, padx=5)
        self.finish_button.grid(row=0, column=2, padx=5)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_placeholder(self):
        # Just a temporary placeholder until we implement real pages
        placeholder = ttk.Label(self.content_frame, text="Page content will go here")
        placeholder.grid(row=0, column=0, pady=20)
    
    def show_page(self, page_index):
        # Clear current page
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if 0 <= page_index < len(self.pages):
            # Create new page
            self.pages[page_index](self.content_frame)
            self.current_page = page_index
            
            # Update button states
            self.back_button.config(state=tk.NORMAL if page_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if page_index < len(self.pages) - 1 else tk.DISABLED)
            self.finish_button.config(state=tk.NORMAL if page_index == len(self.pages) - 1 else tk.DISABLED)
        else:
            self.show_placeholder()
    
    def go_back(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
    
    def go_next(self):
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)
    
    def finish(self):
        # Placeholder for finish button functionality
        self.root.destroy()
    
    def get_dimensions(self):
        self.root.mainloop()
        return self.rows, self.cols

def get_grid_config():
    config_wizard = ConfigWizard()
    return config_wizard.get_dimensions()