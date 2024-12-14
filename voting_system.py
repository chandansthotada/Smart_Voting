import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import hashlib
import datetime
import re

class SmartVotingSystemGUI:
    def __init__(self, master):  # Corrected constructor method
        self.master = master
        master.title("Smart Voting System")
        master.geometry("800x600")
        master.configure(bg='#f0f0f0')

        # Setup database
        self.conn = sqlite3.connect('voting_system.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Styling
        self.style = ttk.Style()
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12))

        # Create main interface
        self.create_main_interface()

    def create_tables(self):
        """Create database tables for voter registration"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            voter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            aadhaar_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            address TEXT,
            fingerprint_hash TEXT,
            is_registered BOOLEAN DEFAULT 0,
            registration_date DATETIME
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS voting_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER,
            election_name TEXT,
            voted_candidate TEXT,
            voting_timestamp DATETIME,
            FOREIGN KEY(voter_id) REFERENCES voters(voter_id)
        )
        ''')
        self.conn.commit()

    def create_main_interface(self):
        """Create the main interface with registration and login options"""
        # Clear existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = tk.Frame(self.master, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Title
        title_label = ttk.Label(main_frame, text="Smart Voting System", 
                                font=('Arial', 20, 'bold'), 
                                background='#f0f0f0')
        title_label.pack(pady=20)

        # Button Frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(expand=True)

        # New Voter Registration Button
        register_btn = ttk.Button(button_frame, text="New Voter Registration", 
                                  command=self.open_registration_window)
        register_btn.pack(pady=10, ipadx=20, ipady=10)

        # Existing Voter Login Button
        login_btn = ttk.Button(button_frame, text="Existing Voter Login", 
                               command=self.open_login_window)
        login_btn.pack(pady=10, ipadx=20, ipady=10)

        # Exit Button
        exit_btn = ttk.Button(button_frame, text="Exit", 
                              command=self.master.quit)
        exit_btn.pack(pady=10, ipadx=20, ipady=10)

    def open_registration_window(self):
        """Open registration window for new voters"""
        reg_window = tk.Toplevel(self.master)
        reg_window.title("New Voter Registration")
        reg_window.geometry("600x500")
        reg_window.configure(bg='#f0f0f0')

        # Registration Form
        tk.Label(reg_window, text="Voter Registration", 
                 font=('Arial', 16, 'bold'), 
                 bg='#f0f0f0').pack(pady=10)

        # Input Fields
        fields = [
            ("Aadhaar Number", "aadhaar"),
            ("Full Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Address", "address"),
            ("Password", "Password")
        ]

        entries = {}
        for label, key in fields:
            frame = tk.Frame(reg_window, bg='#f0f0f0')
            frame.pack(fill='x', padx=50, pady=5)
            
            tk.Label(frame, text=label, width=15, 
                     font=('Arial', 10), 
                     bg='#f0f0f0').pack(side='left')
            
            if key == "gender":
                # Dropdown for gender
                gender_var = tk.StringVar()
                entries[key] = ttk.Combobox(frame, textvariable=gender_var, 
                                            values=["Male", "Female", "Other"])
                entries[key].pack(side='left', expand=True, fill='x')
            elif key == "age":
                # Numeric entry for age
                entries[key] = tk.Entry(frame, validate='key')
                entries[key]['validatecommand'] = (entries[key].register(self.validate_numeric), '%P')
                entries[key].pack(side='left', expand=True, fill='x')
            else:
                # Standard text entry
                entries[key] = tk.Entry(frame)
                entries[key].pack(side='left', expand=True, fill='x')

        # Registration Button
        def submit_registration():
            try:
                # Validate and register voter
                self.register_voter(
                    aadhaar_number=entries['aadhaar'].get(),
                    name=entries['name'].get(),
                    age=int(entries['age'].get()),
                    gender=entries['gender'].get(),
                    address=entries['address'].get(),
                    fingerprint_data=entries['Password'].get()
                )
                messagebox.showinfo("Success", "Voter Registered Successfully!")
                reg_window.destroy()
            except ValueError as e:
                messagebox.showerror("Registration Error", str(e))

        register_btn = ttk.Button(reg_window, text="Register", command=submit_registration)
        register_btn.pack(pady=10)

    def open_login_window(self):
        """Open login window for existing voters"""
        login_window = tk.Toplevel(self.master)
        login_window.title("Voter Login")
        login_window.geometry("500x300")
        login_window.configure(bg='#f0f0f0')

        # Login Frame
        frame = tk.Frame(login_window, bg='#f0f0f0')
        frame.pack(expand=True, padx=50, pady=20)

        # Aadhaar Number
        tk.Label(frame, text="Aadhaar Number", 
                 font=('Arial', 12), 
                 bg='#f0f0f0').pack(pady=5)
        aadhaar_entry = tk.Entry(frame, font=('Arial', 12))
        aadhaar_entry.pack(pady=5, fill='x')

        # Fingerprint
        tk.Label(frame, text="Password", 
                 font=('Arial', 12), 
                 bg='#f0f0f0').pack(pady=5)
        fingerprint_entry = tk.Entry(frame, font=('Arial', 12), show='*')
        fingerprint_entry.pack(pady=5, fill='x')

        def perform_login():
            try:
                # Attempt login
                voter_id = self.voter_login(
                    aadhaar_number=aadhaar_entry.get(),
                    fingerprint_data=fingerprint_entry.get()
                )
                # Open voting interface if login successful
                self.open_voting_interface(voter_id)
                login_window.destroy()
            except ValueError as e:
                messagebox.showerror("Login Error", str(e))

        # Login Button
        login_btn = ttk.Button(frame, text="Login", command=perform_login)
        login_btn.pack(pady=10)

    def open_voting_interface(self, voter_id):
        """Open voting interface for authenticated voter"""
        voting_window = tk.Toplevel(self.master)
        voting_window.title("Cast Your Vote")
        voting_window.geometry("600x400")
        voting_window.configure(bg='#f0f0f0')

        # Candidates
        candidates = ["Candidate A", "Candidate B", "Candidate C", "Candidate D"]

        # Candidate Selection
        tk.Label(voting_window, text="Select Your Candidate", 
                 font=('Arial', 16, 'bold'), 
                 bg='#f0f0f0').pack(pady=20)

        candidate_var = tk.StringVar()
        for candidate in candidates:
            rb = tk.Radiobutton(voting_window, text=candidate, 
                                variable=candidate_var, 
                                value=candidate,
                                font=('Arial', 12),
                                bg='#f0f0f0')
            rb.pack(pady=5)

        def submit_vote():
            if not candidate_var.get():
                messagebox.showwarning("Vote Error", "Please select a candidate")
                return
            
            try:
                self.cast_vote(voter_id, "General Election 2024", candidate_var.get())
                messagebox.showinfo("Success", "Vote Casted Successfully!")
                voting_window.destroy()
            except ValueError as e:
                messagebox.showerror("Voting Error", str(e))

        # Submit Vote Button
        submit_btn = ttk.Button(voting_window, text="Submit Vote", command=submit_vote)
        submit_btn.pack(pady=20)

    def validate_numeric(self, new_value):
        """Validate numeric input"""
        return new_value.isdigit() or new_value == ""

    def hash_fingerprint(self, fingerprint_data):
        """Generate secure hash of fingerprint data"""
        return hashlib.sha256(str(fingerprint_data).encode()).hexdigest()

    def validate_aadhaar(self, aadhaar_number):
        """Validate Aadhaar number format"""
        return len(aadhaar_number) == 12 and aadhaar_number.isdigit()

    def register_voter(self, aadhaar_number, name, age, gender, address, fingerprint_data):
        """Register a new voter"""
        # Validate inputs
        if not self.validate_aadhaar(aadhaar_number):
            raise ValueError("Invalid Aadhaar Number")
        if age < 18:
            raise ValueError("Voter must be 18 or older")
        if not name or not gender or not address or not fingerprint_data:
            raise ValueError("All fields are required")

        # Hash fingerprint
        fingerprint_hash = self.hash_fingerprint(fingerprint_data)
        
        try:
            # Insert voter details
            self.cursor.execute('''
            INSERT INTO voters 
            (aadhaar_number, name, age, gender, address, fingerprint_hash, is_registered, registration_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                aadhaar_number, 
                name, 
                age, 
                gender, 
                address, 
                fingerprint_hash, 
                True, 
                datetime.datetime.now()
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError("Voter already registered")

    def voter_login(self, aadhaar_number, fingerprint_data):
        """Authenticate voter using Aadhaar and Fingerprint"""
        # Hash the input fingerprint
        input_fingerprint_hash = self.hash_fingerprint(fingerprint_data)
        
        # Verify voter
        self.cursor.execute('''
        SELECT voter_id, fingerprint_hash 
        FROM voters 
        WHERE aadhaar_number = ? AND is_registered = 1
        ''', (aadhaar_number,))
        
        result = self.cursor.fetchone()
        
        if not result:
            raise ValueError("Voter not found or not registered")
        
        # Compare fingerprint hashes
        if result[1] != input_fingerprint_hash:
            raise ValueError("Fingerprint authentication failed")
        
        return result[0]  # Return voter ID

    def cast_vote(self, voter_id, election_name, candidate):
        """Cast a vote for a specific election"""
        # Check if voter has already voted in this election
        self.cursor.execute('''
        SELECT * FROM voting_records 
        WHERE voter_id = ? AND election_name = ?
        ''', (voter_id, election_name))
        
        if self.cursor.fetchone():
            raise ValueError("Voter has already voted in this election")
        
        # Record the vote
        self.cursor.execute('''
        INSERT INTO voting_records 
        (voter_id, election_name, voted_candidate, voting_timestamp) 
        VALUES (?, ?, ?, ?)
        ''', (voter_id, election_name, candidate, datetime.datetime.now()))
        
        self.conn.commit()
        return True

    def __del__(self):  # Corrected destructor method
        """Close database connection"""
        self.conn.close()

def main():
    root = tk.Tk()
    try:
        app = SmartVotingSystemGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":  # Corrected name check
    main()