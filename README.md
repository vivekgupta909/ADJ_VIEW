# Floorplanning Tool - Desktop Application

An interactive desktop application for VLSI floorplanning that allows designers to visualize and manipulate hardmacros based on adjacency matrices.

## Features

- **Interactive Desktop GUI**: Native tkinter application with immediate visual feedback
- **CSV Import**: Upload adjacency matrices from CSV files with hardmacro names
- **Drag & Drop**: Move hardmacros by clicking and dragging
- **Interactive Reshaping**: Resize blocks while maintaining area
- **Connection Visualization**: See connections between blocks with connection counts
- **Real-time Updates**: Instant visual feedback for all changes
- **Properties Editor**: Precise editing of block dimensions and positions

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements_desktop.txt
   ```

2. **Run the Application**:
   ```bash
   python floorplan_desktop.py
   ```
   
   Or use the startup script:
   ```bash
   python run.py
   ```

## Usage

### CSV File Format

The tool expects a square adjacency matrix in CSV format with hardmacro names in the header:
- **First row/column**: Hardmacro names
- **Diagonal elements**: Represent the area of each hardmacro in μm²
- **Off-diagonal elements**: Represent the number of connections between blocks
- **Zero values**: Indicate no connections between blocks

Example CSV format:
```csv
,CPU_Core,Memory_Controller,GPU_Unit,IO_Bridge,Network_Interface,Power_Management
CPU_Core,1000000,50,30,20,0,0
Memory_Controller,50,800000,40,0,25,0
GPU_Unit,30,40,1200000,35,0,15
IO_Bridge,20,0,35,600000,0,0
Network_Interface,0,25,0,0,400000,10
Power_Management,0,0,15,0,10,300000
```

### Using the Tool

1. **Upload CSV**: Click "Upload CSV" and select your adjacency matrix file
2. **View Floorplan**: Hardmacros appear as rectangles with their areas and dimensions displayed
3. **Select Blocks**: Click on any block to select it (turns red with yellow handles)
4. **Move Blocks**: Drag selected blocks to reposition them
5. **Reshape Blocks**: 
   - Drag yellow edge handles to change width/height (area stays constant)
   - Drag yellow corner handles to reshape aspect ratio (area stays constant)
6. **Edit Properties**: Use the Properties tab for precise editing
7. **View Connections**: See all connections in the Connections tab

### Interactive Controls

- **Click and drag blocks** to move them
- **Drag yellow edge handles** to change width/height (area stays constant)
- **Drag yellow corner handles** to reshape aspect ratio (area stays constant)
- **Area is automatically maintained** during all reshaping
- **Use Properties tab** for precise editing

### Block Properties

When blocks are loaded, you can modify:
- **Area**: Total area in μm² (automatically adjusts dimensions)
- **Width**: Block width in μm
- **Height**: Block height in μm
- **Position**: X and Y coordinates

## Technical Details

### Architecture
- **GUI Framework**: tkinter with matplotlib integration
- **Data Processing**: NumPy and Pandas for matrix operations
- **Visualization**: Matplotlib for interactive plotting
- **File Handling**: Native file dialogs for CSV import

### File Structure
```
floorplanning-tool/
├── floorplan_desktop.py      # Main desktop application
├── requirements_desktop.txt  # Python dependencies
├── test_desktop.py          # Test script
├── sample_adjacency_matrix.csv  # Example data
└── README.md                # This file
```

## Sample Data

The repository includes `sample_adjacency_matrix.csv` with example data for testing:
- 6 hardmacros with varying areas
- Multiple connections between blocks
- Realistic VLSI design scenario

## Troubleshooting

### Common Issues

1. **Matplotlib backend**: Ensure tkinter is available
2. **CSV format error**: Ensure your CSV is square and contains only numbers
3. **Interactive mode not working**: Check that "Interactive Mode" checkbox is enabled

### Dependencies

- Python 3.8+
- tkinter (usually included with Python)
- matplotlib
- pandas
- numpy

## Future Enhancements

- Export functionality (PNG, SVG, JSON)
- Automatic placement algorithms
- Multiple project support
- Advanced optimization features
- Integration with EDA tools

## License

This project is open source and available under the MIT License.
