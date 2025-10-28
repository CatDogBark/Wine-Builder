#!/usr/bin/env python3
"""
Combined Sprite Tools - Godot Development Toolkit
A unified GUI interface combining all sprite processing tools
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import math
import sys

# Add the script directory to Python path so relative imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import all tool classes
from editor.sprite_frame_editor import SpriteFrameEditor
from spriteframe_sizer.sprite_frame_sizer import SpriteFrameSizer
from spritesheet_combiner.spritesheet_combiner import EnhancedSpritesheetCombiner
from spritesheet_id.spritesheet_analyzer import SpritesheetAnalyzer

class SpriteToolsSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("Godot Sprite Tools Suite")
        self.root.geometry("1000x800")

        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tab frames
        self.create_editor_tab()
        self.create_sizer_tab()
        self.create_combiner_tab()
        self.create_analyzer_tab()

        # Setup menu
        self.setup_menu()

    def create_editor_tab(self):
        """Create Sprite Frame Editor tab"""
        editor_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(editor_frame, text="Frame Editor")

        # Initialize the editor with the tab frame as parent
        self.editor = SpriteFrameEditor(editor_frame)
        self.editor.root = editor_frame  # Override the root reference

    def create_sizer_tab(self):
        """Create Sprite Frame Sizer tab"""
        sizer_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(sizer_frame, text="Frame Sizer")

        # Initialize the sizer with the tab frame as parent
        self.sizer = SpriteFrameSizer(sizer_frame)
        self.sizer.root = sizer_frame  # Override the root reference

    def create_combiner_tab(self):
        """Create Spritesheet Combiner tab"""
        combiner_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(combiner_frame, text="Sheet Combiner")

        # Initialize the combiner with the tab frame as parent
        self.combiner = EnhancedSpritesheetCombiner(combiner_frame)
        self.combiner.root = combiner_frame  # Override the root reference

    def create_analyzer_tab(self):
        """Create Spritesheet Analyzer tab"""
        analyzer_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(analyzer_frame, text="Sheet Analyzer")

        # Initialize the analyzer with the tab frame as parent
        self.analyzer = SpritesheetAnalyzer(analyzer_frame)
        self.analyzer.root = analyzer_frame  # Override the root reference

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="About", command=self.show_about)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Tools", command=self.show_about)

    def show_about(self):
        """Show about dialog"""
        about_text = """
Godot Sprite Tools Suite

A unified interface for all your sprite processing needs:

• Frame Editor: Select, delete, and move frames in spritesheets
• Frame Sizer: Resize frames to standard sizes (64x64, 128x128, 256x256)
• Sheet Combiner: Combine multiple animation spritesheets into one
• Sheet Analyzer: Analyze spritesheets to determine grid layouts

Requirements: Python 3.6+, Pillow (PIL)

Version 1.0 - Combined Tool Suite
        """
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = SpriteToolsSuite(root)
    root.mainloop()

if __name__ == "__main__":
    main()