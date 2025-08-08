#!/usr/bin/env python3
"""
Floorplanning Tool - Startup Script
Simple script to run the desktop application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from floorplan_desktop import main
    print("Starting Floorplanning Tool...")
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("Please install dependencies: pip install -r requirements_desktop.txt")
except Exception as e:
    print(f"Error starting application: {e}")
