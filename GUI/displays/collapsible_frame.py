# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Make a tkinter frame that can collapse or expand on a button click.

Originally written by ChatGTP and then edited
"""

__author__ = "Kyle Vitautas Lopin"

import tkinter as tk
from tkinter.font import nametofont

# for testing
BUTTON_OPTS = (["Full", 0, 16000],
               ["OZ 10,000", 8000, 12000],
               ["OZ 8,000", 6500, 9500],
               ["OZ 5,000", 3500, 6500],
               ["OZ 3,500", 2000, 5000],
               ["Full range", -50000, 50000])


class VerticalButton(tk.Canvas):
    """
        A custom widget to display rotated text in Tkinter.

        Attributes:
            text (str): The text to be displayed.
            command (function): function to call when the button is clicked
            button_width (int): how "wide" (really height after rotation) the button
            should be, if None will be automatically calculated from text width
        """
    def __init__(self, parent, text: str = "", command=None,
                 button_width: int =None):
        self.command = command
        # Calculate the coordinates for centering the text
        print(f"vert button text: {text}")
        font = nametofont("TkDefaultFont")
        if not button_width:
            height = font.measure(text) + 8  # 8 are for pads and space for the arrows
        else:
            height = button_width  # the button width is the canvas height as its rotated
        # make it wide enough for the text plus a little padding (1.5*);
        # width and height are reversed after the rotation
        width = int(1.5*font.metrics()['linespace'])
        tk.Canvas.__init__(self, parent, borderwidth=2,
                           relief="raised", width=width,
                           height=height, background="SystemButtonFace")
        # self.text = self.create_text(int(0.5*linespace), int(0.1*button_width),
        #                              text=text, angle=90, anchor="ne")
        # put the text in the center at a 90-degree angle
        self.text = self.create_text(width//2+4, height//2+4,
                                     text=text, angle=90)
        # To mimic a button, add a bind so when the mouse is pressed on the canvas,
        # the command is called
        self.bind("<ButtonPress-1>", self.button_press)

    def button_press(self, *args):
        self.command()

    def config_text(self, text):
        self.itemconfig(self.text, text=text)

    def get_text(self):
        return self.itemcget(self.text, 'text')

# class VerticalButton(tk.Frame):
#     """
#         A custom widget to display rotated text in Tkinter.
#
#         Attributes:
#             text (str): The text to be displayed.
#             angle (float): The angle of rotation in degrees (default is 90).
#         """
#     def __init__(self, parent, text="", angle=90, command=None):
#         super().__init__(parent)
#         # Calculate the coordinates for centering the text
#         font = nametofont("TkDefaultFont")
#         height = font.measure(text) + 4  # 4 are for pads
#         width = font.metrics()['linespace'] + 4
#         # the button can not be rotated, but we can put in a canvas and rotate the canvas
#         self.canvas = tk.Canvas(self, width=width,
#                            height=height, bg="red")
#         self.canvas.pack(side='left', fill='both', expand=True)
#
#         self.button = tk.Button(self.canvas, text=text, command=command)
#         self.button.place(relx=0.5, rely=0.5, anchor='center')
#
#         #
#         self.canvas.create_window(0, 0, anchor="nw", window=self.button)
#         self.canvas.bind("<Configure>", self._on_canvas_configure)
#
#     def _on_canvas_configure(self, event):
#         self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class RotatedText(tk.Canvas):
    """
    A custom widget to display rotated text in Tkinter.

    Attributes:
        text (str): The text to be displayed.
        angle (float): The angle of rotation in degrees (default is 90).
    """

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
    """
    A custom widget that provides a collapsible frame in Tkinter.

    Attributes:
        open_text (str): The text of the button when the collapsible frame is open.
        closed_text (str): The text of the button when the collapsible frame is collapsed.
        collapsed (bool): Whether the frame starts collapsed or expanded.
        collapsible_frame (tk.Frame): The frame that will collapse or expand on button press
        side (str): "left" or "right" The side where the collapsible
        frame and toggle button are positioned.

    """

    def __init__(self, parent, closed_button_text: str = "",
                 open_button_text: str = "", collapsed: bool = False,
                 add_outline: bool = True, side: str = "left", *args, **kwargs):
        """
        Initialize the CollapsibleFrame.

        Args:
            parent (tkinter.Widget): The parent widget.
            closed_button_text (str): Text to display when the collapsed frame is closed.
            open_button_text (str): Text to display when the collapsed frame is open.
            collapsed (bool): Whether the frame starts collapsed or expanded.
            add_outline (bool): Whether to display a black outline around the button and
            collapsible_frame.
            side (str): "left" or "right" The side where the collapsible
            frame and toggle button are positioned.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        tk.Frame.__init__(self, parent, *args, **kwargs)
        if add_outline:
            self.config(highlightbackground="black", highlightthickness=1)

        self.open_text = open_button_text
        self.closed_text = closed_button_text
        self.collapsed = collapsed
        print(f"collapsed: {self.collapsed}")
        self.side = side
        if side == "left":
            self.open_symbol = "⬆"
            self.closed_symbol = "⬇"
        elif side == "right":
            self.open_symbol = "⬇"
            self.closed_symbol = "⬆"
        else:
            raise ValueError("Invalid side. Side must be 'left' or 'right'.")

        # Create a frame to hold the collapsible elements
        self.collapsible_frame = tk.Frame(self)
        if not self.collapsed:
            self.collapsible_frame.pack(fill="both", expand=True, side=side)

        # figure out all the coordinates needed to put the text in the middle
        # of the simulated button
        max_text = max(closed_button_text, open_button_text)  # get longest string
        # get font properties
        font = nametofont("TkDefaultFont")
        # calculated how big the button is based on longest text
        button_length = int(font.measure(max_text) * 1.2)

        print(f"max text: {max_text}")
        close_len = font.measure(closed_button_text)
        open_len = font.measure(open_button_text)
        print(f"close len: {close_len}, open_len: {open_len}")
        # button_length = None
        print(f"button length: {button_length}")
        # Create a toggle button
        self.toggle_button = VerticalButton(
            self, text=f"{self.closed_symbol} {closed_button_text}" if self.collapsed
            else f"{self.open_symbol} {open_button_text}", button_width=button_length,
            command=self.toggle)
        self.toggle_button.pack(side=side)

    def toggle(self, event=None):
        """
        Toggle the visibility of the inner frame and update the toggle button text.

        Args:
            event: The event that triggered the toggle (optional).
        """
        print("toogle")
        if self.collapsed:
            print("pack")
            self.collapsible_frame.pack(fill="both", expand=True,
                                        side=self.side, before=self.toggle_button)
            self.toggle_button.config_text(text=f"{self.open_symbol} {self.open_text}")
        else:
            print("collapse")
            self.collapsible_frame.pack_forget()
            self.toggle_button.config_text(text=f"{self.closed_symbol} {self.closed_text}")
        self.collapsed = not self.collapsed


if __name__ == '__main__':
    # test that the frame looks correct
    def print_hello():
        print("Hello")
    root = tk.Tk()
    root.geometry("400x400")
    TEST = "Frame"  # set to "Button" or "Frame" to test each part
    pack_side = "left"
    if TEST == "Frame":
        collapse_frame = CollapsibleFrame(root, closed_button_text="Show y axis options",
                                          open_button_text="Collapse options",
                                          collapsed=True, side=pack_side)
        for button_opt in BUTTON_OPTS:
            _button_text = f"{button_opt[0]}\n({button_opt[1]:,}-{button_opt[2]:,})"
            tk.Button(collapse_frame.collapsible_frame, text=_button_text,
                      width=15).pack(side=tk.TOP, pady=10)

        # collapse_frame.pack(side="right")
        collapse_frame.pack(side=pack_side, fill="y")
    elif TEST == "Button":
        button = VerticalButton(root, "Show y axis options", command=print_hello)
        button.pack()
    root.mainloop()
