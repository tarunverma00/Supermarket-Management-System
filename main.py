"""
Main entry point for Supermarket Management System
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime

# Now import your modules
from config import *
from database import DatabaseManager
from ui.main_window import MainWindow

def setup_logging():
    """Setup logging configuration"""
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
    
    log_filename = os.path.join(LOG_DIRECTORY, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO if DEBUG_MODE else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logging.info("Starting Supermarket Management System")
        
        # Initialize database
        db_manager = DatabaseManager()
        
        # Create main window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start application
        root.mainloop()
        
        # Cleanup
        db_manager.close_connection()
        logging.info("Application closed successfully")
        
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        if 'root' in locals():
            messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
