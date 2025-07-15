import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from ethereum_wallet import EthereumWallet
import threading
import time
from datetime import datetime

class WalletManager:
    def __init__(self, parent):
        self.parent = parent
        self.wallet = EthereumWallet()
        self.wallet_window = None
        
    def create_wallet_window(self):
        """Create the wallet management window (legacy method)"""
        self.wallet_window = tk.Toplevel(self.parent.root)
        self.wallet_window.title("ETHEREUM WALLET MANAGER")
        self.wallet_window.geometry("1000x700")
        self.wallet_window.configure(bg='black')
        
        # Create interface in the window
        self.create_wallet_interface(self.wallet_window)
    
    def create_wallet_interface(self, parent_frame):
        """Create wallet management interface in the given frame"""
        # Terminal colors
        bg_color = '#000000'
        fg_color = '#00FF00'
        accent_color = '#FFFF00'
        error_color = '#FF0000'
        info_color = '#00FFFF'
        
        # Main content
        content_frame = tk.Frame(parent_frame, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Wallet operations
        left_panel = tk.Frame(content_frame, bg=bg_color, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Wallet operations
        operations_frame = tk.LabelFrame(left_panel, text=" WALLET OPERATIONS ", fg=fg_color, bg=bg_color,
                                       font=('Courier', 10, 'bold'))
        operations_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create wallet section
        create_frame = tk.LabelFrame(operations_frame, text=" CREATE NEW WALLET ", fg=info_color, bg=bg_color,
                                   font=('Courier', 9, 'bold'))
        create_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(create_frame, text="Wallet Name:", fg=fg_color, bg=bg_color, 
               font=('Courier', 9)).pack(anchor=tk.W, padx=5, pady=2)
        
        self.wallet_name_var = tk.StringVar()
        wallet_name_entry = tk.Entry(create_frame, textvariable=self.wallet_name_var, bg=bg_color, fg=fg_color,
                                   font=('Courier', 9))
        wallet_name_entry.pack(fill=tk.X, padx=5, pady=2)
        
        create_btn = tk.Button(create_frame, text="CREATE WALLET", command=self.create_wallet,
                             bg=bg_color, fg=accent_color, font=('Courier', 9, 'bold'),
                             relief=tk.RAISED, bd=2)
        create_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Import wallet section
        import_frame = tk.LabelFrame(operations_frame, text=" IMPORT WALLET ", fg=info_color, bg=bg_color,
                                   font=('Courier', 9, 'bold'))
        import_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(import_frame, text="Wallet Data (JSON):", fg=fg_color, bg=bg_color, 
               font=('Courier', 9)).pack(anchor=tk.W, padx=5, pady=2)
        
        self.import_data_var = tk.StringVar()
        import_data_entry = tk.Entry(import_frame, textvariable=self.import_data_var, bg=bg_color, fg=fg_color,
                                   font=('Courier', 9))
        import_data_entry.pack(fill=tk.X, padx=5, pady=2)
        
        import_btn = tk.Button(import_frame, text="IMPORT WALLET", command=self.import_wallet,
                             bg=bg_color, fg=accent_color, font=('Courier', 9, 'bold'),
                             relief=tk.RAISED, bd=2)
        import_btn.pack(fill=tk.X, padx=5, pady=5)

        # Export wallet section
        export_frame = tk.LabelFrame(operations_frame, text=" EXPORT WALLET ", fg=info_color, bg=bg_color,
                                   font=('Courier', 9, 'bold'))
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(export_frame, text="Wallet Address:", fg=fg_color, bg=bg_color, 
               font=('Courier', 9)).pack(anchor=tk.W, padx=5, pady=2)
        
        self.export_address_var = tk.StringVar()
        export_address_entry = tk.Entry(export_frame, textvariable=self.export_address_var, bg=bg_color, fg=fg_color,
                                   font=('Courier', 9))
        export_address_entry.pack(fill=tk.X, padx=5, pady=2)
        
        export_btn = tk.Button(export_frame, text="EXPORT WALLET", command=self.export_wallet,
                             bg=bg_color, fg=accent_color, font=('Courier', 9, 'bold'),
                             relief=tk.RAISED, bd=2)
        export_btn.pack(fill=tk.X, padx=5, pady=5)

        self.export_result_text = tk.Text(export_frame, height=3, bg=bg_color, fg=info_color, font=('Courier', 8), wrap=tk.WORD)
        self.export_result_text.pack(fill=tk.X, padx=5, pady=2)

        # Wallet list
        wallets_frame = tk.LabelFrame(left_panel, text=" AVAILABLE WALLETS ", fg=fg_color, bg=bg_color,
                                    font=('Courier', 10, 'bold'))
        wallets_frame.pack(fill=tk.BOTH, expand=True)
        
        self.wallets_listbox = tk.Listbox(wallets_frame, bg=bg_color, fg=fg_color, font=('Courier', 9),
                                         selectbackground=accent_color, selectforeground=bg_color)
        self.wallets_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.wallets_listbox.bind('<<ListboxSelect>>', self.on_wallet_select)
        
        # Right panel - Wallet info and balance
        right_panel = tk.Frame(content_frame, bg=bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Current wallet info
        info_frame = tk.LabelFrame(right_panel, text=" CURRENT WALLET ", fg=fg_color, bg=bg_color,
                                 font=('Courier', 10, 'bold'))
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.wallet_info_text = scrolledtext.ScrolledText(info_frame, height=8, bg=bg_color, fg=fg_color,
                                                        font=('Courier', 9), insertbackground=fg_color)
        self.wallet_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Balance and actions
        balance_frame = tk.LabelFrame(right_panel, text=" BALANCE & ACTIONS ", fg=fg_color, bg=bg_color,
                                    font=('Courier', 10, 'bold'))
        balance_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.balance_label = tk.Label(balance_frame, text="No wallet selected", fg=info_color, 
                                    bg=bg_color, font=('Courier', 10, 'bold'))
        self.balance_label.pack(pady=5)
        
        # Action buttons
        buttons_frame = tk.Frame(balance_frame, bg=bg_color)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = tk.Button(buttons_frame, text="REFRESH BALANCE", command=self.refresh_balance,
                              bg=bg_color, fg=fg_color, font=('Courier', 9, 'bold'),
                              relief=tk.RAISED, bd=2)
        refresh_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Lock button removed - wallets stay unlocked
        
        # Transaction history
        history_frame = tk.LabelFrame(right_panel, text=" TRANSACTION HISTORY ", fg=fg_color, bg=bg_color,
                                    font=('Courier', 10, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, bg=bg_color, fg=fg_color,
                                                    font=('Courier', 9), insertbackground=fg_color)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add token balances display below balance_frame
        token_balances_frame = tk.LabelFrame(right_panel, text=" ERC20 TOKEN BALANCES ", fg=fg_color, bg=bg_color,
                                    font=('Courier', 10, 'bold'))
        token_balances_frame.pack(fill=tk.X, pady=(0, 10))
        self.token_balances_text = scrolledtext.ScrolledText(token_balances_frame, height=8, bg=bg_color, fg=fg_color,
                                                        font=('Courier', 9), insertbackground=fg_color)
        self.token_balances_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add custom token section below token_balances_frame
        custom_token_frame = tk.LabelFrame(right_panel, text=" CUSTOM ERC20 TOKEN ", fg=fg_color, bg=bg_color,
                                    font=('Courier', 10, 'bold'))
        custom_token_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(custom_token_frame, text="Token Contract Address:", fg=fg_color, bg=bg_color, font=('Courier', 9)).pack(anchor=tk.W, padx=5, pady=2)
        self.custom_token_address_var = tk.StringVar()
        custom_token_entry = tk.Entry(custom_token_frame, textvariable=self.custom_token_address_var, bg=bg_color, fg=fg_color, font=('Courier', 9), insertbackground=fg_color)
        custom_token_entry.pack(fill=tk.X, padx=5, pady=2)
        custom_token_btn = tk.Button(custom_token_frame, text="FETCH TOKEN BALANCE", command=self.fetch_custom_token_balance,
                             bg=bg_color, fg=accent_color, font=('Courier', 9, 'bold'), relief=tk.RAISED, bd=2)
        custom_token_btn.pack(fill=tk.X, padx=5, pady=5)
        self.custom_token_result_text = tk.Text(custom_token_frame, height=2, bg=bg_color, fg=info_color, font=('Courier', 9), wrap=tk.WORD)
        self.custom_token_result_text.pack(fill=tk.X, padx=5, pady=2)
        
        # Add advanced features section below custom_token_frame
        advanced_frame = tk.LabelFrame(right_panel, text=" ADVANCED FEATURES ", fg=fg_color, bg=bg_color,
                                    font=('Courier', 10, 'bold'))
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Portfolio value
        portfolio_frame = tk.Frame(advanced_frame, bg=bg_color)
        portfolio_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.portfolio_value_label = tk.Label(portfolio_frame, text="Portfolio Value: $0.00", 
                                            fg=accent_color, bg=bg_color, font=('Courier', 10, 'bold'))
        self.portfolio_value_label.pack(side=tk.LEFT)
        
        refresh_portfolio_btn = tk.Button(portfolio_frame, text="REFRESH", command=self.refresh_portfolio,
                                        bg=bg_color, fg=fg_color, font=('Courier', 8, 'bold'),
                                        relief=tk.RAISED, bd=1)
        refresh_portfolio_btn.pack(side=tk.RIGHT)
        
        # Transaction creation
        tx_frame = tk.LabelFrame(advanced_frame, text=" CREATE TRANSACTION ", fg=info_color, bg=bg_color,
                               font=('Courier', 9, 'bold'))
        tx_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tx_input_frame = tk.Frame(tx_frame, bg=bg_color)
        tx_input_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(tx_input_frame, text="To:", fg=fg_color, bg=bg_color, font=('Courier', 8)).pack(side=tk.LEFT)
        self.tx_to_var = tk.StringVar()
        tx_to_entry = tk.Entry(tx_input_frame, textvariable=self.tx_to_var, bg=bg_color, fg=fg_color,
                             font=('Courier', 8), insertbackground=fg_color, width=30)
        tx_to_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        tk.Label(tx_input_frame, text="Amount (ETH):", fg=fg_color, bg=bg_color, font=('Courier', 8)).pack(side=tk.LEFT)
        self.tx_amount_var = tk.StringVar()
        tx_amount_entry = tk.Entry(tx_input_frame, textvariable=self.tx_amount_var, bg=bg_color, fg=fg_color,
                                 font=('Courier', 8), insertbackground=fg_color, width=10)
        tx_amount_entry.pack(side=tk.LEFT, padx=5)
        
        tx_buttons_frame = tk.Frame(tx_frame, bg=bg_color)
        tx_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        estimate_gas_btn = tk.Button(tx_buttons_frame, text="ESTIMATE GAS", command=self.estimate_gas,
                                   bg=bg_color, fg=info_color, font=('Courier', 8, 'bold'),
                                   relief=tk.RAISED, bd=1)
        estimate_gas_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        create_tx_btn = tk.Button(tx_buttons_frame, text="CREATE TX", command=self.create_transaction,
                                bg=bg_color, fg=accent_color, font=('Courier', 8, 'bold'),
                                relief=tk.RAISED, bd=1)
        create_tx_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        sign_tx_btn = tk.Button(tx_buttons_frame, text="SIGN TX", command=self.sign_transaction,
                              bg=bg_color, fg=fg_color, font=('Courier', 8, 'bold'),
                              relief=tk.RAISED, bd=1)
        sign_tx_btn.pack(side=tk.LEFT)
        
        self.tx_result_text = tk.Text(tx_frame, height=3, bg=bg_color, fg=info_color, font=('Courier', 8), wrap=tk.WORD)
        self.tx_result_text.pack(fill=tk.X, padx=5, pady=2)
        
        # Gas info
        gas_frame = tk.Frame(advanced_frame, bg=bg_color)
        gas_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.gas_price_label = tk.Label(gas_frame, text="Gas Price: -- gwei", fg=fg_color, bg=bg_color, font=('Courier', 8))
        self.gas_price_label.pack(side=tk.LEFT)
        
        self.gas_limit_label = tk.Label(gas_frame, text="Gas Limit: --", fg=fg_color, bg=bg_color, font=('Courier', 8))
        self.gas_limit_label.pack(side=tk.RIGHT)
        
        # Status bar
        status_frame = tk.Frame(self.wallet_window, bg=bg_color, height=25)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.wallet_status_label = tk.Label(status_frame, text="Ready to manage wallets", 
                                          fg=fg_color, bg=bg_color, font=('Courier', 9))
        self.wallet_status_label.pack(side=tk.LEFT, padx=5)
        
        # Initialize wallet list
        self.refresh_wallet_list()
        
        # Auto-select first wallet if available
        wallets = self.wallet.list_wallets()
        if wallets:
            self.wallets_listbox.selection_set(0)
            self.on_wallet_select(None)
        
        # Add test balance button
        test_balance_frame = tk.Frame(self.wallet_window, bg=bg_color)
        test_balance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        add_balance_button = tk.Button(test_balance_frame, text="ADD TEST BALANCE", 
                                     bg='#FF6B35', fg='white', font=('Courier', 10, 'bold'),
                                     command=self.add_test_balance)
        add_balance_button.pack(side=tk.LEFT, padx=5)
        
        self.test_balance_label = tk.Label(test_balance_frame, text="Click to add 1.0 ETH test balance", 
                                         fg=fg_color, bg=bg_color, font=('Courier', 9))
        self.test_balance_label.pack(side=tk.LEFT, padx=10)
        
        # Start balance updates
        self.start_balance_updates()
        
    def create_wallet(self):
        wallet_name = self.wallet_name_var.get().strip()
        if not wallet_name:
            messagebox.showerror("Error", "Please enter a wallet name")
            return
        address, wallet_data = self.wallet.generate_wallet(wallet_name)
        messagebox.showinfo("Success", f"Wallet created! Address: {address}")
        self.refresh_wallet_list()
        # Automatically set the new wallet as active
        success, message = self.wallet.unlock_wallet(address, "dummy_password")
        if success:
            self.update_wallet_info(address)
            self.update_token_balances(address)
            self.refresh_balance()
            self.update_transaction_history()
            # Update parent balance
            if self.parent:
                self.parent.update_wallet_balance()
            # Show success message
            self.balance_label.config(text=f"Wallet active: {address[:10]}...")
            self.wallet_status_label.config(text=f"Wallet active: {address[:10]}...")
    
    def refresh_balance(self):
        """Refresh wallet balance"""
        if not self.wallet.current_wallet:
            self.balance_label.config(text="No wallet selected")
            return
        
        try:
            balance = self.wallet.get_wallet_balance()
            self.balance_label.config(text=f"Balance: {balance:.6f} ETH")
            self.wallet_status_label.config(text=f"Balance updated at {time.strftime('%H:%M:%S')}")
            
            # Update parent balance
            if self.parent:
                self.parent.update_wallet_balance()
                
        except Exception as e:
            # Show 0.00 ETH instead of error
            self.balance_label.config(text="Balance: 0.000000 ETH")
            self.wallet_status_label.config(text="Balance: 0.000000 ETH (offline)")
            print(f"Error refreshing balance: {e}")
    
    def refresh_wallet_list(self):
        """Refresh the wallet list"""
        self.wallets_listbox.delete(0, tk.END)
        wallets = self.wallet.list_wallets()
        
        for address in wallets:
            wallet_info = self.wallet.get_wallet_info(address)
            if wallet_info:
                display_text = f"{wallet_info['name']} ({address[:10]}...)"
                self.wallets_listbox.insert(tk.END, display_text)
    
    def import_wallet(self):
        wallet_data_str = self.import_data_var.get().strip()
        if not wallet_data_str:
            messagebox.showerror("Error", "Please enter wallet data (JSON)")
            return
        try:
            import json
            wallet_data = json.loads(wallet_data_str)
            address, wallet_data = self.wallet.import_wallet(wallet_data)
            messagebox.showinfo("Success", f"Wallet imported! Address: {address}")
            self.refresh_wallet_list()
            # Automatically set the imported wallet as active
            success, message = self.wallet.unlock_wallet(address, "dummy_password")
            if success:
                self.update_wallet_info(address)
                self.update_token_balances(address)
                self.refresh_balance()
                self.update_transaction_history()
                # Update parent balance
                if self.parent:
                    self.parent.update_wallet_balance()
                # Show success message
                self.balance_label.config(text=f"Wallet active: {address[:10]}...")
                self.wallet_status_label.config(text=f"Wallet active: {address[:10]}...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import wallet: {e}")

    def export_wallet(self):
        address = self.export_address_var.get().strip()
        if not address:
            messagebox.showerror("Error", "Please enter wallet address")
            return
        wallet_json, msg = self.wallet.export_wallet(address)
        if wallet_json:
            self.export_result_text.delete(1.0, tk.END)
            self.export_result_text.insert(tk.END, wallet_json)
            messagebox.showinfo("Exported", "Wallet exported successfully!")
        else:
            messagebox.showerror("Error", msg)

    def fetch_custom_token_balance(self):
        """Fetch balance and info for a custom ERC20 token contract address"""
        address = self.custom_token_address_var.get().strip()
        if not address:
            self.custom_token_result_text.delete(1.0, tk.END)
            self.custom_token_result_text.insert(tk.END, "Enter a contract address.")
            return
        wallet_address = None
        if self.wallet.current_wallet:
            wallet_address = self.wallet.current_wallet['address']
        if not wallet_address:
            self.custom_token_result_text.delete(1.0, tk.END)
            self.custom_token_result_text.insert(tk.END, "Select a wallet first.")
            return
        # Fetch symbol and decimals
        symbol, decimals = self.wallet.get_token_info(address)
        balance = self.wallet.get_token_balance(address, wallet_address)
        if symbol:
            self.custom_token_result_text.delete(1.0, tk.END)
            self.custom_token_result_text.insert(tk.END, f"{symbol}: {balance:.{decimals}f}")
        else:
            self.custom_token_result_text.delete(1.0, tk.END)
            self.custom_token_result_text.insert(tk.END, f"Balance: {balance} (Unknown symbol)")

    def refresh_portfolio(self):
        """Refresh portfolio value display"""
        if not self.wallet.current_wallet:
            self.portfolio_value_label.config(text="Portfolio Value: $0.00 (No wallet selected)")
            return
        
        try:
            portfolio_value = self.wallet.get_portfolio_value()
            self.portfolio_value_label.config(text=f"Portfolio Value: ${portfolio_value:,.2f}")
        except Exception as e:
            self.portfolio_value_label.config(text=f"Portfolio Value: Error ({str(e)})")

    def estimate_gas(self):
        """Estimate gas for the current transaction"""
        to_address = self.tx_to_var.get().strip()
        amount_str = self.tx_amount_var.get().strip()
        
        if not to_address or not amount_str:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, "Please enter recipient address and amount")
            return
        
        try:
            amount = float(amount_str)
            gas_limit = self.wallet.get_gas_estimate(to_address, amount)
            gas_price = self.wallet.get_gas_price()
            
            self.gas_limit_label.config(text=f"Gas Limit: {gas_limit:,}")
            self.gas_price_label.config(text=f"Gas Price: {gas_price:.1f} gwei")
            
            total_cost_eth = (gas_limit * gas_price) / 10**9
            total_cost_usd = total_cost_eth * 3200  # Approximate ETH price
            
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, f"Gas Estimate: {gas_limit:,} units\nTotal Cost: {total_cost_eth:.6f} ETH (~${total_cost_usd:.2f})")
            
        except ValueError:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, "Invalid amount. Please enter a valid number.")
        except Exception as e:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, f"Error estimating gas: {str(e)}")

    def create_transaction(self):
        """Create transaction data"""
        to_address = self.tx_to_var.get().strip()
        amount_str = self.tx_amount_var.get().strip()
        
        if not to_address or not amount_str:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, "Please enter recipient address and amount")
            return
        
        try:
            amount = float(amount_str)
            gas_price = self.wallet.get_gas_price()
            gas_limit = self.wallet.get_gas_estimate(to_address, amount)
            
            tx_data, message = self.wallet.create_transaction_data(to_address, amount, gas_price, gas_limit)
            
            if tx_data:
                self.tx_result_text.delete(1.0, tk.END)
                self.tx_result_text.insert(tk.END, f"Transaction created successfully!\nNonce: {tx_data['nonce']}\nGas: {tx_data['gas']}\nGas Price: {tx_data['gasPrice']} wei")
                self.current_tx_data = tx_data
            else:
                self.tx_result_text.delete(1.0, tk.END)
                self.tx_result_text.insert(tk.END, f"Error: {message}")
                
        except ValueError:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, "Invalid amount. Please enter a valid number.")
        except Exception as e:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, f"Error creating transaction: {str(e)}")

    def sign_transaction(self):
        """Sign the current transaction"""
        if not hasattr(self, 'current_tx_data') or not self.current_tx_data:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, "No transaction to sign. Create a transaction first.")
            return
        
        try:
            signed_tx, message = self.wallet.sign_transaction(self.current_tx_data)
            
            if signed_tx:
                self.tx_result_text.delete(1.0, tk.END)
                self.tx_result_text.insert(tk.END, f"Transaction signed successfully!\nHash: {signed_tx['hash']}\nSignature: {signed_tx['signature'][:20]}...")
            else:
                self.tx_result_text.delete(1.0, tk.END)
                self.tx_result_text.insert(tk.END, f"Error signing: {message}")
                
        except Exception as e:
            self.tx_result_text.delete(1.0, tk.END)
            self.tx_result_text.insert(tk.END, f"Error signing transaction: {str(e)}")

    def update_token_balances(self, address=None):
        """Update ERC20 token balances display with prices"""
        self.token_balances_text.delete(1.0, tk.END)
        if address is None and self.wallet.current_wallet:
            address = self.wallet.current_wallet['address']
        if not address:
            self.token_balances_text.insert(tk.END, "No wallet selected")
            return
        
        # List of major ERC20 tokens (symbol: contract)
        token_contracts = {
            'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
            'DAI':  '0x6B175474E89094C44Da98b954EedeAC495271d0F',
            'UNI':  '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
            'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DdAE9',
            'COMP': '0xc00e94Cb662C3520282E6f5717214004A7f26888',
            'MKR':  '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
            'CRV':  '0xD533a949740bb3306d119CC777fa900bA034cd52',
            'SUSHI':'0x6B3595068778DD592e39A122f4f5a5cF09C90fE2',
            'YFI':  '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e',
            'SNX':  '0xC011A72400E58ecD99Ee497CF89E3775d4bd732F',
            'BAL':  '0xba100000625a3754423978a60c9317c58a424e3D',
            'REN':  '0x408e41876cCCDC0F92210600ef50372656052a38',
            'ZRX':  '0xE41d2489571d322189246DaFA5ebDe1F4699F498',
            'BAT':  '0x0D8775F648430679A709E98d2b0Cb6250d2887EF',
        }
        
        balances = self.wallet.get_all_token_balances(token_contracts, address)
        
        # Header
        self.token_balances_text.insert(tk.END, f"{'Token':<8} {'Balance':<15} {'Price':<10} {'Value':<12}\n")
        self.token_balances_text.insert(tk.END, "-" * 50 + "\n")
        
        for symbol, balance in balances.items():
            if balance is not None and balance > 0:
                price = self.wallet.get_token_price(symbol=symbol)
                if price:
                    value = balance * price
                    self.token_balances_text.insert(tk.END, f"{symbol:<8} {balance:<15.6f} ${price:<9.4f} ${value:<11.2f}\n")
                else:
                    self.token_balances_text.insert(tk.END, f"{symbol:<8} {balance:<15.6f} {'N/A':<10} {'N/A':<12}\n")
            elif balance == 0:
                self.token_balances_text.insert(tk.END, f"{symbol:<8} {'0.000000':<15} {'--':<10} {'--':<12}\n")
            else:
                self.token_balances_text.insert(tk.END, f"{symbol:<8} {'Error':<15} {'--':<10} {'--':<12}\n")

    def on_wallet_select(self, event):
        """Handle wallet selection - always active on select"""
        selection = self.wallets_listbox.curselection()
        if selection:
            wallets = self.wallet.list_wallets()
            if selection[0] < len(wallets):
                address = wallets[selection[0]]
                # Set wallet as active in the backend
                success, message = self.wallet.unlock_wallet(address, "dummy_password")
                if success:
                    # Update wallet info displays
                    self.update_wallet_info(address)
                    self.update_token_balances(address)
                    self.refresh_balance()
                    self.update_transaction_history()
                    
                    # Update parent balance
                    if self.parent:
                        self.parent.update_wallet_balance()
                    
                    # Show success message with better visibility
                    self.balance_label.config(text=f"✅ WALLET ACTIVE: {address[:10]}...")
                    self.wallet_status_label.config(text=f"✅ WALLET ACTIVE: {address[:10]}...")
                    
                    # Show popup confirmation
                    messagebox.showinfo("Wallet Selected", f"Wallet {address[:10]}... is now active!")
                else:
                    messagebox.showerror("Error", f"Failed to activate wallet: {message}")
        else:
            # No selection
            self.balance_label.config(text="No wallet selected")
            self.wallet_status_label.config(text="No wallet selected")
    
    def update_wallet_info(self, address=None):
        """Update wallet information display"""
        self.wallet_info_text.delete(1.0, tk.END)
        
        if address is None and self.wallet.current_wallet:
            address = self.wallet.current_wallet['address']
        
        if not address:
            self.wallet_info_text.insert(tk.END, "No wallet selected")
            return
        
        wallet_info = self.wallet.get_wallet_info(address)
        if wallet_info:
            info_text = f"Name: {wallet_info['name']}\n"
            info_text += f"Address: {wallet_info['address']}\n"
            info_text += f"Created: {wallet_info['created_at']}\n"
            info_text += f"Cached Balance: {wallet_info['balance']:.6f} ETH\n"
            
            if self.wallet.current_wallet and self.wallet.current_wallet['address'] == address:
                info_text += "\n🟢 WALLET ACTIVE\n"
            else:
                info_text += "\n⚪ WALLET INACTIVE\n"
            
            self.wallet_info_text.insert(tk.END, info_text)
        else:
            self.wallet_info_text.insert(tk.END, "Wallet not found")
    
    def update_transaction_history(self):
        """Update transaction history display"""
        self.history_text.delete(1.0, tk.END)
        
        if not self.wallet.current_wallet:
            self.history_text.insert(tk.END, "No wallet selected")
            return
        
        try:
            transactions = self.wallet.get_transaction_history()
            
            if transactions:
                for tx in transactions[:10]:  # Show last 10 transactions
                    timestamp = datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
                    value_eth = int(tx['value']) / 10**18
                    
                    line = f"[{timestamp}] {tx['hash'][:10]}... | {value_eth:.6f} ETH\n"
                    self.history_text.insert(tk.END, line)
            else:
                self.history_text.insert(tk.END, "No transactions found")
                
        except Exception as e:
            self.history_text.insert(tk.END, f"Error fetching transactions: {str(e)}")
    
    def start_balance_updates(self):
        """Start automatic balance updates with enhanced functionality"""
        def update_loop():
            consecutive_failures = 0
            while True:
                try:
                    if self.wallet_window and self.wallet_window.winfo_exists():
                        if self.wallet.current_wallet:
                            # Update all wallet data with error handling
                            try:
                                self.refresh_balance()
                            except Exception as e:
                                print(f"Balance refresh error: {e}")
                            
                            try:
                                self.refresh_portfolio()
                            except Exception as e:
                                print(f"Portfolio refresh error: {e}")
                            
                            try:
                                self.update_transaction_history()
                            except Exception as e:
                                print(f"Transaction history error: {e}")
                            
                            try:
                                self.update_token_balances()
                            except Exception as e:
                                print(f"Token balance error: {e}")
                            
                            try:
                                self.update_wallet_info()
                            except Exception as e:
                                print(f"Wallet info error: {e}")
                            
                            # Reset failure counter on success
                            consecutive_failures = 0
                            update_interval = 15  # Normal interval
                        else:
                            # No wallet selected, check less frequently
                            update_interval = 60
                    else:
                        # Window closed, wait longer
                        update_interval = 120
                    
                    time.sleep(update_interval)
                    
                except Exception as e:
                    print(f"Wallet update error: {e}")
                    consecutive_failures += 1
                    # Increase interval on consecutive failures
                    update_interval = min(300, 30 * (2 ** consecutive_failures))
                    time.sleep(update_interval)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
        # Start a separate thread for price updates
        def price_update_loop():
            while True:
                try:
                    if self.wallet_window and self.wallet_window.winfo_exists():
                        if self.wallet.current_wallet:
                            # Update token prices with error handling
                            try:
                                self.update_token_balances()
                            except Exception as e:
                                print(f"Token balance update error: {e}")
                            
                            try:
                                self.refresh_portfolio()
                            except Exception as e:
                                print(f"Portfolio update error: {e}")
                    time.sleep(45)  # Update prices every 45 seconds
                except Exception as e:
                    print(f"Price update error: {e}")
                    time.sleep(90)
        
        price_thread = threading.Thread(target=price_update_loop, daemon=True)
        price_thread.start()
    
    def get_current_balance(self):
        """Get current wallet balance for parent"""
        if self.wallet.current_wallet:
            return self.wallet.get_wallet_balance()
        return 0.0
    
    def get_current_wallet_address(self):
        """Get current wallet address for parent"""
        if self.wallet.current_wallet:
            return self.wallet.current_wallet['address']
        return None
    
    def add_test_balance(self):
        """Add test balance to the current wallet"""
        if not self.wallet.current_wallet:
            messagebox.showwarning("Warning", "Please select a wallet first!")
            return
        
        try:
            # Add 1.0 ETH test balance
            test_balance = 1.0
            address = self.wallet.current_wallet['address']
            
            # Update the wallet's cached balance
            self.wallet.add_test_balance(address, test_balance)
            
            # Refresh displays
            self.refresh_balance()
            self.refresh_portfolio()
            self.update_wallet_info(address)
            
            # Update parent
            if self.parent:
                self.parent.update_wallet_balance()
            
            # Show success message
            messagebox.showinfo("Success", f"Added {test_balance} ETH test balance to wallet!")
            self.test_balance_label.config(text=f"Added {test_balance} ETH test balance")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add test balance: {str(e)}") 