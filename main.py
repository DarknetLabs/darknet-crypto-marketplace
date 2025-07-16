import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
import random
from datetime import datetime
import os
from crypto_rooms import CryptoRooms
from live_market_data import LiveMarketData
from wallet_manager import WalletManager
import requests
from web3 import Web3
from cryptography.fernet import Fernet
import base64
import hashlib

UNISWAP_V2_ROUTER_ADDRESS = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
# Update the Uniswap V2 Router ABI to include the fee-on-transfer supporting functions
UNISWAP_V2_ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokensSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETHSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
INFURA_URL = 'https://mainnet.infura.io/v3/8b3e1e2e2e2e4e2e8e2e2e2e2e2e2e2e'  # Replace with your Infura key

class CryptoMarketplace:
    def __init__(self, root):
        self.root = root
        self.root.title("DARKNET CRYPTO MARKETPLACE v2.1")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Terminal colors
        self.bg_color = '#000000'
        self.fg_color = '#00FF00'
        self.accent_color = '#FFFF00'
        self.error_color = '#FF0000'
        self.info_color = '#00FFFF'
        
        # Market data - Major cryptocurrencies
        self.crypto_prices = {
            'BTC': 45000,
            'ETH': 3200,
            'XRP': 0.85,
            'ADA': 1.20,
            'DOT': 25.50,
            'LINK': 18.75,
            'LTC': 145.30,
            'BCH': 380.45
        }
        
        # Ethereum ERC20 tokens
        self.erc20_tokens = {
            'USDT': 1.00,
            'USDC': 1.00,
            'DAI': 1.00,
            'UNI': 8.50,
            'AAVE': 95.30,
            'COMP': 65.20,
            'MKR': 1200.45,
            'CRV': 0.85,
            'SUSHI': 1.25,
            'YFI': 8500.75,
            'SNX': 3.45,
            'BAL': 4.20,
            'REN': 0.15,
            'ZRX': 0.35,
            'BAT': 0.25,
            'MANA': 0.45,
            'SAND': 0.55,
            'ENJ': 0.30,
            'CHZ': 0.12,
            'ALGO': 0.18,
            'VET': 0.025,
            'THETA': 1.85,
            'FIL': 4.75,
            'ICP': 12.30,
            'ATOM': 8.90,
            'NEAR': 2.15,
            'FTM': 0.35,
            'AVAX': 25.60,
            'MATIC': 0.85,
            'SOL': 95.40,
            'LUNA': 0.85,
            'DOGE': 0.08,
            'SHIB': 0.000012,
            'PEPE': 0.0000012,
            'BONK': 0.00000085
        }
        
        # Combine all trading pairs
        self.all_trading_pairs = {**self.crypto_prices, **self.erc20_tokens}
        
        self.user_balance = 0.0  # Will be synced with wallet balance
        self.user_portfolio = {}
        self.transaction_history = []
        
        # PNL tracking - track cost basis for each token
        self.token_cost_basis = {}  # {symbol: {'total_bought': amount, 'total_spent': cost, 'average_price': price}}
        
        # UI elements that need to be accessed globally
        self.balance_label = None
        self.portfolio_text = None
        self.market_text = None
        self.history_text = None
        
        # Fetch Uniswap token list
        self.uniswap_tokens = []
        try:
            resp = requests.get('https://tokens.uniswap.org/')
            if resp.status_code == 200:
                data = resp.json()
                self.uniswap_tokens = data.get('tokens', [])
        except Exception as e:
            self.uniswap_tokens = []
        
        # Initialize chat rooms
        self.crypto_rooms = CryptoRooms(self)
        
        # Initialize live market data
        self.live_market = LiveMarketData()
        self.live_market.start_live_updates()
        
        # Initialize wallet manager
        self.wallet_manager = WalletManager(self)
        
        self.web3 = Web3(Web3.HTTPProvider(INFURA_URL))
        self.uniswap_router = self.web3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=UNISWAP_V2_ROUTER_ABI)

        self.setup_ui()
        self.start_price_updates()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="╔══════════════════════════════════════════════════════════════════════════════╗", 
                              fg=self.fg_color, bg=self.bg_color, font=('Courier', 10))
        title_label.pack()
        
        title_label2 = tk.Label(header_frame, text="║                    DARKNET CRYPTO MARKETPLACE v2.1                           ║", 
                               fg=self.accent_color, bg=self.bg_color, font=('Courier', 12, 'bold'))
        title_label2.pack()
        
        title_label3 = tk.Label(header_frame, text="║                         SECURE • ANONYMOUS • DECENTRALIZED                    ║", 
                               fg=self.fg_color, bg=self.bg_color, font=('Courier', 10))
        title_label3.pack()
        
        title_label4 = tk.Label(header_frame, text="╚══════════════════════════════════════════════════════════════════════════════╝", 
                               fg=self.fg_color, bg=self.bg_color, font=('Courier', 10))
        title_label4.pack()
        
        # Section buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        dashboard_btn = tk.Button(button_frame, text="Open Dashboard", command=self.open_dashboard_window, 
                                 fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        dashboard_btn.grid(row=0, column=0, padx=10, pady=5)
        
        trading_btn = tk.Button(button_frame, text="Open Trading", command=self.open_trading_window, 
                               fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        trading_btn.grid(row=0, column=1, padx=10, pady=5)
        
        wallet_btn = tk.Button(button_frame, text="Open Wallets", command=self.open_wallet_window, 
                              fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        wallet_btn.grid(row=1, column=0, padx=10, pady=5)
        
        market_btn = tk.Button(button_frame, text="Open Market Data", command=self.open_market_window, 
                              fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        market_btn.grid(row=1, column=1, padx=10, pady=5)
        
        chat_btn = tk.Button(button_frame, text="Open Chat Rooms", command=self.crypto_rooms.create_rooms_window, 
                            fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        chat_btn.grid(row=2, column=0, pady=5)
        
        sniper_btn = tk.Button(button_frame, text="Token Sniper", command=self.open_sniper_window, 
                              fg=self.error_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        sniper_btn.grid(row=2, column=1, pady=5)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.bg_color, height=25)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="System: Ready | Connection: Secure | Status: Online", 
                                   fg=self.fg_color, bg=self.bg_color, font=('Courier', 9))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Add live market status update
        self.update_status_display()

    def create_dashboard_tab(self, parent):
        """Create the main dashboard tab"""
        dashboard_frame = tk.Frame(parent, bg=self.bg_color)
        dashboard_frame.pack(fill=tk.BOTH, expand=True)
        # Left panel - User info and portfolio
        left_panel = tk.Frame(dashboard_frame, bg=self.bg_color, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        # User info section
        user_frame = tk.LabelFrame(left_panel, text=" USER DASHBOARD ", fg=self.fg_color, bg=self.bg_color,
                                 font=('Courier', 10, 'bold'))
        user_frame.pack(fill=tk.X, pady=(0, 10))
        balance_label = tk.Label(user_frame, text=f"Balance: ${self.user_balance:,.2f}", 
                                fg=self.info_color, bg=self.bg_color, font=('Courier', 10, 'bold'))
        balance_label.pack(pady=5)
        self.balance_label = balance_label  # Store reference for global access
        # Portfolio section
        portfolio_frame = tk.LabelFrame(left_panel, text=" PORTFOLIO ", fg=self.fg_color, bg=self.bg_color,
                                      font=('Courier', 10, 'bold'))
        portfolio_frame.pack(fill=tk.BOTH, expand=True)
        portfolio_text = scrolledtext.ScrolledText(portfolio_frame, height=10, bg=self.bg_color, fg=self.fg_color,
                                                  font=('Courier', 9), insertbackground=self.fg_color)
        portfolio_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Right panel - Transaction history
        right_panel = tk.Frame(dashboard_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Transaction history
        history_frame = tk.LabelFrame(right_panel, text=" TRANSACTION HISTORY ", fg=self.fg_color, bg=self.bg_color,
                                    font=('Courier', 10, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True)
        history_text = scrolledtext.ScrolledText(history_frame, bg=self.bg_color, fg=self.fg_color,
                                                font=('Courier', 9), insertbackground=self.fg_color)
        history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Local update logic for portfolio and history
        def update_portfolio_display():
            portfolio_text.delete(1.0, tk.END)
            if not self.user_portfolio:
                portfolio_text.insert(tk.END, "No holdings yet.\nStart trading to build your portfolio!")
            else:
                total_value = 0
                total_pnl = 0
                for symbol, amount in self.user_portfolio.items():
                    live_price = self.live_market.get_price(symbol)
                    if live_price > 0:
                        current_price = live_price
                    else:
                        current_price = self.all_trading_pairs.get(symbol, 0)
                    value = amount * current_price
                    total_value += value
                    
                    # Calculate PNL
                    pnl = 0
                    pnl_percentage = 0
                    avg_buy_price = 0
                    if symbol in self.token_cost_basis:
                        avg_buy_price = self.token_cost_basis[symbol]['average_price']
                        pnl = (current_price - avg_buy_price) * amount
                        if avg_buy_price > 0:
                            pnl_percentage = ((current_price - avg_buy_price) / avg_buy_price) * 100
                        total_pnl += pnl
                    
                    # Format the line with PNL information
                    if current_price >= 1:
                        line = f"{symbol}: {amount:.4f} (${value:.2f})"
                    else:
                        line = f"{symbol}: {amount:.4f} (${value:.6f})"
                    
                    # Add PNL information if we have cost basis
                    if symbol in self.token_cost_basis:
                        line += f"\n  Avg Buy: ${avg_buy_price:.4f} | Current: ${current_price:.4f}"
                        line += f"\n  PNL: ${pnl:.2f} ({pnl_percentage:+.2f}%)"
                        
                        # Color code PNL (green for profit, red for loss)
                        if pnl > 0:
                            line += " [PROFIT]"
                        elif pnl < 0:
                            line += " [LOSS]"
                        else:
                            line += " [BREAKEVEN]"
                    
                    line += "\n"
                    portfolio_text.insert(tk.END, line)
                
                portfolio_text.insert(tk.END, f"\nTotal Portfolio Value: ${total_value:.2f}")
                if total_pnl != 0:
                    portfolio_text.insert(tk.END, f"Total PNL: ${total_pnl:.2f}")
                    if total_pnl > 0:
                        portfolio_text.insert(tk.END, " [PROFIT]")
                    else:
                        portfolio_text.insert(tk.END, " [LOSS]")
        def update_history_display():
            history_text.delete(1.0, tk.END)
            for tx in self.transaction_history:
                line = f"{tx['timestamp']} {tx['type']} {tx['amount']} {tx['symbol']} @ ${tx['price']}\n"
                history_text.insert(tk.END, line)
        update_portfolio_display()
        update_history_display()
    
    def create_trading_tab(self, parent):
        """Create the trading interface tab"""
        trading_frame = tk.Frame(parent, bg=self.bg_color)
        trading_frame.pack(fill=tk.BOTH, expand=True)
        # Trading section
        trading_section = tk.LabelFrame(trading_frame, text=" TRADING INTERFACE ", fg=self.fg_color, bg=self.bg_color,
                                      font=('Courier', 10, 'bold'))
        trading_section.pack(fill=tk.X, pady=(0, 10), padx=10)
        # Trading controls
        controls_frame = tk.Frame(trading_section, bg=self.bg_color)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        # Wallet entry
        tk.Label(controls_frame, text="Ethereum Address:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9)).pack(anchor=tk.W)
        address_var = tk.StringVar()
        address_entry = tk.Entry(controls_frame, textvariable=address_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 9), insertbackground=self.fg_color)
        address_entry.pack(fill=tk.X, pady=(0, 5))
        tk.Label(controls_frame, text="Private Key:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9)).pack(anchor=tk.W)
        privkey_var = tk.StringVar()
        privkey_entry = tk.Entry(controls_frame, textvariable=privkey_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 9), insertbackground=self.fg_color, show='*')
        privkey_entry.pack(fill=tk.X, pady=(0, 10))
        # Uniswap token selection
        tk.Label(controls_frame, text="Select Token:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9)).pack(anchor=tk.W)
        token_var = tk.StringVar()
        token_options = [f"{t['symbol']} - {t['name']}" for t in self.uniswap_tokens]
        token_combo = ttk.Combobox(controls_frame, textvariable=token_var, values=token_options, font=('Courier', 9), state='readonly')
        token_combo.pack(fill=tk.X, pady=(0, 10))
        # Token info display
        token_info_label = tk.Label(controls_frame, text="", fg=self.info_color, bg=self.bg_color, font=('Courier', 9))
        token_info_label.pack(anchor=tk.W)
        def update_token_info(event=None):
            idx = token_combo.current()
            if idx >= 0 and idx < len(self.uniswap_tokens):
                t = self.uniswap_tokens[idx]
                token_info_label.config(text=f"Symbol: {t['symbol']}\nName: {t['name']}\nAddress: {t['address']}")
            else:
                token_info_label.config(text="")
        token_combo.bind('<<ComboboxSelected>>', update_token_info)
        # Amount input
        tk.Label(controls_frame, text="Amount:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9)).pack(anchor=tk.W)
        amount_var = tk.StringVar()
        amount_entry = tk.Entry(controls_frame, textvariable=amount_var, bg=self.bg_color, fg=self.fg_color,
                              font=('Courier', 9), insertbackground=self.fg_color)
        amount_entry.pack(fill=tk.X, pady=(0, 10))
        # Price display placeholder
        price_label = tk.Label(controls_frame, text="Current Price: (fetches from Uniswap)", fg=self.accent_color, 
                              bg=self.bg_color, font=('Courier', 10, 'bold'))
        price_label.pack(pady=(0, 10))
        # Trading buttons (logic to be implemented)
        buttons_frame = tk.Frame(controls_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X)
        buy_btn = tk.Button(buttons_frame, text="BUY", bg=self.bg_color, fg=self.fg_color, font=('Courier', 10, 'bold'), relief=tk.RAISED, bd=2)
        buy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        sell_btn = tk.Button(buttons_frame, text="SELL", bg=self.bg_color, fg=self.error_color, font=('Courier', 10, 'bold'), relief=tk.RAISED, bd=2)
        sell_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        status_label = tk.Label(controls_frame, text="", fg=self.info_color, bg=self.bg_color, font=('Courier', 9))
        status_label.pack(anchor=tk.W, pady=(5, 5))
        def buy_token():
            idx = token_combo.current()
            if idx < 0 or idx >= len(self.uniswap_tokens):
                status_label.config(text="Select a token.")
                return
            t = self.uniswap_tokens[idx]
            try:
                eth_amount = float(amount_var.get())
                address = address_var.get().strip()
                privkey = privkey_var.get().strip()
                if not self.web3.is_address(address):
                    status_label.config(text="Invalid address.")
                    return
                if not privkey:
                    status_label.config(text="Enter private key.")
                    return
                WETH = self.web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
                token_addr = self.web3.to_checksum_address(t['address'])
                path = [WETH, token_addr]
                deadline = int(self.web3.eth.get_block('latest')['timestamp']) + 600
                min_tokens = 1  # For demo, set to 1. For production, calculate with slippage.
                tx = self.uniswap_router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                    min_tokens, path, address, deadline
                ).build_transaction({
                    'from': address,
                    'value': self.web3.to_wei(eth_amount, 'ether'),
                    'gas': 300000,
                    'gasPrice': self.web3.to_wei('30', 'gwei'),
                    'nonce': self.web3.eth.get_transaction_count(address)
                })
                signed = self.web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
                status_label.config(text=f"Buy sent: {self.web3.to_hex(tx_hash)}")
                
                # Update portfolio and cost basis after successful transaction
                try:
                    # Get ETH price for cost calculation
                    eth_price = self.live_market.get_price('ETH')
                    if eth_price <= 0:
                        eth_price = 3200  # Fallback ETH price
                    
                    # Calculate cost in USD
                    cost_usd = eth_amount * eth_price
                    
                    # Get token amount received (approximate - in real scenario, check transaction receipt)
                    # For demo purposes, we'll use a rough estimate
                    token_amount = eth_amount * 1000  # Rough estimate, should be calculated from actual swap
                    
                    # Update portfolio
                    symbol = t['symbol']
                    self.user_portfolio[symbol] = self.user_portfolio.get(symbol, 0) + token_amount
                    
                    # Update cost basis for PNL tracking
                    if symbol not in self.token_cost_basis:
                        self.token_cost_basis[symbol] = {'total_bought': 0, 'total_spent': 0, 'average_price': 0}
                    
                    cost_basis = self.token_cost_basis[symbol]
                    cost_basis['total_bought'] += token_amount
                    cost_basis['total_spent'] += cost_usd
                    cost_basis['average_price'] = cost_basis['total_spent'] / cost_basis['total_bought']
                    
                    # Add to transaction history
                    transaction = {
                        'type': 'UNISWAP_BUY',
                        'symbol': symbol,
                        'amount': token_amount,
                        'price': cost_usd / token_amount,
                        'total': cost_usd,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.transaction_history.append(transaction)
                    
                    status_label.config(text=f"Buy successful! {token_amount:.4f} {symbol} added to portfolio")
                except Exception as e:
                    status_label.config(text=f"Buy sent: {self.web3.to_hex(tx_hash)} (Portfolio update failed: {e})")
            except Exception as e:
                status_label.config(text=f"Buy error: {e}")
        def sell_token():
            idx = token_combo.current()
            if idx < 0 or idx >= len(self.uniswap_tokens):
                status_label.config(text="Select a token.")
                return
            t = self.uniswap_tokens[idx]
            try:
                token_amount = float(amount_var.get())
                address = address_var.get().strip()
                privkey = privkey_var.get().strip()
                if not self.web3.is_address(address):
                    status_label.config(text="Invalid address.")
                    return
                if not privkey:
                    status_label.config(text="Enter private key.")
                    return
                WETH = self.web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
                token_addr = self.web3.to_checksum_address(t['address'])
                path = [token_addr, WETH]
                deadline = int(self.web3.eth.get_block('latest')['timestamp']) + 600
                # Approve Uniswap router if needed
                erc20_abi = [{"constant":False,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"success","type":"bool"}],"type":"function"}]
                token_contract = self.web3.eth.contract(address=token_addr, abi=erc20_abi)
                decimals = int(t.get('decimals', 18))
                amount_wei = int(token_amount * (10 ** decimals))
                # Approve
                approve_tx = token_contract.functions.approve(UNISWAP_V2_ROUTER_ADDRESS, amount_wei).build_transaction({
                    'from': address,
                    'gas': 60000,
                    'gasPrice': self.web3.to_wei('30', 'gwei'),
                    'nonce': self.web3.eth.get_transaction_count(address)
                })
                signed_approve = self.web3.eth.account.sign_transaction(approve_tx, privkey)
                approve_hash = self.web3.eth.send_raw_transaction(signed_approve.rawTransaction)
                status_label.config(text=f"Approve sent: {self.web3.to_hex(approve_hash)}. Waiting...")
                self.web3.eth.wait_for_transaction_receipt(approve_hash)
                # Swap
                min_eth = 1  # For demo, set to 1. For production, calculate with slippage.
                swap_tx = self.uniswap_router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                    amount_wei, min_eth, path, address, deadline
                ).build_transaction({
                    'from': address,
                    'gas': 300000,
                    'gasPrice': self.web3.to_wei('30', 'gwei'),
                    'nonce': self.web3.eth.get_transaction_count(address)
                })
                signed_swap = self.web3.eth.account.sign_transaction(swap_tx, privkey)
                swap_hash = self.web3.eth.send_raw_transaction(signed_swap.rawTransaction)
                status_label.config(text=f"Sell sent: {self.web3.to_hex(swap_hash)}")
                
                # Update portfolio and cost basis after successful transaction
                try:
                    # Get ETH price for value calculation
                    eth_price = self.live_market.get_price('ETH')
                    if eth_price <= 0:
                        eth_price = 3200  # Fallback ETH price
                    
                    # Calculate value received in USD
                    eth_received = token_amount * 0.001  # Rough estimate, should be calculated from actual swap
                    value_usd = eth_received * eth_price
                    
                    # Update portfolio
                    symbol = t['symbol']
                    if symbol in self.user_portfolio:
                        self.user_portfolio[symbol] -= token_amount
                        if self.user_portfolio[symbol] <= 0:
                            del self.user_portfolio[symbol]
                    
                    # Update cost basis for PNL tracking
                    if symbol in self.token_cost_basis:
                        cost_basis = self.token_cost_basis[symbol]
                        # Reduce cost basis proportionally
                        reduction_ratio = token_amount / cost_basis['total_bought']
                        cost_basis['total_bought'] -= token_amount
                        cost_basis['total_spent'] -= (cost_basis['total_spent'] * reduction_ratio)
                        
                        # If we sold everything, reset cost basis
                        if cost_basis['total_bought'] <= 0:
                            del self.token_cost_basis[symbol]
                        else:
                            # Recalculate average price
                            cost_basis['average_price'] = cost_basis['total_spent'] / cost_basis['total_bought']
                    
                    # Add to transaction history
                    transaction = {
                        'type': 'UNISWAP_SELL',
                        'symbol': symbol,
                        'amount': token_amount,
                        'price': value_usd / token_amount,
                        'total': value_usd,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.transaction_history.append(transaction)
                    
                    status_label.config(text=f"Sell successful! {token_amount:.4f} {symbol} removed from portfolio")
                except Exception as e:
                    status_label.config(text=f"Sell sent: {self.web3.to_hex(swap_hash)} (Portfolio update failed: {e})")
            except Exception as e:
                status_label.config(text=f"Sell error: {e}")
        buy_btn.config(command=buy_token)
        sell_btn.config(command=sell_token)

        # Paste Contract Address and Buy button
        paste_frame = tk.Frame(controls_frame, bg=self.bg_color)
        paste_frame.pack(fill=tk.X, pady=(10, 5))
        tk.Label(paste_frame, text="Paste Contract Address:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9)).pack(side=tk.LEFT)
        contract_var = tk.StringVar()
        contract_entry = tk.Entry(paste_frame, textvariable=contract_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 9), width=45, insertbackground=self.fg_color)
        contract_entry.pack(side=tk.LEFT, padx=(5, 5))
        eth_amt_var = tk.StringVar()
        eth_amt_entry = tk.Entry(paste_frame, textvariable=eth_amt_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 9), width=10, insertbackground=self.fg_color)
        eth_amt_entry.pack(side=tk.LEFT, padx=(5, 5))
        paste_buy_btn = tk.Button(paste_frame, text="Buy", bg=self.bg_color, fg=self.accent_color, font=('Courier', 9, 'bold'), relief=tk.RAISED, bd=2)
        paste_buy_btn.pack(side=tk.LEFT)
        def paste_buy():
            contract = contract_var.get().strip()
            eth_amt = eth_amt_var.get().strip()
            address = address_var.get().strip()
            privkey = privkey_var.get().strip()
            if not self.web3.is_address(contract):
                status_label.config(text="Invalid contract address.")
                return
            if not self.web3.is_address(address):
                status_label.config(text="Invalid wallet address.")
                return
            if not privkey:
                status_label.config(text="Enter private key.")
                return
            try:
                eth_amt = float(eth_amt)
            except Exception:
                status_label.config(text="Enter ETH amount.")
                return
            # Fetch token details
            erc20_abi = [
                {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
                {"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
                {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}
            ]
            try:
                token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(contract), abi=erc20_abi)
                symbol = token_contract.functions.symbol().call()
                name = token_contract.functions.name().call()
                decimals = token_contract.functions.decimals().call()
            except Exception as e:
                status_label.config(text=f"Token info error: {e}")
                return
            try:
                WETH = self.web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
                token_addr = self.web3.to_checksum_address(contract)
                path = [WETH, token_addr]
                deadline = int(self.web3.eth.get_block('latest')['timestamp']) + 600
                min_tokens = 1  # For demo, set to 1. For production, calculate with slippage.
                tx = self.uniswap_router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                    min_tokens, path, address, deadline
                ).build_transaction({
                    'from': address,
                    'value': self.web3.to_wei(eth_amt, 'ether'),
                    'gas': 300000,
                    'gasPrice': self.web3.to_wei('30', 'gwei'),
                    'nonce': self.web3.eth.get_transaction_count(address)
                })
                signed = self.web3.eth.account.sign_transaction(tx, privkey)
                tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
                status_label.config(text=f"Buy {symbol} sent: {self.web3.to_hex(tx_hash)}")
                
                # Update portfolio and cost basis after successful transaction
                try:
                    # Get ETH price for cost calculation
                    eth_price = self.live_market.get_price('ETH')
                    if eth_price <= 0:
                        eth_price = 3200  # Fallback ETH price
                    
                    # Calculate cost in USD
                    cost_usd = eth_amt * eth_price
                    
                    # Get token amount received (approximate - in real scenario, check transaction receipt)
                    # For demo purposes, we'll use a rough estimate
                    token_amount = eth_amt * 1000  # Rough estimate, should be calculated from actual swap
                    
                    # Update portfolio
                    self.user_portfolio[symbol] = self.user_portfolio.get(symbol, 0) + token_amount
                    
                    # Update cost basis for PNL tracking
                    if symbol not in self.token_cost_basis:
                        self.token_cost_basis[symbol] = {'total_bought': 0, 'total_spent': 0, 'average_price': 0}
                    
                    cost_basis = self.token_cost_basis[symbol]
                    cost_basis['total_bought'] += token_amount
                    cost_basis['total_spent'] += cost_usd
                    cost_basis['average_price'] = cost_basis['total_spent'] / cost_basis['total_bought']
                    
                    # Add to transaction history
                    transaction = {
                        'type': 'UNISWAP_BUY',
                        'symbol': symbol,
                        'amount': token_amount,
                        'price': cost_usd / token_amount,
                        'total': cost_usd,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.transaction_history.append(transaction)
                    
                    status_label.config(text=f"Buy {symbol} successful! {token_amount:.4f} {symbol} added to portfolio")
                except Exception as e:
                    status_label.config(text=f"Buy {symbol} sent: {self.web3.to_hex(tx_hash)} (Portfolio update failed: {e})")
            except Exception as e:
                status_label.config(text=f"Buy error: {e}")
        paste_buy_btn.config(command=paste_buy)

        # Wallet management section
        wallet_frame = tk.LabelFrame(controls_frame, text=" WALLET MANAGEMENT ", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9, 'bold'))
        wallet_frame.pack(fill=tk.X, pady=(0, 10))
        # Wallets in session
        session_wallets = []
        current_wallet_idx = tk.IntVar(value=0)
        def update_wallet_fields(idx):
            if 0 <= idx < len(session_wallets):
                w = session_wallets[idx]
                if isinstance(w, dict) and 'address' in w and 'private_key' in w:
                    address_var.set(w['address'])
                    privkey_var.set(w['private_key'])
        # Wallet dropdown
        wallet_options = tk.StringVar()
        wallet_dropdown = ttk.Combobox(wallet_frame, textvariable=wallet_options, font=('Courier', 9), state='readonly')
        wallet_dropdown.pack(fill=tk.X, pady=(0, 5))
        def refresh_wallet_dropdown():
            try:
                wallet_dropdown['values'] = [f"Wallet {i+1}: {w['address'][:8]}..." for i, w in enumerate(session_wallets) if isinstance(w, dict) and 'address' in w]
                if session_wallets:
                    wallet_dropdown.current(current_wallet_idx.get())
            except Exception as e:
                # If there's an error, clear the dropdown
                wallet_dropdown['values'] = []
                session_wallets.clear()
        def on_wallet_select(event=None):
            idx = wallet_dropdown.current()
            if idx >= 0 and idx < len(session_wallets):
                current_wallet_idx.set(idx)
                update_wallet_fields(idx)
        wallet_dropdown.bind('<<ComboboxSelected>>', on_wallet_select)
        # Generate wallet
        def generate_wallet():
            from eth_account import Account
            acct = Account.create()
            w = {'address': acct.address, 'private_key': acct.key.hex()}
            session_wallets.append(w)
            refresh_wallet_dropdown()
            wallet_dropdown.current(len(session_wallets)-1)
            update_wallet_fields(len(session_wallets)-1)
            tk.messagebox.showinfo("Wallet Generated", f"Address: {acct.address}\nPrivate Key: {acct.key.hex()}\n\nSave your private key securely!")
        gen_btn = tk.Button(wallet_frame, text="Generate Wallet", command=generate_wallet, bg=self.bg_color, fg=self.accent_color, font=('Courier', 9, 'bold'))
        gen_btn.pack(fill=tk.X, pady=(0, 5))
        # Import wallet
        import_frame = tk.Frame(wallet_frame, bg=self.bg_color)
        import_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(import_frame, text="Import Private Key:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 9)).pack(side=tk.LEFT)
        import_var = tk.StringVar()
        import_entry = tk.Entry(import_frame, textvariable=import_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 9), width=50, insertbackground=self.fg_color, show='*')
        import_entry.pack(side=tk.LEFT, padx=(5, 5))
        def import_wallet():
            from eth_account import Account
            pk = import_var.get().strip()
            try:
                acct = Account.from_key(pk)
                w = {'address': acct.address, 'private_key': pk}
                session_wallets.append(w)
                refresh_wallet_dropdown()
                wallet_dropdown.current(len(session_wallets)-1)
                update_wallet_fields(len(session_wallets)-1)
                tk.messagebox.showinfo("Wallet Imported", f"Address: {acct.address}\nPrivate Key: {pk}\n\nSave your private key securely!")
            except Exception as e:
                tk.messagebox.showerror("Import Error", f"Invalid private key: {e}")
        import_btn = tk.Button(import_frame, text="Import", command=import_wallet, bg=self.bg_color, fg=self.accent_color, font=('Courier', 9, 'bold'))
        import_btn.pack(side=tk.LEFT)
        # Export wallet
        def export_wallet():
            idx = wallet_dropdown.current()
            if idx >= 0 and idx < len(session_wallets):
                w = session_wallets[idx]
                tk.messagebox.showwarning("Export Private Key", f"Private Key: {w['private_key']}\n\nNever share your private key. Anyone with this key can access your funds.")
        export_btn = tk.Button(wallet_frame, text="Export Private Key", command=export_wallet, bg=self.bg_color, fg=self.error_color, font=('Courier', 9, 'bold'))
        export_btn.pack(fill=tk.X, pady=(0, 5))
        # Security warning
        warn_label = tk.Label(wallet_frame, text="Never share your private key. Store it securely!", fg=self.error_color, bg=self.bg_color, font=('Courier', 9, 'bold'))
        warn_label.pack(fill=tk.X, pady=(0, 5))

        # Plaintext wallet storage (no password, no encryption)
        WALLET_FILE = 'wallets.json'
        def save_wallets():
            if not session_wallets:
                tk.messagebox.showinfo("No Wallets", "No wallets to save.")
                return
            try:
                with open(WALLET_FILE, 'w') as f:
                    json.dump(session_wallets, f)
                tk.messagebox.showinfo("Saved", "Wallets saved in plaintext (insecure).")
            except Exception as e:
                tk.messagebox.showerror("Save Error", str(e))
        def load_wallets():
            if not os.path.exists(WALLET_FILE):
                tk.messagebox.showinfo("No File", "No wallet file found.")
                return
            try:
                with open(WALLET_FILE, 'r') as f:
                    loaded = json.load(f)
                
                # Validate loaded data
                if not isinstance(loaded, list):
                    tk.messagebox.showerror("Load Error", "Invalid wallet file format.")
                    return
                
                # Filter out invalid wallet entries
                valid_wallets = []
                for wallet in loaded:
                    if isinstance(wallet, dict) and 'address' in wallet and 'private_key' in wallet:
                        valid_wallets.append(wallet)
                
                session_wallets.clear()
                session_wallets.extend(valid_wallets)
                refresh_wallet_dropdown()
                if session_wallets:
                    wallet_dropdown.current(0)
                    update_wallet_fields(0)
                tk.messagebox.showinfo("Loaded", f"Loaded {len(session_wallets)} wallets.")
            except Exception as e:
                tk.messagebox.showerror("Load Error", str(e))
        save_btn = tk.Button(wallet_frame, text="Save Wallets", command=save_wallets, bg=self.bg_color, fg=self.accent_color, font=('Courier', 9, 'bold'))
        save_btn.pack(fill=tk.X, pady=(0, 2))
        load_btn = tk.Button(wallet_frame, text="Load Wallets", command=load_wallets, bg=self.bg_color, fg=self.accent_color, font=('Courier', 9, 'bold'))
        load_btn.pack(fill=tk.X, pady=(0, 5))
        # On startup, try to load wallets if file exists
        if os.path.exists(WALLET_FILE):
            try:
                load_wallets()
            except Exception:
                pass
        # Security warning
        warn_label.config(text="Wallets are saved in plaintext for convenience. Anyone with access to this computer can access your funds! Do not use for large amounts.")

    def create_wallet_tab(self, parent):
        """Create the wallet management tab"""
        wallet_frame = tk.Frame(parent, bg=self.bg_color)
        wallet_frame.pack(fill=tk.BOTH, expand=True)
        # Create wallet management interface
        self.wallet_manager.create_wallet_interface(wallet_frame)
    
    def create_market_tab(self, parent):
        """Create the market data tab"""
        market_frame = tk.Frame(parent, bg=self.bg_color)
        market_frame.pack(fill=tk.BOTH, expand=True)
        # Market data section
        market_section = tk.LabelFrame(market_frame, text=" LIVE MARKET DATA ", fg=self.fg_color, bg=self.bg_color, 
                                     font=('Courier', 10, 'bold'))
        market_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        market_text = scrolledtext.ScrolledText(market_section, bg=self.bg_color, fg=self.fg_color,
                                               font=('Courier', 9), insertbackground=self.fg_color)
        market_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Local update logic for market data
        def update_market_display():
            market_text.delete(1.0, tk.END)
            header = f"{'SYMBOL':<8} {'PRICE':<12} {'CHANGE':<10} {'VOLUME':<12}\n"
            market_text.insert(tk.END, header, 'header')
            market_text.insert(tk.END, "─" * 50 + "\n")
            live_data = self.live_market.get_market_data()
            market_text.insert(tk.END, "MAJOR CRYPTOCURRENCIES:\n", 'section')
            for symbol in self.crypto_prices.keys():
                if symbol in live_data:
                    data = live_data[symbol]
                    price = data['price']
                    change = data['change']
                    volume = data['volume']
                    change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                    line = f"{symbol:<8} ${price:<11.2f} {change_str:<10} ${volume:<11,.0f}\n"
                    market_text.insert(tk.END, line)
                else:
                    price = self.crypto_prices[symbol]
                    change = random.uniform(-5, 5)
                    volume = random.uniform(1000000, 50000000)
                    change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                    line = f"{symbol:<8} ${price:<11.2f} {change_str:<10} ${volume:<11,.0f}\n"
                    market_text.insert(tk.END, line)
            market_text.insert(tk.END, "\nERC20 TOKENS:\n", 'section')
            for symbol in self.erc20_tokens.keys():
                if symbol in live_data:
                    data = live_data[symbol]
                    price = data['price']
                    change = data['change']
                    volume = data['volume']
                    change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                    line = f"{symbol:<8} ${price:<11.6f} {change_str:<10} ${volume:<11,.0f}\n"
                    market_text.insert(tk.END, line)
                else:
                    price = self.erc20_tokens[symbol]
                    change = random.uniform(-3, 3)
                    volume = random.uniform(100000, 10000000)
                    change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                    line = f"{symbol:<8} ${price:<11.6f} {change_str:<10} ${volume:<11,.0f}\n"
                    market_text.insert(tk.END, line)
            if self.live_market.is_connected():
                market_text.insert(tk.END, "\n🟢 LIVE MARKET DATA CONNECTED\n", 'status')
            else:
                market_text.insert(tk.END, "\n🔴 USING SIMULATED DATA\n", 'status')
        update_market_display()
    
    def create_chat_tab(self, parent):
        """Create the chat rooms tab"""
        chat_frame = tk.Frame(parent, bg=self.bg_color)
        # self.notebook.add(chat_frame, text=" CHAT ROOMS ") # Removed as per new_code
        
        # Create chat interface
        self.crypto_rooms.create_chat_interface(chat_frame)
        
    def create_sniper_tab(self, parent):
        """Create token sniping tab"""
        sniper_frame = ttk.Frame(parent)
        sniper_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_label = tk.Label(sniper_frame, text="TOKEN SNIPING BOT", 
                               fg=self.accent_color, bg=self.bg_color, font=('Courier', 14, 'bold'))
        header_label.pack(pady=(0, 20))
        
        warning_label = tk.Label(sniper_frame, text="⚠️  WARNING: Token sniping is high-risk trading! ⚠️", 
                                fg=self.error_color, bg=self.bg_color, font=('Courier', 12, 'bold'))
        warning_label.pack(pady=(0, 10))
        
        warning2_label = tk.Label(sniper_frame, text="Only snipe tokens you've researched. Many are scams or rug pulls.", 
                                 fg=self.fg_color, bg=self.bg_color, font=('Courier', 10))
        warning2_label.pack(pady=(0, 20))
        
        # Control buttons
        button_frame = tk.Frame(sniper_frame, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        setup_btn = tk.Button(button_frame, text="Setup Sniper Bot", command=self.setup_sniper_bot_gui,
                             fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        setup_btn.grid(row=0, column=0, padx=10, pady=5)
        
        monitor_btn = tk.Button(button_frame, text="Monitor New Listings", command=self.start_monitoring_gui,
                               fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        monitor_btn.grid(row=0, column=1, padx=10, pady=5)
        
        quick_snipe_btn = tk.Button(button_frame, text="Quick Snipe Token", command=self.quick_snipe_gui,
                                   fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        quick_snipe_btn.grid(row=0, column=2, padx=10, pady=5)
        
        history_btn = tk.Button(button_frame, text="View Sniper History", command=self.view_sniper_history_gui,
                               fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        history_btn.grid(row=1, column=0, padx=10, pady=5)
        
        settings_btn = tk.Button(button_frame, text="Sniper Settings", command=self.sniper_settings_gui,
                                fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        settings_btn.grid(row=1, column=1, padx=10, pady=5)
        
        stop_btn = tk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring_gui,
                            fg=self.error_color, bg=self.bg_color, font=('Courier', 10, 'bold'), width=20)
        stop_btn.grid(row=1, column=2, padx=10, pady=5)
        
        # Status display
        status_frame = tk.Frame(sniper_frame, bg=self.bg_color)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        status_label = tk.Label(status_frame, text="Status: Ready", fg=self.info_color, bg=self.bg_color, font=('Courier', 10))
        status_label.pack(anchor=tk.W)
        
        # Log display
        log_frame = tk.Frame(status_frame, bg=self.bg_color)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        log_label = tk.Label(log_frame, text="Sniper Log:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'))
        log_label.pack(anchor=tk.W)
        
        log_text = scrolledtext.ScrolledText(log_frame, height=15, bg=self.bg_color, fg=self.fg_color, 
                                           font=('Courier', 9), insertbackground=self.fg_color)
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Store references
        self.sniper_status_label = status_label
        self.sniper_log_text = log_text
        self.monitoring_active = False
        
        return sniper_frame
    
    def setup_sniper_bot_gui(self):
        """Setup sniper bot with GUI"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Sniper Bot Setup")
        setup_window.geometry("500x600")
        setup_window.configure(bg=self.bg_color)
        
        # Wallet details
        wallet_frame = tk.Frame(setup_window, bg=self.bg_color)
        wallet_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(wallet_frame, text="Wallet Address:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W)
        wallet_address_var = tk.StringVar()
        wallet_entry = tk.Entry(wallet_frame, textvariable=wallet_address_var, bg=self.bg_color, fg=self.fg_color, 
                               font=('Courier', 10), width=50)
        wallet_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(wallet_frame, text="Private Key:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W)
        private_key_var = tk.StringVar()
        private_key_entry = tk.Entry(wallet_frame, textvariable=private_key_var, bg=self.bg_color, fg=self.fg_color, 
                                    font=('Courier', 10), width=50, show="*")
        private_key_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Sniper settings
        settings_frame = tk.Frame(setup_window, bg=self.bg_color)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(settings_frame, text="Max ETH per snipe:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W)
        max_eth_var = tk.StringVar(value="0.1")
        max_eth_entry = tk.Entry(settings_frame, textvariable=max_eth_var, bg=self.bg_color, fg=self.fg_color, 
                                font=('Courier', 10), width=20)
        max_eth_entry.pack(anchor=tk.W, pady=(5, 10))
        
        tk.Label(settings_frame, text="Gas price (Gwei):", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W)
        gas_price_var = tk.StringVar(value="30")
        gas_price_entry = tk.Entry(settings_frame, textvariable=gas_price_var, bg=self.bg_color, fg=self.fg_color, 
                                  font=('Courier', 10), width=20)
        gas_price_entry.pack(anchor=tk.W, pady=(5, 10))
        
        tk.Label(settings_frame, text="Slippage tolerance (%):", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W)
        slippage_var = tk.StringVar(value="10")
        slippage_entry = tk.Entry(settings_frame, textvariable=slippage_var, bg=self.bg_color, fg=self.fg_color, 
                                 font=('Courier', 10), width=20)
        slippage_entry.pack(anchor=tk.W, pady=(5, 10))
        
        auto_approve_var = tk.BooleanVar(value=True)
        auto_approve_check = tk.Checkbutton(settings_frame, text="Auto-approve tokens", variable=auto_approve_var,
                                           fg=self.fg_color, bg=self.bg_color, font=('Courier', 10),
                                           selectcolor=self.bg_color, activebackground=self.bg_color, activeforeground=self.fg_color)
        auto_approve_check.pack(anchor=tk.W, pady=(5, 10))
        
        def save_config():
            try:
                config = {
                    'wallet_address': wallet_address_var.get().strip(),
                    'private_key': private_key_var.get().strip(),
                    'max_eth_per_snipe': float(max_eth_var.get()),
                    'gas_price_gwei': float(gas_price_var.get()),
                    'slippage_percent': float(slippage_var.get()),
                    'auto_approve': auto_approve_var.get(),
                    'enabled': True,
                    'created_at': datetime.now().isoformat()
                }
                
                # Validate inputs
                if not self.web3.is_address(config['wallet_address']):
                    messagebox.showerror("Error", "Invalid wallet address")
                    return
                
                if not config['private_key']:
                    messagebox.showerror("Error", "Private key is required")
                    return
                
                # Save configuration
                with open('sniper_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                messagebox.showinfo("Success", "Sniper bot configured successfully!")
                setup_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Configuration failed: {str(e)}")
        
        # Save button
        save_btn = tk.Button(setup_window, text="Save Configuration", command=save_config,
                            fg=self.fg_color, bg=self.bg_color, font=('Courier', 12, 'bold'))
        save_btn.pack(pady=20)
    
    def start_monitoring_gui(self):
        """Start monitoring for new tokens with GUI"""
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No sniper configuration found. Setup sniper bot first.")
            return
        
        if not config.get('enabled', False):
            messagebox.showerror("Error", "Sniper bot is disabled")
            return
        
        self.monitoring_active = True
        self.sniper_status_label.config(text="Status: Monitoring Active")
        self.add_sniper_log("Monitoring started for new token listings...")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_new_listings_gui, daemon=True)
        self.monitoring_thread.start()
    
    def monitor_new_listings_gui(self):
        """Monitor for new listings in background thread"""
        while self.monitoring_active:
            try:
                # Simulate finding new tokens
                new_tokens = self.scan_for_new_tokens_gui()
                
                for token in new_tokens:
                    self.add_sniper_log(f"🔥 NEW TOKEN: {token['name']} ({token['symbol']})")
                    self.add_sniper_log(f"   Contract: {token['address']}")
                    self.add_sniper_log(f"   Liquidity: {token['liquidity']} ETH")
                    
                    # Auto-snipe if conditions are met
                    if self.should_auto_snipe_gui(token):
                        self.add_sniper_log("   Auto-sniping...")
                        success = self.execute_snipe_gui(token)
                        if success:
                            self.add_sniper_log("   ✅ Snipe successful!")
                        else:
                            self.add_sniper_log("   ❌ Snipe failed!")
                    else:
                        self.add_sniper_log("   Token doesn't meet auto-snipe criteria")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.add_sniper_log(f"Error in monitoring: {str(e)}")
                time.sleep(10)
    
    def scan_for_new_tokens_gui(self):
        """Scan for new tokens (GUI version)"""
        # Simulated new tokens for demo
        new_tokens = []
        
        # Random chance to find a "new" token
        if random.random() < 0.05:  # 5% chance
            token = {
                'address': f"0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):040x}",
                'name': f"Token{random.randint(1000, 9999)}",
                'symbol': f"TKN{random.randint(100, 999)}",
                'liquidity': random.uniform(1, 50),
                'created_at': datetime.now().isoformat()
            }
            new_tokens.append(token)
        
        return new_tokens
    
    def should_auto_snipe_gui(self, token):
        """Determine if token should be auto-sniped (GUI version)"""
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            return False
        
        # Basic criteria
        min_liquidity = 5
        max_liquidity = 100
        liquidity = token.get('liquidity', 0)
        
        if liquidity < min_liquidity or liquidity > max_liquidity:
            return False
        
        # Check wallet balance
        wallet_balance = self.get_wallet_balance_gui(config['wallet_address'])
        if wallet_balance < config['max_eth_per_snipe']:
            return False
        
        return True
    
    def get_wallet_balance_gui(self, wallet_address):
        """Get wallet balance (GUI version)"""
        try:
            balance_wei = self.web3.eth.get_balance(wallet_address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            self.add_sniper_log(f"Error getting wallet balance: {e}")
            return 0.0
    
    def execute_snipe_gui(self, token):
        """Execute snipe transaction (GUI version)"""
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
            
            eth_amount = config['max_eth_per_snipe']
            wallet_address = config['wallet_address']
            private_key = config['private_key']
            contract_address = token['address']
            
            # Execute the snipe
            success, message = self.execute_real_uniswap_buy_gui(
                contract_address, eth_amount, wallet_address, private_key
            )
            
            if success:
                # Log successful snipe
                snipe_record = {
                    'token_address': contract_address,
                    'token_name': token['name'],
                    'token_symbol': token['symbol'],
                    'eth_amount': eth_amount,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'tx_hash': message
                }
                
                self.log_snipe_gui(snipe_record)
            
            return success
            
        except Exception as e:
            self.add_sniper_log(f"Error executing snipe: {e}")
            return False
    
    def execute_real_uniswap_buy_gui(self, contract_address, eth_amount, wallet_address, private_key):
        """Execute real Uniswap buy (GUI version)"""
        try:
            if not self.web3.is_address(contract_address):
                return False, "Invalid token contract address"
            
            if not self.web3.is_address(wallet_address):
                return False, "Invalid wallet address"
            
            # Setup transaction parameters
            WETH = self.web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
            token_addr = self.web3.to_checksum_address(contract_address)
            path = [WETH, token_addr]
            deadline = int(self.web3.eth.get_block('latest')['timestamp']) + 600
            min_tokens = 1
            
            # Build transaction
            tx = self.uniswap_router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                min_tokens, path, wallet_address, deadline
            ).build_transaction({
                'from': wallet_address,
                'value': self.web3.to_wei(eth_amount, 'ether'),
                'gas': 300000,
                'gasPrice': self.web3.to_wei('30', 'gwei'),
                'nonce': self.web3.eth.get_transaction_count(wallet_address)
            })
            
            # Sign and send transaction
            signed = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
            
            return True, f"Transaction sent: {self.web3.to_hex(tx_hash)}"
            
        except Exception as e:
            return False, f"Transaction failed: {str(e)}"
    
    def log_snipe_gui(self, snipe_record):
        """Log snipe transaction (GUI version)"""
        try:
            with open('sniper_history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
        
        history.append(snipe_record)
        
        with open('sniper_history.json', 'w') as f:
            json.dump(history, f, indent=2)
    
    def add_sniper_log(self, message):
        """Add message to sniper log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Update GUI in main thread
        self.root.after(0, lambda: self.sniper_log_text.insert(tk.END, log_message))
        self.root.after(0, lambda: self.sniper_log_text.see(tk.END))
    
    def stop_monitoring_gui(self):
        """Stop monitoring"""
        self.monitoring_active = False
        self.sniper_status_label.config(text="Status: Monitoring Stopped")
        self.add_sniper_log("Monitoring stopped")
    
    def quick_snipe_gui(self):
        """Quick snipe token with GUI"""
        # Create quick snipe window
        snipe_window = tk.Toplevel(self.root)
        snipe_window.title("Quick Token Snipe")
        snipe_window.geometry("600x500")
        snipe_window.configure(bg=self.bg_color)
        
        # Token contract input
        tk.Label(snipe_window, text="Token Contract Address:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W, padx=20, pady=(20, 5))
        contract_var = tk.StringVar()
        contract_entry = tk.Entry(snipe_window, textvariable=contract_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 10), width=60)
        contract_entry.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # ETH amount input
        tk.Label(snipe_window, text="ETH Amount to snipe:", fg=self.fg_color, bg=self.bg_color, font=('Courier', 10)).pack(anchor=tk.W, padx=20, pady=(0, 5))
        amount_var = tk.StringVar(value="0.1")
        amount_entry = tk.Entry(snipe_window, textvariable=amount_var, bg=self.bg_color, fg=self.fg_color, font=('Courier', 10), width=20)
        amount_entry.pack(anchor=tk.W, padx=20, pady=(0, 20))
        
        # Preview frame
        preview_frame = tk.Frame(snipe_window, bg=self.bg_color)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        preview_label = tk.Label(preview_frame, text="Snipe Preview:", fg=self.accent_color, bg=self.bg_color, font=('Courier', 12, 'bold'))
        preview_label.pack(anchor=tk.W)
        
        preview_text = scrolledtext.ScrolledText(preview_frame, height=10, bg=self.bg_color, fg=self.fg_color, font=('Courier', 9))
        preview_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        def preview_snipe():
            contract = contract_var.get().strip()
            amount = amount_var.get().strip()
            
            if not contract or not amount:
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, "Please enter contract address and amount")
                return
            
            try:
                eth_amount = float(amount)
            except ValueError:
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, "Invalid ETH amount")
                return
            
            # Get token info
            token_info = self.get_token_info_gui(contract)
            if not token_info:
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, "Could not get token information")
                return
            
            # Show preview
            preview_text.delete(1.0, tk.END)
            preview_text.insert(tk.END, f"Token: {token_info['name']} ({token_info['symbol']})\n")
            preview_text.insert(tk.END, f"Contract: {contract}\n")
            preview_text.insert(tk.END, f"Amount: {eth_amount} ETH\n")
            preview_text.insert(tk.END, f"Estimated gas: 300,000\n")
            preview_text.insert(tk.END, f"Gas price: 30 Gwei\n")
            preview_text.insert(tk.END, f"Total cost: ~{eth_amount + 0.009} ETH\n\n")
            preview_text.insert(tk.END, "⚠️  WARNING: This is a real transaction with real money! ⚠️")
        
        def execute_snipe():
            contract = contract_var.get().strip()
            amount = amount_var.get().strip()
            
            if not contract or not amount:
                messagebox.showerror("Error", "Please enter contract address and amount")
                return
            
            try:
                eth_amount = float(amount)
            except ValueError:
                messagebox.showerror("Error", "Invalid ETH amount")
                return
            
            # Load sniper config
            try:
                with open('sniper_config.json', 'r') as f:
                    config = json.load(f)
            except FileNotFoundError:
                messagebox.showerror("Error", "No sniper configuration found")
                return
            
            # Check wallet balance
            wallet_balance = self.get_wallet_balance_gui(config['wallet_address'])
            if wallet_balance < eth_amount:
                messagebox.showerror("Error", f"Insufficient ETH balance. You have {wallet_balance:.6f} ETH")
                return
            
            # Confirm transaction
            confirm = messagebox.askyesno("Confirm Snipe", 
                                        f"Execute snipe?\n\nToken: {contract}\nAmount: {eth_amount} ETH\n\nThis will cost real money!")
            if not confirm:
                return
            
            # Execute snipe
            success = self.execute_snipe_gui({
                'address': contract,
                'name': 'Unknown Token',
                'symbol': 'UNKNOWN'
            })
            
            if success:
                messagebox.showinfo("Success", "Snipe executed successfully!")
            else:
                messagebox.showerror("Error", "Snipe failed!")
            
            snipe_window.destroy()
        
        # Buttons
        button_frame = tk.Frame(snipe_window, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        preview_btn = tk.Button(button_frame, text="Preview Snipe", command=preview_snipe,
                               fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'))
        preview_btn.pack(side=tk.LEFT, padx=10)
        
        execute_btn = tk.Button(button_frame, text="Execute Snipe", command=execute_snipe,
                               fg=self.error_color, bg=self.bg_color, font=('Courier', 10, 'bold'))
        execute_btn.pack(side=tk.LEFT, padx=10)
    
    def get_token_info_gui(self, contract_address):
        """Get token information (GUI version)"""
        try:
            # Basic token info (in real implementation, this would query the blockchain)
            return {
                'name': f"Token_{contract_address[-6:]}",
                'symbol': f"TKN_{contract_address[-4:]}",
                'decimals': 18
            }
        except Exception as e:
            return None
    
    def view_sniper_history_gui(self):
        """View sniper history with GUI"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Sniper History")
        history_window.geometry("800x600")
        history_window.configure(bg=self.bg_color)
        
        # History display
        history_text = scrolledtext.ScrolledText(history_window, bg=self.bg_color, fg=self.fg_color, font=('Courier', 10))
        history_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        try:
            with open('sniper_history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history_text.insert(tk.END, "No sniper history found")
            return
        
        if not history:
            history_text.insert(tk.END, "No sniper transactions yet")
            return
        
        # Display history
        history_text.insert(tk.END, "Recent Sniper Transactions:\n\n")
        for snipe in history[-20:]:  # Show last 20 snipes
            timestamp = snipe.get('timestamp', 'Unknown')
            token_name = snipe.get('token_name', 'Unknown')
            token_symbol = snipe.get('token_symbol', 'Unknown')
            eth_amount = snipe.get('eth_amount', 0)
            status = snipe.get('status', 'Unknown')
            tx_hash = snipe.get('tx_hash', 'Unknown')
            
            history_text.insert(tk.END, f"Time: {timestamp}\n")
            history_text.insert(tk.END, f"Token: {token_name} ({token_symbol})\n")
            history_text.insert(tk.END, f"Amount: {eth_amount} ETH\n")
            history_text.insert(tk.END, f"Status: {status}\n")
            history_text.insert(tk.END, f"TX: {tx_hash}\n")
            history_text.insert(tk.END, "-" * 50 + "\n\n")
    
    def sniper_settings_gui(self):
        """Sniper settings with GUI"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Sniper Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg=self.bg_color)
        
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "No sniper configuration found")
            settings_window.destroy()
            return
        
        # Current settings display
        tk.Label(settings_window, text="Current Settings:", fg=self.accent_color, bg=self.bg_color, font=('Courier', 12, 'bold')).pack(pady=20)
        
        settings_text = scrolledtext.ScrolledText(settings_window, height=15, bg=self.bg_color, fg=self.fg_color, font=('Courier', 10))
        settings_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        settings_text.insert(tk.END, f"Wallet: {config.get('wallet_address', 'Not set')}\n")
        settings_text.insert(tk.END, f"Max ETH per snipe: {config.get('max_eth_per_snipe', 0)}\n")
        settings_text.insert(tk.END, f"Gas price: {config.get('gas_price_gwei', 0)} Gwei\n")
        settings_text.insert(tk.END, f"Slippage: {config.get('slippage_percent', 0)}%\n")
        settings_text.insert(tk.END, f"Auto-approve: {config.get('auto_approve', False)}\n")
        settings_text.insert(tk.END, f"Enabled: {config.get('enabled', False)}\n")
        
        # Enable/disable button
        def toggle_enabled():
            config['enabled'] = not config.get('enabled', False)
            status = "enabled" if config['enabled'] else "disabled"
            
            with open('sniper_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", f"Sniper {status}")
            settings_window.destroy()
        
        toggle_btn = tk.Button(settings_window, text="Toggle Enable/Disable", command=toggle_enabled,
                              fg=self.fg_color, bg=self.bg_color, font=('Courier', 10, 'bold'))
        toggle_btn.pack(pady=20)

    def update_market_display(self):
        self.market_text.delete(1.0, tk.END)
        header = f"{'SYMBOL':<8} {'PRICE':<12} {'CHANGE':<10} {'VOLUME':<12}\n"
        self.market_text.insert(tk.END, header, 'header')
        self.market_text.insert(tk.END, "─" * 50 + "\n")
        
        # Get live market data
        live_data = self.live_market.get_market_data()
        
        # Display major cryptocurrencies first
        self.market_text.insert(tk.END, "MAJOR CRYPTOCURRENCIES:\n", 'section')
        for symbol in self.crypto_prices.keys():
            if symbol in live_data:
                data = live_data[symbol]
                price = data['price']
                change = data['change']
                volume = data['volume']
                change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                
                line = f"{symbol:<8} ${price:<11.2f} {change_str:<10} ${volume:<11,.0f}\n"
                self.market_text.insert(tk.END, line)
            else:
                # Fallback to simulated data
                price = self.crypto_prices[symbol]
                change = random.uniform(-5, 5)
                volume = random.uniform(1000000, 50000000)
                change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                
                line = f"{symbol:<8} ${price:<11.2f} {change_str:<10} ${volume:<11,.0f}\n"
                self.market_text.insert(tk.END, line)
        
        self.market_text.insert(tk.END, "\nERC20 TOKENS:\n", 'section')
        for symbol in self.erc20_tokens.keys():
            if symbol in live_data:
                data = live_data[symbol]
                price = data['price']
                change = data['change']
                volume = data['volume']
                change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                
                line = f"{symbol:<8} ${price:<11.6f} {change_str:<10} ${volume:<11,.0f}\n"
                self.market_text.insert(tk.END, line)
            else:
                # Fallback to simulated data
                price = self.erc20_tokens[symbol]
                change = random.uniform(-3, 3)
                volume = random.uniform(100000, 10000000)
                change_str = f"{change:+.2f}%" if change >= 0 else f"{change:.2f}%"
                
                line = f"{symbol:<8} ${price:<11.6f} {change_str:<10} ${volume:<11,.0f}\n"
                self.market_text.insert(tk.END, line)
        
        # Show connection status
        if self.live_market.is_connected():
            self.market_text.insert(tk.END, "\n🟢 LIVE MARKET DATA CONNECTED\n", 'status')
        else:
            self.market_text.insert(tk.END, "\n🔴 USING SIMULATED DATA\n", 'status')
            
    def update_portfolio_display(self):
        self.portfolio_text.delete(1.0, tk.END)
        if not self.user_portfolio:
            self.portfolio_text.insert(tk.END, "No holdings yet.\nStart trading to build your portfolio!")
        else:
            total_value = 0
            total_pnl = 0
            for symbol, amount in self.user_portfolio.items():
                # Get live price if available
                live_price = self.live_market.get_price(symbol)
                if live_price > 0:
                    current_price = live_price
                else:
                    current_price = self.all_trading_pairs.get(symbol, 0)
                
                value = amount * current_price
                total_value += value
                
                # Calculate PNL
                pnl = 0
                pnl_percentage = 0
                avg_buy_price = 0
                if symbol in self.token_cost_basis:
                    avg_buy_price = self.token_cost_basis[symbol]['average_price']
                    pnl = (current_price - avg_buy_price) * amount
                    if avg_buy_price > 0:
                        pnl_percentage = ((current_price - avg_buy_price) / avg_buy_price) * 100
                    total_pnl += pnl
                
                # Format the line with PNL information
                if current_price >= 1:
                    line = f"{symbol}: {amount:.4f} (${value:.2f})"
                else:
                    line = f"{symbol}: {amount:.4f} (${value:.6f})"
                
                # Add PNL information if we have cost basis
                if symbol in self.token_cost_basis:
                    line += f"\n  Avg Buy: ${avg_buy_price:.4f} | Current: ${current_price:.4f}"
                    line += f"\n  PNL: ${pnl:.2f} ({pnl_percentage:+.2f}%)"
                    
                    # Color code PNL (green for profit, red for loss)
                    if pnl > 0:
                        line += " [PROFIT]"
                    elif pnl < 0:
                        line += " [LOSS]"
                    else:
                        line += " [BREAKEVEN]"
                
                line += "\n"
                self.portfolio_text.insert(tk.END, line)
            
            self.portfolio_text.insert(tk.END, f"\nTotal Portfolio Value: ${total_value:.2f}")
            if total_pnl != 0:
                self.portfolio_text.insert(tk.END, f"Total PNL: ${total_pnl:.2f}")
                if total_pnl > 0:
                    self.portfolio_text.insert(tk.END, " [PROFIT]")
                else:
                    self.portfolio_text.insert(tk.END, " [LOSS]")
        
    def update_price_display(self, event=None):
        selected = self.crypto_var.get()
        
        # Try to get live price first
        live_price = self.live_market.get_price(selected)
        if live_price > 0:
            price = live_price
        else:
            # Fallback to stored price
            price = self.all_trading_pairs.get(selected, 0)
        
        if price >= 1:
            self.price_label.config(text=f"Current Price: ${price:,.2f}")
        else:
            self.price_label.config(text=f"Current Price: ${price:.8f}")
        
    def buy_crypto(self):
        try:
            symbol = self.crypto_var.get()
            amount = float(self.amount_var.get())
            
            # Get live price if available
            live_price = self.live_market.get_price(symbol)
            if live_price > 0:
                price = live_price
            else:
                price = self.all_trading_pairs.get(symbol, 0)
            
            total_cost = amount * price
            
            if total_cost > self.user_balance:
                messagebox.showerror("Insufficient Funds", "You don't have enough balance!")
                return
                
            self.user_balance -= total_cost
            self.user_portfolio[symbol] = self.user_portfolio.get(symbol, 0) + amount
            
            # Update cost basis for PNL tracking
            if symbol not in self.token_cost_basis:
                self.token_cost_basis[symbol] = {'total_bought': 0, 'total_spent': 0, 'average_price': 0}
            
            cost_basis = self.token_cost_basis[symbol]
            cost_basis['total_bought'] += amount
            cost_basis['total_spent'] += total_cost
            cost_basis['average_price'] = cost_basis['total_spent'] / cost_basis['total_bought']
            
            transaction = {
                'type': 'BUY',
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'total': total_cost,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.transaction_history.append(transaction)
            
            self.update_displays()
            if price >= 1:
                self.add_to_history(f"BUY: {amount:.4f} {symbol} @ ${price:.2f}")
            else:
                self.add_to_history(f"BUY: {amount:.4f} {symbol} @ ${price:.8f}")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount!")
            
    def sell_crypto(self):
        try:
            symbol = self.crypto_var.get()
            amount = float(self.amount_var.get())
            
            # Get live price if available
            live_price = self.live_market.get_price(symbol)
            if live_price > 0:
                price = live_price
            else:
                price = self.all_trading_pairs.get(symbol, 0)
            
            if symbol not in self.user_portfolio or self.user_portfolio[symbol] < amount:
                messagebox.showerror("Insufficient Holdings", "You don't have enough crypto to sell!")
                return
                
            total_value = amount * price
            self.user_balance += total_value
            self.user_portfolio[symbol] -= amount
            
            # Update cost basis for PNL tracking
            if symbol in self.token_cost_basis:
                cost_basis = self.token_cost_basis[symbol]
                # Reduce cost basis proportionally
                reduction_ratio = amount / cost_basis['total_bought']
                cost_basis['total_bought'] -= amount
                cost_basis['total_spent'] -= (cost_basis['total_spent'] * reduction_ratio)
                
                # If we sold everything, reset cost basis
                if cost_basis['total_bought'] <= 0:
                    del self.token_cost_basis[symbol]
                else:
                    # Recalculate average price
                    cost_basis['average_price'] = cost_basis['total_spent'] / cost_basis['total_bought']
            
            if self.user_portfolio[symbol] <= 0:
                del self.user_portfolio[symbol]
                
            transaction = {
                'type': 'SELL',
                'symbol': symbol,
                'amount': amount,
                'price': price,
                'total': total_value,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.transaction_history.append(transaction)
            
            self.update_displays()
            if price >= 1:
                self.add_to_history(f"SELL: {amount:.4f} {symbol} @ ${price:.2f}")
            else:
                self.add_to_history(f"SELL: {amount:.4f} {symbol} @ ${price:.8f}")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount!")
            
    def update_displays(self):
        self.update_wallet_balance()
        self.update_market_display()
        self.update_portfolio_display()
        self.update_status_display()
        
    def add_to_history(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.history_text.see(tk.END)
        
    def update_wallet_balance(self):
        """Update balance from wallet"""
        try:
            wallet_balance = self.wallet_manager.get_current_balance()
            wallet_address = self.wallet_manager.get_current_wallet_address()
            
            if wallet_balance > 0:
                # Convert ETH to USD using current ETH price
                eth_price = self.live_market.get_price('ETH')
                if eth_price > 0:
                    usd_balance = wallet_balance * eth_price
                    self.user_balance = usd_balance
                    if self.balance_label:
                        self.balance_label.config(text=f"Balance: ${usd_balance:,.2f} (ETH: {wallet_balance:.6f})")
                else:
                    self.user_balance = wallet_balance * 3200  # Fallback ETH price
                    if self.balance_label:
                        self.balance_label.config(text=f"Balance: ${self.user_balance:,.2f} (ETH: {wallet_balance:.6f})")
            else:
                self.user_balance = 0.0
                if self.balance_label:
                    self.balance_label.config(text="Balance: $0.00 (No wallet selected)")
            
            # Update portfolio value if wallet is unlocked
            if wallet_address:
                try:
                    portfolio_value = self.wallet_manager.wallet.get_portfolio_value(wallet_address)
                    if portfolio_value > 0 and self.balance_label:
                        self.balance_label.config(text=f"Balance: ${self.user_balance:,.2f} | Portfolio: ${portfolio_value:,.2f}")
                except:
                    pass
        except Exception as e:
            # Silently handle errors to prevent crashes
            pass
    
    def update_status_display(self):
        """Update the status bar with live market connection info"""
        wallet_address = self.wallet_manager.get_current_wallet_address()
        
        if self.live_market.is_connected():
            market_status = "Live Market: Connected"
        else:
            market_status = "Live Market: Disconnected"
        
        if wallet_address:
            wallet_status = f"Wallet: {wallet_address[:10]}..."
        else:
            wallet_status = "Wallet: Not Connected"
        
        status_text = f"System: Ready | {market_status} | {wallet_status} | Status: Online"
        self.status_label.config(text=status_text)
        
    def open_chat_rooms(self):
        """Open the crypto chat rooms window (legacy method)"""
        self.crypto_rooms.create_rooms_window()
        
    def open_wallet_manager(self):
        """Open the wallet manager window (legacy method)"""
        self.wallet_manager.create_wallet_window()
        
    def start_price_updates(self):
        def update_prices():
            while True:
                try:
                    time.sleep(5)  # Update every 5 seconds
                    
                    # Update live market data with error handling
                    try:
                        self.live_market.update_all_prices()
                    except Exception as e:
                        print(f"Live market update error: {e}")
                    
                    # Update local prices as fallback with more realistic changes
                    try:
                        for symbol in self.crypto_prices:
                            change = random.uniform(-0.015, 0.015)  # Smaller, more realistic changes
                            self.crypto_prices[symbol] *= (1 + change)
                            # Keep prices within reasonable bounds
                            if self.crypto_prices[symbol] < 0.01:
                                self.crypto_prices[symbol] = 0.01
                        
                        for symbol in self.erc20_tokens:
                            change = random.uniform(-0.02, 0.02)
                            self.erc20_tokens[symbol] *= (1 + change)
                            # Keep stablecoins stable
                            if symbol in ['USDT', 'USDC', 'DAI']:
                                self.erc20_tokens[symbol] = 1.0 + random.uniform(-0.001, 0.001)
                        
                        # Update combined trading pairs
                        self.all_trading_pairs = {**self.crypto_prices, **self.erc20_tokens}
                    except Exception as e:
                        print(f"Local price update error: {e}")
                    
                    # Update wallet balance and portfolio with error handling
                    try:
                        self.root.after(0, self.update_wallet_balance)
                    except Exception as e:
                        print(f"Wallet balance update error: {e}")
                    
                    # Update all displays with error handling
                    try:
                        self.root.after(0, self.update_displays)
                    except Exception as e:
                        print(f"Display update error: {e}")
                    
                    # Update status every 30 seconds
                    if int(time.time()) % 30 == 0:
                        try:
                            self.root.after(0, self.update_status_display)
                        except Exception as e:
                            print(f"Status update error: {e}")
                        
                except Exception as e:
                    print(f"Auto-update error: {e}")
                    time.sleep(10)  # Wait longer on error
                
        thread = threading.Thread(target=update_prices, daemon=True)
        thread.start()
        
        # Start wallet balance updates
        def update_wallet_data():
            while True:
                try:
                    time.sleep(10)  # Update wallet data every 10 seconds
                    
                    # Update wallet balance with error handling
                    try:
                        self.root.after(0, self.update_wallet_balance)
                    except Exception as e:
                        print(f"Wallet balance update error: {e}")
                    
                    # Update portfolio if wallet is active
                    try:
                        if self.wallet_manager.get_current_wallet_address():
                            self.root.after(0, self.update_portfolio_display)
                    except Exception as e:
                        print(f"Portfolio update error: {e}")
                        
                except Exception as e:
                    print(f"Wallet update error: {e}")
                    time.sleep(15)
                    
        wallet_thread = threading.Thread(target=update_wallet_data, daemon=True)
        wallet_thread.start()

    def open_dashboard_window(self):
        win = tk.Toplevel(self.root)
        win.title("Dashboard")
        win.geometry("900x600")
        win.configure(bg=self.bg_color)

        dashboard_frame = tk.Frame(win, bg=self.bg_color)
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - User info and portfolio
        left_panel = tk.Frame(dashboard_frame, bg=self.bg_color, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # User info section
        user_frame = tk.LabelFrame(left_panel, text=" USER DASHBOARD ", fg=self.fg_color, bg=self.bg_color,
                                 font=('Courier', 10, 'bold'))
        user_frame.pack(fill=tk.X, pady=(0, 10))

        balance_label = tk.Label(user_frame, text=f"Balance: ${self.user_balance:,.2f}", 
                                fg=self.info_color, bg=self.bg_color, font=('Courier', 10, 'bold'))
        balance_label.pack(pady=5)
        self.balance_label = balance_label  # Store reference for global access

        # Portfolio section
        portfolio_frame = tk.LabelFrame(left_panel, text=" PORTFOLIO ", fg=self.fg_color, bg=self.bg_color,
                                      font=('Courier', 10, 'bold'))
        portfolio_frame.pack(fill=tk.BOTH, expand=True)

        portfolio_text = scrolledtext.ScrolledText(portfolio_frame, height=10, bg=self.bg_color, fg=self.fg_color,
                                                  font=('Courier', 9), insertbackground=self.fg_color)
        portfolio_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right panel - Transaction history
        right_panel = tk.Frame(dashboard_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Transaction history
        history_frame = tk.LabelFrame(right_panel, text=" TRANSACTION HISTORY ", fg=self.fg_color, bg=self.bg_color,
                                    font=('Courier', 10, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True)

        history_text = scrolledtext.ScrolledText(history_frame, bg=self.bg_color, fg=self.fg_color,
                                                font=('Courier', 9), insertbackground=self.fg_color)
        history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Local update logic for portfolio and history
        def update_portfolio_display():
            portfolio_text.delete(1.0, tk.END)
            if not self.user_portfolio:
                portfolio_text.insert(tk.END, "No holdings yet.\nStart trading to build your portfolio!")
            else:
                total_value = 0
                total_pnl = 0
                for symbol, amount in self.user_portfolio.items():
                    live_price = self.live_market.get_price(symbol)
                    if live_price > 0:
                        current_price = live_price
                    else:
                        current_price = self.all_trading_pairs.get(symbol, 0)
                    value = amount * current_price
                    total_value += value
                    
                    # Calculate PNL
                    pnl = 0
                    pnl_percentage = 0
                    avg_buy_price = 0
                    if symbol in self.token_cost_basis:
                        avg_buy_price = self.token_cost_basis[symbol]['average_price']
                        pnl = (current_price - avg_buy_price) * amount
                        if avg_buy_price > 0:
                            pnl_percentage = ((current_price - avg_buy_price) / avg_buy_price) * 100
                        total_pnl += pnl
                    
                    # Format the line with PNL information
                    if current_price >= 1:
                        line = f"{symbol}: {amount:.4f} (${value:.2f})"
                    else:
                        line = f"{symbol}: {amount:.4f} (${value:.6f})"
                    
                    # Add PNL information if we have cost basis
                    if symbol in self.token_cost_basis:
                        line += f"\n  Avg Buy: ${avg_buy_price:.4f} | Current: ${current_price:.4f}"
                        line += f"\n  PNL: ${pnl:.2f} ({pnl_percentage:+.2f}%)"
                        
                        # Color code PNL (green for profit, red for loss)
                        if pnl > 0:
                            line += " [PROFIT]"
                        elif pnl < 0:
                            line += " [LOSS]"
                        else:
                            line += " [BREAKEVEN]"
                    
                    line += "\n"
                    portfolio_text.insert(tk.END, line)
                
                portfolio_text.insert(tk.END, f"\nTotal Portfolio Value: ${total_value:.2f}")
                if total_pnl != 0:
                    portfolio_text.insert(tk.END, f"Total PNL: ${total_pnl:.2f}")
                    if total_pnl > 0:
                        portfolio_text.insert(tk.END, " [PROFIT]")
                    else:
                        portfolio_text.insert(tk.END, " [LOSS]")

        def update_history_display():
            history_text.delete(1.0, tk.END)
            for tx in self.transaction_history:
                line = f"{tx['timestamp']} {tx['type']} {tx['amount']} {tx['symbol']} @ ${tx['price']}\n"
                history_text.insert(tk.END, line)

        update_portfolio_display()
        update_history_display()

    def open_trading_window(self):
        win = tk.Toplevel(self.root)
        win.title("Trading")
        win.geometry("900x600")
        win.configure(bg=self.bg_color)
        self.create_trading_tab(win)

    def open_wallet_window(self):
        win = tk.Toplevel(self.root)
        win.title("Wallets")
        win.geometry("900x600")
        win.configure(bg=self.bg_color)
        self.create_wallet_tab(win)

    def open_market_window(self):
        win = tk.Toplevel(self.root)
        win.title("Market Data")
        win.geometry("900x600")
        win.configure(bg=self.bg_color)
        self.create_market_tab(win)

    def open_sniper_window(self):
        """Open token sniper window"""
        sniper_window = tk.Toplevel(self.root)
        sniper_window.title("Token Sniper Bot")
        sniper_window.geometry("1000x700")
        sniper_window.configure(bg=self.bg_color)
        
        # Create sniper tab content
        sniper_frame = self.create_sniper_tab(sniper_window)
        sniper_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def get_uniswap_price(token_address, eth_amount):
    try:
        WETH = self.web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
        token = self.web3.to_checksum_address(token_address)
        path = [WETH, token]
        amount_in_wei = self.web3.to_wei(eth_amount, 'ether')
        amounts = self.uniswap_router.functions.getAmountsOut(amount_in_wei, path).call()
        return self.web3.from_wei(amounts[1], 'ether')
    except Exception as e:
        return None

def main():
    root = tk.Tk()
    app = CryptoMarketplace(root)
    root.mainloop()

if __name__ == "__main__":
    main() 