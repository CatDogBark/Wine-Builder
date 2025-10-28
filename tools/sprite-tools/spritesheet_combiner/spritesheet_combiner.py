#!/usr/bin/env python3
"""
Enhanced Spritesheet Combiner for Godot
Now with explicit grid layout specification
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os

class EnhancedSpritesheetCombiner:
    def __init__(self, root):
        self.root = root
        # Only set title and geometry if this is the main window, not a tab
        if hasattr(root, 'title') and callable(getattr(root, 'title')):
            self.root.title("Godot Spritesheet Combiner v2")
            self.root.geometry("800x700")

        # Animation data storage with grid info
        self.animations = {
            'idle': {'file': None, 'frames': 16, 'grid_cols': 4, 'grid_rows': 4},
            'run': {'file': None, 'frames': 16, 'grid_cols': 4, 'grid_rows': 4},
            'front_attack': {'file': None, 'frames': 16, 'grid_cols': 4, 'grid_rows': 4},
            'back_attack': {'file': None, 'frames': 16, 'grid_cols': 4, 'grid_rows': 4},
            'dying': {'file': None, 'frames': 16, 'grid_cols': 4, 'grid_rows': 4}
        }

        self.target_size = tk.IntVar(value=128)
        self.layout = tk.StringVar(value="horizontal")

        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Enhanced Spritesheet Combiner", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Settings Frame
        settings_frame = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        settings_frame.pack(padx=10, pady=5, fill="x")
        
        # Target frame size
        tk.Label(settings_frame, text="Target Frame Size:").grid(row=0, column=0, sticky="w", pady=5)
        size_frame = tk.Frame(settings_frame)
        size_frame.grid(row=0, column=1, sticky="w", pady=5)
        tk.Radiobutton(size_frame, text="64x64", variable=self.target_size, value=64).pack(side="left", padx=5)
        tk.Radiobutton(size_frame, text="128x128", variable=self.target_size, value=128).pack(side="left", padx=5)
        tk.Radiobutton(size_frame, text="256x256", variable=self.target_size, value=256).pack(side="left", padx=5)
        
        # Layout option
        tk.Label(settings_frame, text="Layout:").grid(row=1, column=0, sticky="w", pady=5)
        layout_frame = tk.Frame(settings_frame)
        layout_frame.grid(row=1, column=1, sticky="w", pady=5)
        tk.Radiobutton(layout_frame, text="Horizontal Strips", variable=self.layout, value="horizontal").pack(side="left", padx=5)
        tk.Radiobutton(layout_frame, text="Vertical Strips", variable=self.layout, value="vertical").pack(side="left", padx=5)
        
        # Animations Frame with scrollbar
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        anim_frame = tk.Frame(canvas)
        
        canvas.create_window((0, 0), window=anim_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create UI for each animation
        tk.Label(anim_frame, text="Animation", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(anim_frame, text="File", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)
        tk.Label(anim_frame, text="", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        tk.Label(anim_frame, text="Frames", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5)
        tk.Label(anim_frame, text="Grid (CxR)", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5)
        
        row = 1
        for anim_name, anim_data in self.animations.items():
            display_name = anim_name.replace('_', ' ').title()
            
            # Label
            tk.Label(anim_frame, text=f"{display_name}:", font=("Arial", 10, "bold")).grid(
                row=row, column=0, sticky="w", pady=5, padx=5
            )
            
            # File path display
            file_var = tk.StringVar(value="No file")
            anim_data['file_var'] = file_var
            tk.Label(anim_frame, textvariable=file_var, fg="gray", width=20, anchor="w").grid(
                row=row, column=1, sticky="w", padx=5
            )
            
            # Browse button
            browse_btn = tk.Button(
                anim_frame, 
                text="Browse", 
                command=lambda name=anim_name: self.browse_file(name),
                width=8
            )
            browse_btn.grid(row=row, column=2, padx=5)
            
            # Frame count
            frame_spinbox = tk.Spinbox(anim_frame, from_=1, to=30, width=5)
            frame_spinbox.delete(0, "end")
            frame_spinbox.insert(0, str(anim_data['frames']))
            frame_spinbox.grid(row=row, column=3, padx=5)
            anim_data['frame_widget'] = frame_spinbox
            
            # Grid layout (columns x rows)
            grid_frame = tk.Frame(anim_frame)
            grid_frame.grid(row=row, column=4, padx=5)
            
            cols_spin = tk.Spinbox(grid_frame, from_=1, to=10, width=3)
            cols_spin.delete(0, "end")
            cols_spin.insert(0, str(anim_data['grid_cols']))
            cols_spin.pack(side="left")
            
            tk.Label(grid_frame, text="×").pack(side="left")
            
            rows_spin = tk.Spinbox(grid_frame, from_=1, to=10, width=3)
            rows_spin.delete(0, "end")
            rows_spin.insert(0, str(anim_data['grid_rows']))
            rows_spin.pack(side="left")
            
            anim_data['cols_widget'] = cols_spin
            anim_data['rows_widget'] = rows_spin
            
            row += 1
        
        # Update canvas scroll region
        anim_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        combine_btn = tk.Button(
            button_frame, 
            text="Combine Spritesheets", 
            command=self.combine_spritesheets,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        combine_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_all,
            padx=20,
            pady=10
        )
        clear_btn.pack(side="left", padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready - Specify grid layout for each animation")
        status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue", wraplength=700)
        status_label.pack(pady=5)
    
    def browse_file(self, anim_name):
        filename = filedialog.askopenfilename(
            title=f"Select {anim_name.replace('_', ' ').title()} Spritesheet",
            filetypes=[("PNG files", "*.png"), ("WEBP files", "*.webp"), ("All files", "*.*")]
        )
        if filename:
            self.animations[anim_name]['file'] = filename
            short_name = os.path.basename(filename)
            self.animations[anim_name]['file_var'].set(short_name[:25])
            self.status_var.set(f"Loaded: {short_name}")
    
    def clear_all(self):
        for anim_data in self.animations.values():
            anim_data['file'] = None
            anim_data['file_var'].set("No file")
        self.status_var.set("Cleared all files")
    
    def combine_spritesheets(self):
        # Get all values from spinboxes
        for anim_name, anim_data in self.animations.items():
            anim_data['frames'] = int(anim_data['frame_widget'].get())
            anim_data['grid_cols'] = int(anim_data['cols_widget'].get())
            anim_data['grid_rows'] = int(anim_data['rows_widget'].get())

        # Check if at least one file is selected
        selected_files = [data for data in self.animations.values() if data['file']]
        if not selected_files:
            messagebox.showerror("Error", "Please select at least one spritesheet!")
            return

        try:
            self.status_var.set("Processing...")
            self.root.update()

            target_size = self.target_size.get()
            layout = self.layout.get()

            # Extract and resize frames from each animation
            all_frames = []
            animation_info = []

            for anim_name in ['idle', 'run', 'front_attack', 'back_attack', 'dying']:
                anim_data = self.animations[anim_name]
                if not anim_data['file']:
                    continue

                frames = self.extract_frames_explicit(
                    anim_data['file'],
                    anim_data['frames'],
                    anim_data['grid_cols'],
                    anim_data['grid_rows'],
                    target_size
                )

                animation_info.append({
                    'name': anim_name,
                    'start_frame': len(all_frames),
                    'frame_count': len(frames)
                })

                all_frames.extend(frames)

            # Create combined spritesheet
            if layout == "horizontal":
                combined = self.create_vertical_sheet(all_frames, target_size, animation_info)
            else:
                combined = self.create_horizontal_sheet(all_frames, target_size, animation_info)

            # Save file
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile="combined_spritesheet.png"
            )

            if save_path:
                print(f"DEBUG: Starting file saves to: {save_path}")
                combined.save(save_path)
                print("DEBUG: PNG file saved successfully")

                # Consolidate all metadata into .layout file
                print("DEBUG: Calling save_layout_config with all metadata...")
                self.save_layout_config(save_path, target_size, animation_info)
                print("DEBUG: save_layout_config call completed")

                self.status_var.set(f"✓ Saved: {os.path.basename(save_path)}")
                messagebox.showinfo(
                    "Success",
                    f"Spritesheet saved!\n\nTotal frames: {len(all_frames)}\n"
                    f"Size: {combined.width}x{combined.height}px\n\n"
                    f"Layout config saved to: {os.path.basename(save_path).replace('.png', '.layout')}"
                )
            else:
                print("DEBUG: No save path - save was cancelled by user")
                self.status_var.set("Cancelled")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to combine spritesheets:\n{str(e)}")
            self.status_var.set("Error occurred")
            import traceback
            traceback.print_exc()
    
    def extract_frames_explicit(self, filepath, frame_count, grid_cols, grid_rows, target_size):
        """Extract frames using explicitly specified grid layout"""
        img = Image.open(filepath)
        width, height = img.size
        
        frame_width = width // grid_cols
        frame_height = height // grid_rows
        
        frames = []
        frames_extracted = 0
        
        for row in range(grid_rows):
            for col in range(grid_cols):
                if frames_extracted >= frame_count:
                    break
                    
                left = col * frame_width
                top = row * frame_height
                right = left + frame_width
                bottom = top + frame_height
                
                frame = img.crop((left, top, right, bottom))

                # Resize proportionally to target size while maintaining aspect ratio
                frame = self.resize_maintaining_ratio(frame, target_size)
                frames.append(frame)
                
                frames_extracted += 1
            
            if frames_extracted >= frame_count:
                break
        
        return frames

    def resize_maintaining_ratio(self, frame, target_size):
        """Resize frame while maintaining aspect ratio, center on square canvas"""
        orig_width, orig_height = frame.size

        # Calculate scaling factor to fit within target size while maintaining ratio
        scale = min(target_size / orig_width, target_size / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        # Resize maintaining aspect ratio
        resized = frame.resize((new_width, new_height), Image.LANCZOS)

        # Create square canvas
        square_canvas = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))

        # Center the resized frame on the square canvas
        x_offset = (target_size - new_width) // 2
        y_offset = (target_size - new_height) // 2

        square_canvas.paste(resized, (x_offset, y_offset))

        return square_canvas
    
    def create_horizontal_sheet(self, frames, target_size, animation_info):
        """Create horizontal strip layout with one column per animation"""
        max_frames = max([info['frame_count'] for info in animation_info])
        combined_width = len(animation_info) * target_size
        combined_height = max_frames * target_size

        combined = Image.new('RGBA', (combined_width, combined_height), (0, 0, 0, 0))

        current_col = 0
        for anim in animation_info:
            start = anim['start_frame']
            count = anim['frame_count']

            for i in range(count):
                frame = frames[start + i]
                combined.paste(frame, (current_col * target_size, i * target_size))

            current_col += 1

        return combined
    
    def create_vertical_sheet(self, frames, target_size, animation_info):
        """Create vertical strip layout with one row per animation"""
        max_frames = max([info['frame_count'] for info in animation_info])
        combined_width = max_frames * target_size
        combined_height = len(animation_info) * target_size
        
        combined = Image.new('RGBA', (combined_width, combined_height), (0, 0, 0, 0))
        
        current_row = 0
        for anim in animation_info:
            start = anim['start_frame']
            count = anim['frame_count']
            
            for i in range(count):
                frame = frames[start + i]
                combined.paste(frame, (i * target_size, current_row * target_size))
            
            current_row += 1
        
        return combined
    
    # Method removed as animation data is now saved in the .layout file

    def save_layout_config(self, image_path, target_size, animation_info):
        """Save complete layout configuration and animation data for Sprite Frame Editor"""
        layout_path = image_path.replace('.png', '.layout')
        print(f"DEBUG: Saving complete layout config to: {layout_path}")

        # Calculate grid dimensions for the final spritesheet
        if self.layout.get() == "horizontal":
            # Horizontal strips: frames across, animations down
            grid_cols = max([info['frame_count'] for info in animation_info])
            grid_rows = len(animation_info)
        else:
            # Vertical strips: animations across, frames down
            grid_cols = len(animation_info)
            grid_rows = max([info['frame_count'] for info in animation_info])

        try:
            with open(layout_path, 'w') as f:
                f.write("# Comprehensive Metadata File for Godot Spritesheets\n")
                f.write("# Generated by Spritesheet Combiner - Contains layout and animation data\n\n")

                f.write("[layout]\n")
                f.write(f"mode = {self.layout.get()}\n")
                f.write(f"target_size = {target_size}\n")
                f.write(f"grid_cols = {grid_cols}\n")
                f.write(f"grid_rows = {grid_rows}\n\n")

                f.write("[animations]\n")
                for anim in animation_info:
                    f.write(f"{anim['name']} = {anim['frame_count']}\n")
                f.write("\n")

                f.write("[animation_data]\n")
                for anim in animation_info:
                    f.write(f"{anim['name']}:\n")
                    f.write(f"  start_frame: {anim['start_frame']}\n")
                    f.write(f"  frame_count: {anim['frame_count']}\n")
                    f.write(f"  end_frame: {anim['start_frame'] + anim['frame_count'] - 1}\n\n")

                # Include frame mapping for reference
                f.write("[frame_mapping]\n")
                for anim in animation_info:
                    end_frame = anim['start_frame'] + anim['frame_count'] - 1
                    f.write(f"# {anim['name']}: frames {anim['start_frame']}-{end_frame}\n")

            print("DEBUG: Complete layout config saved successfully!")
        except Exception as e:
            print(f"ERROR: Failed to save layout config: {e}")
            import traceback
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = EnhancedSpritesheetCombiner(root)
    root.mainloop()

if __name__ == "__main__":
    main()