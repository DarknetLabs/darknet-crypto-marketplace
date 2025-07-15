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

    def sell_crypto(self):
        """Sell cryptocurrency"""
        print(f"\n{Colors.YELLOW}SELL CRYPTOCURRENCY{Colors.END}")
        
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
        """Display chat rooms"""
        print(f"\n{Colors.YELLOW}CHAT ROOMS{Colors.END}")
        print(f"{Colors.WHITE}Chat rooms are available in the GUI version.{Colors.END}")
        print(f"{Colors.WHITE}This terminal version focuses on trading functionality.{Colors.END}")
        input("Press Enter to continue...")

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
                else:
                    print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}Application terminated by user.{Colors.END}")
        finally:
            self.running = False

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