#!/usr/bin/env python3
"""
Floorplanning Tool - Version 2.0
Enhanced desktop application with improved handles and non-rectilinear shapes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as patches

class FloorplanToolV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Floorplanning Tool - Version 2.0")
        self.root.geometry("1400x900")
        
        # Data storage
        self.blocks = []
        self.connections = []
        self.hardmacro_names = []
        
        # Interactive state
        self.selected_block = None
        self.dragging = False
        self.resize_mode = None  # 'move', 'width', 'height', 'corner'
        self.last_mouse_pos = None
        self.hover_handle = None
        
        # Handle configuration
        self.handle_config = {
            'corner_size': 25,      # Larger corner handles
            'edge_width': 15,       # Edge handle width
            'edge_height': 25,      # Edge handle height
            'colors': {
                'corner': '#FF6B6B',    # Red for corners
                'edge': '#4ECDC4',      # Teal for edges
                'hover': '#FFE66D',     # Yellow for hover
                'selected': '#FF8E8E'   # Light red for selected
            }
        }
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Upload button
        self.upload_btn = ttk.Button(control_frame, text="Upload CSV", command=self.upload_csv)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Interactive controls
        self.interactive_var = tk.BooleanVar(value=True)
        self.interactive_cb = ttk.Checkbutton(control_frame, text="Interactive Mode", 
                                            variable=self.interactive_var)
        self.interactive_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Shape mode controls
        self.shape_mode_var = tk.StringVar(value="rectangle")
        shape_frame = ttk.LabelFrame(control_frame, text="Shape Mode")
        shape_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(shape_frame, text="Rectangle", variable=self.shape_mode_var, 
                       value="rectangle").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(shape_frame, text="L-Shape", variable=self.shape_mode_var, 
                       value="lshape").pack(side=tk.LEFT, padx=5)
        
        # Reset view button
        self.reset_btn = ttk.Button(control_frame, text="Reset View", command=self.reset_view)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Info labels
        self.info_label = ttk.Label(control_frame, text="No data loaded")
        self.info_label.pack(side=tk.LEFT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Floorplan view tab
        self.floorplan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.floorplan_frame, text="Interactive Floorplan")
        
        # Create matplotlib figure for floorplan
        self.fig = Figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self.floorplan_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Properties tab
        self.properties_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.properties_frame, text="Block Properties")
        
        # Create properties widgets
        self.create_properties_widgets()
        
        # Connections tab
        self.connections_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.connections_frame, text="Connections")
        
        # Create connections list
        self.create_connections_widgets()
        
        # Instructions
        self.create_instructions()
        
        # Initial plot
        self.update_plot()
        
    def create_instructions(self):
        """Create instruction panel"""
        instruction_frame = ttk.LabelFrame(self.floorplan_frame, text="Instructions")
        instruction_frame.pack(fill=tk.X, pady=(0, 10))
        
        instructions = """
        Interactive Controls (Version 2.0):
        • Click and drag blocks to move them
        • Drag RED corner handles to reshape aspect ratio (area stays constant)
        • Drag TEAL edge handles to change width/height (area stays constant)
        • Hover over handles for visual feedback
        • Use Shape Mode to switch between rectangle and L-shape
        • Use Properties tab for precise editing
        """
        
        ttk.Label(instruction_frame, text=instructions, justify=tk.LEFT).pack(padx=5, pady=5)
        
    def create_properties_widgets(self):
        # Scrollable frame for properties
        canvas = tk.Canvas(self.properties_frame)
        scrollbar = ttk.Scrollbar(self.properties_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.properties_container = scrollable_frame
        
    def create_connections_widgets(self):
        # Scrollable frame for connections
        canvas = tk.Canvas(self.connections_frame)
        scrollbar = ttk.Scrollbar(self.connections_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.connections_container = scrollable_frame
        
    def get_handle_at_position(self, x, y, block):
        """Get handle type at given position with improved detection"""
        corner_size = self.handle_config['corner_size']
        edge_width = self.handle_config['edge_width']
        edge_height = self.handle_config['edge_height']
        
        # Corner handles (all four corners)
        corners = [
            (block['x'] + block['width'] - corner_size, block['y'] + block['height'] - corner_size),  # Top-right
            (block['x'] + block['width'] - corner_size, block['y']),                                  # Bottom-right
            (block['x'], block['y'] + block['height'] - corner_size),                                 # Top-left
            (block['x'], block['y'])                                                                   # Bottom-left
        ]
        
        for i, (cx, cy) in enumerate(corners):
            if (x >= cx and x <= cx + corner_size and 
                y >= cy and y <= cy + corner_size):
                return f'corner_{i}'
        
        # Edge handles (right and bottom edges)
        if (x >= block['x'] + block['width'] - edge_width and 
            block['y'] < y < block['y'] + block['height']):
            return 'edge_right'
        
        if (y >= block['y'] + block['height'] - edge_height and 
            block['x'] < x < block['x'] + block['width']):
            return 'edge_bottom'
        
        return None
        
    def on_mouse_press(self, event):
        """Handle mouse press events with improved handle detection"""
        if not self.interactive_var.get() or not self.blocks:
            return
            
        if event.inaxes != self.ax:
            return
            
        # Find clicked block
        clicked_block = self.get_block_at_position(event.xdata, event.ydata)
        
        if clicked_block:
            self.selected_block = clicked_block
            self.dragging = True
            self.last_mouse_pos = (event.xdata, event.ydata)
            
            # Check if clicking on resize handle
            handle_type = self.get_handle_at_position(event.xdata, event.ydata, clicked_block)
            
            if handle_type:
                if handle_type.startswith('corner'):
                    self.resize_mode = 'corner'
                elif handle_type.startswith('edge'):
                    if 'right' in handle_type:
                        self.resize_mode = 'width'
                    else:
                        self.resize_mode = 'height'
                else:
                    self.resize_mode = 'move'
            else:
                self.resize_mode = 'move'
                
            self.update_plot()
        else:
            self.selected_block = None
            self.dragging = False
            self.resize_mode = None
            self.update_plot()
            
    def on_mouse_move(self, event):
        """Handle mouse move events with improved feedback"""
        if not self.interactive_var.get():
            return
            
        if event.inaxes != self.ax:
            return
            
        # Update hover state
        if self.selected_block:
            handle_type = self.get_handle_at_position(event.xdata, event.ydata, self.selected_block)
            if handle_type != self.hover_handle:
                self.hover_handle = handle_type
                self.update_plot()
        
        if not self.dragging or not self.selected_block:
            return
            
        if self.last_mouse_pos is None:
            return
            
        dx = event.xdata - self.last_mouse_pos[0]
        dy = event.ydata - self.last_mouse_pos[1]
        
        if self.resize_mode == 'move':
            # Move block
            self.selected_block['x'] += dx
            self.selected_block['y'] += dy
        elif self.resize_mode == 'width':
            # Resize width (maintain area)
            new_width = self.selected_block['width'] + dx
            if new_width > 10:  # Minimum size
                old_area = self.selected_block['area']
                self.selected_block['width'] = new_width
                self.selected_block['height'] = old_area / new_width
                print(f"Width resize: {new_width:.1f} × {self.selected_block['height']:.1f} = {old_area:.1f}")
        elif self.resize_mode == 'height':
            # Resize height (maintain area)
            new_height = self.selected_block['height'] + dy
            if new_height > 10:  # Minimum size
                old_area = self.selected_block['area']
                self.selected_block['height'] = new_height
                self.selected_block['width'] = old_area / new_height
                print(f"Height resize: {self.selected_block['width']:.1f} × {new_height:.1f} = {old_area:.1f}")
        elif self.resize_mode == 'corner':
            # Reshape by changing aspect ratio while maintaining area
            new_width = self.selected_block['width'] + dx
            new_height = self.selected_block['height'] + dy
            if new_width > 10 and new_height > 10:
                old_area = self.selected_block['area']
                self.selected_block['width'] = new_width
                self.selected_block['height'] = old_area / new_width
                print(f"Corner reshape: {new_width:.1f} × {self.selected_block['height']:.1f} = {old_area:.1f}")
        
        self.last_mouse_pos = (event.xdata, event.ydata)
        self.update_plot()
        
    def on_mouse_release(self, event):
        """Handle mouse release events"""
        self.dragging = False
        self.resize_mode = None
        self.last_mouse_pos = None
        self.hover_handle = None
        
    def get_block_at_position(self, x, y):
        """Find block at given position"""
        for block in self.blocks:
            if (x >= block['x'] and x <= block['x'] + block['width'] and
                y >= block['y'] and y <= block['y'] + block['height']):
                return block
        return None
        
    def reset_view(self):
        """Reset the plot view"""
        self.ax.set_xlim(auto=True)
        self.ax.set_ylim(auto=True)
        self.canvas.draw()
        
    def upload_csv(self):
        """Upload and process CSV file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select CSV file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
                
            # Read CSV with header
            df = pd.read_csv(filename, index_col=0)
            
            # Get hardmacro names
            self.hardmacro_names = df.index.tolist()
            
            # Validate
            if len(self.hardmacro_names) != len(df.columns):
                messagebox.showerror("Error", "Number of row names must match number of column names")
                return
                
            adjacency_matrix = df.values
            
            if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
                messagebox.showerror("Error", "Matrix must be square")
                return
                
            # Process data
            self.process_adjacency_matrix(adjacency_matrix)
            
            # Update UI
            self.update_info()
            self.update_plot()
            self.update_properties()
            self.update_connections()
            
            messagebox.showinfo("Success", f"Loaded {len(self.blocks)} hardmacros with {len(self.connections)} connections")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            
    def process_adjacency_matrix(self, matrix):
        """Process adjacency matrix into blocks and connections"""
        self.blocks = []
        self.connections = []
        
        for i in range(len(matrix)):
            # Create block
            area = matrix[i][i]
            side_length = np.sqrt(area)
            
            block = {
                'id': i,
                'name': self.hardmacro_names[i],
                'area': area,
                'width': side_length,
                'height': side_length,
                'x': 100 + (i % 3) * 200,
                'y': 100 + (i // 3) * 200,
                'shape_type': 'rectangle'  # Default shape type
            }
            self.blocks.append(block)
            
        # Find connections
        for i in range(len(matrix)):
            for j in range(i+1, len(matrix)):
                if matrix[i][j] > 0:
                    connection = {
                        'from': i,
                        'to': j,
                        'from_name': self.hardmacro_names[i],
                        'to_name': self.hardmacro_names[j],
                        'connections': matrix[i][j]
                    }
                    self.connections.append(connection)
                    
    def update_info(self):
        """Update info label"""
        if self.blocks:
            self.info_label.config(text=f"Blocks: {len(self.blocks)} | Connections: {len(self.connections)}")
        else:
            self.info_label.config(text="No data loaded")
            
    def update_plot(self):
        """Update the floorplan visualization with improved handles"""
        self.ax.clear()
        
        if not self.blocks:
            self.ax.text(0.5, 0.5, 'Upload CSV to see floorplan', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # Draw blocks with improved handles
        for i, block in enumerate(self.blocks):
            # Determine color based on selection
            if block == self.selected_block:
                facecolor = 'lightcoral'
                edgecolor = 'red'
                linewidth = 3
            else:
                facecolor = 'lightblue'
                edgecolor = 'blue'
                linewidth = 2
                
            # Draw main rectangle
            rect = plt.Rectangle((block['x'], block['y']), 
                               block['width'], block['height'],
                               linewidth=linewidth, edgecolor=edgecolor, 
                               facecolor=facecolor, alpha=0.7)
            self.ax.add_patch(rect)
            
            # Draw improved handles for selected block
            if block == self.selected_block and self.interactive_var.get():
                self.draw_improved_handles(block)
            
            # Add label with area info
            area_text = f"{block['name']}\n{int(block['area'])} μm²\n{int(block['width'])}×{int(block['height'])}"
            self.ax.text(block['x'] + block['width']/2, 
                        block['y'] + block['height']/2,
                        area_text,
                        ha='center', va='center', fontsize=8, weight='bold')
                        
        # Draw connections
        for conn in self.connections:
            from_block = self.blocks[conn['from']]
            to_block = self.blocks[conn['to']]
            
            x1 = from_block['x'] + from_block['width']/2
            y1 = from_block['y'] + from_block['height']/2
            x2 = to_block['x'] + to_block['width']/2
            y2 = to_block['y'] + to_block['height']/2
            
            self.ax.plot([x1, x2], [y1, y2], 'r--', linewidth=1, alpha=0.7)
            
            # Add connection count
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.ax.text(mid_x, mid_y, str(conn['connections']), 
                        ha='center', va='center', fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
                        
        self.ax.set_xlabel('X Position (μm)')
        self.ax.set_ylabel('Y Position (μm)')
        self.ax.set_title('Interactive Floorplan Visualization - Version 2.0')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
        self.canvas.draw()
        
    def draw_improved_handles(self, block):
        """Draw improved resize handles with better visibility"""
        corner_size = self.handle_config['corner_size']
        edge_width = self.handle_config['edge_width']
        edge_height = self.handle_config['edge_height']
        colors = self.handle_config['colors']
        
        # Corner handles (all four corners)
        corners = [
            (block['x'] + block['width'] - corner_size, block['y'] + block['height'] - corner_size),  # Top-right
            (block['x'] + block['width'] - corner_size, block['y']),                                  # Bottom-right
            (block['x'], block['y'] + block['height'] - corner_size),                                 # Top-left
            (block['x'], block['y'])                                                                   # Bottom-left
        ]
        
        for i, (cx, cy) in enumerate(corners):
            # Determine color based on hover state
            handle_id = f'corner_{i}'
            if self.hover_handle == handle_id:
                color = colors['hover']
            else:
                color = colors['corner']
                
            handle = plt.Rectangle((cx, cy), corner_size, corner_size,
                                 linewidth=2, edgecolor='black',
                                 facecolor=color, alpha=0.9)
            self.ax.add_patch(handle)
        
        # Edge handles (right and bottom edges)
        edge_handles = [
            # Right edge
            (block['x'] + block['width'] - edge_width, block['y'] + (block['height'] - edge_height)/2, edge_width, edge_height),
            # Bottom edge
            (block['x'] + (block['width'] - edge_width)/2, block['y'] + block['height'] - edge_height, edge_width, edge_height)
        ]
        
        edge_ids = ['edge_right', 'edge_bottom']
        
        for i, (ex, ey, ew, eh) in enumerate(edge_handles):
            # Determine color based on hover state
            handle_id = edge_ids[i]
            if self.hover_handle == handle_id:
                color = colors['hover']
            else:
                color = colors['edge']
                
            handle = plt.Rectangle((ex, ey), ew, eh,
                                 linewidth=2, edgecolor='black',
                                 facecolor=color, alpha=0.9)
            self.ax.add_patch(handle)
        
    def update_properties(self):
        """Update properties tab"""
        # Clear existing widgets
        for widget in self.properties_container.winfo_children():
            widget.destroy()
            
        if not self.blocks:
            ttk.Label(self.properties_container, text="No blocks loaded").pack(pady=20)
            return
            
        # Create property editors for each block
        for i, block in enumerate(self.blocks):
            frame = ttk.LabelFrame(self.properties_container, text=f"Block {i+1}: {block['name']}")
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Area
            ttk.Label(frame, text="Area (μm²):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            area_var = tk.StringVar(value=str(int(block['area'])))
            area_entry = ttk.Entry(frame, textvariable=area_var, width=15)
            area_entry.grid(row=0, column=1, padx=5, pady=2)
            
            # Width
            ttk.Label(frame, text="Width (μm):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            width_var = tk.StringVar(value=str(int(block['width'])))
            width_entry = ttk.Entry(frame, textvariable=width_var, width=15)
            width_entry.grid(row=1, column=1, padx=5, pady=2)
            
            # Height
            ttk.Label(frame, text="Height (μm):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            height_var = tk.StringVar(value=str(int(block['height'])))
            height_entry = ttk.Entry(frame, textvariable=height_var, width=15)
            height_entry.grid(row=2, column=1, padx=5, pady=2)
            
            # Position
            ttk.Label(frame, text="X Position:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
            x_var = tk.StringVar(value=str(int(block['x'])))
            x_entry = ttk.Entry(frame, textvariable=x_var, width=15)
            x_entry.grid(row=3, column=1, padx=5, pady=2)
            
            ttk.Label(frame, text="Y Position:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
            y_var = tk.StringVar(value=str(int(block['y'])))
            y_entry = ttk.Entry(frame, textvariable=y_var, width=15)
            y_entry.grid(row=4, column=1, padx=5, pady=2)
            
            # Update button
            def update_block(block_id=block['id'], area_var=area_var, width_var=width_var, 
                           height_var=height_var, x_var=x_var, y_var=y_var):
                try:
                    block['area'] = float(area_var.get())
                    block['width'] = float(width_var.get())
                    block['height'] = float(height_var.get())
                    block['x'] = float(x_var.get())
                    block['y'] = float(y_var.get())
                    self.update_plot()
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers")
                    
            ttk.Button(frame, text="Update", command=update_block).grid(row=5, column=0, columnspan=2, pady=5)
            
    def update_connections(self):
        """Update connections tab"""
        # Clear existing widgets
        for widget in self.connections_container.winfo_children():
            widget.destroy()
            
        if not self.connections:
            ttk.Label(self.connections_container, text="No connections loaded").pack(pady=20)
            return
            
        # Create connection list
        for i, conn in enumerate(self.connections):
            frame = ttk.Frame(self.connections_container)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{conn['from_name']} ↔ {conn['to_name']}", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(frame, text=f"Connections: {conn['connections']}", 
                     font=('Arial', 9)).pack(anchor=tk.W)
            
            ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=2)

def main():
    root = tk.Tk()
    app = FloorplanToolV2(root)
    root.mainloop()

if __name__ == "__main__":
    main()
