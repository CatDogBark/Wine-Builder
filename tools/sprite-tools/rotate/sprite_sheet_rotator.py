#!/usr/bin/env python3
"""
Spritesheet Frame Rotator for Godot
Rotates individual frames in a spritesheet by specified degrees
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import math

class SpritesheetRotator:
    def __init__(self, root):
        self.root = root
        # Only set title and geometry if this is the main window, not a tab
        if hasattr(root, 'title') and callable(getattr(root, 'title')):
            self.root.title("Spritesheet Frame Rotator")
            self.root.geometry("600x500")

        self.input_file = None
        self.grid_cols = tk.IntVar(value=4)
        self.grid_rows = tk.IntVar(value=4)
        self.rotation_angle = tk.DoubleVar(value=-15.0)

        self.setup_ui()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Spritesheet Frame Rotator", font=("Arial", 16, "bold"))
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
        settings_frame = tk.LabelFrame(self.root, text="Grid Layout & Rotation", padx=10, pady=10)
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

        # Rotation angle
        rotation_frame = tk.Frame(settings_frame)
        rotation_frame.pack(pady=10)

        tk.Label(rotation_frame, text="Rotation Angle (degrees):").grid(row=0, column=0, sticky="w", padx=5)
        rotation_spin = tk.Spinbox(rotation_frame, from_=-180, to=180, width=8, textvariable=self.rotation_angle, increment=1.0)
        rotation_spin.grid(row=0, column=1, padx=5)

        # Add some preset buttons for common angles
        preset_frame = tk.Frame(rotation_frame)
        preset_frame.grid(row=0, column=2, padx=10)
        for angle in [-90, -45, 45, 90, -15]:
            btn = tk.Button(preset_frame, text=f"{angle}°", command=lambda a=angle: self.rotation_angle.set(a), width=5)
            btn.pack(side="left", padx=1)

        # Progress/status
        status_frame = tk.Frame(self.root)
        status_frame.pack(padx=10, pady=5, fill="x")

        self.status_var = tk.StringVar(value="Ready - Select a spritesheet and set rotation parameters")
        status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue", wraplength=550, justify="left")
        status_label.pack()

        # Preview area (optional image display)
        preview_frame = tk.LabelFrame(self.root, text="Preview", padx=10, pady=10)
        preview_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.preview_text = tk.Text(preview_frame, height=8, wrap="word", state="disabled")
        scroll = tk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text.config(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.preview_text.pack(fill="both", expand=True)

        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        rotate_btn = tk.Button(
            button_frame,
            text="Rotate Frames",
            command=self.rotate_frames,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        rotate_btn.pack(side="left", padx=5)

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

            # Update preview info
            self.update_preview()

    def update_preview(self):
        """Update the preview information"""
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)

        if self.input_file:
            try:
                img = Image.open(self.input_file)
                width, height = img.size
                cols = self.grid_cols.get()
                rows = self.grid_rows.get()
                rotation = self.rotation_angle.get()

                frame_width = width // cols
                frame_height = height // rows

                # Calculate the diagonal to determine expansion needed for rotation
                diagonal = math.sqrt(frame_width ** 2 + frame_height ** 2)
                expanded_size = math.ceil(diagonal)

                info = f"""Input Spritesheet: {os.path.basename(self.input_file)}
Size: {width}×{height} pixels
Grid: {cols}×{rows} ({cols * rows} frames)
Frame size: {frame_width}×{frame_height} pixels

Rotation: {rotation}°

Output: Same dimensions as input
{cols}×{rows} frames cropped back to {frame_width}×{frame_height} pixels each
(expand internally to ~{expanded_size}×{expanded_size} for rotation)"""

                self.preview_text.insert(1.0, info)
            except Exception as e:
                self.preview_text.insert(1.0, f"Error reading file: {e}")

        self.preview_text.config(state="disabled")

    def clear_all(self):
        self.input_file = None
        self.file_var.set("No file selected")
        self.grid_cols.set(4)
        self.grid_rows.set(4)
        self.rotation_angle.set(-15.0)
        self.status_var.set("Ready - Select a spritesheet and set rotation parameters")

        # Clear preview
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state="disabled")

    def rotate_frames(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a spritesheet file!")
            return

        try:
            self.status_var.set("Processing spritesheet rotation...")
            self.root.update()

            # Load the image
            img = Image.open(self.input_file)
            width, height = img.size

            cols = self.grid_cols.get()
            rows = self.grid_rows.get()
            rotation = self.rotation_angle.get()

            # Calculate frame size
            frame_width = width // cols
            frame_height = height // rows

            self.status_var.set(f"Rotating {cols * rows} frames by {rotation}°...")
            self.root.update()

            # Output will use original frame dimensions (no expansion)
            # Use expanded canvas internally for rotation only
            output_width = width
            output_height = height
            output_img = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))

            # Calculate expanded frame size for rotation (not final output)
            diagonal = math.sqrt(frame_width ** 2 + frame_height ** 2)
            expanded_frame_size = math.ceil(diagonal)

            # Process each frame
            frame_idx = 0
            for row in range(rows):
                for col in range(cols):
                    # Extract frame
                    left = col * frame_width
                    top = row * frame_height
                    right = left + frame_width
                    bottom = top + frame_height

                    frame = img.crop((left, top, right, bottom))

                    # Rotate the frame and crop back to original size
                    rotated_expanded = frame.rotate(rotation, expand=True)

                    # Crop the center of the rotated result back to original frame size
                    # This prevents clipping while maintaining uniform frame dimensions
                    crop_left = (rotated_expanded.width - frame_width) // 2
                    crop_top = (rotated_expanded.height - frame_height) // 2
                    crop_right = crop_left + frame_width
                    crop_bottom = crop_top + frame_height

                    final_frame = rotated_expanded.crop((crop_left, crop_top, crop_right, crop_bottom))

                    # Position in output grid (original positions maintain spritesheet dimensions)
                    x_offset = col * frame_width
                    y_offset = row * frame_height

                    output_img.paste(final_frame, (x_offset, y_offset))
                    frame_idx += 1

            # Save the output
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile=f"{os.path.splitext(os.path.basename(self.input_file))[0]}_rotated_{rotation:.0f}deg.png"
            )

            if save_path:
                output_img.save(save_path)
                self.status_var.set(f"✓ Saved: {os.path.basename(save_path)}")

                # Show success message
                frame_info = f"{frame_width}x{frame_height}"
                output_info = f"{output_width}x{output_height}"
                messagebox.showinfo(
                    "Success",
                    f"Frame rotation completed!\n\n"
                    f"Original spritesheet: {width}×{height} pixels\n"
                    f"Frame size: {frame_info}\n"
                    f"Rotated by: {rotation}°\n"
                    f"Output: {output_info} pixels (same as input)\n"
                    f"Total frames: {cols * rows}\n"
                    f"Grid: {cols}×{rows}\n\n"
                    f"Saved to: {os.path.basename(save_path)}"
                )
            else:
                self.status_var.set("Operation cancelled")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate frames:\n{str(e)}")
            self.status_var.set("Error occurred")
            import traceback
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = SpritesheetRotator(root)
    root.mainloop()

if __name__ == "__main__":
    main()