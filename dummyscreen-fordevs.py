# This file is a dummy file for drawing on the resolution of the epaper hat
# The purpose is to give other members in our synoptic project group an ability
# to test UI designs without needing physical access to the board
# Author: Jake Dolan


import tkinter as tk

class EInkDisplayDummy:
    def __init__(self, root):
        self.root = root
        self.root.title("128x256 E-Ink Dummy Display")

        # Canvas dimensions
        self.canvas_width = 128
        self.canvas_height = 256

        # Create canvas
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack()

        # Draw initial content on the canvas
        self.draw_initial_content()

    def draw_initial_content(self):
        # Clear the canvas
        self.canvas.delete("all")

        # Draw a rectangle to represent the display border
        self.canvas.create_rectangle(1, 1, self.canvas_width-1, self.canvas_height-1, outline='black')

        # Draw some text
        self.canvas.create_text(self.canvas_width//2, self.canvas_height//2, text="Hello", fill="black", font=("Arial", 20))

        # Draw a line
        self.canvas.create_line(0, 0, self.canvas_width, self.canvas_height, fill='black')

        # Draw a circle
        self.canvas.create_oval(10, 10, 50, 50, outline='black', fill='black')

if __name__ == "__main__":
    root = tk.Tk()
    app = EInkDisplayDummy(root)
    root.mainloop()
