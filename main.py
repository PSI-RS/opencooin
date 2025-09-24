#!/usr/bin/env python3
"""
OpenCooin Trading Platform - Python GUI Version
Created by: [Your Name]
Status: Retired Project (Educational Demo)

A complete cryptocurrency trading platform with GUI interface.
Features account creation, dynamic EUR pricing, and buy/sell functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time

class OpenCooinExchange:
    def __init__(self):
        self.data_file = "opencooin_data.json"
        self.accounts = {}
        self.transactions = []
        self.current_user = None
        self.current_price = 0.0
        self.load_data()
        self.initialize_default_accounts()
        self.update_price()

    def load_data(self):
        """Load accounts and transactions from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.accounts = data.get('accounts', {})
                    self.transactions = data.get('transactions', [])
            except Exception as e:
                print(f"Error loading data: {e}")

    def save_data(self):
        """Save accounts and transactions to file"""
        try:
            data = {
                'accounts': self.accounts,
                'transactions': self.transactions
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def initialize_default_accounts(self):
        """Initialize default pigeon accounts if they don't exist"""
        default_accounts = {
            'homer_pigeon': {'coo_balance': 500.0, 'eur_balance': 1000.0},
            'racing_pete': {'coo_balance': 750.0, 'eur_balance': 500.0},
            'city_pigeon_bob': {'coo_balance': 300.0, 'eur_balance': 2000.0},
            'carrier_clara': {'coo_balance': 1000.0, 'eur_balance': 800.0},
            'pigeon_mike': {'coo_balance': 250.0, 'eur_balance': 1500.0}
        }

        for name, balance in default_accounts.items():
            if name not in self.accounts:
                self.accounts[name] = balance

        self.save_data()

    def calculate_monthly_price(self):
        """Calculate current OpenCooin price in EUR based on month/year"""
        now = datetime.now()
        month = now.month
        year = now.year

        # Base price starts at €0.25, varies by month with realistic volatility
        base_price = 0.25
        month_multiplier = 1 + (month * 0.1) + (math.sin(month) * 0.2)
        year_multiplier = 1 + ((year - 2024) * 0.5)
        
        # Add some realistic market volatility
        volatility = 1 + ((math.sin(month * 2.5) + math.cos(year)) * 0.3)
        
        price = base_price * month_multiplier * year_multiplier * volatility
        return round(price, 4)

    def get_price_change(self):
        """Calculate monthly price change percentage"""
        last_month = datetime.now().replace(day=1) - timedelta(days=1)
        
        # Calculate price for last month
        month = last_month.month
        year = last_month.year
        base_price = 0.25
        month_multiplier = 1 + (month * 0.1) + (math.sin(month) * 0.2)
        year_multiplier = 1 + ((year - 2024) * 0.5)
        volatility = 1 + ((math.sin(month * 2.5) + math.cos(year)) * 0.3)
        last_price = base_price * month_multiplier * year_multiplier * volatility
        
        change = ((self.current_price - last_price) / last_price) * 100
        return round(change, 2)

    def get_next_update_date(self):
        """Get next month's first day for price update"""
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        return next_month.strftime("%B %d, %Y")

    def update_price(self):
        """Update current price"""
        self.current_price = self.calculate_monthly_price()

    def create_account(self, name: str) -> bool:
        """Create a new pigeon account"""
        if not name or not name.strip():
            return False

        account_name = name.strip().lower().replace(' ', '_')
        
        if account_name in self.accounts:
            return False

        self.accounts[account_name] = {
            'coo_balance': 0.0,
            'eur_balance': 100.0  # Starting bonus
        }

        self.save_data()
        return True

    def login(self, account_name: str):
        """Login to an account"""
        if account_name in self.accounts:
            self.current_user = account_name
            return True
        return False

    def get_account_balance(self, account_name: str) -> Optional[Dict]:
        """Get account balance"""
        return self.accounts.get(account_name)

    def buy_coo(self, eur_amount: float) -> bool:
        """Buy COO with EUR"""
        if not self.current_user:
            return False

        account = self.accounts[self.current_user]
        
        if account['eur_balance'] < eur_amount:
            return False

        coo_amount = eur_amount / self.current_price
        
        account['eur_balance'] -= eur_amount
        account['coo_balance'] += coo_amount

        # Add transaction record
        self.add_transaction('buy', coo_amount, eur_amount)
        self.save_data()
        return True

    def sell_coo(self, coo_amount: float) -> bool:
        """Sell COO for EUR"""
        if not self.current_user:
            return False

        account = self.accounts[self.current_user]
        
        if account['coo_balance'] < coo_amount:
            return False

        eur_amount = coo_amount * self.current_price
        
        account['coo_balance'] -= coo_amount
        account['eur_balance'] += eur_amount

        # Add transaction record
        self.add_transaction('sell', coo_amount, eur_amount)
        self.save_data()
        return True

    def add_transaction(self, tx_type: str, coo_amount: float, eur_amount: float):
        """Add transaction to history"""
        transaction = {
            'user': self.current_user,
            'type': tx_type,
            'coo_amount': coo_amount,
            'eur_amount': eur_amount,
            'price': self.current_price,
            'timestamp': datetime.now().isoformat()
        }
        self.transactions.insert(0, transaction)

    def get_user_transactions(self, limit: int = 20) -> List[Dict]:
        """Get transaction history for current user"""
        if not self.current_user:
            return []
        
        user_transactions = [
            tx for tx in self.transactions 
            if tx['user'] == self.current_user
        ]
        return user_transactions[:limit]


class OpenCooinGUI:
    def __init__(self):
        self.exchange = OpenCooinExchange()
        self.root = tk.Tk()
        self.setup_window()
        self.create_login_interface()

    def setup_window(self):
        """Setup main window"""
        self.root.title("🐦 OpenCooin Trading Platform")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Subtitle.TLabel', font=('Arial', 10), background='#2c3e50', foreground='#bdc3c7')
        style.configure('Price.TLabel', font=('Arial', 24, 'bold'), background='#e74c3c', foreground='white')
        style.configure('Balance.TLabel', font=('Arial', 14, 'bold'), background='#3498db', foreground='white')
        style.configure('Success.TButton', background='#27ae60')
        style.configure('Danger.TButton', background='#e74c3c')

    def create_login_interface(self):
        """Create login/account selection interface"""
        self.clear_window()
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=20)
        
        ttk.Label(title_frame, text="🐦 OpenCooin Exchange", style='Title.TLabel').pack()
        ttk.Label(title_frame, text="The Premier Pigeon Cryptocurrency Trading Platform", style='Subtitle.TLabel').pack()

        # Account selection frame
        account_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        account_frame.pack(pady=20, padx=40, fill='both', expand=True)

        ttk.Label(account_frame, text="Select Pigeon Account:", font=('Arial', 12, 'bold')).pack(pady=10)

        # Account listbox
        self.account_listbox = tk.Listbox(account_frame, height=8, font=('Arial', 10))
        self.account_listbox.pack(fill='x', pady=10)
        
        # Populate accounts
        self.refresh_account_list()

        # Buttons frame
        button_frame = tk.Frame(account_frame, bg='#34495e')
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Login", command=self.login_selected).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Create New Account", command=self.show_create_account).pack(side='left', padx=5)

    def refresh_account_list(self):
        """Refresh the account listbox"""
        self.account_listbox.delete(0, tk.END)
        for account_name, balance in self.exchange.accounts.items():
            display_text = f"{account_name} - {balance['coo_balance']:.2f} COO | €{balance['eur_balance']:.2f}"
            self.account_listbox.insert(tk.END, display_text)

    def show_create_account(self):
        """Show create account dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Pigeon Account")
        dialog.geometry("300x150")
        dialog.configure(bg='#34495e')
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Enter pigeon name:", bg='#34495e', fg='white', font=('Arial', 10)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, font=('Arial', 10))
        name_entry.pack(pady=10, padx=20, fill='x')
        name_entry.focus()

        def create_account():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a pigeon name!")
                return
            
            if self.exchange.create_account(name):
                messagebox.showinfo("Success", f"Account '{name}' created successfully!\nStarting bonus: €100")
                self.refresh_account_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Account already exists or invalid name!")

        def on_enter(event):
            create_account()

        name_entry.bind('<Return>', on_enter)
        
        button_frame = tk.Frame(dialog, bg='#34495e')
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Create", command=create_account).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    def login_selected(self):
        """Login to selected account"""
        selection = self.account_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an account!")
            return

        account_name = list(self.exchange.accounts.keys())[selection[0]]
        if self.exchange.login(account_name):
            self.create_trading_interface()
        else:
            messagebox.showerror("Error", "Login failed!")

    def create_trading_interface(self):
        """Create main trading interface"""
        self.clear_window()

        # Header frame
        header_frame = tk.Frame(self.root, bg='#e74c3c', padx=20, pady=10)
        header_frame.pack(fill='x')

        # Price display
        price_frame = tk.Frame(header_frame, bg='#e74c3c')
        price_frame.pack()

        self.price_label = tk.Label(price_frame, text=f"€{self.exchange.current_price:.4f}", 
                                   font=('Arial', 24, 'bold'), bg='#e74c3c', fg='white')
        self.price_label.pack()

        change = self.exchange.get_price_change()
        change_color = '#27ae60' if change >= 0 else '#e74c3c'
        change_text = f"Monthly Change: {'+' if change >= 0 else ''}{change:.2f}%"
        
        tk.Label(price_frame, text=change_text, font=('Arial', 10), 
                bg='#e74c3c', fg=change_color).pack()
        
        tk.Label(price_frame, text=f"Next Update: {self.exchange.get_next_update_date()}", 
                font=('Arial', 8), bg='#e74c3c', fg='white').pack()

        # Main content frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left panel - Account info and trading
        left_panel = tk.Frame(main_frame, bg='#34495e', padx=15, pady=15)
        left_panel.pack(side='left', fill='both', expand=True, padx=5)

        # Account info
        account_info_frame = tk.Frame(left_panel, bg='#3498db', padx=10, pady=10)
        account_info_frame.pack(fill='x', pady=(0, 15))

        tk.Label(account_info_frame, text=f"Account: {self.exchange.current_user}", 
                font=('Arial', 12, 'bold'), bg='#3498db', fg='white').pack()

        balance_frame = tk.Frame(account_info_frame, bg='#3498db')
        balance_frame.pack(fill='x', pady=5)

        account = self.exchange.get_account_balance(self.exchange.current_user)
        self.coo_balance_label = tk.Label(balance_frame, text=f"{account['coo_balance']:.2f} COO", 
                                         font=('Arial', 14, 'bold'), bg='#3498db', fg='white')
        self.coo_balance_label.pack(side='left')

        self.eur_balance_label = tk.Label(balance_frame, text=f"€{account['eur_balance']:.2f}", 
                                         font=('Arial', 14, 'bold'), bg='#3498db', fg='white')
        self.eur_balance_label.pack(side='right')

        ttk.Button(account_info_frame, text="Logout", command=self.logout).pack(pady=5)

        # Trading section
        trading_frame = tk.LabelFrame(left_panel, text="Trade OpenCooin", font=('Arial', 12, 'bold'))
        trading_frame.pack(fill='x', pady=10)

        # Buy section
        buy_frame = tk.LabelFrame(trading_frame, text="🐦 Buy COO", bg='#d5f4e6', font=('Arial', 10, 'bold'))
        buy_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(buy_frame, text="Amount (EUR):", bg='#d5f4e6').pack(anchor='w')
        self.buy_entry = tk.Entry(buy_frame)
        self.buy_entry.pack(fill='x', padx=5, pady=2)
        self.buy_entry.bind('<KeyRelease>', self.update_buy_preview)

        tk.Label(buy_frame, text="You'll receive:", bg='#d5f4e6').pack(anchor='w')
        self.buy_preview = tk.Entry(buy_frame, state='readonly')
        self.buy_preview.pack(fill='x', padx=5, pady=2)

        tk.Button(buy_frame, text="Buy COO", bg='#27ae60', fg='white', 
                 font=('Arial', 10, 'bold'), command=self.buy_coo).pack(pady=5)

        # Sell section
        sell_frame = tk.LabelFrame(trading_frame, text="💰 Sell COO", bg='#fdeaea', font=('Arial', 10, 'bold'))
        sell_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(sell_frame, text="Amount (COO):", bg='#fdeaea').pack(anchor='w')
        self.sell_entry = tk.Entry(sell_frame)
        self.sell_entry.pack(fill='x', padx=5, pady=2)
        self.sell_entry.bind('<KeyRelease>', self.update_sell_preview)

        tk.Label(sell_frame, text="You'll receive:", bg='#fdeaea').pack(anchor='w')
        self.sell_preview = tk.Entry(sell_frame, state='readonly')
        self.sell_preview.pack(fill='x', padx=5, pady=2)

        tk.Button(sell_frame, text="Sell COO", bg='#e74c3c', fg='white', 
                 font=('Arial', 10, 'bold'), command=self.sell_coo).pack(pady=5)

        # Right panel - Transaction history
        right_panel = tk.Frame(main_frame, bg='#34495e', padx=15, pady=15)
        right_panel.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(right_panel, text="Transaction History", font=('Arial', 12, 'bold'), 
                bg='#34495e', fg='white').pack()

        # Transaction list
        self.transaction_text = scrolledtext.ScrolledText(right_panel, height=20, width=40, 
                                                         font=('Courier', 9), state='disabled')
        self.transaction_text.pack(fill='both', expand=True, pady=10)

        self.update_transaction_history()
        self.update_balances()

    def update_buy_preview(self, event=None):
        """Update buy preview in real-time"""
        try:
            eur_amount = float(self.buy_entry.get() or 0)
            coo_amount = eur_amount / self.exchange.current_price
            self.buy_preview.config(state='normal')
            self.buy_preview.delete(0, tk.END)
            self.buy_preview.insert(0, f"{coo_amount:.4f} COO")
            self.buy_preview.config(state='readonly')
        except ValueError:
            self.buy_preview.config(state='normal')
            self.buy_preview.delete(0, tk.END)
            self.buy_preview.insert(0, "0 COO")
            self.buy_preview.config(state='readonly')

    def update_sell_preview(self, event=None):
        """Update sell preview in real-time"""
        try:
            coo_amount = float(self.sell_entry.get() or 0)
            eur_amount = coo_amount * self.exchange.current_price
            self.sell_preview.config(state='normal')
            self.sell_preview.delete(0, tk.END)
            self.sell_preview.insert(0, f"€{eur_amount:.2f}")
            self.sell_preview.config(state='readonly')
        except ValueError:
            self.sell_preview.config(state='normal')
            self.sell_preview.delete(0, tk.END)
            self.sell_preview.insert(0, "€0.00")
            self.sell_preview.config(state='readonly')

    def buy_coo(self):
        """Execute buy order"""
        try:
            eur_amount = float(self.buy_entry.get())
            if eur_amount <= 0:
                messagebox.showerror("Error", "Please enter a valid EUR amount!")
                return

            if self.exchange.buy_coo(eur_amount):
                coo_amount = eur_amount / self.exchange.current_price
                messagebox.showinfo("Success", f"Successfully bought {coo_amount:.4f} COO for €{eur_amount:.2f}! 🐦💰")
                self.buy_entry.delete(0, tk.END)
                self.update_buy_preview()
                self.update_balances()
                self.update_transaction_history()
            else:
                messagebox.showerror("Error", "Insufficient EUR balance! 💸")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")

    def sell_coo(self):
        """Execute sell order"""
        try:
            coo_amount = float(self.sell_entry.get())
            if coo_amount <= 0:
                messagebox.showerror("Error", "Please enter a valid COO amount!")
                return

            if self.exchange.sell_coo(coo_amount):
                eur_amount = coo_amount * self.exchange.current_price
                messagebox.showinfo("Success", f"Successfully sold {coo_amount:.4f} COO for €{eur_amount:.2f}! 💰🐦")
                self.sell_entry.delete(0, tk.END)
                self.update_sell_preview()
                self.update_balances()
                self.update_transaction_history()
            else:
                messagebox.showerror("Error", "Insufficient COO balance! 🐦")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")

    def update_balances(self):
        """Update balance display"""
        account = self.exchange.get_account_balance(self.exchange.current_user)
        self.coo_balance_label.config(text=f"{account['coo_balance']:.4f} COO")
        self.eur_balance_label.config(text=f"€{account['eur_balance']:.2f}")

    def update_transaction_history(self):
        """Update transaction history display"""
        transactions = self.exchange.get_user_transactions()
        
        self.transaction_text.config(state='normal')
        self.transaction_text.delete(1.0, tk.END)

        if not transactions:
            self.transaction_text.insert(tk.END, "No transactions yet.\nStart trading! 🐦\n")
        else:
            for tx in transactions:
                tx_type = tx['type'].upper()
                date = datetime.fromisoformat(tx['timestamp']).strftime("%m/%d %H:%M")
                
                line = f"{tx_type:4} | {tx['coo_amount']:8.4f} COO | €{tx['eur_amount']:7.2f} | {date}\n"
                line += f"     | Price: €{tx['price']:.4f}/COO\n"
                line += "-" * 50 + "\n"
                
                self.transaction_text.insert(tk.END, line)

        self.transaction_text.config(state='disabled')
        self.transaction_text.see(tk.END)

    def logout(self):
        """Logout current user"""
        self.exchange.current_user = None
        self.create_login_interface()

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main function to run OpenCooin Trading Platform"""
    print("🐦 Starting OpenCooin Trading Platform...")
    print("📅 Project Status: Retired (Educational Demo)")
    
    try:
        app = OpenCooinGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Thanks for using OpenCooin! *coo coo*")
    except Exception as e:
        print(f"❌ Error starting application: {e}")


if __name__ == "__main__":
    main()
