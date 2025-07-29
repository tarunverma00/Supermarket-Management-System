"""
UI utility functions
"""
import tkinter as tk
from tkinter import ttk

class UIUtils:
    @staticmethod
    def show_text_dialog(parent, title, text):
        """Show text in a dialog window"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.transient(parent)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert('1.0', text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    @staticmethod
    def show_log_viewer(parent):
        """Show log viewer window"""
        try:
            log_content = ""
            try:
                with open('logs/audit_log.txt', 'r') as f:
                    log_content = f.read()
            except FileNotFoundError:
                log_content = "No log file found. Logs will appear here once the system is used."
            
            UIUtils.show_text_dialog(parent, "System Logs", log_content)
        except Exception as e:
            UIUtils.show_text_dialog(parent, "Error", f"Failed to load logs: {str(e)}")
    
    @staticmethod
    def center_window(window, width, height):
        """Center a window on the screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def validate_number_input(value):
        """Validate numeric input"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_integer_input(value):
        """Validate integer input"""
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
