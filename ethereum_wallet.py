import json
import os
import hashlib
import secrets
from datetime import datetime
import requests
from cryptography.fernet import Fernet
import base64

class EthereumWallet:
    def __init__(self):
        self.wallets_file = "wallets.json"
        self.wallets = {}
        self.current_wallet = None
        self.load_wallets()
        
        # Ethereum network endpoints
        self.ethereum_rpc = "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
        self.etherscan_api = "https://api.etherscan.io/api"
        self.etherscan_key = "YourApiKeyToken"  # Replace with actual API key
        
    def load_wallets(self):
        """Load existing wallets from file"""
        if os.path.exists(self.wallets_file):
            try:
                with open(self.wallets_file, 'r') as f:
                    self.wallets = json.load(f)
            except:
                self.wallets = {}
    
    def save_wallets(self):
        """Save wallets to file"""
        with open(self.wallets_file, 'w') as f:
            json.dump(self.wallets, f, indent=2)
    
    def generate_wallet(self, wallet_name):
        """Generate a new wallet with no password or encryption"""
        # Generate private key
        private_key = secrets.token_hex(32)
        
        # Generate public key (simplified - in real implementation use proper ECDSA)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        # Generate address (simplified - in real implementation use proper address derivation)
        address = "0x" + public_key[:40]
        
        # Create wallet data
        wallet_data = {
            'name': wallet_name,
            'address': address,
            'private_key': private_key,
            'balance': 0.0,
            'transactions': [],
            'created_at': datetime.now().isoformat()
        }
        
        self.wallets[address] = wallet_data
        self.save_wallets()
        
        return address, wallet_data
    
    def unlock_wallet(self, address, password):
        """Unlock wallet (now always succeeds, no password needed)"""
        if address not in self.wallets:
            return False, "Wallet not found"
        
        wallet = self.wallets[address]
        
        # Check if private_key exists, if not generate a new one
        if 'private_key' not in wallet:
            # Generate a new private key for existing wallet
            wallet['private_key'] = secrets.token_hex(32)
            self.save_wallets()
        
        # No password needed - directly use private key
        self.current_wallet = {
            'address': address,
            'private_key': wallet['private_key'],
            'data': wallet
        }
        
        return True, "Wallet unlocked successfully"
    
    def lock_wallet(self):
        """Lock current wallet (now does nothing)"""
        # Locking removed - wallets stay unlocked
        pass
    
    def get_wallet_balance(self, address=None):
        """Get wallet balance from Ethereum network"""
        if address is None and self.current_wallet:
            address = self.current_wallet['address']
        
        if not address:
            return 0.0
        
        try:
            # Try to get balance from Etherscan API
            params = {
                'module': 'account',
                'action': 'balance',
                'address': address,
                'tag': 'latest',
                'apikey': self.etherscan_key
            }
            
            response = requests.get(self.etherscan_api, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '1':
                    # Convert wei to ETH
                    balance_wei = int(data['result'])
                    balance_eth = balance_wei / 10**18
                    
                    # Update wallet balance
                    if address in self.wallets:
                        self.wallets[address]['balance'] = balance_eth
                        self.save_wallets()
                    
                    return balance_eth
            
            # Fallback: use Infura RPC
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    balance_wei = int(data['result'], 16)
                    balance_eth = balance_wei / 10**18
                    
                    # Update wallet balance
                    if address in self.wallets:
                        self.wallets[address]['balance'] = balance_eth
                        self.save_wallets()
                    
                    return balance_eth
                    
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching balance: {e}")
        except Exception as e:
            print(f"Unexpected error fetching balance: {e}")
        
        # Return cached balance if API fails
        if address in self.wallets:
            return self.wallets[address]['balance']
        
        return 0.0
    
    def get_token_balance(self, token_address, wallet_address=None):
        """Get ERC20 token balance"""
        if wallet_address is None and self.current_wallet:
            wallet_address = self.current_wallet['address']
        
        if not wallet_address:
            return 0.0
        
        try:
            # ERC20 balanceOf function signature
            balance_of_signature = "0x70a08231"
            
            # Encode the function call
            encoded_data = balance_of_signature + "000000000000000000000000" + wallet_address[2:]
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {
                        "to": token_address,
                        "data": encoded_data
                    },
                    "latest"
                ],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and data['result'] != '0x':
                    balance_wei = int(data['result'], 16)
                    # For most tokens, 18 decimals
                    balance = balance_wei / 10**18
                    return balance
                    
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching token balance: {e}")
        except Exception as e:
            print(f"Unexpected error fetching token balance: {e}")
        
        return 0.0
    
    def get_transaction_history(self, address=None):
        """Get transaction history from Etherscan"""
        if address is None and self.current_wallet:
            address = self.current_wallet['address']
        
        if not address:
            return []
        
        try:
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'sort': 'desc',
                'apikey': self.etherscan_key
            }
            
            response = requests.get(self.etherscan_api, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '1':
                    return data['result'][:20]  # Return last 20 transactions
                    
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching transaction history: {e}")
        except Exception as e:
            print(f"Unexpected error fetching transaction history: {e}")
        
        return []
    
    def create_transaction(self, to_address, amount, gas_price=20):
        """Create a transaction (simulated)"""
        if not self.current_wallet:
            return False, "No wallet selected"
        
        # This is a simplified transaction creation
        # In a real implementation, you would:
        # 1. Get the current nonce
        # 2. Sign the transaction with the private key
        # 3. Send it to the network
        
        tx_data = {
            'from': self.current_wallet['address'],
            'to': to_address,
            'value': amount,
            'gas_price': gas_price,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Add to wallet transaction history
        if self.current_wallet['address'] in self.wallets:
            self.wallets[self.current_wallet['address']]['transactions'].append(tx_data)
            self.save_wallets()
        
        return True, "Transaction created successfully"
    
    def list_wallets(self):
        """List all available wallets"""
        return list(self.wallets.keys())
    
    def get_wallet_info(self, address):
        """Get wallet information"""
        if address in self.wallets:
            wallet = self.wallets[address].copy()
            # Don't return encrypted private key
            if 'encrypted_private_key' in wallet:
                del wallet['encrypted_private_key']
            return wallet
        return None
    
    def delete_wallet(self, address, password):
        """Delete a wallet (no password needed)"""
        if address not in self.wallets:
            return False, "Wallet not found"
        
        # No password verification needed
        # Delete wallet
        del self.wallets[address]
        self.save_wallets()
        
        return True, "Wallet deleted successfully"
    
    def get_token_info(self, token_address):
        """Fetch ERC20 token symbol and decimals using eth_call"""
        try:
            # symbol() selector: 0x95d89b41, decimals() selector: 0x313ce567
            symbol_sig = "0x95d89b41"
            decimals_sig = "0x313ce567"
            # Symbol
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {"to": token_address, "data": symbol_sig},
                    "latest"
                ],
                "id": 1
            }
            resp = requests.post(self.ethereum_rpc, json=payload, timeout=5)
            symbol = None
            if resp.status_code == 200:
                data = resp.json()
                if 'result' in data and data['result'] != '0x':
                    hex_bytes = data['result'][2:]
                    symbol = bytearray.fromhex(hex_bytes).decode(errors='ignore').strip('\x00')
            # Decimals
            payload['params'][0]['data'] = decimals_sig
            resp = requests.post(self.ethereum_rpc, json=payload, timeout=5)
            decimals = 18
            if resp.status_code == 200:
                data = resp.json()
                if 'result' in data and data['result'] != '0x':
                    decimals = int(data['result'], 16)
            return symbol, decimals
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching token info: {e}")
            return None, 18
        except Exception as e:
            print(f"Unexpected error fetching token info: {e}")
            return None, 18

    def export_wallet(self, address):
        """Export wallet data as JSON for backup/import"""
        if address not in self.wallets:
            return None, "Wallet not found"
        import json
        wallet_data = self.wallets[address].copy()
        return json.dumps(wallet_data), "Wallet exported successfully"
    
    def get_all_token_balances(self, token_contracts, wallet_address=None):
        """Get balances for a list of ERC20 tokens for a wallet address"""
        balances = {}
        for symbol, contract in token_contracts.items():
            try:
                balance = self.get_token_balance(contract, wallet_address)
                balances[symbol] = balance
            except Exception as e:
                balances[symbol] = None
        return balances

    def import_wallet(self, wallet_data):
        """Import a wallet with no password or encryption"""
        address = wallet_data['address']
        self.wallets[address] = wallet_data
        self.save_wallets()
        return address, wallet_data
    
    def get_token_price(self, token_address=None, symbol=None):
        """Get token price from multiple sources"""
        try:
            # Try CoinGecko API first
            if symbol:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if symbol.lower() in data and 'usd' in data[symbol.lower()]:
                        return data[symbol.lower()]['usd']
            
            # Try CoinMarketCap API (if available)
            if symbol:
                url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}"
                headers = {'X-CMC_PRO_API_KEY': 'your-api-key'}  # Replace with actual API key
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and symbol in data['data']:
                        return data['data'][symbol]['quote']['USD']['price']
            
            # Try Uniswap V2 price (simplified)
            if token_address:
                # This is a simplified price calculation
                # In a real implementation, you'd query Uniswap pools
                return self.get_uniswap_price(token_address)
                
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching token price: {e}")
        except Exception as e:
            print(f"Unexpected error fetching token price: {e}")
        
        return None
    
    def get_uniswap_price(self, token_address):
        """Get token price from Uniswap V2 (simplified)"""
        try:
            # WETH address
            weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            
            # Uniswap V2 Factory
            factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
            
            # Get reserves from pair contract
            pair_address = self.get_pair_address(token_address, weth_address, factory_address)
            if pair_address:
                reserves = self.get_pair_reserves(pair_address)
                if reserves:
                    token_reserve, weth_reserve = reserves
                    if token_reserve > 0 and weth_reserve > 0:
                        # Calculate price in ETH, then convert to USD
                        price_in_eth = weth_reserve / token_reserve
                        eth_price = self.get_eth_price()
                        if eth_price:
                            return price_in_eth * eth_price
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Error getting Uniswap price: {e}")
        except Exception as e:
            print(f"Unexpected error getting Uniswap price: {e}")
        
        return None
    
    def get_pair_address(self, token0, token1, factory_address):
        """Get Uniswap pair address"""
        try:
            # getPair function selector
            selector = "0xe6a43905"
            # Sort tokens
            if token0.lower() < token1.lower():
                token_a, token_b = token0, token1
            else:
                token_a, token_b = token1, token0
            
            # Encode parameters
            data = selector + "000000000000000000000000" + token_a[2:] + "000000000000000000000000" + token_b[2:]
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": factory_address, "data": data}, "latest"],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and data['result'] != '0x0000000000000000000000000000000000000000000000000000000000000000':
                    return "0x" + data['result'][-40:]
        except Exception as e:
            print(f"Error getting pair address: {e}")
        return None
    
    def get_pair_reserves(self, pair_address):
        """Get reserves from Uniswap pair"""
        try:
            # getReserves function selector
            selector = "0x0902f1ac"
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": pair_address, "data": selector}, "latest"],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    result = data['result'][2:]  # Remove 0x
                    reserve0 = int(result[:64], 16)
                    reserve1 = int(result[64:128], 16)
                    return reserve0, reserve1
        except Exception as e:
            print(f"Error getting reserves: {e}")
        return None
    
    def get_eth_price(self):
        """Get ETH price in USD"""
        try:
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['ethereum']['usd']
        except Exception as e:
            print(f"Error getting ETH price: {e}")
        return None
    
    def get_portfolio_value(self, wallet_address=None):
        """Calculate total portfolio value in USD"""
        if wallet_address is None and self.current_wallet:
            wallet_address = self.current_wallet['address']
        
        if not wallet_address:
            return 0.0
        
        total_value = 0.0
        
        # Get ETH balance and value
        eth_balance = self.get_wallet_balance(wallet_address)
        eth_price = self.get_eth_price()
        if eth_price:
            total_value += eth_balance * eth_price
        
        # Get ERC20 token balances and values
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
        
        balances = self.get_all_token_balances(token_contracts, wallet_address)
        for symbol, balance in balances.items():
            if balance and balance > 0:
                price = self.get_token_price(symbol=symbol)
                if price:
                    total_value += balance * price
        
        return total_value
    
    def create_transaction_data(self, to_address, amount, gas_price=20, gas_limit=21000):
        """Create transaction data for signing"""
        if not self.current_wallet:
            return None, "No wallet selected"
        
        try:
            # Get nonce
            nonce = self.get_nonce(self.current_wallet['address'])
            
            # Create transaction data
            tx_data = {
                'nonce': nonce,
                'to': to_address,
                'value': int(amount * 10**18),  # Convert to wei
                'gas': gas_limit,
                'gasPrice': int(gas_price * 10**9),  # Convert to gwei
                'chainId': 1  # Ethereum mainnet
            }
            
            return tx_data, "Transaction data created"
            
        except Exception as e:
            return None, f"Error creating transaction: {str(e)}"
    
    def get_nonce(self, address):
        """Get current nonce for an address"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionCount",
                "params": [address, "latest"],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return int(data['result'], 16)
        except Exception as e:
            print(f"Error getting nonce: {e}")
        return 0
    
    def sign_transaction(self, tx_data):
        """Sign a transaction with the current wallet's private key"""
        if not self.current_wallet:
            return None, "No wallet selected"
        
        try:
            # This is a simplified signing process
            # In a real implementation, you'd use proper ECDSA signing
            import hashlib
            
            # Create transaction hash (simplified)
            tx_string = f"{tx_data['nonce']}{tx_data['to']}{tx_data['value']}{tx_data['gas']}{tx_data['gasPrice']}"
            tx_hash = hashlib.sha256(tx_string.encode()).hexdigest()
            
            # Sign with private key (simplified)
            private_key = self.current_wallet['private_key']
            signature = hashlib.sha256((tx_hash + private_key).encode()).hexdigest()
            
            return {
                'hash': tx_hash,
                'signature': signature,
                'rawTransaction': tx_string
            }, "Transaction signed successfully"
            
        except Exception as e:
            return None, f"Error signing transaction: {str(e)}"
    
    def get_gas_estimate(self, to_address, amount):
        """Estimate gas for a transaction"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_estimateGas",
                "params": [{
                    "to": to_address,
                    "value": hex(int(amount * 10**18))
                }],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return int(data['result'], 16)
        except Exception as e:
            print(f"Error estimating gas: {e}")
        return 21000  # Default gas limit
    
    def get_gas_price(self):
        """Get current gas price"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 1
            }
            
            response = requests.post(self.ethereum_rpc, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    gas_price_wei = int(data['result'], 16)
                    return gas_price_wei / 10**9  # Convert to gwei
        except Exception as e:
            print(f"Error getting gas price: {e}")
        return 20  # Default gas price in gwei
    
    def add_test_balance(self, address, amount):
        """Add test balance to wallet (for testing purposes)"""
        if address not in self.wallets:
            raise Exception("Wallet not found")
        
        # Add the test balance to the wallet's cached balance
        current_balance = self.wallets[address].get('balance', 0.0)
        new_balance = current_balance + amount
        
        self.wallets[address]['balance'] = new_balance
        self.save_wallets()
        
        # Update current wallet if it's the active one
        if self.current_wallet and self.current_wallet['address'] == address:
            self.current_wallet['data']['balance'] = new_balance
        
        return new_balance 