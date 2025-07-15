import requests
import json
import time
import threading
from datetime import datetime
import random
import socket

class LiveMarketData:
    def __init__(self):
        self.api_endpoints = {
            'coinbase': 'https://api.coinbase.com/v2/prices/{}-USD/spot',
            'binance': 'https://api.binance.com/api/v3/ticker/price',
            'coingecko': 'https://api.coingecko.com/api/v3/simple/price',
            'cryptocompare': 'https://min-api.cryptocompare.com/data/price'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Add timeout and retry configuration
        self.session.timeout = 3  # 3 second timeout
        self.max_retries = 2
        
        self.live_prices = {}
        self.last_update = {}
        self.update_interval = 30  # Update every 30 seconds
        self.is_running = False
        self.network_available = True
        self.last_network_check = 0
        
    def check_network_connectivity(self):
        """Check if network is available"""
        try:
            # Check if we can resolve a domain
            socket.gethostbyname("api.binance.com")
            self.network_available = True
            return True
        except (socket.gaierror, socket.error):
            self.network_available = False
            return False
    
    def get_coinbase_price(self, symbol):
        """Get price from Coinbase API"""
        if not self.network_available:
            return None
            
        try:
            url = self.api_endpoints['coinbase'].format(symbol)
            response = self.session.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                return float(data['data']['amount'])
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            if "getaddrinfo failed" not in str(e):  # Don't log DNS errors
                print(f"Coinbase API error for {symbol}: {e}")
        return None
    
    def get_binance_price(self, symbol):
        """Get price from Binance API"""
        if not self.network_available:
            return None
            
        try:
            params = {'symbol': f'{symbol}USDT'}
            response = self.session.get(self.api_endpoints['binance'], params=params, timeout=3)
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            if "getaddrinfo failed" not in str(e):  # Don't log DNS errors
                print(f"Binance API error for {symbol}: {e}")
        return None
    
    def get_coingecko_price(self, symbol):
        """Get price from CoinGecko API"""
        if not self.network_available:
            return None
            
        try:
            # Map symbols to CoinGecko IDs
            symbol_mapping = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'BCH': 'bitcoin-cash',
                'USDT': 'tether',
                'USDC': 'usd-coin',
                'DAI': 'dai',
                'UNI': 'uniswap',
                'AAVE': 'aave',
                'COMP': 'compound-governance-token',
                'MKR': 'maker',
                'CRV': 'curve-dao-token',
                'SUSHI': 'sushi',
                'YFI': 'yearn-finance',
                'SNX': 'havven',
                'BAL': 'balancer',
                'REN': 'republic-protocol',
                'ZRX': '0x',
                'BAT': 'basic-attention-token',
                'MANA': 'decentraland',
                'SAND': 'the-sandbox',
                'ENJ': 'enjincoin',
                'CHZ': 'chiliz',
                'ALGO': 'algorand',
                'VET': 'vechain',
                'THETA': 'theta-token',
                'FIL': 'filecoin',
                'ICP': 'internet-computer',
                'ATOM': 'cosmos',
                'NEAR': 'near',
                'FTM': 'fantom',
                'AVAX': 'avalanche-2',
                'MATIC': 'matic-network',
                'SOL': 'solana',
                'LUNA': 'terra-luna-2',
                'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu',
                'PEPE': 'pepe',
                'BONK': 'bonk'
            }
            
            coin_id = symbol_mapping.get(symbol, symbol.lower())
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            response = self.session.get(self.api_endpoints['coingecko'], params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if coin_id in data and 'usd' in data[coin_id]:
                    return float(data[coin_id]['usd'])
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            if "getaddrinfo failed" not in str(e):  # Don't log DNS errors
                print(f"CoinGecko API error for {symbol}: {e}")
        return None
    
    def get_cryptocompare_price(self, symbol):
        """Get price from CryptoCompare API"""
        if not self.network_available:
            return None
            
        try:
            params = {
                'fsym': symbol,
                'tsyms': 'USD'
            }
            response = self.session.get(self.api_endpoints['cryptocompare'], params=params, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if 'USD' in data:
                    return float(data['USD'])
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            if "getaddrinfo failed" not in str(e):  # Don't log DNS errors
                print(f"CryptoCompare API error for {symbol}: {e}")
        return None
    
    def get_live_price(self, symbol):
        """Get live price from multiple sources with fallback"""
        # Check network connectivity periodically
        current_time = time.time()
        if current_time - self.last_network_check > 60:  # Check every minute
            self.check_network_connectivity()
            self.last_network_check = current_time
        
        # Try different APIs in order of preference
        apis = [
            ('coingecko', self.get_coingecko_price),
            ('binance', self.get_binance_price),
            ('cryptocompare', self.get_cryptocompare_price),
            ('coinbase', self.get_coinbase_price)
        ]
        
        for api_name, api_func in apis:
            try:
                price = api_func(symbol)
                if price is not None and price > 0:
                    return price
            except Exception as e:
                continue
        
        # If all APIs fail, return None
        return None
    
    def update_all_prices(self):
        """Update prices for all supported symbols"""
        symbols = [
            'BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH',
            'USDT', 'USDC', 'DAI', 'UNI', 'AAVE', 'COMP', 'MKR', 'CRV',
            'SUSHI', 'YFI', 'SNX', 'BAL', 'REN', 'ZRX', 'BAT', 'MANA',
            'SAND', 'ENJ', 'CHZ', 'ALGO', 'VET', 'THETA', 'FIL', 'ICP',
            'ATOM', 'NEAR', 'FTM', 'AVAX', 'MATIC', 'SOL', 'LUNA',
            'DOGE', 'SHIB', 'PEPE', 'BONK'
        ]
        
        updated_prices = {}
        success_count = 0
        
        for symbol in symbols:
            try:
                price = self.get_live_price(symbol)
                if price is not None:
                    updated_prices[symbol] = price
                    self.last_update[symbol] = datetime.now()
                    success_count += 1
            except Exception as e:
                continue
        
        if updated_prices:
            self.live_prices.update(updated_prices)
            print(f"Updated {success_count} prices at {datetime.now().strftime('%H:%M:%S')}")
        
        return updated_prices
    
    def get_price_change(self, symbol, hours=24):
        """Get price change percentage (simulated for now)"""
        # For now, we'll simulate price changes
        # In a full implementation, you'd fetch historical data
        if symbol in self.live_prices:
            # Simulate realistic price changes
            base_price = self.live_prices[symbol]
            if symbol in ['BTC', 'ETH']:
                change_percent = random.uniform(-5, 5)
            elif symbol in ['USDT', 'USDC', 'DAI']:
                change_percent = random.uniform(-0.5, 0.5)
            else:
                change_percent = random.uniform(-8, 8)
            
            return change_percent
        return 0.0
    
    def get_volume(self, symbol):
        """Get trading volume (simulated for now)"""
        if symbol in self.live_prices:
            price = self.live_prices[symbol]
            if price > 1000:
                return random.uniform(10000000, 100000000)
            elif price > 100:
                return random.uniform(1000000, 10000000)
            elif price > 10:
                return random.uniform(100000, 1000000)
            else:
                return random.uniform(10000, 100000)
        return 0
    
    def start_live_updates(self):
        """Start the live price update thread with enhanced auto-update"""
        if not self.is_running:
            self.is_running = True
            
            def update_loop():
                consecutive_failures = 0
                while self.is_running:
                    try:
                        # Update all prices
                        updated_count = len(self.update_all_prices())
                        
                        # Reset failure counter on success
                        if updated_count > 0:
                            consecutive_failures = 0
                            self.update_interval = 30  # Normal interval
                        else:
                            consecutive_failures += 1
                            # Increase interval on consecutive failures
                            self.update_interval = min(300, 30 * (2 ** consecutive_failures))
                        
                        time.sleep(self.update_interval)
                        
                    except Exception as e:
                        print(f"Error in update loop: {e}")
                        consecutive_failures += 1
                        # Wait longer on error, but cap at 5 minutes
                        wait_time = min(300, 60 * (2 ** consecutive_failures))
                        time.sleep(wait_time)
            
            self.update_thread = threading.Thread(target=update_loop, daemon=True)
            self.update_thread.start()
            
            # Start a separate thread for market status updates
            def status_loop():
                while self.is_running:
                    try:
                        # Update market status every 60 seconds
                        self.update_market_status()
                        time.sleep(60)
                    except Exception as e:
                        print(f"Status update error: {e}")
                        time.sleep(120)
            
            self.status_thread = threading.Thread(target=status_loop, daemon=True)
            self.status_thread.start()
            
            print("Live market data updates started with enhanced auto-update")
    
    def stop_live_updates(self):
        """Stop the live price update thread"""
        self.is_running = False
        print("Live market data updates stopped")
    
    def get_market_data(self):
        """Get complete market data for display"""
        market_data = {}
        
        for symbol, price in self.live_prices.items():
            change = self.get_price_change(symbol)
            volume = self.get_volume(symbol)
            last_update = self.last_update.get(symbol, datetime.now())
            
            market_data[symbol] = {
                'price': price,
                'change': change,
                'volume': volume,
                'last_update': last_update
            }
        
        return market_data
    
    def get_price(self, symbol):
        """Get current price for a symbol"""
        return self.live_prices.get(symbol, 0.0)
    
    def is_connected(self):
        """Check if we have recent price data"""
        if not self.live_prices:
            return False
        
        # Check if we have recent updates (within last 5 minutes)
        now = datetime.now()
        recent_updates = 0
        
        for symbol, last_update in self.last_update.items():
            if (now - last_update).total_seconds() < 300:  # 5 minutes
                recent_updates += 1
        
        return recent_updates > 0
    
    def update_market_status(self):
        """Update market status and connection health"""
        try:
            # Test connection to primary API
            test_price = self.get_coingecko_price('BTC')
            if test_price:
                self.market_status = "Connected"
                self.last_successful_update = datetime.now()
            else:
                self.market_status = "Disconnected"
        except Exception as e:
            self.market_status = "Error"
            print(f"Market status update error: {e}")
    
    def get_market_status(self):
        """Get current market status"""
        return getattr(self, 'market_status', 'Unknown') 