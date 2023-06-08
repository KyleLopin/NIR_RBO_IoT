import tkinter as tk

class RotatedText(tk.Canvas):
    """A custom widget to display rotated text in Tkinter."""

    def __init__(self, parent, text="", angle=90, *args, **kwargs):
        """
        Initialize the RotatedText widget.

        Args:
            parent (tkinter.Widget): The parent widget.
            text (str): The text to be displayed.
            angle (float): The angle of rotation in degrees (default is 90).
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.text = text
        self.angle = angle

        self.bind("<Configure>", self._draw_text)

    def _draw_text(self, event=None):
        """
        Draw the rotated text on the canvas.

        Args:
            event: The event that triggered the drawing (optional).
        """
        self.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()

        # Calculate the coordinates for centering the text
        x = width / 2
        y = height / 2

        # Rotate the canvas
        self.create_text(x, y, text=self.text, angle=self.angle, anchor="center")

class CollapsibleFrame(tk.Frame):
    """A custom widget that provides a collapsible frame in Tkinter."""

    def __init__(self, parent, title="", collapsed=False, *args, **kwargs):
        """
        Initialize the CollapsibleFrame.

        Args:
            parent (tkinter.Widget): The parent widget.
            title (str): The title of the collapsible frame.
            collapsed (bool): Whether the frame starts collapsed or expanded.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.title = title
        self.collapsed = collapsed

        # Create a frame to hold the collapsible elements
        self.collapsible_frame = tk.Frame(self)
        self.collapsible_frame.pack(fill="both", expand=True, side="left")

        # Create a label frame with a vertical title
        self.label_frame = tk.LabelFrame(self.collapsible_frame)
        self.label_frame.pack(fill="both", expand=True)

        title_canvas = RotatedText(self.label_frame, text=self.title, angle=90)
        title_canvas.pack(fill="both", expand=True)

        # Create a frame inside the label frame
        self.inner_frame = tk.Frame(self.label_frame)
        self.inner_frame.pack(fill="both", expand=True)

        # Create a toggle button
        self.toggle_button = tk.Button(self, text="◀" if self.collapsed else "▶", command=self.toggle)
        self.toggle_button.pack(side="left")

        # Configure the label frame to toggle visibility
        self.label_frame.bind("<Button-1>", self.toggle)

        self.toggle()

    def toggle(self, event=None):
        """
        Toggle the visibility of the inner frame and update the toggle button text.

        Args:
            event: The event that triggered the toggle (optional).
        """
        if self.collapsed:
            self.collapsible_frame.pack(fill="both", expand=True, side="left")
            self.toggle_button.config(text="◀")
        else:
            self.collapsible_frame.pack_forget()
            self.toggle_button.config(text="▶")

        self.collapsed = not self.collapsed

# Create the main window
root = tk.Tk()

# Create a collapsible frame
collapsible_frame = CollapsibleFrame(root, title="My Collapsible Frame")
collapsible_frame.pack(fill="both", expand=True)

# Add widgets to the inner frame of the collapsible frame
label = tk.Label(collapsible_frame.inner_frame, text="Hello, World!")
label.pack(padx=10, pady=10)

# Run the application
root.mainloop()
