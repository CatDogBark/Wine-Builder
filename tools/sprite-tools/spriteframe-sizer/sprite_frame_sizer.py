#!/usr/bin/env python3
"""
Sprite Frame Sizer for Godot
Resizes frames in spritesheets to standard sizes (64x64, 128x128, 256x256)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os

class SpriteFrameSizer:
    def __init__(self, root):
        self.root = root
        # Only set title and geometry if this is the main window, not a tab
        if hasattr(root, 'title') and callable(getattr(root, 'title')):
            self.root.title("Sprite Frame Sizer")
            self.root.geometry("600x400")

        self.input_file = None
        self.grid_cols = tk.IntVar(value=4)
        self.grid_rows = tk.IntVar(value=4)
        self.target_size = tk.IntVar(value=128)

        self.setup_ui()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Sprite Frame Sizer", font=("Arial", 16, "bold"))
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

        # Settings frame
        settings_frame = tk.LabelFrame(self.root, text="Grid Layout & Target Size", padx=10, pady=10)
        settings_frame.pack(padx=10, pady=5, fill="x")

        # Grid layout
        grid_frame = tk.Frame(settings_frame)
        grid_frame.pack(pady=5)

        tk.Label(grid_frame, text="Grid Columns:").grid(row=0, column=0, sticky="w", padx=5)
        cols_spin = tk.Spinbox(grid_frame, from_=1, to=16, width=5, textvariable=self.grid_cols)
        cols_spin.grid(row=0, column=1, padx=5)

        tk.Label(grid_frame, text="×").grid(row=0, column=2, padx=5)

        tk.Label(grid_frame, text="Grid Rows:").grid(row=0, column=3, sticky="w", padx=5)
        rows_spin = tk.Spinbox(grid_frame, from_=1, to=16, width=5, textvariable=self.grid_rows)
        rows_spin.grid(row=0, column=4, padx=5)

        # Target size selection
        size_frame = tk.Frame(settings_frame)
        size_frame.pack(pady=10)

        tk.Label(size_frame, text="Target Frame Size:").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        size_radio_frame = tk.Frame(size_frame)
        size_radio_frame.grid(row=0, column=1, sticky="w", padx=5)

        tk.Radiobutton(size_radio_frame, text="64x64", variable=self.target_size, value=64).pack(side="left", padx=10)
        tk.Radiobutton(size_radio_frame, text="128x128", variable=self.target_size, value=128).pack(side="left", padx=10)
        tk.Radiobutton(size_radio_frame, text="256x256", variable=self.target_size, value=256).pack(side="left", padx=10)

        # Progress/status
        status_frame = tk.Frame(self.root)
        status_frame.pack(padx=10, pady=5, fill="x")

        self.status_var = tk.StringVar(value="Ready - Select a spritesheet and grid layout")
        status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue", wraplength=550, justify="left")
        status_label.pack()

        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        resize_btn = tk.Button(
            button_frame,
            text="Resize Frames",
            command=self.resize_frames,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        resize_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all,
            padx=20,
            pady=10
        )
        clear_btn.pack(side="left", padx=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Spritesheet",
            filetypes=[("PNG files", "*.png"), ("WEBP files", "*.webp"), ("All files", "*.*")]
        )
        if filename:
            self.input_file = filename
            short_name = os.path.basename(filename)
            self.file_var.set(short_name)
            self.status_var.set(f"Loaded: {short_name}")

    def clear_all(self):
        self.input_file = None
        self.file_var.set("No file selected")
        self.grid_cols.set(4)
        self.grid_rows.set(4)
        self.target_size.set(128)
        self.status_var.set("Ready - Select a spritesheet and grid layout")

    def resize_frames(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a spritesheet file!")
            return

        try:
            self.status_var.set("Processing spritesheet...")
            self.root.update()

            # Load the image
            img = Image.open(self.input_file)
            width, height = img.size

            cols = self.grid_cols.get()
            rows = self.grid_rows.get()
            target_size = self.target_size.get()

            # Calculate frame size
            frame_width = width // cols
            frame_height = height // rows

            # Extract and resize all frames
            resized_frames = []
            total_frames = cols * rows

            self.status_var.set(f"Extracting and resizing {total_frames} frames...")
            self.root.update()

            for row in range(rows):
                for col in range(cols):
                    left = col * frame_width
                    top = row * frame_height
                    right = left + frame_width
                    bottom = top + frame_height

                    frame = img.crop((left, top, right, bottom))

                    # Resize to target size
                    resized_frame = frame.resize((target_size, target_size), Image.LANCZOS)
                    resized_frames.append(resized_frame)

            # Create output grid
            output_cols = cols  # Keep same number of columns
            output_rows = rows  # Keep same number of rows

            output_width = output_cols * target_size
            output_height = output_rows * target_size

            # Create new image
            output_img = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))

            # Paste resized frames
            frame_idx = 0
            for row in range(output_rows):
                for col in range(output_cols):
                    if frame_idx < len(resized_frames):
                        x = col * target_size
                        y = row * target_size
                        output_img.paste(resized_frames[frame_idx], (x, y))
                        frame_idx += 1

            # Save the output
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile=f"{os.path.splitext(os.path.basename(self.input_file))[0]}_resized_{target_size}.png"
            )

            if save_path:
                output_img.save(save_path)
                self.status_var.set(f"✓ Saved: {os.path.basename(save_path)}")

                # Show success message
                frame_info = f"{frame_width}x{frame_height}"
                messagebox.showinfo(
                    "Success",
                    f"Frame sizer completed!\n\n"
                    f"Original frame size: {frame_info}\n"
                    f"Resized to: {target_size}x{target_size}\n"
                    f"Total frames: {len(resized_frames)}\n"
                    f"Grid: {cols}×{rows} → {output_cols}×{output_rows}\n\n"
                    f"Saved to: {os.path.basename(save_path)}"
                )
            else:
                self.status_var.set("Operation cancelled")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize frames:\n{str(e)}")
            self.status_var.set("Error occurred")
            import traceback
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = SpriteFrameSizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()