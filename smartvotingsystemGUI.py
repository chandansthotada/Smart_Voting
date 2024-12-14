import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib
import datetime

class SmartVotingSystemGUI:
    def __init__(self, master):
        try:
            self.master = master
            master.title("Smart Voting System")
            master.geometry("800x600")
            master.configure(bg='#f0f0f0')

            # Setup database
            self.conn = sqlite3.connect('voting_system.db')
            self.cursor = self.conn.cursor()
            self.create_tables()

            # Setup theme and style
            self.style = ttk.Style()
            self.style.theme_use('clam')
            self.style.configure('TButton', 
                                 background='#4CAF50', 
                                 foreground='white', 
                                 font=('Arial', 12, 'bold'), 
                                 padding=10)
            self.style.map('TButton', background=[('active', '#45a049')])
            self.style.configure('TLabel', font=('Arial', 12), background='#f0f0f0')
            self.style.configure('TEntry', padding=5)
            self.style.configure('TFrame', padding=20)

            # Create main interface
            self.create_main_interface()

        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            master.quit()

    def __del__(self):
        # Ensure database connection is closed
        if hasattr(self, 'conn'):
            self.conn.close()

    # [Rest of the methods remain the same as in the original code]

def main():
    try:
        root = tk.Tk()
        app = SmartVotingSystemGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()