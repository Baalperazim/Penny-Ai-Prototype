import tkinter as tk
from tkinter import ttk, messagebox, font
from auth_manager import AuthManager
from penny import BudgetManager
from sms_reader import SMSReader
import json
import os
import sys

class DashboardWindow:
    """Main application dashboard showing budget status and transactions"""
    def __init__(self, phone):
        self.phone = phone
        self.root = tk.Tk()
        self.root.title(f"Budget Tracker - {phone}")
        self.budget_manager = BudgetManager()
        self.sms_reader = SMSReader()

        # Window configuration - centered on screen
        window_width = 900
        window_height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.configure(bg='#f8f9fa')  # Light background

        # UI styling configuration
        self.configure_styles()
        self.create_widgets()
        self.process_sms()  # Automatically process SMS on startup
        self.update_dashboard()

        # Check for budget breaches
        if self.budget_manager.is_budget_breached():
            messagebox.showwarning("Budget Alert", "Budget limit exceeded!")

        self.root.mainloop()

    def configure_styles(self):
        """Setup custom styling for widgets"""
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Base theme

        # Color scheme
        self.bg_color = '#f8f9fa'
        self.card_color = '#ffffff'
        self.primary_color = '#1877f2'
        self.success_color = '#42b72a'
        self.danger_color = '#dc3545'
        self.text_color = '#1c1e21'

        # Custom button style
        self.style.configure('Accent.TButton',
                            background=self.primary_color,
                            foreground='white',
                            font=('Helvetica', 10, 'bold'),
                            padding=5)

        # Custom treeview style
        self.style.configure('Custom.Treeview',
                            background=self.card_color,
                            fieldbackground=self.card_color,
                            foreground=self.text_color,
                            rowheight=25)
        self.style.configure('Custom.Treeview.Heading',
                            font=('Helvetica', 10, 'bold'),
                            background=self.primary_color,
                            foreground='white')

    def create_widgets(self):
        """Build all dashboard UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with welcome message and action buttons
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Welcome label
        tk.Label(header_frame,
                text=f"Welcome, {self.phone}",
                font=('Helvetica', 16, 'bold'),
                bg=self.bg_color,
                fg=self.text_color).pack(side=tk.LEFT)

        # Action buttons frame
        action_frame = tk.Frame(header_frame, bg=self.bg_color)
        action_frame.pack(side=tk.RIGHT)

        # Logout button
        logout_btn = ttk.Button(action_frame,
                              text="Logout",
                              style='Accent.TButton',
                              command=self.logout)
        logout_btn.pack(side=tk.LEFT, padx=5)

        # Exit button
        exit_btn = ttk.Button(action_frame,
                            text="Exit",
                            style='Accent.TButton',
                            command=self.exit_app)
        exit_btn.pack(side=tk.LEFT)

        # Left panel - Budget information cards
        left_frame = tk.Frame(main_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        # Budget card
        budget_card = self.create_card(left_frame, "Monthly Budget")
        self.budget_var = tk.StringVar()
        tk.Label(budget_card,
                textvariable=self.budget_var,
                font=('Helvetica', 18, 'bold'),
                bg=self.card_color,
                fg=self.primary_color).pack(anchor='w')

        # Spending card
        spending_card = self.create_card(left_frame, "Current Month Spending")
        self.spending_var = tk.StringVar()
        tk.Label(spending_card,
                textvariable=self.spending_var,
                font=('Helvetica', 18, 'bold'),
                bg=self.card_color,
                fg=self.primary_color).pack(anchor='w')

        # Status card
        status_card = self.create_card(left_frame, "Budget Status")
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(status_card,
                                   textvariable=self.status_var,
                                   font=('Helvetica', 18, 'bold'),
                                   bg=self.card_color)
        self.status_label.pack(anchor='w')

        # Budget setting controls
        budget_set_card = self.create_card(left_frame, "Set New Budget")
        entry_frame = tk.Frame(budget_set_card, bg=self.card_color)
        entry_frame.pack(fill=tk.X)
        self.new_budget_entry = ttk.Entry(entry_frame)
        self.new_budget_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(entry_frame,
                 text="Update",
                 style='Accent.TButton',
                 command=self.update_budget).pack(side=tk.LEFT)

        # Right panel - Transactions
        right_frame = tk.Frame(main_frame, bg=self.bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Transactions card with treeview
        transactions_card = self.create_card(right_frame, "Recent Transactions", True)

        # Transaction treeview setup
        self.transaction_tree = ttk.Treeview(transactions_card,
                                          columns=('date', 'amount', 'type', 'source'),
                                          show='headings',
                                          style='Custom.Treeview')

        # Configure columns
        self.transaction_tree.heading('date', text='Date')
        self.transaction_tree.heading('amount', text='Amount')
        self.transaction_tree.heading('type', text='Type')
        self.transaction_tree.heading('source', text='Source')
        self.transaction_tree.column('date', width=120, anchor='w')
        self.transaction_tree.column('amount', width=120, anchor='e')
        self.transaction_tree.column('type', width=100, anchor='center')
        self.transaction_tree.column('source', width=200, anchor='w')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(transactions_card,
                                orient=tk.VERTICAL,
                                command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transaction_tree.pack(fill=tk.BOTH, expand=True)

        # Process SMS button
        button_frame = tk.Frame(transactions_card, bg=self.card_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame,
                 text="Process New SMS",
                 style='Accent.TButton',
                 command=self.process_sms).pack(fill=tk.X)

    def exit_app(self):
        """Close the application completely"""
        self.root.destroy()
        sys.exit()

    def logout(self):
        """Log out the user and return to login screen"""
        self.root.destroy()  # Close the dashboard
        root = tk.Tk()  # Create new root window
        LoginWindow(root)  # Show login window
        root.mainloop()

    def create_card(self, parent, title, expand=False):
        """Helper to create consistent card containers"""
        card = tk.Frame(parent,
                       bg=self.card_color,
                       bd=0,
                       highlightthickness=0,
                       padx=10,
                       pady=10)
        card.pack(fill=tk.X, pady=(0, 20), ipadx=10, ipady=10, expand=expand)
        tk.Label(card,
                text=title,
                font=('Helvetica', 12),
                bg=self.card_color).pack(anchor='w', pady=(0, 5))
        return card

    def process_sms(self):
        """Process SMS messages and update transactions"""
        try:
            # Read and process SMS data
            transactions = self.sms_reader.read_sms()

            # Add to budget manager
            for tx in transactions:
                self.budget_manager.add_transaction(tx)

            # Save to file
            self.budget_manager.export_transactions()
            messagebox.showinfo("Success", f"Processed {len(transactions)} new transactions")

            # Update display
            self.update_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process SMS: {str(e)}")

    def update_dashboard(self):
        """Refresh all dashboard data displays"""
        # Update budget information
        monthly_budget = self.budget_manager.budgets.get("monthly", 0)
        self.budget_var.set(f"₦{monthly_budget:,.2f}")

        # Update spending information
        current_spending = self.budget_manager.get_monthly_spending()
        self.spending_var.set(f"₦{current_spending:,.2f}")

        # Update status indicator
        if monthly_budget == 0:
            self.status_var.set("No budget set")
            self.status_label.config(fg='gray')
        elif current_spending > monthly_budget:
            overspend = current_spending - monthly_budget
            self.status_var.set(f"OVER BY ₦{overspend:,.2f}")
            self.status_label.config(fg=self.danger_color)
        else:
            remaining = monthly_budget - current_spending
            self.status_var.set(f"₦{remaining:,.2f} remaining")
            self.status_label.config(fg=self.success_color)

        # Refresh transaction list
        self.update_transactions()

    def update_transactions(self):
        """Reload and display transactions from file"""
        # Clear existing entries
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)

        try:
            # Load transactions from JSON file
            with open("transactions.json", "r") as f:
                transactions = json.load(f)

                # Add transactions in reverse chronological order
                for tx in reversed(transactions):
                    amount = f"₦{float(tx['amount']):,.2f}"
                    self.transaction_tree.insert('', 'end', values=(
                        tx['date'],
                        amount,
                        tx['type'].capitalize(),
                        tx['source']
                    ))
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Corrupted transactions file")

    def update_budget(self):
        """Update the monthly budget amount"""
        new_budget = self.new_budget_entry.get()
        try:
            # Validate and update budget
            new_budget = float(new_budget)
            if new_budget < 0:
                raise ValueError("Budget cannot be negative")

            # Confirmation dialog
            if not messagebox.askyesno(
                "Confirm Reset",
                "This will clear all transactions and restart processing.\nAre you sure?",
                icon='warning'
            ):
                return  # User clicked No

            self.budget_manager.update_budget(new_budget)
            self.sms_reader.reset_processed_ids()  # Clear processed SMS records
            self.budget_manager.transactions = []  # Reset transactions
            self.budget_manager.export_transactions()  # Clear transactions file
            messagebox.showinfo("Success", "Budget updated and transactions reset")
            self.update_dashboard()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid budget amount: {str(e)}")

class LoginWindow:
    """Handles user authentication with a modern UI login screen"""
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker - Login")
        self.auth = AuthManager()

        # Window configuration
        window_width = 350
        window_height = 300
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.configure(bg='#f0f2f5')

        self.title_font = font.Font(family='Helvetica', size=16, weight='bold')
        self.label_font = font.Font(family='Helvetica', size=10)

        self.create_widgets()

    def create_widgets(self):
        """Construct all UI elements for the login window"""
        # Main container frame
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # Application title
        title_label = tk.Label(main_frame,
                             text="Welcome back",
                             font=self.title_font,
                             bg='#f0f2f5',
                             fg='#1877f2')
        title_label.pack(pady=(0, 20))

        # Phone number input
        phone_frame = tk.Frame(main_frame, bg='#f0f2f5')
        phone_frame.pack(fill='x', pady=(0, 10))
        tk.Label(phone_frame,
                text="Phone number",
                font=self.label_font,
                bg='#f0f2f5').pack(anchor='w')
        self.phone_entry = ttk.Entry(phone_frame)
        self.phone_entry.pack(fill='x', pady=(5, 0))

        # Password input
        password_frame = tk.Frame(main_frame, bg='#f0f2f5')
        password_frame.pack(fill='x', pady=(0, 20))
        tk.Label(password_frame,
                text="Password",
                font=self.label_font,
                bg='#f0f2f5').pack(anchor='w')
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(fill='x', pady=(5, 0))

        # Button container
        button_frame = tk.Frame(main_frame, bg='#f0f2f5')
        button_frame.pack(fill='x', pady=(10, 0))

        # Login button (blue)
        login_btn = tk.Button(button_frame,
                            text="Login",
                            bg='#1877f2',
                            fg='white',
                            relief='flat',
                            font=('Helvetica', 10, 'bold'),
                            command=self.handle_login)
        login_btn.pack(side='left', expand=True, fill='x', padx=2)

        # Sign Up button (green)
        signup_btn = tk.Button(button_frame,
                              text="Sign Up",
                              bg='#42b72a',
                              fg='white',
                              relief='flat',
                              font=('Helvetica', 10, 'bold'),
                              command=self.handle_register)
        signup_btn.pack(side='left', expand=True, fill='x', padx=2)

        # Exit button (red)
        exit_btn = tk.Button(button_frame,
                           text="Exit",
                           bg='#dc3545',
                           fg='white',
                           relief='flat',
                           font=('Helvetica', 10, 'bold'),
                           command=self.exit_app)
        exit_btn.pack(side='left', expand=True, fill='x', padx=2)

    def exit_app(self):
        """Close the application completely"""
        self.root.destroy()
        sys.exit()

    def handle_login(self):
        """Authenticate user credentials and open dashboard on success"""
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        # Validate input
        if not phone or not password:
            messagebox.showerror("Error", "Please enter both phone and password")
            return

        # Check credentials
        if self.auth.authenticate_user(phone, password):
            self.root.destroy()  # Close login window
            DashboardWindow(phone)  # Open dashboard
        else:
            messagebox.showerror("Error", "Invalid phone or password")

    def handle_register(self):
        """Register new user with phone and password"""
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        # Validate input
        if not phone or not password:
            messagebox.showerror("Error", "Please enter both phone and password")
            return

        # Attempt registration
        success, message = self.auth.register_user(phone, password)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

def main():
    """Application entry point"""
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()