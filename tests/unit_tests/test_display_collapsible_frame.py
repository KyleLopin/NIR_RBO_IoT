# Copyright (c) 2023 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Unit tests for the GUI.display.collapbsible_frame.py file.
"""

__author__ = "Kyle Vitautas Lopin"

# standard tests
from time import sleep
import tkinter as tk
import unittest

# local files
from context import GUI  # add the GUI directory to path
from GUI.displays.collapsible_frame import CollapsibleFrame

class CollapsibleFrameTestCase(unittest.TestCase):
    """
    Test case class for CollapsibleFrame.  From ChatGPT
    """

    def test_default_initialization(self):
        """
        Test default initialization of CollapsibleFrame.
        """
        parent_widget = tk.Tk()
        collapsible_frame = CollapsibleFrame(parent_widget)
        print('aa2', collapsible_frame.collapsed)
        self.assertEqual(collapsible_frame.closed_text, "")
        self.assertEqual(collapsible_frame.open_text, "")
        print('aa', collapsible_frame.collapsed)
        self.assertFalse(collapsible_frame.collapsed)
        self.assertEqual(collapsible_frame.side, "left")

    def test_custom_initialization(self):
        """
        Test initialization of CollapsibleFrame with custom values.
        """
        parent_widget = tk.Tk()
        collapsible_frame = CollapsibleFrame(parent_widget, "Closed", "Open", True, True, "right")
        self.assertEqual(collapsible_frame.closed_text, "Closed")
        self.assertEqual(collapsible_frame.open_text, "Open")
        self.assertTrue(collapsible_frame.collapsed)
        self.assertEqual(collapsible_frame.side, "right")

    def test_toggle_frame(self):
        """
        Test the collapsed variable changes with toggle, the
        winfo_ismapped() function does not work to test
        visibility in unit tests for some reason
        # Test toggling the visibility of the inner frame.
        """
        parent_widget = tk.Tk()
        collapsible_frame = CollapsibleFrame(parent_widget,
                                             closed_button_text="Closed",
                                             open_button_text="Open",
                                             collapsed=False,
                                             add_outline=True,
                                             side="left")
        print(f"1: {collapsible_frame.collapsed}")
        self.assertFalse(collapsible_frame.collapsed)
        collapsible_frame.toggle()
        print(f"2: {collapsible_frame.collapsed}")
        self.assertTrue(collapsible_frame.collapsed)
        collapsible_frame.toggle()
        print(f"2: {collapsible_frame.collapsed}")
        self.assertFalse(collapsible_frame.collapsed)

    def test_update_button_text(self):
        """
        Test updating the toggle button text after toggling.
        """
        parent_widget = tk.Tk()
        collapsible_frame = CollapsibleFrame(parent_widget, "Closed", "Open", True, True, "left")
        print(f"ll: |{collapsible_frame.toggle_button.get_text()}|")
        self.assertEqual(collapsible_frame.toggle_button.get_text(), "⬇ Closed")
        collapsible_frame.toggle()
        self.assertEqual(collapsible_frame.toggle_button.get_text(), "⬆ Open")


if __name__ == '__main__':
    unittest.main()
