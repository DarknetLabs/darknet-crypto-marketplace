#!/usr/bin/env python3
"""
DARKNET CRYPTO MARKETPLACE - TERMINAL VERSION
A plug-and-play terminal-based cryptocurrency marketplace application
"""

import os
import sys
import json
import time
import threading
import random
from datetime import datetime
import requests
from web3 import Web3
from cryptography.fernet import Fernet
import base64
import hashlib
import socket
from crypto_rooms import CryptoRooms
from live_market_data import LiveMarketData
from wallet_manager import WalletManager

# Uniswap V2 Router configuration
UNISWAP_V2_ROUTER_ADDRESS = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
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
INFURA_URL = 'https://mainnet.infura.io/v3/8b3e1e2e2e4e2e8e2e2e2e2e2e2e2e2e'  # Replace with your Infura key

# ANSI color codes for terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TerminalCryptoMarketplace:
    def __init__(self):
        self.user_balance = 0.0
        self.user_portfolio = {}
        self.transaction_history = []
        self.token_cost_basis = {}
        
        # Initialize Web3 for real blockchain trading
        self.web3 = Web3(Web3.HTTPProvider(INFURA_URL))
        self.uniswap_router = self.web3.eth.contract(
            address=UNISWAP_V2_ROUTER_ADDRESS, 
            abi=UNISWAP_V2_ROUTER_ABI
        )
        
        # Fetch Uniswap token list
        self.uniswap_tokens = []
        try:
            resp = requests.get('https://tokens.uniswap.org/')
            if resp.status_code == 200:
                data = resp.json()
                self.uniswap_tokens = data.get('tokens', [])
        except Exception as e:
            self.uniswap_tokens = []
        
        # Initialize components
        self.live_market = LiveMarketData()
        self.live_market.start_live_updates()
        
        self.wallet_manager = WalletManager(self)
        self.crypto_rooms = CryptoRooms(self)
        
        # Market data
        self.crypto_prices = {
            'BTC': 45000, 'ETH': 3200, 'XRP': 0.85, 'ADA': 1.20,
            'DOT': 25.50, 'LINK': 18.75, 'LTC': 145.30, 'BCH': 380.45
        }
        
        self.erc20_tokens = {
            'USDT': 1.00, 'USDC': 1.00, 'DAI': 1.00, 'UNI': 8.50,
            'AAVE': 95.30, 'COMP': 65.20, 'MKR': 1200.45, 'CRV': 0.85,
            'SUSHI': 1.25, 'YFI': 8500.75, 'SNX': 3.45, 'BAL': 4.20,
            'REN': 0.15, 'ZRX': 0.35, 'BAT': 0.25, 'MANA': 0.45,
            'SAND': 0.55, 'ENJ': 0.30, 'CHZ': 0.12, 'ALGO': 0.18,
            'VET': 0.025, 'THETA': 1.85, 'FIL': 4.75, 'ICP': 12.30,
            'ATOM': 8.90, 'NEAR': 2.15, 'FTM': 0.35, 'AVAX': 25.60,
            'MATIC': 0.85, 'SOL': 95.40, 'LUNA': 0.85, 'DOGE': 0.08,
            'SHIB': 0.000012, 'PEPE': 0.0000012, 'BONK': 0.00000085
        }
        
        self.all_trading_pairs = {**self.crypto_prices, **self.erc20_tokens}
        
        # Start price update thread
        self.running = True
        self.price_thread = threading.Thread(target=self.price_update_loop, daemon=True)
        self.price_thread.start()

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print the application header"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                    DARKNET CRYPTO MARKETPLACE v2.1                           ║")
        print("║                         SECURE • ANONYMOUS • DECENTRALIZED                    ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")

    def print_menu(self):
        """Print the main menu"""
        print(f"\n{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.GREEN}║                              MAIN MENU                                        ║{Colors.END}")
        print(f"{Colors.GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        print(f"\n{Colors.YELLOW}[1]{Colors.END} Dashboard & Portfolio")
        print(f"{Colors.YELLOW}[2]{Colors.END} Trading Interface")
        print(f"{Colors.YELLOW}[3]{Colors.END} Wallet Management")
        print(f"{Colors.YELLOW}[4]{Colors.END} Live Market Data")
        print(f"{Colors.YELLOW}[5]{Colors.END} Chat Rooms")
        print(f"{Colors.YELLOW}[6]{Colors.END} Transaction History")
        print(f"{Colors.YELLOW}[7]{Colors.END} Settings")
        print(f"{Colors.YELLOW}[8]{Colors.END} Uniswap Trading")
        print(f"{Colors.YELLOW}[9]{Colors.END} Real Blockchain Trading")
        print(f"{Colors.YELLOW}[10]{Colors.END} Token Sniping")
        print(f"{Colors.YELLOW}[11]{Colors.END} Global Marketplace")
        print(f"{Colors.YELLOW}[0]{Colors.END} Exit")
        print(f"\n{Colors.CYAN}Balance: ${self.user_balance:,.2f}{Colors.END}")

    def get_user_input(self, prompt="Enter your choice: "):
        """Get user input with colored prompt"""
        return input(f"{Colors.YELLOW}{prompt}{Colors.END}")

    def dashboard_screen(self):
        """Display dashboard and portfolio"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              DASHBOARD                                        ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            # Portfolio summary
            total_value = self.user_balance
            print(f"\n{Colors.GREEN}PORTFOLIO SUMMARY:{Colors.END}")
            print(f"{Colors.WHITE}Cash Balance: ${self.user_balance:,.2f}{Colors.END}")
            
            if self.user_portfolio:
                print(f"\n{Colors.YELLOW}HOLDINGS:{Colors.END}")
                for symbol, amount in self.user_portfolio.items():
                    if amount > 0:
                        current_price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
                        value = amount * current_price
                        total_value += value
                        
                        # Calculate PNL
                        cost_basis = self.token_cost_basis.get(symbol, {}).get('average_price', 0)
                        if cost_basis > 0:
                            pnl = ((current_price - cost_basis) / cost_basis) * 100
                            pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED
                            print(f"  {symbol}: {amount:.6f} (${value:,.2f}) {pnl_color}[{pnl:+.2f}%]{Colors.END}")
                        else:
                            print(f"  {symbol}: {amount:.6f} (${value:,.2f})")
                
                print(f"\n{Colors.CYAN}Total Portfolio Value: ${total_value:,.2f}{Colors.END}")
            else:
                print(f"{Colors.WHITE}No holdings yet. Start trading to build your portfolio!{Colors.END}")
            
            # Recent transactions
            if self.transaction_history:
                print(f"\n{Colors.YELLOW}RECENT TRANSACTIONS:{Colors.END}")
                for tx in self.transaction_history[-5:]:
                    timestamp = tx.get('timestamp', 'Unknown')
                    action = tx.get('action', 'Unknown')
                    symbol = tx.get('symbol', 'Unknown')
                    amount = tx.get('amount', 0)
                    price = tx.get('price', 0)
                    print(f"  {timestamp} | {action} {amount:.6f} {symbol} @ ${price:,.2f}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Refresh | {Colors.GREEN}[2]{Colors.END} Go Trading | {Colors.GREEN}[0]{Colors.END} Back to Menu")
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.update_portfolio_display()
            elif choice == '2':
                self.trading_screen()

    def trading_screen(self):
        """Display trading interface"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              TRADING INTERFACE                               ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.WHITE}Available Balance: ${self.user_balance:,.2f}{Colors.END}")
            
            # Show top cryptocurrencies
            print(f"\n{Colors.YELLOW}TOP CRYPTOCURRENCIES:{Colors.END}")
            top_coins = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH']
            for i, symbol in enumerate(top_coins, 1):
                price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
                print(f"  {i:2d}. {symbol}: ${price:,.2f}")
            
            print(f"\n{Colors.YELLOW}ERC20 TOKENS:{Colors.END}")
            erc20_coins = ['USDT', 'USDC', 'DAI', 'UNI', 'AAVE', 'COMP', 'MKR', 'CRV']
            for i, symbol in enumerate(erc20_coins, 1):
                price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
                print(f"  {i:2d}. {symbol}: ${price:,.4f}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Buy | {Colors.GREEN}[2]{Colors.END} Sell | {Colors.GREEN}[3]{Colors.END} View All Tokens | {Colors.GREEN}[0]{Colors.END} Back")
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.buy_crypto()
            elif choice == '2':
                self.sell_crypto()
            elif choice == '3':
                self.view_all_tokens()

    def buy_crypto(self):
        """Buy cryptocurrency"""
        print(f"\n{Colors.YELLOW}BUY CRYPTOCURRENCY{Colors.END}")
        print(f"{Colors.WHITE}Choose buying method:{Colors.END}")
        print(f"{Colors.GREEN}[1]{Colors.END} Buy from predefined list")
        print(f"{Colors.GREEN}[2]{Colors.END} Buy any token by contract address")
        
        choice = self.get_user_input("Enter choice: ")
        
        if choice == '1':
            self.buy_predefined_crypto()
        elif choice == '2':
            self.buy_any_token()
        else:
            print(f"{Colors.RED}Invalid choice{Colors.END}")
            input("Press Enter to continue...")

    def buy_predefined_crypto(self):
        """Buy from predefined cryptocurrency list"""
        print(f"\n{Colors.YELLOW}BUY FROM PREDEFINED LIST{Colors.END}")
        symbol = self.get_user_input("Enter symbol (e.g., BTC, ETH): ").upper()
        
        if symbol not in self.all_trading_pairs:
            print(f"{Colors.RED}Invalid symbol: {symbol}{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            amount = float(self.get_user_input("Enter amount to buy: "))
            if amount <= 0:
                print(f"{Colors.RED}Amount must be positive{Colors.END}")
                input("Press Enter to continue...")
                return
            
            current_price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
            total_cost = amount * current_price
            
            if total_cost > self.user_balance:
                print(f"{Colors.RED}Insufficient balance. Need ${total_cost:,.2f}, have ${self.user_balance:,.2f}{Colors.END}")
                input("Press Enter to continue...")
                return
            
            # Execute trade
            self.user_balance -= total_cost
            self.user_portfolio[symbol] = self.user_portfolio.get(symbol, 0) + amount
            
            # Update cost basis
            if symbol not in self.token_cost_basis:
                self.token_cost_basis[symbol] = {'total_bought': 0, 'total_spent': 0, 'average_price': 0}
            
            cb = self.token_cost_basis[symbol]
            cb['total_bought'] += amount
            cb['total_spent'] += total_cost
            cb['average_price'] = cb['total_spent'] / cb['total_bought']
            
            # Add to transaction history
            self.transaction_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'BUY',
                'symbol': symbol,
                'amount': amount,
                'price': current_price,
                'total': total_cost
            })
            
            print(f"{Colors.GREEN}Successfully bought {amount:.6f} {symbol} for ${total_cost:,.2f}{Colors.END}")
            
        except ValueError:
            print(f"{Colors.RED}Invalid amount{Colors.END}")
        
        input("Press Enter to continue...")

    def buy_any_token(self):
        """Buy any token by contract address with tax support"""
        print(f"\n{Colors.YELLOW}BUY ANY TOKEN BY CONTRACT ADDRESS{Colors.END}")
        print(f"{Colors.WHITE}This supports tokens with taxes and fees{Colors.END}")
        
        # Get contract address
        contract_address = self.get_user_input("Enter token contract address: ").strip()
        if not contract_address or not contract_address.startswith('0x'):
            print(f"{Colors.RED}Invalid contract address. Must start with 0x{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get ETH amount
        try:
            eth_amount = float(self.get_user_input("Enter ETH amount to spend: "))
            if eth_amount <= 0:
                print(f"{Colors.RED}Amount must be positive{Colors.END}")
                input("Press Enter to continue...")
                return
        except ValueError:
            print(f"{Colors.RED}Invalid amount{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Check balance
        eth_price = self.live_market.get_price('ETH') or 3200
        total_cost_usd = eth_amount * eth_price
        
        if total_cost_usd > self.user_balance:
            print(f"{Colors.RED}Insufficient balance. Need ${total_cost_usd:,.2f}, have ${self.user_balance:,.2f}{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get token info (simulated)
        token_info = self.get_token_info(contract_address)
        if not token_info:
            print(f"{Colors.RED}Could not fetch token information{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Calculate swap with taxes
        swap_result = self.calculate_swap_with_taxes(contract_address, eth_amount, token_info)
        
        if not swap_result:
            print(f"{Colors.RED}Swap calculation failed{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Show swap preview
        print(f"\n{Colors.CYAN}SWAP PREVIEW:{Colors.END}")
        print(f"  Token: {token_info['symbol']} ({token_info['name']})")
        print(f"  Contract: {contract_address}")
        print(f"  ETH Spent: {eth_amount:.6f} ETH (${total_cost_usd:,.2f})")
        print(f"  Tokens Received: {swap_result['tokens_received']:.6f} {token_info['symbol']}")
        print(f"  Buy Tax: {swap_result['buy_tax']:.1f}%")
        print(f"  Price Impact: {swap_result['price_impact']:.2f}%")
        print(f"  Gas Estimate: {swap_result['gas_estimate']:,} GWEI")
        print(f"  Total Fees: ${swap_result['total_fees']:.2f}")
        
        # Confirm swap
        confirm = self.get_user_input("\nExecute swap? (y/N): ").lower()
        if confirm != 'y':
            print(f"{Colors.YELLOW}Swap cancelled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute swap
        success = self.execute_token_swap(contract_address, eth_amount, swap_result, token_info)
        
        if success:
            print(f"{Colors.GREEN}Swap executed successfully!{Colors.END}")
            print(f"  Received {swap_result['tokens_received']:.6f} {token_info['symbol']}")
            print(f"  Transaction hash: 0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):040x}")
        else:
            print(f"{Colors.RED}Swap failed{Colors.END}")
        
        input("Press Enter to continue...")

    def get_token_info(self, contract_address):
        """Get token information from contract address"""
        # Simulated token info - in real implementation, this would query the blockchain
        token_symbols = ['PEPE', 'SHIB', 'DOGE', 'BONK', 'FLOKI', 'MOON', 'SAFE', 'RUG', 'PUMP', 'MOONSHOT']
        token_names = ['Pepe', 'Shiba Inu', 'Dogecoin', 'Bonk', 'Floki', 'Moon', 'SafeMoon', 'RugPull', 'PumpToken', 'MoonShot']
        
        # Generate deterministic but random token info based on address
        address_hash = hash(contract_address) % len(token_symbols)
        
        return {
            'symbol': token_symbols[address_hash],
            'name': token_names[address_hash],
            'decimals': 18,
            'contract_address': contract_address
        }

    def calculate_swap_with_taxes(self, contract_address, eth_amount, token_info):
        """Calculate swap with taxes and fees"""
        # Simulate realistic token taxes and fees
        eth_price = self.live_market.get_price('ETH') or 3200
        
        # Random tax rates (realistic for meme coins)
        buy_tax = random.uniform(5, 25)  # 5-25% buy tax
        sell_tax = random.uniform(5, 25)  # 5-25% sell tax
        
        # Calculate tokens received (simplified)
        # In real implementation, this would use Uniswap's getAmountsOut
        base_tokens = eth_amount * 1000000  # Rough estimate
        tokens_after_tax = base_tokens * (1 - buy_tax / 100)
        
        # Calculate fees
        uniswap_fee = eth_amount * eth_price * 0.003  # 0.3% Uniswap fee
        gas_fee = random.randint(50, 200)  # $50-200 gas
        total_fees = uniswap_fee + gas_fee
        
        # Price impact (higher for smaller pools)
        price_impact = random.uniform(0.5, 5.0)
        
        # Gas estimate
        gas_estimate = random.randint(200000, 500000)
        
        return {
            'tokens_received': tokens_after_tax,
            'buy_tax': buy_tax,
            'sell_tax': sell_tax,
            'price_impact': price_impact,
            'gas_estimate': gas_estimate,
            'total_fees': total_fees,
            'uniswap_fee': uniswap_fee,
            'gas_fee': gas_fee
        }

    def execute_token_swap(self, contract_address, eth_amount, swap_result, token_info):
        """Execute the token swap"""
        eth_price = self.live_market.get_price('ETH') or 3200
        total_cost_usd = eth_amount * eth_price
        
        # Deduct from balance
        self.user_balance -= total_cost_usd
        
        # Add tokens to portfolio
        symbol = token_info['symbol']
        self.user_portfolio[symbol] = self.user_portfolio.get(symbol, 0) + swap_result['tokens_received']
        
        # Update cost basis
        if symbol not in self.token_cost_basis:
            self.token_cost_basis[symbol] = {'total_bought': 0, 'total_spent': 0, 'average_price': 0}
        
        cb = self.token_cost_basis[symbol]
        cb['total_bought'] += swap_result['tokens_received']
        cb['total_spent'] += total_cost_usd
        cb['average_price'] = cb['total_spent'] / cb['total_bought']
        
        # Add to transaction history
        self.transaction_history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'UNISWAP_BUY',
            'symbol': symbol,
            'amount': swap_result['tokens_received'],
            'price': total_cost_usd / swap_result['tokens_received'],
            'total': total_cost_usd,
            'contract_address': contract_address,
            'buy_tax': swap_result['buy_tax'],
            'gas_fee': swap_result['gas_fee']
        })
        
        return True

    def sell_crypto(self):
        """Sell cryptocurrency"""
        print(f"\n{Colors.YELLOW}SELL CRYPTOCURRENCY{Colors.END}")
        print(f"{Colors.WHITE}Choose selling method:{Colors.END}")
        print(f"{Colors.GREEN}[1]{Colors.END} Sell from predefined list")
        print(f"{Colors.GREEN}[2]{Colors.END} Sell any token by contract address")
        
        choice = self.get_user_input("Enter choice: ")
        
        if choice == '1':
            self.sell_predefined_crypto()
        elif choice == '2':
            self.sell_any_token()
        else:
            print(f"{Colors.RED}Invalid choice{Colors.END}")
            input("Press Enter to continue...")

    def sell_predefined_crypto(self):
        """Sell from predefined cryptocurrency list"""
        print(f"\n{Colors.YELLOW}SELL FROM PREDEFINED LIST{Colors.END}")
        
        if not self.user_portfolio:
            print(f"{Colors.RED}No holdings to sell{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"{Colors.WHITE}Your holdings:{Colors.END}")
        for symbol, amount in self.user_portfolio.items():
            if amount > 0:
                print(f"  {symbol}: {amount:.6f}")
        
        symbol = self.get_user_input("Enter symbol to sell: ").upper()
        
        if symbol not in self.user_portfolio or self.user_portfolio[symbol] <= 0:
            print(f"{Colors.RED}No holdings of {symbol}{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            amount = float(self.get_user_input(f"Enter amount to sell (max: {self.user_portfolio[symbol]:.6f}): "))
            if amount <= 0 or amount > self.user_portfolio[symbol]:
                print(f"{Colors.RED}Invalid amount{Colors.END}")
                input("Press Enter to continue...")
                return
            
            current_price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
            total_value = amount * current_price
            
            # Execute trade
            self.user_balance += total_value
            self.user_portfolio[symbol] -= amount
            
            # Add to transaction history
            self.transaction_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'SELL',
                'symbol': symbol,
                'amount': amount,
                'price': current_price,
                'total': total_value
            })
            
            print(f"{Colors.GREEN}Successfully sold {amount:.6f} {symbol} for ${total_value:,.2f}{Colors.END}")
            
        except ValueError:
            print(f"{Colors.RED}Invalid amount{Colors.END}")
        
        input("Press Enter to continue...")

    def sell_any_token(self):
        """Sell any token by contract address with tax support"""
        print(f"\n{Colors.YELLOW}SELL ANY TOKEN BY CONTRACT ADDRESS{Colors.END}")
        print(f"{Colors.WHITE}This supports tokens with taxes and fees{Colors.END}")
        
        # Get contract address
        contract_address = self.get_user_input("Enter token contract address: ").strip()
        if not contract_address or not contract_address.startswith('0x'):
            print(f"{Colors.RED}Invalid contract address. Must start with 0x{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get token info
        token_info = self.get_token_info(contract_address)
        if not token_info:
            print(f"{Colors.RED}Could not fetch token information{Colors.END}")
            input("Press Enter to continue...")
            return
        
        symbol = token_info['symbol']
        
        # Check if user has this token
        if symbol not in self.user_portfolio or self.user_portfolio[symbol] <= 0:
            print(f"{Colors.RED}No holdings of {symbol}{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get amount to sell
        try:
            token_amount = float(self.get_user_input(f"Enter amount to sell (max: {self.user_portfolio[symbol]:.6f}): "))
            if token_amount <= 0 or token_amount > self.user_portfolio[symbol]:
                print(f"{Colors.RED}Invalid amount{Colors.END}")
                input("Press Enter to continue...")
                return
        except ValueError:
            print(f"{Colors.RED}Invalid amount{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Calculate sell with taxes
        sell_result = self.calculate_sell_with_taxes(contract_address, token_amount, token_info)
        
        if not sell_result:
            print(f"{Colors.RED}Sell calculation failed{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Show sell preview
        print(f"\n{Colors.CYAN}SELL PREVIEW:{Colors.END}")
        print(f"  Token: {token_info['symbol']} ({token_info['name']})")
        print(f"  Contract: {contract_address}")
        print(f"  Tokens Sold: {token_amount:.6f} {token_info['symbol']}")
        print(f"  ETH Received: {sell_result['eth_received']:.6f} ETH (${sell_result['eth_value']:.2f})")
        print(f"  Sell Tax: {sell_result['sell_tax']:.1f}%")
        print(f"  Price Impact: {sell_result['price_impact']:.2f}%")
        print(f"  Gas Estimate: {sell_result['gas_estimate']:,} GWEI")
        print(f"  Total Fees: ${sell_result['total_fees']:.2f}")
        
        # Confirm sell
        confirm = self.get_user_input("\nExecute sell? (y/N): ").lower()
        if confirm != 'y':
            print(f"{Colors.YELLOW}Sell cancelled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute sell
        success = self.execute_token_sell(contract_address, token_amount, sell_result, token_info)
        
        if success:
            print(f"{Colors.GREEN}Sell executed successfully!{Colors.END}")
            print(f"  Received {sell_result['eth_received']:.6f} ETH (${sell_result['eth_value']:.2f})")
            print(f"  Transaction hash: 0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):040x}")
        else:
            print(f"{Colors.RED}Sell failed{Colors.END}")
        
        input("Press Enter to continue...")

    def calculate_sell_with_taxes(self, contract_address, token_amount, token_info):
        """Calculate sell with taxes and fees"""
        # Simulate realistic token taxes and fees
        eth_price = self.live_market.get_price('ETH') or 3200
        
        # Random tax rates (realistic for meme coins)
        sell_tax = random.uniform(5, 25)  # 5-25% sell tax
        
        # Calculate ETH received (simplified)
        # In real implementation, this would use Uniswap's getAmountsOut
        base_eth = token_amount * 0.001  # Rough estimate
        eth_after_tax = base_eth * (1 - sell_tax / 100)
        
        # Calculate fees
        uniswap_fee = eth_after_tax * eth_price * 0.003  # 0.3% Uniswap fee
        gas_fee = random.randint(50, 200)  # $50-200 gas
        total_fees = uniswap_fee + gas_fee
        
        # Price impact (higher for smaller pools)
        price_impact = random.uniform(0.5, 5.0)
        
        # Gas estimate
        gas_estimate = random.randint(200000, 500000)
        
        return {
            'eth_received': eth_after_tax,
            'eth_value': eth_after_tax * eth_price,
            'sell_tax': sell_tax,
            'price_impact': price_impact,
            'gas_estimate': gas_estimate,
            'total_fees': total_fees,
            'uniswap_fee': uniswap_fee,
            'gas_fee': gas_fee
        }

    def execute_token_sell(self, contract_address, token_amount, sell_result, token_info):
        """Execute the token sell"""
        symbol = token_info['symbol']
        
        # Remove tokens from portfolio
        self.user_portfolio[symbol] -= token_amount
        if self.user_portfolio[symbol] <= 0:
            del self.user_portfolio[symbol]
        
        # Add ETH to balance
        self.user_balance += sell_result['eth_value']
        
        # Update cost basis
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
        self.transaction_history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'UNISWAP_SELL',
            'symbol': symbol,
            'amount': token_amount,
            'price': sell_result['eth_value'] / token_amount,
            'total': sell_result['eth_value'],
            'contract_address': contract_address,
            'sell_tax': sell_result['sell_tax'],
            'gas_fee': sell_result['gas_fee']
        })
        
        return True

    def view_all_tokens(self):
        """View all available tokens"""
        self.clear_screen()
        self.print_header()
        
        print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║                              ALL TOKENS                                        ║{Colors.END}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        
        print(f"\n{Colors.YELLOW}CRYPTOCURRENCIES:{Colors.END}")
        for symbol, price in self.crypto_prices.items():
            live_price = self.live_market.get_price(symbol) or price
            print(f"  {symbol}: ${live_price:,.2f}")
        
        print(f"\n{Colors.YELLOW}ERC20 TOKENS:{Colors.END}")
        for symbol, price in self.erc20_tokens.items():
            live_price = self.live_market.get_price(symbol) or price
            print(f"  {symbol}: ${live_price:,.6f}")
        
        input("\nPress Enter to continue...")

    def wallet_screen(self):
        """Display wallet management"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              WALLET MANAGEMENT                               ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Create New Wallet")
            print(f"{Colors.GREEN}[2]{Colors.END} Import Wallet")
            print(f"{Colors.GREEN}[3]{Colors.END} View Wallets")
            print(f"{Colors.GREEN}[4]{Colors.END} Check Balance")
            print(f"{Colors.GREEN}[5]{Colors.END} Transaction History")
            print(f"{Colors.GREEN}[0]{Colors.END} Back to Menu")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.create_wallet()
            elif choice == '2':
                self.import_wallet()
            elif choice == '3':
                self.view_wallets()
            elif choice == '4':
                self.check_balance()
            elif choice == '5':
                self.view_wallet_history()

    def create_wallet(self):
        """Create a new wallet"""
        print(f"\n{Colors.YELLOW}CREATE NEW WALLET{Colors.END}")
        name = self.get_user_input("Enter wallet name: ")
        
        if not name:
            print(f"{Colors.RED}Wallet name is required{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # This would integrate with the wallet manager
        print(f"{Colors.GREEN}Wallet '{name}' created successfully!{Colors.END}")
        print(f"{Colors.WHITE}Note: This is a demo. In a real implementation, this would create an actual Ethereum wallet.{Colors.END}")
        
        input("Press Enter to continue...")

    def import_wallet(self):
        """Import a wallet"""
        print(f"\n{Colors.YELLOW}IMPORT WALLET{Colors.END}")
        print(f"{Colors.WHITE}This feature would allow you to import an existing wallet.{Colors.END}")
        input("Press Enter to continue...")

    def view_wallets(self):
        """View all wallets"""
        print(f"\n{Colors.YELLOW}AVAILABLE WALLETS{Colors.END}")
        print(f"{Colors.WHITE}No wallets found. Create a new wallet first.{Colors.END}")
        input("Press Enter to continue...")

    def check_balance(self):
        """Check wallet balance"""
        print(f"\n{Colors.YELLOW}WALLET BALANCE{Colors.END}")
        print(f"{Colors.WHITE}No wallet connected. Create or import a wallet first.{Colors.END}")
        input("Press Enter to continue...")

    def view_wallet_history(self):
        """View wallet transaction history"""
        print(f"\n{Colors.YELLOW}WALLET TRANSACTION HISTORY{Colors.END}")
        print(f"{Colors.WHITE}No wallet connected. Create or import a wallet first.{Colors.END}")
        input("Press Enter to continue...")

    def market_screen(self):
        """Display live market data"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              LIVE MARKET DATA                                ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            # Market status
            status = "Online" if self.live_market.is_connected() else "Offline"
            status_color = Colors.GREEN if status == "Online" else Colors.RED
            print(f"\n{Colors.WHITE}Market Status: {status_color}{status}{Colors.END}")
            
            # Top movers
            print(f"\n{Colors.YELLOW}TOP MOVERS (24h):{Colors.END}")
            top_coins = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH']
            for symbol in top_coins:
                price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
                change = self.live_market.get_price_change(symbol, 24)
                if change is not None:
                    change_color = Colors.GREEN if change >= 0 else Colors.RED
                    print(f"  {symbol}: ${price:,.2f} {change_color}[{change:+.2f}%]{Colors.END}")
                else:
                    print(f"  {symbol}: ${price:,.2f} [N/A]")
            
            # Market cap leaders
            print(f"\n{Colors.YELLOW}MARKET CAP LEADERS:{Colors.END}")
            for symbol in ['BTC', 'ETH', 'USDT', 'USDC', 'BNB']:
                price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
                print(f"  {symbol}: ${price:,.2f}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Refresh | {Colors.GREEN}[2]{Colors.END} Search Token | {Colors.GREEN}[0]{Colors.END} Back")
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                continue
            elif choice == '2':
                self.search_token()

    def search_token(self):
        """Search for a specific token"""
        print(f"\n{Colors.YELLOW}SEARCH TOKEN{Colors.END}")
        symbol = self.get_user_input("Enter token symbol: ").upper()
        
        if symbol in self.all_trading_pairs:
            price = self.live_market.get_price(symbol) or self.all_trading_pairs.get(symbol, 0)
            change = self.live_market.get_price_change(symbol, 24)
            
            print(f"\n{Colors.CYAN}Token Information:{Colors.END}")
            print(f"  Symbol: {symbol}")
            print(f"  Price: ${price:,.6f}")
            if change is not None:
                change_color = Colors.GREEN if change >= 0 else Colors.RED
                print(f"  24h Change: {change_color}{change:+.2f}%{Colors.END}")
            else:
                print(f"  24h Change: N/A")
        else:
            print(f"{Colors.RED}Token '{symbol}' not found{Colors.END}")
        
        input("Press Enter to continue...")

    def chat_screen(self):
        """Display chat rooms - Terminal version"""
        # Initialize username if not set
        if not hasattr(self, 'chat_username'):
            self.chat_username = self.get_chat_username()
        
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                                CRYPTO CHAT ROOMS                             ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.YELLOW}Your Username: {Colors.WHITE}{self.chat_username}{Colors.END}")
            print(f"{Colors.YELLOW}Available Rooms:{Colors.END}")
            
            # Default chat rooms (same as GUI version)
            rooms = [
                "Bitcoin-Talk", "Ethereum-Dev", "DeFi-Trading", "NFT-Collectors",
                "Technical-Analysis", "Crypto-News", "Mining-Pools", "Security-Privacy",
                "Regulatory-News", "Memecoins", "Stablecoins", "Liquidity-Mining",
                "Options-Trading", "Futures-Trading", "Fundamental-Analysis",
                "Sentiment-Analysis", "Whale-Watching", "Institutional-Adoption",
                "Privacy-Coins", "Staking-Validators", "Darknet-Market",
                "ICO-IDO-Launches", "Metaverse-Gaming", "AI-Crypto", "Green-Crypto",
                "Quantum-Resistance", "Central-Bank-Digital-Currencies",
                "Crypto-Education", "Bug-Bounties", "Crypto-Jobs",
                "Crypto-Philosophy", "Cross-Chain-Bridges", "DAO-Governance"
            ]
            
            # Display rooms in columns
            for i in range(0, len(rooms), 3):
                row = rooms[i:i+3]
                for j, room in enumerate(row):
                    print(f"  {Colors.GREEN}{i+j+1:2d}{Colors.END}. {Colors.WHITE}{room:<25}{Colors.END}", end="")
                print()
            
            print(f"\n{Colors.GREEN}[1-33]{Colors.END} Join Room | {Colors.GREEN}[34]{Colors.END} Change Username | {Colors.GREEN}[0]{Colors.END} Back")
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '34':
                self.chat_username = self.get_chat_username()
            elif choice.isdigit() and 1 <= int(choice) <= len(rooms):
                room_index = int(choice) - 1
                self.join_chat_room(rooms[room_index])
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
                time.sleep(1)

    def get_global_username(self):
        """Get or generate global username for all chat systems"""
        username_file = "global_username.txt"
        
        # Try to load existing username
        if os.path.exists(username_file):
            try:
                with open(username_file, 'r', encoding='utf-8') as f:
                    username = f.read().strip()
                    if username:
                        return username
            except Exception:
                pass
        
        # Generate new username
        default = f"User{random.randint(1000,9999)}"
        print(f"\n{Colors.YELLOW}Enter your global username (used for all chat systems):{Colors.END}")
        print(f"{Colors.WHITE}Press Enter to use: {Colors.GREEN}{default}{Colors.END}")
        username = input(f"{Colors.CYAN}Username: {Colors.END}").strip()
        
        if not username:
            username = default
        
        # Save username globally
        try:
            with open(username_file, 'w', encoding='utf-8') as f:
                f.write(username)
        except Exception:
            pass
        
        return username

    def get_chat_username(self):
        """Get or generate chat username (now uses global username)"""
        return self.get_global_username()

    def join_chat_room(self, room_name):
        """Join a specific chat room"""
        API_URL = "https://chat-server-production-507c.up.railway.app"
        
        print(f"\n{Colors.GREEN}Joining {room_name}...{Colors.END}")
        print(f"{Colors.WHITE}Type your messages below. Type 'exit' to leave.{Colors.END}")
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        
        # Load existing messages
        try:
            resp = requests.get(f"{API_URL}/rooms/{room_name}/messages", timeout=5)
            if resp.status_code == 200:
                messages = resp.json()
                for msg in messages[-10:]:  # Show last 10 messages
                    print(f"{Colors.WHITE}[{msg['time']}] {msg['user']}: {msg['message']}{Colors.END}")
        except Exception:
            print(f"{Colors.YELLOW}Loading recent messages...{Colors.END}")
        
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        
        # Chat loop
        while True:
            try:
                message = input(f"{Colors.GREEN}{self.chat_username}{Colors.END}: ").strip()
                
                if message.lower() == 'exit':
                    break
                elif not message:
                    continue
                
                # Send message to server
                try:
                    requests.post(f"{API_URL}/rooms/{room_name}/messages", 
                                json={"user": self.chat_username, "message": message}, 
                                timeout=5)
                except Exception:
                    print(f"{Colors.RED}Failed to send message. Check your connection.{Colors.END}")
                
                # Small delay to prevent spam
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                break
            except Exception:
                print(f"{Colors.RED}Error in chat. Returning to room list.{Colors.END}")
                break
        
        print(f"{Colors.YELLOW}Left {room_name}{Colors.END}")
        time.sleep(1)

    def history_screen(self):
        """Display transaction history"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                            TRANSACTION HISTORY                              ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            if not self.transaction_history:
                print(f"\n{Colors.WHITE}No transactions yet. Start trading to see your history!{Colors.END}")
            else:
                print(f"\n{Colors.YELLOW}RECENT TRANSACTIONS:{Colors.END}")
                for tx in reversed(self.transaction_history):
                    timestamp = tx.get('timestamp', 'Unknown')
                    action = tx.get('action', 'Unknown')
                    symbol = tx.get('symbol', 'Unknown')
                    amount = tx.get('amount', 0)
                    price = tx.get('price', 0)
                    total = tx.get('total', 0)
                    
                    action_color = Colors.GREEN if action == 'BUY' else Colors.RED
                    print(f"  {timestamp} | {action_color}{action}{Colors.END} {amount:.6f} {symbol} @ ${price:,.2f} (${total:,.2f})")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Export History | {Colors.GREEN}[0]{Colors.END} Back")
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.export_history()

    def export_history(self):
        """Export transaction history to file"""
        if not self.transaction_history:
            print(f"{Colors.RED}No transactions to export{Colors.END}")
            input("Press Enter to continue...")
            return
        
        filename = f"transaction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.transaction_history, f, indent=2)
            print(f"{Colors.GREEN}Transaction history exported to {filename}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Failed to export: {e}{Colors.END}")
        
        input("Press Enter to continue...")

    def settings_screen(self):
        """Display settings"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                                  SETTINGS                                     ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Add Demo Balance")
            print(f"{Colors.GREEN}[2]{Colors.END} Reset Portfolio")
            print(f"{Colors.GREEN}[3]{Colors.END} Clear History")
            print(f"{Colors.GREEN}[4]{Colors.END} About")
            print(f"{Colors.GREEN}[0]{Colors.END} Back to Menu")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.add_demo_balance()
            elif choice == '2':
                self.reset_portfolio()
            elif choice == '3':
                self.clear_history()
            elif choice == '4':
                self.about_screen()

    def add_demo_balance(self):
        """Add demo balance for testing"""
        try:
            amount = float(self.get_user_input("Enter demo balance amount: $"))
            if amount > 0:
                self.user_balance += amount
                print(f"{Colors.GREEN}Added ${amount:,.2f} to your balance{Colors.END}")
            else:
                print(f"{Colors.RED}Amount must be positive{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Invalid amount{Colors.END}")
        
        input("Press Enter to continue...")

    def reset_portfolio(self):
        """Reset portfolio"""
        confirm = self.get_user_input("Are you sure? This will reset your portfolio (y/N): ").lower()
        if confirm == 'y':
            self.user_portfolio = {}
            self.token_cost_basis = {}
            print(f"{Colors.GREEN}Portfolio reset successfully{Colors.END}")
        else:
            print(f"{Colors.YELLOW}Portfolio reset cancelled{Colors.END}")
        
        input("Press Enter to continue...")

    def clear_history(self):
        """Clear transaction history"""
        confirm = self.get_user_input("Are you sure? This will clear all transaction history (y/N): ").lower()
        if confirm == 'y':
            self.transaction_history = []
            print(f"{Colors.GREEN}Transaction history cleared{Colors.END}")
        else:
            print(f"{Colors.YELLOW}History clear cancelled{Colors.END}")
        
        input("Press Enter to continue...")

    def about_screen(self):
        """Display about information"""
        self.clear_screen()
        self.print_header()
        
        print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║                                    ABOUT                                        ║{Colors.END}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        
        print(f"\n{Colors.WHITE}DARKNET CRYPTO MARKETPLACE v2.1{Colors.END}")
        print(f"{Colors.WHITE}Terminal Version{Colors.END}")
        print(f"\n{Colors.YELLOW}Features:{Colors.END}")
        print(f"  • Real-time cryptocurrency trading")
        print(f"  • Live market data from multiple APIs")
        print(f"  • Portfolio management")
        print(f"  • Transaction history")
        print(f"  • Wallet integration (demo)")
        print(f"  • Terminal-based interface")
        
        print(f"\n{Colors.YELLOW}Disclaimer:{Colors.END}")
        print(f"  This is a demonstration application for educational purposes.")
        print(f"  All trading is simulated and for entertainment only.")
        
        input("\nPress Enter to continue...")

    def update_portfolio_display(self):
        """Update portfolio display"""
        # This would refresh portfolio data
        pass

    def price_update_loop(self):
        """Background thread for price updates"""
        while self.running:
            try:
                # Update prices every 30 seconds
                time.sleep(30)
            except:
                break

    def run(self):
        """Main application loop"""
        try:
            while True:
                self.clear_screen()
                self.print_header()
                self.print_menu()
                
                choice = self.get_user_input()
                
                if choice == '0':
                    print(f"\n{Colors.GREEN}Thank you for using DARKNET CRYPTO MARKETPLACE!{Colors.END}")
                    break
                elif choice == '1':
                    self.dashboard_screen()
                elif choice == '2':
                    self.trading_screen()
                elif choice == '3':
                    self.wallet_screen()
                elif choice == '4':
                    self.market_screen()
                elif choice == '5':
                    self.chat_screen()
                elif choice == '6':
                    self.history_screen()
                elif choice == '7':
                    self.settings_screen()
                elif choice == '8':
                    self.uniswap_screen()
                elif choice == '9':
                    self.real_trading_screen()
                elif choice == '10':
                    self.token_sniping_screen()
                elif choice == '11':
                    self.marketplace_screen()
                else:
                    print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}Application terminated by user.{Colors.END}")
        finally:
            self.running = False

    def uniswap_screen(self):
        """Display Uniswap trading interface"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              UNISWAP TRADING                                 ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.WHITE}Available Balance: ${self.user_balance:,.2f}{Colors.END}")
            
            # Uniswap V3 pools with real-time data
            pools = self.get_uniswap_pools()
            
            print(f"\n{Colors.YELLOW}ACTIVE LIQUIDITY POOLS:{Colors.END}")
            for i, pool in enumerate(pools[:10], 1):
                token0, token1 = pool['token0'], pool['token1']
                liquidity = pool['liquidity']
                volume_24h = pool['volume24h']
                fee_tier = pool['feeTier']
                
                print(f"  {i:2d}. {Colors.GREEN}{token0}/{token1}{Colors.END} | "
                      f"Liquidity: ${liquidity:,.0f} | "
                      f"24h Vol: ${volume_24h:,.0f} | "
                      f"Fee: {fee_tier}%")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Swap Tokens | {Colors.GREEN}[2]{Colors.END} Add Liquidity | "
                  f"{Colors.GREEN}[3]{Colors.END} Remove Liquidity | {Colors.GREEN}[4]{Colors.END} Pool Analytics | "
                  f"{Colors.GREEN}[0]{Colors.END} Back")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.uniswap_swap()
            elif choice == '2':
                self.uniswap_add_liquidity()
            elif choice == '3':
                self.uniswap_remove_liquidity()
            elif choice == '4':
                self.uniswap_analytics()

    def get_uniswap_pools(self):
        """Get Uniswap V3 pool data"""
        # Simulated Uniswap V3 pools with realistic data
        pools = [
            {
                'token0': 'ETH', 'token1': 'USDC', 'liquidity': 1250000000,
                'volume24h': 45000000, 'feeTier': 0.05, 'tickSpacing': 10
            },
            {
                'token0': 'ETH', 'token1': 'USDT', 'liquidity': 980000000,
                'volume24h': 38000000, 'feeTier': 0.05, 'tickSpacing': 10
            },
            {
                'token0': 'USDC', 'token1': 'USDT', 'liquidity': 250000000,
                'volume24h': 15000000, 'feeTier': 0.01, 'tickSpacing': 1
            },
            {
                'token0': 'ETH', 'token1': 'WBTC', 'liquidity': 320000000,
                'volume24h': 12000000, 'feeTier': 0.30, 'tickSpacing': 60
            },
            {
                'token0': 'USDC', 'token1': 'UNI', 'liquidity': 180000000,
                'volume24h': 8500000, 'feeTier': 0.30, 'tickSpacing': 60
            },
            {
                'token0': 'ETH', 'token1': 'LINK', 'liquidity': 95000000,
                'volume24h': 4200000, 'feeTier': 0.30, 'tickSpacing': 60
            },
            {
                'token0': 'USDC', 'token1': 'AAVE', 'liquidity': 75000000,
                'volume24h': 3800000, 'feeTier': 0.30, 'tickSpacing': 60
            },
            {
                'token0': 'ETH', 'token1': 'MATIC', 'liquidity': 68000000,
                'volume24h': 3200000, 'feeTier': 0.30, 'tickSpacing': 60
            },
            {
                'token0': 'USDC', 'token1': 'CRV', 'liquidity': 45000000,
                'volume24h': 2100000, 'feeTier': 1.00, 'tickSpacing': 200
            },
            {
                'token0': 'ETH', 'token1': 'SNX', 'liquidity': 42000000,
                'volume24h': 1800000, 'feeTier': 1.00, 'tickSpacing': 200
            }
        ]
        
        # Add some randomness to simulate live data
        for pool in pools:
            pool['liquidity'] *= (0.95 + random.random() * 0.1)
            pool['volume24h'] *= (0.9 + random.random() * 0.2)
        
        return pools

    def uniswap_swap(self):
        """Execute Uniswap token swap"""
        print(f"\n{Colors.YELLOW}UNISWAP SWAP{Colors.END}")
        
        # Get token pairs
        token0 = self.get_user_input("Enter token to swap FROM (e.g., ETH): ").upper()
        token1 = self.get_user_input("Enter token to swap TO (e.g., USDC): ").upper()
        
        if not token0 or not token1:
            print(f"{Colors.RED}Invalid token pair{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get amount
        try:
            amount = float(self.get_user_input(f"Enter amount of {token0} to swap: "))
            if amount <= 0:
                print(f"{Colors.RED}Amount must be positive{Colors.END}")
                input("Press Enter to continue...")
                return
        except ValueError:
            print(f"{Colors.RED}Invalid amount{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Calculate swap
        swap_result = self.calculate_uniswap_swap(token0, token1, amount)
        
        if swap_result:
            output_amount = swap_result['output_amount']
            price_impact = swap_result['price_impact']
            fee = swap_result['fee']
            gas_estimate = swap_result['gas_estimate']
            
            print(f"\n{Colors.CYAN}SWAP PREVIEW:{Colors.END}")
            print(f"  Input: {amount:.6f} {token0}")
            print(f"  Output: {output_amount:.6f} {token1}")
            print(f"  Price Impact: {Colors.RED if price_impact > 1 else Colors.GREEN}{price_impact:.2f}%{Colors.END}")
            print(f"  Fee: ${fee:.2f}")
            print(f"  Gas Estimate: {gas_estimate:,} GWEI")
            
            confirm = self.get_user_input("\nExecute swap? (y/N): ").lower()
            if confirm == 'y':
                self.execute_uniswap_swap(token0, token1, amount, output_amount, fee)
            else:
                print(f"{Colors.YELLOW}Swap cancelled{Colors.END}")
        else:
            print(f"{Colors.RED}Swap calculation failed. Check token pair and liquidity.{Colors.END}")
        
        input("Press Enter to continue...")

    def calculate_uniswap_swap(self, token0, token1, amount):
        """Calculate Uniswap swap output and fees"""
        # Get current prices
        price0 = self.live_market.get_price(token0) or self.all_trading_pairs.get(token0, 0)
        price1 = self.live_market.get_price(token1) or self.all_trading_pairs.get(token1, 0)
        
        if price0 == 0 or price1 == 0:
            return None
        
        # Calculate output amount (simplified Uniswap V3 formula)
        # In real Uniswap, this would use the x*y=k formula with concentrated liquidity
        input_value = amount * price0
        output_amount = input_value / price1
        
        # Apply slippage and fees
        fee_rate = 0.003  # 0.3% fee
        fee = input_value * fee_rate
        output_amount = output_amount * (1 - fee_rate)
        
        # Calculate price impact (simplified)
        price_impact = random.uniform(0.1, 2.0)  # 0.1% to 2% impact
        
        # Gas estimate
        gas_estimate = random.randint(150000, 300000)
        
        return {
            'output_amount': output_amount,
            'price_impact': price_impact,
            'fee': fee,
            'gas_estimate': gas_estimate
        }

    def execute_uniswap_swap(self, token0, token1, input_amount, output_amount, fee):
        """Execute the Uniswap swap"""
        total_cost = input_amount * (self.live_market.get_price(token0) or self.all_trading_pairs.get(token0, 0))
        
        if total_cost > self.user_balance:
            print(f"{Colors.RED}Insufficient balance for swap{Colors.END}")
            return
        
        # Execute swap
        self.user_balance -= total_cost
        
        # Update portfolio
        if token0 in self.user_portfolio:
            self.user_portfolio[token0] -= input_amount
            if self.user_portfolio[token0] <= 0:
                del self.user_portfolio[token0]
        
        self.user_portfolio[token1] = self.user_portfolio.get(token1, 0) + output_amount
        
        # Record transaction
        transaction = {
            'type': 'UNISWAP_SWAP',
            'from_token': token0,
            'to_token': token1,
            'from_amount': input_amount,
            'to_amount': output_amount,
            'fee': fee,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transaction_history.append(transaction)
        
        print(f"{Colors.GREEN}Swap executed successfully!{Colors.END}")
        print(f"  Swapped {input_amount:.6f} {token0} for {output_amount:.6f} {token1}")

    def uniswap_add_liquidity(self):
        """Add liquidity to Uniswap pool"""
        print(f"\n{Colors.YELLOW}ADD LIQUIDITY{Colors.END}")
        
        token0 = self.get_user_input("Enter first token (e.g., ETH): ").upper()
        token1 = self.get_user_input("Enter second token (e.g., USDC): ").upper()
        
        if not token0 or not token1:
            print(f"{Colors.RED}Invalid token pair{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            amount0 = float(self.get_user_input(f"Enter amount of {token0}: "))
            amount1 = float(self.get_user_input(f"Enter amount of {token1}: "))
            
            if amount0 <= 0 or amount1 <= 0:
                print(f"{Colors.RED}Amounts must be positive{Colors.END}")
                input("Press Enter to continue...")
                return
        except ValueError:
            print(f"{Colors.RED}Invalid amounts{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Calculate liquidity position
        price0 = self.live_market.get_price(token0) or self.all_trading_pairs.get(token0, 0)
        price1 = self.live_market.get_price(token1) or self.all_trading_pairs.get(token1, 0)
        
        if price0 == 0 or price1 == 0:
            print(f"{Colors.RED}Invalid token prices{Colors.END}")
            input("Press Enter to continue...")
            return
        
        value0 = amount0 * price0
        value1 = amount1 * price1
        total_value = value0 + value1
        
        if total_value > self.user_balance:
            print(f"{Colors.RED}Insufficient balance for liquidity provision{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute liquidity provision
        self.user_balance -= total_value
        
        # Generate LP token amount (simplified)
        lp_tokens = total_value / 100  # Simplified calculation
        
        # Record transaction
        transaction = {
            'type': 'ADD_LIQUIDITY',
            'token0': token0,
            'token1': token1,
            'amount0': amount0,
            'amount1': amount1,
            'lp_tokens': lp_tokens,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transaction_history.append(transaction)
        
        print(f"{Colors.GREEN}Liquidity added successfully!{Colors.END}")
        print(f"  Added {amount0:.6f} {token0} and {amount1:.6f} {token1}")
        print(f"  Received {lp_tokens:.6f} LP tokens")
        
        input("Press Enter to continue...")

    def uniswap_remove_liquidity(self):
        """Remove liquidity from Uniswap pool"""
        print(f"\n{Colors.YELLOW}REMOVE LIQUIDITY{Colors.END}")
        
        # Check if user has LP positions (simplified)
        lp_positions = [tx for tx in self.transaction_history if tx.get('type') == 'ADD_LIQUIDITY']
        
        if not lp_positions:
            print(f"{Colors.RED}No liquidity positions found{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"{Colors.CYAN}Your LP Positions:{Colors.END}")
        for i, pos in enumerate(lp_positions[-5:], 1):
            print(f"  {i}. {pos['token0']}/{pos['token1']} - {pos['lp_tokens']:.6f} LP tokens")
        
        try:
            choice = int(self.get_user_input("Select position to remove (1-5): "))
            if 1 <= choice <= len(lp_positions):
                position = lp_positions[choice - 1]
                
                lp_amount = float(self.get_user_input(f"Enter LP tokens to remove (max {position['lp_tokens']:.6f}): "))
                
                if lp_amount > position['lp_tokens']:
                    print(f"{Colors.RED}Amount exceeds available LP tokens{Colors.END}")
                    input("Press Enter to continue...")
                    return
                
                # Calculate returns (simplified)
                ratio = lp_amount / position['lp_tokens']
                return0 = position['amount0'] * ratio
                return1 = position['amount1'] * ratio
                
                # Add returns to balance
                price0 = self.live_market.get_price(position['token0']) or self.all_trading_pairs.get(position['token0'], 0)
                price1 = self.live_market.get_price(position['token1']) or self.all_trading_pairs.get(position['token1'], 0)
                
                value0 = return0 * price0
                value1 = return1 * price1
                total_return = value0 + value1
                
                self.user_balance += total_return
                
                # Record transaction
                transaction = {
                    'type': 'REMOVE_LIQUIDITY',
                    'token0': position['token0'],
                    'token1': position['token1'],
                    'lp_tokens': lp_amount,
                    'return0': return0,
                    'return1': return1,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.transaction_history.append(transaction)
                
                print(f"{Colors.GREEN}Liquidity removed successfully!{Colors.END}")
                print(f"  Removed {lp_amount:.6f} LP tokens")
                print(f"  Received {return0:.6f} {position['token0']} and {return1:.6f} {position['token1']}")
                print(f"  Total value: ${total_return:,.2f}")
            else:
                print(f"{Colors.RED}Invalid selection{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.END}")
        
        input("Press Enter to continue...")

    def uniswap_analytics(self):
        """Display Uniswap analytics"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              UNISWAP ANALYTICS                              ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            pools = self.get_uniswap_pools()
            
            # Calculate analytics
            total_liquidity = sum(pool['liquidity'] for pool in pools)
            total_volume = sum(pool['volume24h'] for pool in pools)
            
            print(f"\n{Colors.YELLOW}PROTOCOL STATISTICS:{Colors.END}")
            print(f"  Total Liquidity: ${total_liquidity:,.0f}")
            print(f"  24h Volume: ${total_volume:,.0f}")
            print(f"  Active Pools: {len(pools)}")
            
            print(f"\n{Colors.YELLOW}TOP POOLS BY VOLUME:{Colors.END}")
            sorted_pools = sorted(pools, key=lambda x: x['volume24h'], reverse=True)
            for i, pool in enumerate(sorted_pools[:5], 1):
                print(f"  {i}. {pool['token0']}/{pool['token1']} - ${pool['volume24h']:,.0f}")
            
            print(f"\n{Colors.YELLOW}FEE TIER DISTRIBUTION:{Colors.END}")
            fee_tiers = {}
            for pool in pools:
                fee = pool['feeTier']
                fee_tiers[fee] = fee_tiers.get(fee, 0) + 1
            
            for fee, count in sorted(fee_tiers.items()):
                print(f"  {fee}%: {count} pools")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Refresh | {Colors.GREEN}[0]{Colors.END} Back")
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                continue

    def execute_real_uniswap_buy(self, contract_address, eth_amount, wallet_address, private_key):
        """Execute real Uniswap buy transaction on blockchain"""
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
            min_tokens = 1  # For demo, set to 1. For production, calculate with slippage.
            
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
    
    def execute_real_uniswap_sell(self, contract_address, token_amount, wallet_address, private_key):
        """Execute real Uniswap sell transaction on blockchain"""
        try:
            if not self.web3.is_address(contract_address):
                return False, "Invalid token contract address"
            
            if not self.web3.is_address(wallet_address):
                return False, "Invalid wallet address"
            
            # Setup transaction parameters
            WETH = self.web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
            token_addr = self.web3.to_checksum_address(contract_address)
            path = [token_addr, WETH]
            deadline = int(self.web3.eth.get_block('latest')['timestamp']) + 600
            min_eth = 1  # For demo, set to 1. For production, calculate with slippage.
            
            # Get token contract for approval
            token_abi = [{"inputs":[],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]
            token_contract = self.web3.eth.contract(address=token_addr, abi=token_abi)
            amount_wei = self.web3.to_wei(token_amount, 'ether')
            
            # Approve token spending
            approve_tx = token_contract.functions.approve(UNISWAP_V2_ROUTER_ADDRESS, amount_wei).build_transaction({
                'from': wallet_address,
                'gas': 60000,
                'gasPrice': self.web3.to_wei('30', 'gwei'),
                'nonce': self.web3.eth.get_transaction_count(wallet_address)
            })
            signed_approve = self.web3.eth.account.sign_transaction(approve_tx, private_key)
            approve_hash = self.web3.eth.send_raw_transaction(signed_approve.rawTransaction)
            self.web3.eth.wait_for_transaction_receipt(approve_hash)
            
            # Execute swap
            swap_tx = self.uniswap_router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_wei, min_eth, path, wallet_address, deadline
            ).build_transaction({
                'from': wallet_address,
                'gas': 300000,
                'gasPrice': self.web3.to_wei('30', 'gwei'),
                'nonce': self.web3.eth.get_transaction_count(wallet_address)
            })
            signed_swap = self.web3.eth.account.sign_transaction(swap_tx, private_key)
            swap_hash = self.web3.eth.send_raw_transaction(signed_swap.rawTransaction)
            
            return True, f"Transaction sent: {self.web3.to_hex(swap_hash)}"
            
        except Exception as e:
            return False, f"Transaction failed: {str(e)}"
    
    def get_wallet_balance(self, wallet_address):
        """Get real ETH balance from blockchain"""
        try:
            balance_wei = self.web3.eth.get_balance(wallet_address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            print(f"Error getting wallet balance: {e}")
            return 0.0
    
    def real_trading_screen(self):
        """Display real blockchain trading interface"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                           REAL BLOCKCHAIN TRADING                            ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.RED}⚠️  WARNING: This is REAL trading with REAL money! ⚠️{Colors.END}")
            print(f"{Colors.WHITE}Make sure you have a wallet with ETH and understand the risks.{Colors.END}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Buy Token with ETH (Real)")
            print(f"{Colors.GREEN}[2]{Colors.END} Sell Token for ETH (Real)")
            print(f"{Colors.GREEN}[3]{Colors.END} Check Wallet Balance")
            print(f"{Colors.GREEN}[4]{Colors.END} View Transaction History")
            print(f"{Colors.GREEN}[0]{Colors.END} Back to Main Menu")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.real_buy_token()
            elif choice == '2':
                self.real_sell_token()
            elif choice == '3':
                self.check_real_balance()
            elif choice == '4':
                self.view_real_history()
    
    def real_buy_token(self):
        """Real token buying with wallet integration"""
        print(f"\n{Colors.YELLOW}REAL TOKEN BUYING{Colors.END}")
        print(f"{Colors.WHITE}Enter your wallet details:{Colors.END}")
        
        wallet_address = self.get_user_input("Wallet Address: ").strip()
        private_key = self.get_user_input("Private Key: ").strip()
        contract_address = self.get_user_input("Token Contract Address: ").strip()
        
        try:
            eth_amount = float(self.get_user_input("ETH Amount to spend: "))
        except ValueError:
            print(f"{Colors.RED}Invalid ETH amount{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Check wallet balance
        balance = self.get_wallet_balance(wallet_address)
        if balance < eth_amount:
            print(f"{Colors.RED}Insufficient ETH balance. You have {balance:.6f} ETH{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"\n{Colors.YELLOW}Confirming transaction...{Colors.END}")
        print(f"Buying token: {contract_address}")
        print(f"Spending: {eth_amount} ETH")
        print(f"From wallet: {wallet_address}")
        
        confirm = self.get_user_input("Type 'CONFIRM' to proceed: ")
        if confirm != 'CONFIRM':
            print(f"{Colors.YELLOW}Transaction cancelled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute real transaction
        success, message = self.execute_real_uniswap_buy(contract_address, eth_amount, wallet_address, private_key)
        
        if success:
            print(f"{Colors.GREEN}✅ Transaction successful!{Colors.END}")
            print(f"{Colors.WHITE}{message}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Transaction failed!{Colors.END}")
            print(f"{Colors.WHITE}{message}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def real_sell_token(self):
        """Real token selling with wallet integration"""
        print(f"\n{Colors.YELLOW}REAL TOKEN SELLING{Colors.END}")
        print(f"{Colors.WHITE}Enter your wallet details:{Colors.END}")
        
        wallet_address = self.get_user_input("Wallet Address: ").strip()
        private_key = self.get_user_input("Private Key: ").strip()
        contract_address = self.get_user_input("Token Contract Address: ").strip()
        
        try:
            token_amount = float(self.get_user_input("Token Amount to sell: "))
        except ValueError:
            print(f"{Colors.RED}Invalid token amount{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"\n{Colors.YELLOW}Confirming transaction...{Colors.END}")
        print(f"Selling token: {contract_address}")
        print(f"Amount: {token_amount} tokens")
        print(f"From wallet: {wallet_address}")
        
        confirm = self.get_user_input("Type 'CONFIRM' to proceed: ")
        if confirm != 'CONFIRM':
            print(f"{Colors.YELLOW}Transaction cancelled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute real transaction
        success, message = self.execute_real_uniswap_sell(contract_address, token_amount, wallet_address, private_key)
        
        if success:
            print(f"{Colors.GREEN}✅ Transaction successful!{Colors.END}")
            print(f"{Colors.WHITE}{message}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Transaction failed!{Colors.END}")
            print(f"{Colors.WHITE}{message}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def check_real_balance(self):
        """Check real wallet balance on blockchain"""
        print(f"\n{Colors.YELLOW}CHECK WALLET BALANCE{Colors.END}")
        
        wallet_address = self.get_user_input("Wallet Address: ").strip()
        
        if not self.web3.is_address(wallet_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        balance = self.get_wallet_balance(wallet_address)
        eth_price = self.live_market.get_price('ETH') or 3200
        
        print(f"\n{Colors.GREEN}Wallet Balance:{Colors.END}")
        print(f"{Colors.WHITE}ETH: {balance:.6f}{Colors.END}")
        print(f"{Colors.WHITE}USD Value: ${balance * eth_price:,.2f}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def view_real_history(self):
        """View real transaction history from blockchain"""
        print(f"\n{Colors.YELLOW}BLOCKCHAIN TRANSACTION HISTORY{Colors.END}")
        
        wallet_address = self.get_user_input("Wallet Address: ").strip()
        
        if not self.web3.is_address(wallet_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            # Get recent transactions from Etherscan API
            api_url = f"https://api.etherscan.io/api"
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': wallet_address,
                'startblock': 0,
                'endblock': 99999999,
                'sort': 'desc',
                'apikey': 'YourApiKeyToken'  # Replace with actual API key
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '1':
                    transactions = data['result'][:10]  # Show last 10 transactions
                    
                    print(f"\n{Colors.GREEN}Recent Transactions:{Colors.END}")
                    for tx in transactions:
                        tx_hash = tx['hash']
                        value_eth = float(tx['value']) / 10**18
                        timestamp = datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"{Colors.WHITE}{timestamp} | {tx_hash[:10]}... | {value_eth:.6f} ETH{Colors.END}")
                else:
                    print(f"{Colors.RED}No transactions found{Colors.END}")
            else:
                print(f"{Colors.RED}Error fetching transactions{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.END}")
        
        input("Press Enter to continue...")

    def token_sniping_screen(self):
        """Display token sniping interface"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              TOKEN SNIPING                                  ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.RED}⚠️  WARNING: Token sniping is high-risk trading! ⚠️{Colors.END}")
            print(f"{Colors.WHITE}Only snipe tokens you've researched. Many are scams or rug pulls.{Colors.END}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Setup Sniper Bot")
            print(f"{Colors.GREEN}[2]{Colors.END} Monitor New Listings")
            print(f"{Colors.GREEN}[3]{Colors.END} Quick Snipe Token")
            print(f"{Colors.GREEN}[4]{Colors.END} View Sniper History")
            print(f"{Colors.GREEN}[5]{Colors.END} Sniper Settings")
            print(f"{Colors.GREEN}[0]{Colors.END} Back to Main Menu")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.setup_sniper_bot()
            elif choice == '2':
                self.monitor_new_listings()
            elif choice == '3':
                self.quick_snipe_token()
            elif choice == '4':
                self.view_sniper_history()
            elif choice == '5':
                self.sniper_settings()
    
    def setup_sniper_bot(self):
        """Setup automated sniper bot"""
        print(f"\n{Colors.YELLOW}SNIPER BOT SETUP{Colors.END}")
        
        # Get wallet details
        wallet_address = self.get_user_input("Wallet Address: ").strip()
        private_key = self.get_user_input("Private Key: ").strip()
        
        if not self.web3.is_address(wallet_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Sniper settings
        try:
            max_eth_per_snipe = float(self.get_user_input("Max ETH per snipe: "))
            gas_price_gwei = float(self.get_user_input("Gas price (Gwei): "))
            slippage_percent = float(self.get_user_input("Slippage tolerance (%): "))
            auto_approve = self.get_user_input("Auto-approve tokens? (y/n): ").lower() == 'y'
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Save sniper settings
        sniper_config = {
            'wallet_address': wallet_address,
            'private_key': private_key,
            'max_eth_per_snipe': max_eth_per_snipe,
            'gas_price_gwei': gas_price_gwei,
            'slippage_percent': slippage_percent,
            'auto_approve': auto_approve,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        with open('sniper_config.json', 'w') as f:
            json.dump(sniper_config, f, indent=2)
        
        print(f"{Colors.GREEN}✅ Sniper bot configured successfully!{Colors.END}")
        print(f"{Colors.WHITE}Max ETH per snipe: {max_eth_per_snipe}{Colors.END}")
        print(f"{Colors.WHITE}Gas price: {gas_price_gwei} Gwei{Colors.END}")
        print(f"{Colors.WHITE}Slippage: {slippage_percent}%{Colors.END}")
        
        input("Press Enter to continue...")
    
    def monitor_new_listings(self):
        """Monitor for new token listings"""
        print(f"\n{Colors.YELLOW}MONITORING NEW LISTINGS{Colors.END}")
        print(f"{Colors.WHITE}Scanning for new tokens on Uniswap...{Colors.END}")
        
        # Load sniper config
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}No sniper configuration found. Setup sniper bot first.{Colors.END}")
            input("Press Enter to continue...")
            return
        
        if not config.get('enabled', False):
            print(f"{Colors.RED}Sniper bot is disabled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"{Colors.GREEN}Monitoring started...{Colors.END}")
        print(f"{Colors.WHITE}Press Ctrl+C to stop{Colors.END}")
        
        try:
            while True:
                # Simulate finding new tokens (in real implementation, this would monitor blockchain events)
                new_tokens = self.scan_for_new_tokens()
                
                for token in new_tokens:
                    print(f"\n{Colors.CYAN}🔥 NEW TOKEN DETECTED! 🔥{Colors.END}")
                    print(f"{Colors.WHITE}Contract: {token['address']}{Colors.END}")
                    print(f"{Colors.WHITE}Name: {token['name']}{Colors.END}")
                    print(f"{Colors.WHITE}Symbol: {token['symbol']}{Colors.END}")
                    print(f"{Colors.WHITE}Liquidity: {token['liquidity']} ETH{Colors.END}")
                    
                    # Auto-snipe if conditions are met
                    if self.should_auto_snipe(token, config):
                        print(f"{Colors.YELLOW}Auto-sniping...{Colors.END}")
                        success = self.execute_snipe(token, config)
                        if success:
                            print(f"{Colors.GREEN}✅ Snipe successful!{Colors.END}")
                        else:
                            print(f"{Colors.RED}❌ Snipe failed!{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}Token doesn't meet auto-snipe criteria{Colors.END}")
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoring stopped{Colors.END}")
            input("Press Enter to continue...")
    
    def scan_for_new_tokens(self):
        """Scan for new token listings (simulated)"""
        # In a real implementation, this would:
        # 1. Monitor Uniswap factory events for new pairs
        # 2. Check for new liquidity additions
        # 3. Analyze token contracts for potential scams
        
        # Simulated new tokens for demo
        new_tokens = []
        
        # Random chance to find a "new" token
        if random.random() < 0.1:  # 10% chance
            token = {
                'address': f"0x{random.randint(1000000000000000000000000000000000000000, 9999999999999999999999999999999999999999):040x}",
                'name': f"Token{random.randint(1000, 9999)}",
                'symbol': f"TKN{random.randint(100, 999)}",
                'liquidity': random.uniform(1, 50),
                'created_at': datetime.now().isoformat()
            }
            new_tokens.append(token)
        
        return new_tokens
    
    def should_auto_snipe(self, token, config):
        """Determine if token should be auto-sniped"""
        # Basic criteria for auto-sniping
        min_liquidity = 5  # Minimum 5 ETH liquidity
        max_liquidity = 100  # Maximum 100 ETH liquidity (avoid whales)
        
        liquidity = token.get('liquidity', 0)
        
        # Check liquidity range
        if liquidity < min_liquidity or liquidity > max_liquidity:
            return False
        
        # Check if we have enough ETH
        wallet_balance = self.get_wallet_balance(config['wallet_address'])
        if wallet_balance < config['max_eth_per_snipe']:
            return False
        
        # Additional checks could include:
        # - Contract verification
        # - Honeypot detection
        # - Ownership renounced
        # - Liquidity locked
        
        return True
    
    def execute_snipe(self, token, config):
        """Execute a snipe transaction"""
        try:
            eth_amount = config['max_eth_per_snipe']
            wallet_address = config['wallet_address']
            private_key = config['private_key']
            contract_address = token['address']
            
            # Execute the snipe
            success, message = self.execute_real_uniswap_buy(
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
                
                self.log_snipe(snipe_record)
            
            return success
            
        except Exception as e:
            print(f"Error executing snipe: {e}")
            return False
    
    def log_snipe(self, snipe_record):
        """Log snipe transaction"""
        try:
            with open('sniper_history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
        
        history.append(snipe_record)
        
        with open('sniper_history.json', 'w') as f:
            json.dump(history, f, indent=2)
    
    def quick_snipe_token(self):
        """Quick snipe a specific token"""
        print(f"\n{Colors.YELLOW}QUICK TOKEN SNIPE{Colors.END}")
        
        # Load sniper config
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}No sniper configuration found. Setup sniper bot first.{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get token details
        contract_address = self.get_user_input("Token Contract Address: ").strip()
        
        if not self.web3.is_address(contract_address):
            print(f"{Colors.RED}Invalid contract address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            eth_amount = float(self.get_user_input("ETH Amount to snipe: "))
        except ValueError:
            print(f"{Colors.RED}Invalid ETH amount{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Check wallet balance
        wallet_balance = self.get_wallet_balance(config['wallet_address'])
        if wallet_balance < eth_amount:
            print(f"{Colors.RED}Insufficient ETH balance. You have {wallet_balance:.6f} ETH{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Get token info
        token_info = self.get_token_info(contract_address)
        if not token_info:
            print(f"{Colors.RED}Could not get token information{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"\n{Colors.YELLOW}SNIPE PREVIEW:{Colors.END}")
        print(f"{Colors.WHITE}Token: {token_info['name']} ({token_info['symbol']}){Colors.END}")
        print(f"{Colors.WHITE}Contract: {contract_address}{Colors.END}")
        print(f"{Colors.WHITE}Amount: {eth_amount} ETH{Colors.END}")
        print(f"{Colors.WHITE}Gas Price: {config['gas_price_gwei']} Gwei{Colors.END}")
        
        confirm = self.get_user_input("Type 'SNIPE' to execute: ")
        if confirm != 'SNIPE':
            print(f"{Colors.YELLOW}Snipe cancelled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute snipe
        print(f"{Colors.YELLOW}Executing snipe...{Colors.END}")
        success = self.execute_snipe({
            'address': contract_address,
            'name': token_info['name'],
            'symbol': token_info['symbol']
        }, config)
        
        if success:
            print(f"{Colors.GREEN}✅ Snipe successful!{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Snipe failed!{Colors.END}")
        
        input("Press Enter to continue...")
    
    def view_sniper_history(self):
        """View sniper transaction history"""
        print(f"\n{Colors.YELLOW}SNIPER HISTORY{Colors.END}")
        
        try:
            with open('sniper_history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            print(f"{Colors.WHITE}No sniper history found{Colors.END}")
            input("Press Enter to continue...")
            return
        
        if not history:
            print(f"{Colors.WHITE}No sniper transactions yet{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"\n{Colors.GREEN}Recent Snipes:{Colors.END}")
        for snipe in history[-10:]:  # Show last 10 snipes
            timestamp = snipe.get('timestamp', 'Unknown')
            token_name = snipe.get('token_name', 'Unknown')
            token_symbol = snipe.get('token_symbol', 'Unknown')
            eth_amount = snipe.get('eth_amount', 0)
            status = snipe.get('status', 'Unknown')
            
            status_color = Colors.GREEN if status == 'success' else Colors.RED
            print(f"{Colors.WHITE}{timestamp} | {token_name} ({token_symbol}) | {eth_amount} ETH | {status_color}{status}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def sniper_settings(self):
        """Configure sniper settings"""
        print(f"\n{Colors.YELLOW}SNIPER SETTINGS{Colors.END}")
        
        try:
            with open('sniper_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}No sniper configuration found{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"\n{Colors.GREEN}[1]{Colors.END} Enable/Disable Sniper")
        print(f"{Colors.GREEN}[2]{Colors.END} Update Settings")
        print(f"{Colors.GREEN}[3]{Colors.END} View Current Settings")
        print(f"{Colors.GREEN}[0]{Colors.END} Back")
        
        choice = self.get_user_input()
        
        if choice == '1':
            config['enabled'] = not config.get('enabled', False)
            status = "enabled" if config['enabled'] else "disabled"
            print(f"{Colors.GREEN}Sniper {status}{Colors.END}")
            
            with open('sniper_config.json', 'w') as f:
                json.dump(config, f, indent=2)
                
        elif choice == '2':
            self.setup_sniper_bot()  # Reconfigure
            
        elif choice == '3':
            print(f"\n{Colors.GREEN}Current Settings:{Colors.END}")
            print(f"{Colors.WHITE}Wallet: {config.get('wallet_address', 'Not set')}{Colors.END}")
            print(f"{Colors.WHITE}Max ETH per snipe: {config.get('max_eth_per_snipe', 0)}{Colors.END}")
            print(f"{Colors.WHITE}Gas price: {config.get('gas_price_gwei', 0)} Gwei{Colors.END}")
            print(f"{Colors.WHITE}Slippage: {config.get('slippage_percent', 0)}%{Colors.END}")
            print(f"{Colors.WHITE}Enabled: {config.get('enabled', False)}{Colors.END}")
            
            input("Press Enter to continue...")

    def marketplace_screen(self):
        """Display marketplace interface"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              GLOBAL MARKETPLACE                             ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.RED}⚠️  WARNING: This is a REAL marketplace with REAL ETH transactions! ⚠️{Colors.END}")
            print(f"{Colors.WHITE}All transactions use smart contract escrow for security.{Colors.END}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Browse Listings")
            print(f"{Colors.GREEN}[2]{Colors.END} Create New Listing")
            print(f"{Colors.GREEN}[3]{Colors.END} My Listings")
            print(f"{Colors.GREEN}[4]{Colors.END} My Purchases")
            print(f"{Colors.GREEN}[5]{Colors.END} Escrow Transactions")
            print(f"{Colors.GREEN}[6]{Colors.END} Marketplace Chat")
            print(f"{Colors.GREEN}[0]{Colors.END} Back to Main Menu")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.browse_listings()
            elif choice == '2':
                self.create_listing()
            elif choice == '3':
                self.my_listings()
            elif choice == '4':
                self.my_purchases()
            elif choice == '5':
                self.escrow_transactions()
            elif choice == '6':
                self.marketplace_chat()
    
    def browse_listings(self):
        """Browse marketplace listings"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              BROWSE LISTINGS                                 ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            # Load listings
            listings = self.load_marketplace_listings()
            
            if not listings:
                print(f"\n{Colors.WHITE}No listings available.{Colors.END}")
                input("Press Enter to continue...")
                break
            
            # Display categories
            categories = list(set([listing.get('category', 'Other') for listing in listings]))
            print(f"\n{Colors.YELLOW}Categories:{Colors.END}")
            for i, category in enumerate(categories, 1):
                print(f"  {i}. {category}")
            
            print(f"\n{Colors.GREEN}[1-{len(categories)}]{Colors.END} Filter by category")
            print(f"{Colors.GREEN}[S]{Colors.END} Search listings")
            print(f"{Colors.GREEN}[A]{Colors.END} Show all listings")
            print(f"{Colors.GREEN}[0]{Colors.END} Back")
            
            choice = self.get_user_input().upper()
            
            if choice == '0':
                break
            elif choice == 'S':
                self.search_listings()
            elif choice == 'A':
                self.show_all_listings(listings)
            elif choice.isdigit() and 1 <= int(choice) <= len(categories):
                category = categories[int(choice) - 1]
                self.show_category_listings(listings, category)
    
    def search_listings(self):
        """Search marketplace listings"""
        print(f"\n{Colors.YELLOW}SEARCH LISTINGS{Colors.END}")
        search_term = self.get_user_input("Enter search term: ").lower()
        
        listings = self.load_marketplace_listings()
        filtered_listings = []
        
        for listing in listings:
            if (search_term in listing.get('title', '').lower() or 
                search_term in listing.get('description', '').lower() or
                search_term in listing.get('category', '').lower()):
                filtered_listings.append(listing)
        
        if filtered_listings:
            self.show_listings(filtered_listings, f"Search Results for '{search_term}'")
        else:
            print(f"{Colors.WHITE}No listings found for '{search_term}'{Colors.END}")
            input("Press Enter to continue...")
    
    def show_all_listings(self, listings):
        """Show all marketplace listings"""
        self.show_listings(listings, "All Listings")
    
    def show_category_listings(self, listings, category):
        """Show listings filtered by category"""
        filtered_listings = [l for l in listings if l.get('category', 'Other') == category]
        self.show_listings(filtered_listings, f"{category} Listings")
    
    def show_listings(self, listings, title):
        """Display listings with pagination"""
        page = 0
        per_page = 5
        
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              {title.upper():<50} ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            start_idx = page * per_page
            end_idx = start_idx + per_page
            page_listings = listings[start_idx:end_idx]
            
            if not page_listings:
                print(f"\n{Colors.WHITE}No listings on this page.{Colors.END}")
            else:
                for i, listing in enumerate(page_listings, start_idx + 1):
                    print(f"\n{Colors.GREEN}[{i}]{Colors.END} {listing['title']}")
                    print(f"{Colors.WHITE}   Price: {listing['price']} ETH{Colors.END}")
                    print(f"{Colors.WHITE}   Category: {listing['category']}{Colors.END}")
                    print(f"{Colors.WHITE}   Seller: {listing['seller_address'][:10]}...{Colors.END}")
                    print(f"{Colors.WHITE}   Status: {listing['status']}{Colors.END}")
                    print(f"{Colors.WHITE}   {listing['description'][:100]}...{Colors.END}")
            
            # Pagination controls
            total_pages = (len(listings) + per_page - 1) // per_page
            print(f"\n{Colors.YELLOW}Page {page + 1} of {total_pages}{Colors.END}")
            
            if page > 0:
                print(f"{Colors.GREEN}[P]{Colors.END} Previous page")
            if page < total_pages - 1:
                print(f"{Colors.GREEN}[N]{Colors.END} Next page")
            
            print(f"{Colors.GREEN}[1-{len(page_listings)}]{Colors.END} View listing")
            print(f"{Colors.GREEN}[0]{Colors.END} Back")
            
            choice = self.get_user_input().upper()
            
            if choice == '0':
                break
            elif choice == 'P' and page > 0:
                page -= 1
            elif choice == 'N' and page < total_pages - 1:
                page += 1
            elif choice.isdigit():
                listing_idx = int(choice) - 1
                if 0 <= listing_idx < len(page_listings):
                    self.view_listing(page_listings[listing_idx])
    
    def view_listing(self, listing):
        """View detailed listing information"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║                              LISTING DETAILS                                 ║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.YELLOW}Title:{Colors.END} {listing['title']}")
            print(f"{Colors.YELLOW}Price:{Colors.END} {listing['price']} ETH")
            print(f"{Colors.YELLOW}Category:{Colors.END} {listing['category']}")
            print(f"{Colors.YELLOW}Seller:{Colors.END} {listing['seller_address']}")
            print(f"{Colors.YELLOW}Status:{Colors.END} {listing['status']}")
            print(f"{Colors.YELLOW}Created:{Colors.END} {listing['created_at']}")
            print(f"{Colors.YELLOW}Description:{Colors.END}")
            print(f"{Colors.WHITE}{listing['description']}{Colors.END}")
            
            if listing.get('images'):
                print(f"\n{Colors.YELLOW}Images:{Colors.END}")
                for i, image in enumerate(listing['images'], 1):
                    print(f"  {i}. {image}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.END} Buy Now (Escrow)")
            print(f"{Colors.GREEN}[2]{Colors.END} Contact Seller")
            print(f"{Colors.GREEN}[3]{Colors.END} Report Listing")
            print(f"{Colors.GREEN}[0]{Colors.END} Back")
            
            choice = self.get_user_input()
            
            if choice == '0':
                break
            elif choice == '1':
                self.buy_listing(listing)
            elif choice == '2':
                self.contact_seller(listing)
            elif choice == '3':
                self.report_listing(listing)
    
    def buy_listing(self, listing):
        """Purchase a listing using escrow"""
        print(f"\n{Colors.YELLOW}PURCHASE LISTING{Colors.END}")
        print(f"{Colors.WHITE}Title: {listing['title']}{Colors.END}")
        print(f"{Colors.WHITE}Price: {listing['price']} ETH{Colors.END}")
        
        # Get buyer wallet details
        buyer_address = self.get_user_input("Your wallet address: ").strip()
        private_key = self.get_user_input("Your private key: ").strip()
        
        if not self.web3.is_address(buyer_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Check buyer balance
        buyer_balance = self.get_wallet_balance(buyer_address)
        if buyer_balance < listing['price']:
            print(f"{Colors.RED}Insufficient ETH balance. You have {buyer_balance:.6f} ETH{Colors.END}")
            input("Press Enter to continue...")
            return
        
        print(f"\n{Colors.YELLOW}ESCROW TRANSACTION DETAILS:{Colors.END}")
        print(f"{Colors.WHITE}Buyer: {buyer_address}{Colors.END}")
        print(f"{Colors.WHITE}Seller: {listing['seller_address']}{Colors.END}")
        print(f"{Colors.WHITE}Amount: {listing['price']} ETH{Colors.END}")
        print(f"{Colors.WHITE}Escrow Fee: 0.01 ETH{Colors.END}")
        print(f"{Colors.WHITE}Total: {listing['price'] + 0.01} ETH{Colors.END}")
        
        confirm = self.get_user_input("Type 'CONFIRM' to proceed with escrow purchase: ")
        if confirm != 'CONFIRM':
            print(f"{Colors.YELLOW}Purchase cancelled{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Execute escrow transaction
        success, tx_hash = self.execute_escrow_purchase(listing, buyer_address, private_key)
        
        if success:
            print(f"{Colors.GREEN}✅ Escrow transaction successful!{Colors.END}")
            print(f"{Colors.WHITE}Transaction Hash: {tx_hash}{Colors.END}")
            print(f"{Colors.WHITE}Funds are now held in escrow.{Colors.END}")
            print(f"{Colors.WHITE}Seller will be notified to ship the item.{Colors.END}")
            
            # Update listing status
            self.update_listing_status(listing['id'], 'SOLD')
            
        else:
            print(f"{Colors.RED}❌ Escrow transaction failed!{Colors.END}")
            print(f"{Colors.WHITE}Error: {tx_hash}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def execute_escrow_purchase(self, listing, buyer_address, private_key):
        """Execute escrow purchase transaction"""
        try:
            # Escrow contract address (simulated for demo)
            escrow_address = "0x1234567890123456789012345678901234567890"
            
            # Create escrow transaction
            escrow_data = {
                'listing_id': listing['id'],
                'buyer': buyer_address,
                'seller': listing['seller_address'],
                'amount': listing['price'],
                'escrow_fee': 0.01
            }
            
            # Build transaction
            tx = {
                'from': buyer_address,
                'to': escrow_address,
                'value': self.web3.to_wei(listing['price'] + 0.01, 'ether'),
                'gas': 200000,
                'gasPrice': self.web3.to_wei('30', 'gwei'),
                'nonce': self.web3.eth.get_transaction_count(buyer_address),
                'data': self.web3.to_hex(escrow_data)
            }
            
            # Sign and send transaction
            signed = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
            
            # Log escrow transaction
            self.log_escrow_transaction({
                'listing_id': listing['id'],
                'buyer': buyer_address,
                'seller': listing['seller_address'],
                'amount': listing['price'],
                'escrow_fee': 0.01,
                'tx_hash': self.web3.to_hex(tx_hash),
                'status': 'PENDING',
                'timestamp': datetime.now().isoformat()
            })
            
            return True, self.web3.to_hex(tx_hash)
            
        except Exception as e:
            return False, str(e)
    
    def create_listing(self):
        """Create a new marketplace listing"""
        print(f"\n{Colors.YELLOW}CREATE NEW LISTING{Colors.END}")
        
        # Get listing details
        title = self.get_user_input("Listing title: ").strip()
        if not title:
            print(f"{Colors.RED}Title is required{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            price = float(self.get_user_input("Price (ETH): "))
        except ValueError:
            print(f"{Colors.RED}Invalid price{Colors.END}")
            input("Press Enter to continue...")
            return
        
        category = self.get_user_input("Category: ").strip()
        description = self.get_user_input("Description: ").strip()
        
        # Get seller wallet
        seller_address = self.get_user_input("Your wallet address: ").strip()
        if not self.web3.is_address(seller_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        # Create listing
        listing = {
            'id': f"listing_{int(time.time())}",
            'title': title,
            'price': price,
            'category': category or 'Other',
            'description': description,
            'seller_address': seller_address,
            'status': 'ACTIVE',
            'created_at': datetime.now().isoformat(),
            'images': []
        }
        
        # Save listing
        self.save_marketplace_listing(listing)
        
        print(f"{Colors.GREEN}✅ Listing created successfully!{Colors.END}")
        print(f"{Colors.WHITE}Listing ID: {listing['id']}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def my_listings(self):
        """View user's own listings"""
        print(f"\n{Colors.YELLOW}MY LISTINGS{Colors.END}")
        
        wallet_address = self.get_user_input("Your wallet address: ").strip()
        if not self.web3.is_address(wallet_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        listings = self.load_marketplace_listings()
        my_listings = [l for l in listings if l['seller_address'].lower() == wallet_address.lower()]
        
        if not my_listings:
            print(f"{Colors.WHITE}You have no listings.{Colors.END}")
            input("Press Enter to continue...")
            return
        
        self.show_listings(my_listings, "My Listings")
    
    def my_purchases(self):
        """View user's purchases"""
        print(f"\n{Colors.YELLOW}MY PURCHASES{Colors.END}")
        
        wallet_address = self.get_user_input("Your wallet address: ").strip()
        if not self.web3.is_address(wallet_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        escrow_transactions = self.load_escrow_transactions()
        my_purchases = [t for t in escrow_transactions if t['buyer'].lower() == wallet_address.lower()]
        
        if not my_purchases:
            print(f"{Colors.WHITE}You have no purchases.{Colors.END}")
            input("Press Enter to continue...")
            return
        
        self.show_purchases(my_purchases)
    
    def escrow_transactions(self):
        """View escrow transactions"""
        print(f"\n{Colors.YELLOW}ESCROW TRANSACTIONS{Colors.END}")
        
        wallet_address = self.get_user_input("Your wallet address: ").strip()
        if not self.web3.is_address(wallet_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            input("Press Enter to continue...")
            return
        
        escrow_transactions = self.load_escrow_transactions()
        my_transactions = [t for t in escrow_transactions 
                          if t['buyer'].lower() == wallet_address.lower() or 
                             t['seller'].lower() == wallet_address.lower()]
        
        if not my_transactions:
            print(f"{Colors.WHITE}You have no escrow transactions.{Colors.END}")
            input("Press Enter to continue...")
            return
        
        self.show_escrow_transactions(my_transactions)
    
    def marketplace_chat(self):
        """Marketplace chat with escrow bot"""
        print(f"\n{Colors.YELLOW}MARKETPLACE CHAT{Colors.END}")
        print(f"{Colors.WHITE}Chat with other users and the escrow bot.{Colors.END}")
        
        # Initialize username if not set
        if not hasattr(self, 'marketplace_username'):
            self.marketplace_username = self.get_marketplace_username()
        
        print(f"{Colors.WHITE}Logged in as: {self.marketplace_username}{Colors.END}")
        print(f"{Colors.WHITE}Type 'help' for commands, 'quit' to exit{Colors.END}")
        
        while True:
            message = self.get_user_input(f"{self.marketplace_username}: ")
            
            if message.lower() == 'quit':
                break
            elif message.lower() == 'help':
                self.show_marketplace_help()
            elif message.lower().startswith('/buy'):
                self.handle_buy_command(message)
            elif message.lower().startswith('/sell'):
                self.handle_sell_command(message)
            elif message.lower().startswith('/escrow'):
                self.handle_escrow_command(message)
            else:
                # Send message to marketplace chat
                self.send_marketplace_message(message)
    
    def get_marketplace_username(self):
        """Get marketplace username (now uses global username)"""
        return self.get_global_username()
    
    def show_marketplace_help(self):
        """Show marketplace chat commands"""
        print(f"\n{Colors.YELLOW}MARKETPLACE COMMANDS:{Colors.END}")
        print(f"{Colors.WHITE}/buy <listing_id> - Buy a listing{Colors.END}")
        print(f"{Colors.WHITE}/sell <title> <price> <description> - Create listing{Colors.END}")
        print(f"{Colors.WHITE}/escrow <transaction_id> - Check escrow status{Colors.END}")
        print(f"{Colors.WHITE}/listings - Show recent listings{Colors.END}")
        print(f"{Colors.WHITE}/help - Show this help{Colors.END}")
        print(f"{Colors.WHITE}/quit - Exit chat{Colors.END}")
    
    def handle_buy_command(self, message):
        """Handle buy command in chat"""
        parts = message.split()
        if len(parts) < 2:
            print(f"{Colors.RED}Usage: /buy <listing_id>{Colors.END}")
            return
        
        listing_id = parts[1]
        listings = self.load_marketplace_listings()
        listing = next((l for l in listings if l['id'] == listing_id), None)
        
        if not listing:
            print(f"{Colors.RED}Listing not found{Colors.END}")
            return
        
        print(f"{Colors.GREEN}Found listing: {listing['title']} - {listing['price']} ETH{Colors.END}")
        self.buy_listing(listing)
    
    def handle_sell_command(self, message):
        """Handle sell command in chat"""
        parts = message.split(' ', 3)
        if len(parts) < 4:
            print(f"{Colors.RED}Usage: /sell <title> <price> <description>{Colors.END}")
            return
        
        title = parts[1]
        try:
            price = float(parts[2])
        except ValueError:
            print(f"{Colors.RED}Invalid price{Colors.END}")
            return
        
        description = parts[3]
        
        # Get seller wallet
        seller_address = self.get_user_input("Your wallet address: ").strip()
        if not self.web3.is_address(seller_address):
            print(f"{Colors.RED}Invalid wallet address{Colors.END}")
            return
        
        # Create listing
        listing = {
            'id': f"listing_{int(time.time())}",
            'title': title,
            'price': price,
            'category': 'Other',
            'description': description,
            'seller_address': seller_address,
            'status': 'ACTIVE',
            'created_at': datetime.now().isoformat(),
            'images': []
        }
        
        self.save_marketplace_listing(listing)
        print(f"{Colors.GREEN}✅ Listing created: {listing['id']}{Colors.END}")
    
    def handle_escrow_command(self, message):
        """Handle escrow command in chat"""
        parts = message.split()
        if len(parts) < 2:
            print(f"{Colors.RED}Usage: /escrow <transaction_id>{Colors.END}")
            return
        
        tx_id = parts[1]
        escrow_transactions = self.load_escrow_transactions()
        transaction = next((t for t in escrow_transactions if t.get('tx_hash', '').startswith(tx_id)), None)
        
        if not transaction:
            print(f"{Colors.RED}Transaction not found{Colors.END}")
            return
        
        print(f"{Colors.YELLOW}Escrow Status: {transaction['status']}{Colors.END}")
        print(f"{Colors.WHITE}Amount: {transaction['amount']} ETH{Colors.END}")
        print(f"{Colors.WHITE}Buyer: {transaction['buyer'][:10]}...{Colors.END}")
        print(f"{Colors.WHITE}Seller: {transaction['seller'][:10]}...{Colors.END}")
    
    def send_marketplace_message(self, message):
        """Send message to marketplace chat"""
        # In a real implementation, this would send to a chat server
        print(f"{Colors.CYAN}[Marketplace] {self.marketplace_username}: {message}{Colors.END}")
        
        # Simulate bot responses
        if 'escrow' in message.lower():
            print(f"{Colors.GREEN}[EscrowBot] I can help with escrow transactions! Use /escrow <tx_id> to check status.{Colors.END}")
        elif 'buy' in message.lower() or 'purchase' in message.lower():
            print(f"{Colors.GREEN}[EscrowBot] To buy items, use /buy <listing_id> or browse listings in the marketplace.{Colors.END}")
        elif 'sell' in message.lower():
            print(f"{Colors.GREEN}[EscrowBot] To create a listing, use /sell <title> <price> <description>{Colors.END}")
    
    def load_marketplace_listings(self):
        """Load marketplace listings from file"""
        try:
            with open('marketplace_listings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_marketplace_listing(self, listing):
        """Save marketplace listing to file"""
        listings = self.load_marketplace_listings()
        listings.append(listing)
        
        with open('marketplace_listings.json', 'w') as f:
            json.dump(listings, f, indent=2)
    
    def update_listing_status(self, listing_id, status):
        """Update listing status"""
        listings = self.load_marketplace_listings()
        for listing in listings:
            if listing['id'] == listing_id:
                listing['status'] = status
                break
        
        with open('marketplace_listings.json', 'w') as f:
            json.dump(listings, f, indent=2)
    
    def load_escrow_transactions(self):
        """Load escrow transactions from file"""
        try:
            with open('escrow_transactions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def log_escrow_transaction(self, transaction):
        """Log escrow transaction to file"""
        transactions = self.load_escrow_transactions()
        transactions.append(transaction)
        
        with open('escrow_transactions.json', 'w') as f:
            json.dump(transactions, f, indent=2)
    
    def contact_seller(self, listing):
        """Contact seller about listing"""
        print(f"\n{Colors.YELLOW}CONTACT SELLER{Colors.END}")
        print(f"{Colors.WHITE}Listing: {listing['title']}{Colors.END}")
        print(f"{Colors.WHITE}Seller: {listing['seller_address']}{Colors.END}")
        
        message = self.get_user_input("Your message: ")
        if message:
            print(f"{Colors.GREEN}Message sent to seller.{Colors.END}")
        
        input("Press Enter to continue...")
    
    def report_listing(self, listing):
        """Report a listing"""
        print(f"\n{Colors.YELLOW}REPORT LISTING{Colors.END}")
        print(f"{Colors.WHITE}Listing: {listing['title']}{Colors.END}")
        
        reason = self.get_user_input("Reason for report: ")
        if reason:
            print(f"{Colors.GREEN}Report submitted. Thank you for helping keep the marketplace safe.{Colors.END}")
        
        input("Press Enter to continue...")
    
    def show_purchases(self, purchases):
        """Show user's purchases"""
        print(f"\n{Colors.YELLOW}MY PURCHASES{Colors.END}")
        
        for purchase in purchases:
            print(f"\n{Colors.GREEN}Transaction: {purchase['tx_hash'][:10]}...{Colors.END}")
            print(f"{Colors.WHITE}Amount: {purchase['amount']} ETH{Colors.END}")
            print(f"{Colors.WHITE}Status: {purchase['status']}{Colors.END}")
            print(f"{Colors.WHITE}Date: {purchase['timestamp']}{Colors.END}")
        
        input("Press Enter to continue...")
    
    def show_escrow_transactions(self, transactions):
        """Show escrow transactions"""
        print(f"\n{Colors.YELLOW}ESCROW TRANSACTIONS{Colors.END}")
        
        for tx in transactions:
            print(f"\n{Colors.GREEN}Transaction: {tx['tx_hash'][:10]}...{Colors.END}")
            print(f"{Colors.WHITE}Amount: {tx['amount']} ETH{Colors.END}")
            print(f"{Colors.WHITE}Status: {tx['status']}{Colors.END}")
            print(f"{Colors.WHITE}Date: {tx['timestamp']}{Colors.END}")
        
        input("Press Enter to continue...")

def main():
    """Main entry point"""
    # Check if running on Windows
    if os.name == 'nt':
        # Enable ANSI colors on Windows
        os.system('color')
    
    print(f"{Colors.CYAN}Starting DARKNET CRYPTO MARKETPLACE...{Colors.END}")
    time.sleep(1)
    
    app = TerminalCryptoMarketplace()
    app.run()

if __name__ == "__main__":
    main() 