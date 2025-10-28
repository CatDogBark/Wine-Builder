#!/usr/bin/env python3
"""
Spritesheet Analyzer for Godot
Analyzes spritesheets to determine frame sizes, number of frames, and file information
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import os

class SpritesheetAnalyzer:
    def __init__(self, root):
        self.root = root
        # Only set title and geometry if this is the main window, not a tab
        if hasattr(root, 'title') and callable(getattr(root, 'title')):
            self.root.title("Spritesheet Analyzer")
            self.root.geometry("700x600")

        self.input_file = None
        self.analysis_result = None

        self.setup_ui()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Spritesheet Analyzer", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # File selection frame
        file_frame = tk.LabelFrame(self.root, text="Input Spritesheet", padx=10, pady=10)
        file_frame.pack(padx=10, pady=5, fill="x")

        # File path display
        self.file_var = tk.StringVar(value="No file selected")
        file_label = tk.Label(file_frame, textvariable=self.file_var, fg="gray", width=50, anchor="w")
        file_label.pack(side="left", fill="x", expand=True)

        # Browse button
        browse_btn = tk.Button(file_frame, text="Browse...", command=self.browse_file, width=10)
        browse_btn.pack(side="right", padx=(10, 0))

        # Analysis options frame
        options_frame = tk.LabelFrame(self.root, text="Analysis Options", padx=10, pady=10)
        options_frame.pack(padx=10, pady=5, fill="x")

        # Auto detection option
        self.auto_detect = tk.BooleanVar(value=True)
        auto_chk = tk.Checkbutton(options_frame, text="Auto-detect grid layout", variable=self.auto_detect,
                                 command=self.toggle_manual_options)
        auto_chk.pack(anchor="w")

        # Manual grid entry (initially disabled)
        manual_frame = tk.Frame(options_frame)
        manual_frame.pack(pady=5, fill="x")

        tk.Label(manual_frame, text="Manual Grid:").grid(row=0, column=0, sticky="w", padx=5)
        tk.Label(manual_frame, text="Columns:").grid(row=0, column=1, sticky="w", padx=5)
        self.manual_cols = tk.Spinbox(manual_frame, from_=1, to=32, width=5)
        self.manual_cols.grid(row=0, column=2, padx=5)
        self.manual_cols.delete(0, "end")
        self.manual_cols.insert(0, "1")

        tk.Label(manual_frame, text="Rows:").grid(row=0, column=3, sticky="w", padx=5)
        self.manual_rows = tk.Spinbox(manual_frame, from_=1, to=32, width=5)
        self.manual_rows.grid(row=0, column=4, padx=5)
        self.manual_rows.delete(0, "end")
        self.manual_rows.insert(0, "1")

        self.toggle_manual_options()  # Set initial state

        # Analyze button
        analyze_btn = tk.Button(
            self.root,
            text="Analyze Spritesheet",
            command=self.analyze_spritesheet,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        analyze_btn.pack(pady=10)

        # Results area
        results_frame = tk.LabelFrame(self.root, text="Analysis Results", padx=10, pady=10)
        results_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20)
        self.results_text.pack(fill="both", expand=True)

        # Clear button
        clear_btn = tk.Button(self.root, text="Clear Results", command=self.clear_results)
        clear_btn.pack(pady=5)

        # Initial message
        self.update_results("Ready - Select a spritesheet to analyze")

    def toggle_manual_options(self):
        state = "disabled" if self.auto_detect.get() else "normal"
        self.manual_cols.config(state=state)
        self.manual_rows.config(state=state)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Spritesheet",
            filetypes=[("PNG files", "*.png"), ("WEBP files", "*.webp"), ("All files", "*.*")]
        )
        if filename:
            self.input_file = filename
            short_name = os.path.basename(filename)
            self.file_var.set(short_name)
            self.update_results(f"Loaded: {short_name}\n\nClick 'Analyze Spritesheet' to begin analysis.")

    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.update_results("Results cleared")

    def analyze_spritesheet(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a spritesheet file first!")
            return

        try:
            self.update_results("Analyzing spritesheet...")

            # Load the image
            img = Image.open(self.input_file)
            width, height = img.size

            # Get file size
            file_size = os.path.getsize(self.input_file)
            file_size_kb = file_size / 1024
            file_size_mb = file_size / (1024 * 1024)

            # Start analysis report
            report = "=== SPRITESHEET ANALYSIS REPORT ===\n"
            report += f"File: {os.path.basename(self.input_file)}\n"
            report += ".1f"
            report += ".1f"
            report += f"Format: {img.format}\n"
            report += f"Mode: {img.mode} (transparency: {'Yes' if img.mode == 'RGBA' else 'No'})\n\n"

            if self.auto_detect.get():
                # Auto-detect most likely grid layouts
                detected_layouts = self.detect_grid_layout(width, height)
                report += "=== AUTO-DETECTED GRID LAYOUTS ===\n"

                for layout in detected_layouts[:5]:  # Show top 5
                    cols, rows = layout
                    frame_width = width // cols
                    frame_height = height // rows
                    total_frames = cols * rows

                    report += f"{cols}×{rows} grid: {cols}×{rows} = {total_frames} frames ({frame_width}×{frame_height}px each)\n"

                    # Check if it's a power of 2 size (good for game development)
                    if frame_width in [64, 128, 256] and frame_height in [64, 128, 256]:
                        report += "    → RECOMMENDED: Standard game frame size!\n"
                    elif frame_width >= 32 and frame_width <= 512 and frame_height >= 32 and frame_height <= 512:
                        report += "    → VALID: Reasonable game frame size\n"
                    else:
                        report += "    → UNUSUAL: May not be standard frame size\n"

            else:
                # Manual grid analysis
                cols = int(self.manual_cols.get())
                rows = int(self.manual_rows.get())
                report += "=== MANUAL GRID ANALYSIS ===\n"
                report += f"Specified grid: {cols}×{rows}\n"

                if cols > width or rows > height:
                    report += "❌ ERROR: Grid dimensions exceed image size!\n"
                else:
                    frame_width = width // cols
                    frame_height = height // rows
                    total_frames = cols * rows

                    report += f"Frame size: {frame_width}×{frame_height} pixels\n"
                    report += f"Total frames: {total_frames}\n"

                    # Additional analysis
                    report += f"\nPixel efficiency: {total_frames * frame_width * frame_height:,} pixels used\n"
                    report += f"Wasted space: {width * height - (total_frames * frame_width * frame_height):,} pixels\n"

            # Final recommendations
            report += "\n=== RECOMMENDATIONS ===\n"
            if width % 64 == 0 and height % 64 == 0:
                report += "✓ Compatible with 64px frame sizes\n"
            if width % 128 == 0 and height % 128 == 0:
                report += "✓ Compatible with 128px frame sizes\n"
            if width % 256 == 0 and height % 256 == 0:
                report += "✓ Compatible with 256px frame sizes\n"

            if not any(size in [64, 128, 256] and width % size == 0 and height % size == 0
                      for size in [64, 128, 256]):
                report += "⚠️  Not optimally sized for standard frame sizes (64, 128, 256px)\n"

            self.update_results(report)

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze spritesheet:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def detect_grid_layout(self, width, height):
        """Detect possible grid layouts by testing common divisors"""
        layouts = []

        # Common frame sizes to prioritize
        preferred_sizes = [256, 128, 64, 96, 48, 32]

        for frame_size in preferred_sizes:
            if width % frame_size == 0 and height % frame_size == 0:
                cols = width // frame_size
                rows = height // frame_size
                layouts.append((cols, rows))

        # Also try other common grid configurations
        min_frames = 1
        max_frames = 32

        for rows in range(1, 17):
            for cols in range(1, 17):
                if rows * cols > max_frames:
                    continue
                if width % cols == 0 and height % rows == 0:
                    layouts.append((cols, rows))

        # Remove duplicates and sort by total frames (descending)
        unique_layouts = list(set(layouts))
        unique_layouts.sort(key=lambda x: x[0] * x[1], reverse=True)

        return unique_layouts

    def update_results(self, text):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)

def main():
    root = tk.Tk()
    app = SpritesheetAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()