# DARKNET CRYPTO MARKETPLACE - TERMINAL VERSION

A plug-and-play terminal-based cryptocurrency marketplace application with a dark aesthetic, featuring real-time trading, portfolio management, and live market data.

## 🚀 Quick Start

### Windows Users
1. Double-click `run_terminal.bat` to start the application
2. Or run: `python terminal_main.py`

### Linux/Mac Users
1. Make the script executable: `chmod +x run_terminal.sh`
2. Run: `./run_terminal.sh`
3. Or run: `python3 terminal_main.py`

## 📋 Prerequisites

- Python 3.7 or higher
- Internet connection for live market data

## 🔧 Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_terminal.txt
   ```

2. **Run the application:**
   ```bash
   python terminal_main.py
   ```

## 🎯 Features

### Core Trading Features
- **Real-time Crypto Trading**: Buy and sell major cryptocurrencies
- **Live Market Data**: Real-time price updates from multiple APIs
- **Portfolio Management**: Track your holdings and portfolio value
- **Transaction History**: Complete record of all buy/sell transactions
- **Balance Management**: Real-time balance updates

### Terminal Interface
- **Dark Theme**: Black background with green text (classic terminal look)
- **Color-coded Elements**: Different colors for different types of information
- **ASCII Art Borders**: Authentic terminal-style interface
- **Responsive Design**: Works on any terminal size

### Supported Cryptocurrencies
- **Major Coins**: BTC, ETH, XRP, ADA, DOT, LINK, LTC, BCH
- **ERC20 Tokens**: USDT, USDC, DAI, UNI, AAVE, COMP, MKR, CRV, SUSHI, YFI, SNX, BAL, REN, ZRX, BAT, MANA, SAND, ENJ, CHZ, ALGO, VET, THETA, FIL, ICP, ATOM, NEAR, FTM, AVAX, MATIC, SOL, LUNA, DOGE, SHIB, PEPE, BONK

## 🎮 Usage

### Main Menu
The application starts with a main menu showing:
- Dashboard & Portfolio
- Trading Interface
- Wallet Management
- Live Market Data
- Chat Rooms
- Transaction History
- Settings

### Trading
1. Select "Trading Interface" from the main menu
2. Choose "Buy" or "Sell"
3. Enter the cryptocurrency symbol (e.g., BTC, ETH)
4. Enter the amount to trade
5. Confirm the transaction

### Portfolio Management
- View your current holdings and their values
- Track profit/loss for each position
- Monitor total portfolio value
- View recent transaction history

### Market Data
- Real-time cryptocurrency prices
- 24-hour price changes
- Market cap leaders
- Search for specific tokens

## 🎨 Terminal Colors

The application uses ANSI color codes for a rich terminal experience:
- **Green**: Success messages, positive values
- **Red**: Error messages, negative values
- **Yellow**: Warnings, highlights
- **Cyan**: Information, headers
- **White**: Regular text
- **Bold**: Important information

## 📁 File Structure

```
Darknet/
├── terminal_main.py          # Main terminal application
├── crypto_rooms.py           # Chat rooms functionality
├── live_market_data.py       # Live market data integration
├── wallet_manager.py         # Wallet management
├── ethereum_wallet.py        # Ethereum wallet functionality
├── run_terminal.bat          # Windows launcher
├── run_terminal.sh           # Unix/Linux launcher
├── requirements_terminal.txt # Python dependencies
└── TERMINAL_README.md        # This file
```

## 🔧 Configuration

### Adding Demo Balance
1. Go to Settings → Add Demo Balance
2. Enter the amount you want to add
3. Use this balance for trading

### Exporting Data
- Transaction history can be exported to JSON format
- Portfolio data is stored in memory (reset on restart)

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements_terminal.txt
   ```

2. **Color Display Issues**
   - Windows: The batch file automatically enables colors
   - Linux/Mac: Most terminals support ANSI colors by default

3. **Network Issues**
   - Check your internet connection
   - The app will show "Offline" status if no connection

4. **Python Version**
   - Ensure you're using Python 3.7 or higher
   - Check with: `python --version`

### Performance Tips
- Close other applications to free up system resources
- The app updates prices every 30 seconds
- Large portfolios may take longer to display

## 🔒 Security Features

- **Local Storage**: All data stored locally
- **No Real Trading**: This is a demonstration application
- **Privacy-focused**: No personal data collection
- **Secure APIs**: Uses HTTPS for all external connections

## 🎯 Demo Features

Since this is a demonstration application:
- All trading is simulated
- No real money is involved
- Wallet functionality is for educational purposes
- Market data is real but trading is not

## 🚀 Advanced Usage

### Command Line Options
```bash
# Run with specific Python version
python3 terminal_main.py

# Run in background (Linux/Mac)
nohup python3 terminal_main.py &

# Run with custom Python path
/path/to/python terminal_main.py
```

### Customization
You can modify the following in `terminal_main.py`:
- Update intervals for price data
- Add new cryptocurrencies
- Modify color schemes
- Change default settings

## 📊 Data Sources

The application fetches live data from:
- CoinGecko API
- Binance API
- CryptoCompare API
- Coinbase API

## 🔄 Updates

The application automatically:
- Updates prices every 30 seconds
- Refreshes market data
- Maintains transaction history
- Updates portfolio values

## 📞 Support

For issues or questions:
1. Check that all dependencies are installed
2. Ensure you're using Python 3.7 or higher
3. Verify your internet connection
4. Check the troubleshooting section above

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This is a demonstration application for educational purposes. While it includes real market data, all trading is simulated and for entertainment purposes only. No real cryptocurrency trading occurs in this application.

---

**Enjoy trading in the terminal! 🚀** 