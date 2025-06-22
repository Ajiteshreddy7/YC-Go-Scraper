#!/usr/bin/env python3
"""
Main entry point for the Job Dashboard
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the dashboard
from dashboard.dashboard_generator import main

if __name__ == '__main__':
    main() 