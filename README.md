# Darknet Crypto Marketplace

A terminal-based cryptocurrency trading platform with real-time market data, portfolio tracking

## Quick Start

**Windows:**
```bash
git clone https://github.com/YOUR_USERNAME/darknet-crypto-marketplace.git
cd darknet-crypto-marketplace
pip install -r requirements_terminal.txt
python terminal_main.py
```

**Linux/Mac:**
```bash
git clone https://github.com/YOUR_USERNAME/darknet-crypto-marketplace.git
cd darknet-crypto-marketplace
pip3 install -r requirements_terminal.txt
python3 terminal_main.py
```

## Features

- Real-time cryptocurrency trading with live market data
- Portfolio management with profit/loss tracking
- Support for 40+ cryptocurrencies including BTC, ETH, XRP, ADA, DOT, LINK, LTC, BCH
- ERC20 tokens: USDT, USDC, DAI, UNI, AAVE, COMP, MKR, CRV, SUSHI, YFI, SNX, BAL, REN, ZRX, BAT, MANA, SAND, ENJ, CHZ, ALGO, VET, THETA, FIL, ICP, ATOM, NEAR, FTM, AVAX, MATIC, SOL, LUNA, DOGE, SHIB, PEPE, BONK
- Transaction history with export capability
- Classic terminal aesthetic with dark theme
- Cross-platform compatibility

## Usage

1. Start the app: `python terminal_main.py`
2. Add demo balance in Settings
3. Start trading in the Trading Interface
4. Monitor your portfolio in the Dashboard

## Project Structure

```
darknet-crypto-marketplace/
├── terminal_main.py          # Main application
├── crypto_rooms.py           # Chat functionality  
├── live_market_data.py       # Live market data
├── wallet_manager.py         # Wallet management
├── ethereum_wallet.py        # Ethereum wallet features
├── run_terminal.bat          # Windows launcher
├── run_terminal.sh           # Linux/Mac launcher
├── requirements_terminal.txt # Python dependencies
└── README.md                 # This file
```

## Installation

**Prerequisites:** Python 3.7+ and internet connection

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/darknet-crypto-marketplace.git
   cd darknet-crypto-marketplace
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_terminal.txt
   ```

3. Run the application:
   ```bash
   python terminal_main.py
   ```

## Interface

The app uses a classic terminal aesthetic with:
- Dark theme (black background, green text)
- Color-coded information
- ASCII art borders
- Responsive design

## Troubleshooting

**Module not found errors:**
```bash
pip install -r requirements_terminal.txt
```

**Python not found:** Install from [python.org](https://python.org) and add to PATH

**Network issues:** Check your internet connection

**Color display issues:** Most terminals support ANSI colors by default

## Security

- All data stored locally
- No real trading (demonstration only)
- No personal data collection
- Secure HTTPS connections

## Demo Features

This is a demonstration application:
- All trading is simulated
- Market data is real but trading is not
- Perfect for learning crypto trading concepts

## Advanced Usage

**Customization:** Modify `terminal_main.py` to change update intervals, add cryptocurrencies, or adjust color schemes.

**Command line options:**
```bash
python3 terminal_main.py          # Specific Python version
nohup python3 terminal_main.py &  # Background (Linux/Mac)
/path/to/python terminal_main.py  # Custom Python path
```

## Data Sources

Live data from:
- [CoinGecko API](https://coingecko.com/api)
- [Binance API](https://binance.com/api)  
- [CryptoCompare API](https://cryptocompare.com/api)
- [Coinbase API](https://coinbase.com/api)

## Contributing

Contributions welcome! Fork the repository and submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) file.

## Disclaimer

This is a demonstration application for educational purposes. All trading is simulated and for entertainment only.

## Support

If you encounter issues, check the troubleshooting section above or open an issue on GitHub. 