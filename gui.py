import tkinter as tk
from tkinter import ttk

class PathfinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("StockBot")
        self.root.geometry("600x400")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

def main():
    root = tk.Tk()
    app = PathfinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()