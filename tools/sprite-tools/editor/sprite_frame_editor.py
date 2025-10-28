#!/usr/bin/env python3
"""
Sprite Frame Editor for Godot
Interactive tool for selecting, deleting, and moving frames in spritesheets
Handles empty frames while preserving grid structure
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk, ImageDraw
import os
import math

class FrameObject:
    """Represents a frame with its properties"""
    def __init__(self, image, grid_x, grid_y, original_index):
        self.image = image
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.original_index = original_index
        self.is_empty = self.determine_if_empty()
        self.selected = False

    def determine_if_empty(self):
        """Check if frame is mostly transparent/empty"""
        if self.image.mode != 'RGBA':
            return False

        # Check if image has any non-transparent pixels
        pixels = self.image.getdata()
        total_pixels = len(pixels)
        non_transparent = sum(1 for pixel in pixels if pixel[3] > 10)  # Alpha > 10

        # Consider empty if less than 1% non-transparent pixels
        return non_transparent / total_pixels < 0.01

    def copy(self):
        """Create a copy of this frame"""
        return FrameObject(self.image.copy(), self.grid_x, self.grid_y, self.original_index)

class SpriteFrameEditor:
    def __init__(self, root):
        self.root = root
        # Only set title and geometry if this is the main window, not a tab
        if hasattr(root, 'title') and callable(getattr(root, 'title')):
            self.root.title("Sprite Frame Editor")
            self.root.geometry("1200x800")

        self.spritesheet = None
        self.frames = []  # List of FrameObject instances
        self.grid_cols = 4
        self.grid_rows = 4
        self.layout_mode = "horizontal"  # "horizontal" or "vertical"
        self.animation_info = []  # Store animation info from loaded layout

        self.thumbnail_size = 64
        self.canvas_zoom = 1.0
        self.dragged_frame = None
        self.drag_start = None

        self.setup_ui()
        self.setup_canvas()

    def setup_ui(self):
        # Menu bar (only for top-level windows, not when used as a tab)
        if hasattr(self.root, 'title') and callable(getattr(self.root, 'title')):
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)

            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Load Spritesheet", command=self.load_spritesheet)
            file_menu.add_command(label="Save Spritesheet", command=self.save_spritesheet)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.root.quit)

            # Make sure window is visible before showing dialogs
            self.root.update_idletasks()
            self.root.lift()
            self.root.focus_force()

            edit_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Edit", menu=edit_menu)
            edit_menu.add_command(label="Select All", command=self.select_all)
            edit_menu.add_command(label="Select Empty", command=self.select_empty)
            edit_menu.add_command(label="Clear Selection", command=self.clear_selection)
            edit_menu.add_separator()
            edit_menu.add_command(label="Delete Selected", command=self.delete_selected)
            edit_menu.add_command(label="Compact Grid", command=self.compact_grid)

        # Toolbar (always show, regardless of menu availability)
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Add load button if menu is not available (tabbed mode)
        if not hasattr(self.root, 'title') or not callable(getattr(self.root, 'title')):
            load_btn = tk.Button(self.toolbar, text="Load Spritesheet", command=self.load_spritesheet, padx=10)
            load_btn.pack(side=tk.LEFT, padx=5, pady=2)

            save_btn = tk.Button(self.toolbar, text="Save Spritesheet", command=self.save_spritesheet, padx=10)
            save_btn.pack(side=tk.LEFT, padx=5, pady=2)

            delete_btn = tk.Button(self.toolbar, text="Delete Selected", command=self.delete_selected, padx=10)
            delete_btn.pack(side=tk.LEFT, padx=5, pady=2)

            cleanup_btn = tk.Button(self.toolbar, text="Clean Up Empty", command=self.cleanup_empty_frames, padx=10)
            cleanup_btn.pack(side=tk.LEFT, padx=5, pady=2)

        # Grid configuration
        grid_frame = tk.Frame(self.toolbar)
        grid_frame.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(grid_frame, text="Grid:").grid(row=0, column=0, padx=2)
        self.cols_var = tk.StringVar(value=str(self.grid_cols))
        self.rows_var = tk.StringVar(value=str(self.grid_rows))

        cols_spin = tk.Spinbox(grid_frame, from_=1, to=32, width=3, textvariable=self.cols_var,
                              command=self.update_grid_config)
        cols_spin.grid(row=0, column=1, padx=2)

        tk.Label(grid_frame, text="×").grid(row=0, column=2, padx=2)

        rows_spin = tk.Spinbox(grid_frame, from_=1, to=32, width=3, textvariable=self.rows_var,
                              command=self.update_grid_config)
        rows_spin.grid(row=0, column=3, padx=2)

        # Layout direction
        layout_frame = tk.Frame(self.toolbar)
        layout_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(layout_frame, text="Layout:").grid(row=0, column=0, sticky="w")
        layout_options = ["Horizontal Strips (Animations in rows)",
                         "Vertical Strips (Animations in columns)"]
        self.layout_var = tk.StringVar(value=layout_options[0])
        layout_menu = ttk.Combobox(layout_frame, textvariable=self.layout_var,
                                  values=layout_options, state="readonly", width=35)
        layout_menu.grid(row=0, column=1, padx=(5, 0))
        layout_menu.bind('<<ComboboxSelected>>', self.on_layout_change)

        # Zoom control
        zoom_frame = tk.Frame(self.toolbar)
        zoom_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT)
        self.zoom_var = tk.DoubleVar(value=1.0)
        zoom_scale = tk.Scale(zoom_frame, from_=0.25, to=3.0, resolution=0.25,
                             orient=tk.HORIZONTAL, variable=self.zoom_var,
                             command=self.update_zoom)
        zoom_scale.pack(side=tk.LEFT)

        # Status bar
        self.status_var = tk.StringVar(value="Ready - Load a spritesheet to begin editing")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                            bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Info panel
        info_panel = tk.Frame(self.root, bd=1, relief=tk.RIDGE)
        info_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Frame info
        info_label = tk.Label(info_panel, text="Frame Information", font=("Arial", 10, "bold"))
        info_label.pack(pady=5)

        self.frame_info_text = tk.Text(info_panel, height=15, width=30, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(info_panel, command=self.frame_info_text.yview)
        self.frame_info_text.config(yscrollcommand=scrollbar.set)

        self.frame_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Instructions
        instr_text = """
Controls:
• Click frames to select/deselect
• Ctrl+Click for multi-select
• Drag to move selected frames
• Delete key to remove selected
• Right-click for context menu

Status Legend:
[□] Normal frame
[▨] Empty frame (transparent)
[■] Selected frame
"""
        instr_label = tk.Label(info_panel, text="Instructions", font=("Arial", 10, "bold"))
        instr_label.pack(pady=(15, 0))
        tk.Label(info_panel, text=instr_text, justify=tk.LEFT).pack(pady=5)

    def setup_canvas(self):
        # Canvas container
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars for canvas
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(canvas_frame, bg='#2a2a2a',
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)

        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)

        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Button-3>', self.on_canvas_right_click)

        # Bind keyboard shortcuts - bind to root for both modes, canvas for extra coverage
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.canvas.bind('<Delete>', lambda e: self.delete_selected())
        self.canvas.bind('<Control-a>', lambda e: self.select_all())

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete Selected", command=self.delete_selected)
        self.context_menu.add_command(label="Clear Selection", command=self.clear_selection)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select Empty Frames", command=self.select_empty)
        self.context_menu.add_command(label="Compact Grid", command=self.compact_grid)

    def load_spritesheet(self):
        filename = filedialog.askopenfilename(
            title="Select Spritesheet",
            filetypes=[("PNG files", "*.png"), ("WEBP files", "*.webp"), ("All files", "*.*")]
        )
        if not filename:
            return

        try:
            self.spritesheet = Image.open(filename)

            # Check for associated layout file
            layout_file = filename.replace('.png', '.layout')
            layout_loaded = False
            if os.path.exists(layout_file):
                if self.load_layout_config(layout_file):
                    layout_loaded = True
                    self.status_var.set(f"Auto-loaded layout from {os.path.basename(layout_file)}")
                    self.root.update()
                    import time
                    time.sleep(1)  # Brief pause to show the message

            # If no layout file, proceed with setup questions
            if not layout_loaded:
                # Ask for layout direction first
                self.ask_for_layout_and_grid()

            self.extract_frames()
            self.update_display()

            layout_desc = "horizontal strips" if self.layout_mode == "horizontal" else "vertical strips"
            self.status_var.set(f"Loaded: {os.path.basename(filename)} - {len(self.frames)} frames in {self.grid_cols}×{self.grid_rows} grid ({layout_desc})")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load spritesheet:\n{str(e)}")

    def extract_frames(self):
        """Extract all frames from the spritesheet based on grid"""
        if not self.spritesheet:
            return

        self.frames = []
        width, height = self.spritesheet.size

        frame_width = width // self.grid_cols
        frame_height = height // self.grid_rows

        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                left = col * frame_width
                top = row * frame_height
                right = left + frame_width
                bottom = top + frame_height

                frame_img = self.spritesheet.crop((left, top, right, bottom))

                # Create frame object
                frame_obj = FrameObject(frame_img, col, row, len(self.frames))
                self.frames.append(frame_obj)

    def update_display(self):
        """Refresh the canvas display"""
        self.canvas.delete("all")

        if not self.frames:
            return

        # Group frames by animation based on layout mode
        if self.layout_mode == "horizontal":
            # Animations in rows, frames left-to-right in each row
            animation_frames = self.group_frames_by_animation_rows()
        else:
            # Animations in columns, frames top-to-bottom in each column
            animation_frames = self.group_frames_by_animation_cols()

        # Calculate positioning
        margin = 10
        thumb_spacing = 5
        header_height = 25  # Space for animation headers
        thumb_size_display = int(self.thumbnail_size * self.canvas_zoom)

        # Calculate canvas size based on layout mode
        if self.layout_mode == "horizontal":
            # Horizontal mode: animations stacked vertically, frames horizontal within, headers on y-axis
            max_frames_in_anim = max(len(frames) for frames in animation_frames.values()) if animation_frames else 1
            header_width = 100  # Reserve space for headers
            total_width = header_width + max_frames_in_anim * (thumb_size_display + thumb_spacing) + margin
            total_height = len(animation_frames) * (thumb_size_display + thumb_spacing) + margin
            anim_step_x = 0
            anim_step_y = thumb_size_display + thumb_spacing
            frame_step_x = thumb_size_display + thumb_spacing
            frame_step_y = 0
        else:
            # Vertical mode: animations spread horizontally, frames vertical within
            max_frames_in_anim = max(len(frames) for frames in animation_frames.values()) if animation_frames else 1
            total_width = len(animation_frames) * (thumb_size_display + margin)
            total_height = header_height + max_frames_in_anim * (thumb_size_display + thumb_spacing) + margin
            anim_step_x = thumb_size_display + margin
            anim_step_y = 0
            frame_step_x = 0
            frame_step_y = thumb_size_display + thumb_spacing

        # Draw each animation group
        current_x = margin
        current_y = margin
        for anim_name, frames in animation_frames.items():
            if not frames:
                continue

            # Animation header
            header_x = margin if self.layout_mode == "horizontal" else current_x
            header_y = current_y if self.layout_mode == "horizontal" else margin
            self.canvas.create_text(header_x, header_y, anchor=tk.NW, text=f"{anim_name}:",
                                  fill="white", font=("Arial", 10, "bold"))

            # Animation frames starting position
            if self.layout_mode == "horizontal":
                frame_x = margin + header_width
                frame_y = current_y
            else:
                frame_x = current_x
                frame_y = margin + header_height

            for i, frame in enumerate(frames):
                # Display frame thumbnail
                self.draw_frame_thumbnail(frame, frame_x, frame_y, frame.original_index)

                # Move to next frame position
                frame_x += frame_step_x
                frame_y += frame_step_y

                # Update total dimensions
                if self.layout_mode == "horizontal":
                    total_width = max(total_width, frame_x)
                else:
                    total_width = max(total_width, frame_x + thumb_size_display + margin)
                    total_height = max(total_height, frame_y + thumb_size_display + margin)

            # Move to next animation position
            current_x += anim_step_x
            current_y += anim_step_y

        # Update scroll region
        self.canvas.config(scrollregion=(0, 0, max(total_width, self.canvas.winfo_width()),
                                       max(total_height, self.canvas.winfo_height())))

        # Update frame info panel
        self.update_frame_info()

    def draw_frame_thumbnail(self, frame, x, y, index):
        """Draw a frame thumbnail on the canvas"""
        size = int(self.thumbnail_size * self.canvas_zoom)

        # Resize frame for thumbnail
        if frame.is_empty:
            # Create placeholder for empty frames
            thumb = Image.new('RGBA', (size, size), (50, 50, 50, 100))
        else:
            thumb = frame.image.resize((size, size), Image.LANCZOS)

        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(thumb)

        # Store reference to prevent garbage collection
        if not hasattr(frame, 'photo_refs'):
            frame.photo_refs = []
        frame.photo_refs.append(photo)

        # Draw background rectangle
        if frame.selected:
            bg_color = "#4CAF50"  # Green for selected
        elif frame.is_empty:
            bg_color = "#FF6B6B"  # Red for empty
        else:
            bg_color = "#2a2a2a"  # Dark for normal

        self.canvas.create_rectangle(x-2, y-2, x+size+2, y+size+2, fill=bg_color, outline="#555")

        # Draw the frame image
        self.canvas.create_image(x, y, anchor=tk.NW, image=photo, tags=f"frame_{index}")

        # Add frame index label
        self.canvas.create_text(x+5, y+5, anchor=tk.NW, text=str(index),
                              fill="white", font=("Arial", 8, "bold"))

    def update_frame_info(self):
        """Update the frame information panel"""
        self.frame_info_text.delete(1.0, tk.END)

        if not self.frames:
            self.frame_info_text.insert(tk.END, "No frames loaded")
            return

        total_frames = len(self.frames)
        selected_frames = sum(1 for f in self.frames if f.selected)
        empty_frames = sum(1 for f in self.frames if f.is_empty)

        info = f"Total Frames: {total_frames}\n"
        info += f"Selected: {selected_frames}\n"
        info += f"Empty: {empty_frames}\n"
        info += f"Grid: {self.grid_cols}×{self.grid_rows}\n\n"

        info += "Frame Status:\n"
        for i, frame in enumerate(self.frames):
            status = "□" if not frame.is_empty else "▨"
            selected = "■ selected" if frame.selected else ""
            info += f"{i:2d}: {status} pos({frame.grid_x},{frame.grid_y}) {selected}\n"

        self.frame_info_text.insert(tk.END, info)

    def update_grid_config(self):
        """Update grid configuration from spinboxes"""
        try:
            self.grid_cols = int(self.cols_var.get())
            self.grid_rows = int(self.rows_var.get())
            if self.spritesheet:
                self.extract_frames()
                self.update_display()
        except ValueError:
            pass  # Invalid input, ignore

    def update_zoom(self, value):
        """Update canvas zoom"""
        self.canvas_zoom = float(value)
        self.update_display()

    def on_layout_change(self, event=None):
        """Handle layout direction change"""
        selection = self.layout_var.get()
        if "Horizontal" in selection:
            self.layout_mode = "horizontal"
        else:
            self.layout_mode = "vertical"

        self.update_display()
        self.status_var.set(f"Layout switched to: {self.layout_mode} strips")

    def on_canvas_click(self, event):
        """Handle canvas click events"""
        # Account for scroll position
        scroll_x = self.canvas.canvasx(event.x)
        scroll_y = self.canvas.canvasy(event.y)

        # Find clicked frame with scroll adjustment
        items = self.canvas.find_overlapping(scroll_x, scroll_y, scroll_x+1, scroll_y+1)

        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("frame_"):
                    frame_index = int(tag.split("_")[1])

                    # Toggle selection
                    if event.state & 0x4:  # Control key held
                        # Add to selection
                        pass  # Keep existing selections
                    else:
                        # Clear selection if not already selected
                        if not self.frames[frame_index].selected:
                            self.clear_selection()

                    self.frames[frame_index].selected = not self.frames[frame_index].selected
                    self.update_display()
                    return

        # Clicked empty space - clear selection
        if not (event.state & 0x4):  # Only if control not held
            self.clear_selection()

    def on_canvas_drag(self, event):
        """Handle drag events"""
        # For now, just select on drag. Could add frame moving later.
        pass

    def on_canvas_release(self, event):
        """Handle drag release"""
        pass

    def on_canvas_right_click(self, event):
        """Handle right-click for context menu"""
        self.context_menu.post(event.x_root, event.y_root)

    def select_all(self):
        """Select all frames"""
        for frame in self.frames:
            frame.selected = True
        self.update_display()

    def select_empty(self):
        """Select all empty frames"""
        for frame in self.frames:
            frame.selected = frame.is_empty
        self.update_display()

    def clear_selection(self):
        """Clear all selections"""
        for frame in self.frames:
            frame.selected = False
        self.update_display()

    def delete_selected(self):
        """Mark selected frames as deleted (empty)"""
        deleted_count = 0
        for frame in self.frames:
            if frame.selected:
                # Create empty frame to replace
                empty_img = Image.new('RGBA', frame.image.size, (0, 0, 0, 0))
                frame.image = empty_img
                frame.is_empty = True
                frame.selected = False
                deleted_count += 1

        self.update_display()
        self.status_var.set(f"Deleted {deleted_count} frames")

    def cleanup_empty_frames(self):
        """Remove all empty frames from the frames list altogether"""
        if not self.frames:
            return

        original_count = len(self.frames)

        # Keep only non-empty frames
        cleaned_frames = [frame for frame in self.frames if not frame.is_empty]

        if len(cleaned_frames) == original_count:
            messagebox.showinfo("Cleanup", "No empty frames found to remove.")
            return

        deleted_count = original_count - len(cleaned_frames)

        # Update frames with non-empty frames
        self.frames = cleaned_frames

        # Renumber grid positions after removal
        for i, frame in enumerate(self.frames):
            # Convert flat index back to grid position
            frame.original_index = i  # Update the display index
            # Note: We don't change grid_x, grid_y as they represent the logical position

        self.update_display()
        self.status_var.set(f"Removed {deleted_count} empty frames, {len(self.frames)} frames remaining")

    def compact_grid(self):
        """Remove empty columns/rows and compact the grid"""
        if not self.frames:
            return

        # Find which columns and rows have non-empty frames
        active_cols = set()
        active_rows = set()

        for frame in self.frames:
            if not frame.is_empty:
                active_cols.add(frame.grid_x)
                active_rows.add(frame.grid_y)

        if not active_cols or not active_rows:
            messagebox.showerror("Error", "No frames to keep!")
            return

        # Sort active columns and rows
        active_cols = sorted(active_cols)
        active_rows = sorted(active_rows)

        # Create mapping for new positions
        col_mapping = {old_col: new_col for new_col, old_col in enumerate(active_cols)}
        row_mapping = {old_row: new_row for new_row, old_row in enumerate(active_rows)}

        # Create new frame list with only non-empty frames, repositioned
        compacted = []
        for frame in self.frames:
            if not frame.is_empty:
                # Map to new compact positions
                new_x = col_mapping[frame.grid_x]
                new_y = row_mapping[frame.grid_y]
                frame.grid_x = new_x
                frame.grid_y = new_y
                compacted.append(frame)

        # Update grid dimensions
        self.frames = compacted
        self.grid_cols = len(active_cols)
        self.grid_rows = len(active_rows)
        self.cols_var.set(str(self.grid_cols))
        self.rows_var.set(str(self.grid_rows))

        self.update_display()
        self.status_var.set(f"Compacted to {self.grid_cols}×{self.grid_rows} grid ({len(compacted)} frames) - removed empty columns/rows")

    def save_spritesheet(self):
        """Save the modified spritesheet"""
        if not self.frames:
            messagebox.showerror("Error", "No frames to save!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="edited_spritesheet.png"
        )

        if not save_path:
            return

        try:
            # Create new spritesheet from current grid layout
            frame_size = self.frames[0].image.size if self.frames else (64, 64)
            sheet_width = self.grid_cols * frame_size[0]
            sheet_height = self.grid_rows * frame_size[1]

            new_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

            # Place frames according to their grid positions
            for frame in self.frames:
                x = frame.grid_x * frame_size[0]
                y = frame.grid_y * frame_size[1]
                new_sheet.paste(frame.image, (x, y))

            # Save the spritesheet
            new_sheet.save(save_path)

            # Save layout config with all relevant data
            self.save_layout_config(save_path, frame_size[0], [])
            self.status_var.set(f"Saved: {os.path.basename(save_path)} and layout config")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save spritesheet:\n{str(e)}")

    def group_frames_by_animation_rows(self):
        """Group frames by rows for horizontal strips (animations in rows)"""
        groups = {}
        for frame in self.frames:
            anim_name = f"Row {frame.grid_y + 1}"
            if anim_name not in groups:
                groups[anim_name] = []
            groups[anim_name].append(frame)
        return groups

    def group_frames_by_animation_cols(self):
        """Group frames by columns for vertical strips (animations in columns)"""
        groups = {}
        for frame in self.frames:
            anim_name = f"Col {frame.grid_x + 1}"
            if anim_name not in groups:
                groups[anim_name] = []
            groups[anim_name].append(frame)
        return groups

    def load_layout_config(self, layout_path):
        """Load layout configuration from file"""
        try:
            config = {}
            current_section = None

            with open(layout_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        config[current_section] = {}
                    elif '=' in line and current_section:
                        key, value = line.split('=', 1)
                        config[current_section][key.strip()] = value.strip()

            # Apply loaded configuration
            if 'layout' in config:
                layout_config = config['layout']
                mode = layout_config.get('mode', 'horizontal')
                self.layout_mode = mode

                # Update the UI dropdown
                if self.layout_mode == "horizontal":
                    self.layout_var.set("Horizontal Strips (Animations in rows)")
                else:
                    self.layout_var.set("Vertical Strips (Animations in columns)")

                # Set grid dimensions
                self.grid_cols = int(layout_config.get('grid_cols', 4))
                self.grid_rows = int(layout_config.get('grid_rows', 4))
                self.cols_var.set(str(self.grid_cols))
                self.rows_var.set(str(self.grid_rows))

            # Store animation info - prefer animation_data section if available (from combiner)
            # Fall back to animations section for manual layouts
            if 'animation_data' in config:
                # Parse the structured animation data from combiner
                print(f"DEBUG: Loading animation_data section from file: {layout_path}")
                self.animation_info = self.parse_animation_data_section(layout_path)
                print(f"DEBUG: Parsed animation_info: {self.animation_info}")

            elif 'animations' in config:
                # Legacy support for simple animations section
                print("DEBUG: Falling back to basic animations section (no detailed data)")
                self.animation_info = []
                for anim_name, frame_count in config['animations'].items():
                    self.animation_info.append({
                        'name': anim_name,
                        'frame_count': int(frame_count),
                        'start_frame': 0  # Will be calculated
                    })

                # Calculate start frames from frame mapping if available
                if 'frame_mapping' in config:
                    current_frame = 0
                    for anim in self.animation_info:
                        anim['start_frame'] = current_frame
                        current_frame += anim['frame_count']

            # If we have animations data, we could use it for grouping, but for now
            # we just use the grid settings
            return True

        except Exception as e:
            print(f"Failed to load layout config: {e}")
            return False

    def ask_for_layout_and_grid(self):
        """Ask user for layout direction and grid settings"""
        # Ask for layout direction first
        layout_choice = self.show_input_dialog(
            "Layout Direction",
            "How are animations organized in this spritesheet?\n\n"
            "• 'horizontal' = Each row is a different animation\n"
            "• 'vertical' = Each column is a different animation\n\n"
            "Enter 'horizontal' or 'vertical':",
            initialvalue="horizontal"
        )

        if not layout_choice.get():
            return

        self.layout_mode = layout_choice.get().lower().strip()
        if self.layout_mode not in ['horizontal', 'vertical']:
            self.layout_mode = 'horizontal'

        # Update UI dropdown
        if self.layout_mode == 'horizontal':
            self.layout_var.set("Horizontal Strips (Animations in rows)")
        else:
            self.layout_var.set("Vertical Strips (Animations in columns)")

        # Ask for grid confirmation
        cols_result = self.show_input_dialog(
            "Grid Columns",
            "Enter number of columns in the spritesheet:",
            initialvalue=str(self.grid_cols)
        )

        if not cols_result.get():
            return

        try:
            cols = int(cols_result.get())
            if cols < 1 or cols > 32:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of columns (1-32)")
            return

        rows_result = self.show_input_dialog(
            "Grid Rows",
            "Enter number of rows in the spritesheet:",
            initialvalue=str(self.grid_rows)
        )

        if not rows_result.get():
            return

        try:
            rows = int(rows_result.get())
            if rows < 1 or rows > 32:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of rows (1-32)")
            return

        self.grid_cols = cols
        self.grid_rows = rows
        self.cols_var.set(str(cols))
        self.rows_var.set(str(rows))

    def save_layout_config(self, image_path, target_size, animation_info):
        """Save layout configuration file for Sprite Frame Editor (exactsame as combiner)"""
        layout_path = image_path.replace('.png', '.layout')
        print(f"DEBUG: Saving layout config to: {layout_path}")
        print(f"DEBUG: animation_info = {animation_info}")

        # Calculate grid dimensions for the final spritesheet (exactly like combiner)
        if self.layout_mode == "horizontal":
            # Rows mode: frames across, animations down (horizontal strips)
            grid_cols = max([info['frame_count'] for info in animation_info]) if animation_info else 1
            grid_rows = len(animation_info) if animation_info else 1
        else:
            # Columns mode: animations across, frames down (vertical strips)
            grid_cols = len(animation_info) if animation_info else 1
            grid_rows = max([info['frame_count'] for info in animation_info]) if animation_info else 1

        try:
            with open(layout_path, 'w') as f:
                f.write("# Sprite Frame Editor Layout Configuration\n")
                f.write("# Auto-generated by Spritesheet Combiner\n\n")

                f.write("[layout]\n")
                mode = self.layout_mode
                f.write(f"mode = {mode}\n")
                f.write(f"target_size = {target_size}\n")
                f.write(f"grid_cols = {grid_cols}\n")
                f.write(f"grid_rows = {grid_rows}\n\n")

                # Recalculate animation data based on current frame positions
                current_animation_info = []
                if self.layout_mode == "horizontal":
                    row_groups = {}
                    for frame in self.frames:
                        row = frame.grid_y
                        if row not in row_groups:
                            row_groups[row] = []
                        row_groups[row].append(frame.original_index)
                    for row in sorted(row_groups.keys()):
                        frames_in_row = sorted(row_groups[row])
                        current_animation_info.append({
                            'name': f"Row {row + 1}",
                            'start_frame': frames_in_row[0],
                            'frame_count': len(frames_in_row)
                        })
                else:
                    col_groups = {}
                    for frame in self.frames:
                        col = frame.grid_x
                        if col not in col_groups:
                            col_groups[col] = []
                        col_groups[col].append(frame.original_index)
                    for col in sorted(col_groups.keys()):
                        frames_in_col = sorted(col_groups[col])
                        current_animation_info.append({
                            'name': f"Col {col + 1}",
                            'start_frame': frames_in_col[0],
                            'frame_count': len(frames_in_col)
                        })

                if current_animation_info:
                    f.write("[animations]\n")
                    for anim in current_animation_info:
                        f.write(f"{anim['name']} = {anim['frame_count']}\n")
                    f.write("\n")

                    f.write("[animation_data]\n")
                    current_frame = 0
                    for anim in current_animation_info:
                        f.write(f"{anim['name']}:\n")
                        f.write(f"  start_frame: {current_frame}\n")
                        f.write(f"  frame_count: {anim['frame_count']}\n")
                        f.write(f"  end_frame: {current_frame + anim['frame_count'] - 1}\n\n")
                        current_frame += anim['frame_count']
                else:
                    # No animation info available, add basic note
                    f.write("[notes]\n")
                    f.write("# Layout configuration saved from Sprite Frame Editor\n")
                    f.write(f"# Mode: {self.layout_mode}\n")

            print("DEBUG: Layout config saved successfully!")
        except Exception as e:
            print(f"ERROR: Failed to save layout config: {e}")
            import traceback
            traceback.print_exc()

    def show_input_dialog(self, title, prompt, initialvalue=""):
        """Show a custom input dialog that stays on top"""
        result = tk.StringVar(value=initialvalue)

        # Create top-level dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        # Content
        tk.Label(dialog, text=prompt, wraplength=380, justify="left").pack(pady=10)

        entry = tk.Entry(dialog, textvariable=result, width=50)
        entry.pack(pady=5)
        entry.focus()
        entry.select_range(0, tk.END)

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def on_ok():
            dialog.destroy()

        def on_cancel():
            result.set("")
            dialog.destroy()

        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.RIGHT, padx=5)

        # Bind Enter key
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        # Wait for dialog to close
        self.root.wait_window(dialog)

        return result

    def parse_animation_data_section(self, layout_path):
        """Parse the [animation_data] section from the layout file"""
        animation_info = []

        try:
            with open(layout_path, 'r') as f:
                lines = f.readlines()

            in_animation_data = False
            current_anim = None
            current_data = {}

            for line in lines:
                line = line.strip()

                if line.startswith('[animation_data]'):
                    in_animation_data = True
                    continue
                elif line.startswith('[') and line.endswith(']'):
                    # Moved to another section
                    if current_anim:
                        current_data['name'] = current_anim
                        animation_info.append(current_data.copy())
                        current_anim = None
                        current_data = {}
                    if line != '[animation_data]':
                        in_animation_data = False
                    continue

                if not in_animation_data or not line:
                    continue

                # Parse animation data lines
                if line.endswith(':') and not line.startswith('  '):
                    # New animation (e.g., "idle:")
                    if current_anim:
                        current_data['name'] = current_anim
                        animation_info.append(current_data.copy())
                    current_anim = line[:-1]  # Remove colon
                    current_data = {}
                elif line.startswith('  ') and current_anim:
                    # Data field (e.g., "  start_frame: 0")
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in ['start_frame', 'frame_count', 'end_frame']:
                            current_data[key] = int(value)

            # Add the last animation
            if current_anim:
                current_data['name'] = current_anim
                animation_info.append(current_data)

        except Exception as e:
            print(f"Error parsing animation_data section: {e}")

        return animation_info

def main():
    root = tk.Tk()
    app = SpriteFrameEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()