import telebot
from telebot import apihelper
from telebot import types
import logging
import os
from dotenv import load_dotenv
import time
from PIL import Image
from io import BytesIO
import requests
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid GUI threading issues
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter
import google.generativeai as genai  # Make sure to install: pip install google-generativeai
import json
from datetime import datetime
from urllib.parse import quote

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

apihelper.ENABLE_MIDDLEWARE = True

load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(API_TOKEN)

user_languages = {}  # Store user languages {chat_id: 'en'/'fa'/'ar'}

texts = {
    'en': {
        'select_language': "Please select your language:",
        'welcome': "🚀 Welcome to the Crypto Tracker Bot!\n\n📋 Please select a cryptocurrency from the list below:\n\n💡 Tip: Click on any coin to view its performance over different timeframes!",
        'selected': "🔹 You selected: <b>{}</b>\n\n📊 Choose a timeframe to view performance or AI analysis:",
        'loading_chart': "⏳ Loading chart for <b>{}</b> ({})...\n\nThis may take a moment...",
        'chart_caption': "📈 Candlestick Chart for <b>{}</b>\n⏰ Timeframe: {}\n💰 Current Price: {:.2f} USD\n📈 24h Change: {:.2f}%\n📊 Source: Binance (with Volume and SMA 20)",
        'error_chart': "❌ Sorry, couldn't load the chart for <b>{}</b> ({}).\n\nPlease try again later.",
        'error_general': "❌ An error occurred while loading the chart.\n\nPlease try again later.",
        'loading_ai': "⏳ Performing AI analysis for <b>{}</b>...\n\nThis may take a moment...",
        'error_ai': "❌ An error occurred during AI analysis.\n\nPlease try again later.",
        'another_coin': "✨ Would you like to check another cryptocurrency?",
        'available_coins': "🔹 Here are the available cryptocurrencies:",
        'handle_text': "🤖 Please use the buttons below to select a cryptocurrency:",
        'language_set': "Language set to {}",
        'ai_header': "🤖 <b>AI Analysis Report</b>\n",
        'analysis_section': "\n📊 <b>Market Analysis:</b>\n{}",
        'recommendation_section': "\n\n💡 <b>Trading Recommendation:</b>\n🔹 Action: <b>{}</b>\n🔹 Target Price: <b>${:.2f}</b>\n🔹 Target Date: <b>{}</b>",
        'donation_thanks': "⭐ Thank you for your support!\n\n💝 Your donation helps us keep this bot running and improving.\n\nYou can support us with Telegram Stars:",
        'donation_success': "🎉 Thank you for your generous donation!\n\n💖 Your support means the world to us!",
        'donation_cancelled': "No problem! You can donate anytime by using /donate command.",
    },
    'fa': {
        'select_language': "لطفاً زبان خود را انتخاب کنید:",
        'welcome': "🚀 به ربات ردیاب کریپتو خوش آمدید!\n\n📋 لطفاً یک ارز دیجیتال از لیست زیر انتخاب کنید:\n\n💡 نکته: روی هر کوین کلیک کنید تا عملکرد آن را در بازه‌های زمانی مختلف ببینید!",
        'selected': "🔹 شما انتخاب کردید: <b>{}</b>\n\n📊 یک بازه زمانی برای مشاهده عملکرد یا تحلیل هوش مصنوعی انتخاب کنید:",
        'loading_chart': "⏳ در حال بارگذاری نمودار برای <b>{}</b> ({})...\n\nاین ممکن است کمی طول بکشد...",
        'chart_caption': "📈 نمودار شمعی برای <b>{}</b>\n⏰ بازه زمانی: {}\n💰 قیمت فعلی: {:.2f} دلار\n📈 تغییر 24 ساعته: {:.2f}%\n📊 منبع: بایننس (با حجم و SMA 20)",
        'error_chart': "❌ متأسفانه نتوانستیم نمودار را برای <b>{}</b> ({}) بارگذاری کنیم.\n\nلطفاً بعداً امتحان کنید.",
        'error_general': "❌ خطایی در بارگذاری نمودار رخ داد.\n\nلطفاً بعداً امتحان کنید.",
        'loading_ai': "⏳ در حال انجام تحلیل هوش مصنوعی برای <b>{}</b>...\n\nاین ممکن است کمی طول بکشد...",
        'error_ai': "❌ خطایی در تحلیل هوش مصنوعی رخ داد.\n\nلطفاً بعداً امتحان کنید.",
        'another_coin': "✨ آیا مایلید ارز دیجیتال دیگری بررسی کنید؟",
        'available_coins': "🔹 ارزهای دیجیتال موجود عبارتند از:",
        'handle_text': "🤖 لطفاً از دکمه‌های زیر برای انتخاب ارز دیجیتال استفاده کنید:",
        'language_set': "زبان به {} تنظیم شد",
        'ai_header': "🤖 <b>گزارش تحلیل هوش مصنوعی</b>\n",
        'analysis_section': "\n📊 <b>تحلیل بازار:</b>\n{}",
        'recommendation_section': "\n\n💡 <b>توصیه معاملاتی:</b>\n🔹 اقدام: <b>{}</b>\n🔹 قیمت هدف: <b>${:.2f}</b>\n🔹 تاریخ هدف: <b>{}</b>",
        'donation_thanks': "⭐ از حمایت شما متشکریم!\n\n💝 کمک مالی شما به ما کمک می‌کند این ربات را فعال و بهتر نگه داریم.\n\nمی‌توانید با Telegram Stars از ما حمایت کنید:",
        'donation_success': "🎉 از کمک سخاوتمندانه شما متشکریم!\n\n💖 حمایت شما برای ما بسیار ارزشمند است!",
        'donation_cancelled': "مشکلی نیست! می‌توانید هر زمان با دستور /donate کمک کنید.",
    },
    'ar': {
        'select_language': "يرجى اختيار لغتك:",
        'welcome': "🚀 مرحبا بك في بوت تتبع العملات المشفرة!\n\n📋 يرجى تحديد عملة مشفرة من القائمة أدناه:\n\n💡 نصيحة: انقر على أي عملة لعرض أدائها عبر فترات زمنية مختلفة!",
        'selected': "🔹 لقد حددت: <b>{}</b>\n\n📊 اختر إطارًا زمنيًا لعرض الأداء أو تحليل الذكاء الاصطناعي:",
        'loading_chart': "⏳ جاري تحميل الرسم البياني لـ <b>{}</b> ({})...\n\nقد يستغرق هذا لحظة...",
        'chart_caption': "📈 رسم بياني شمعي لـ <b>{}</b>\n⏰ الإطار الزمني: {}\n💰 السعر الحالي: {:.2f} دولار\n📈 التغيير في 24 ساعة: {:.2f}%\n📊 المصدر: بينانس (مع الحجم و SMA 20)",
        'error_chart': "❌ عذرًا، لم نتمكن من تحميل الرسم البياني لـ <b>{}</b> ({}).\n\nيرجى المحاولة لاحقًا.",
        'error_general': "❌ حدث خطأ أثناء تحميل الرسم البياني.\n\nيرجى المحاولة لاحقًا.",
        'loading_ai': "⏳ جاري إجراء تحليل الذكاء الاصطناعي لـ <b>{}</b>...\n\nقد يستغرق هذا لحظة...",
        'error_ai': "❌ حدث خطأ أثناء تحليل الذكاء الاصطناعي.\n\nيرجى المحاولة لاحقًا.",
        'another_coin': "✨ هل ترغب في التحقق من عملة مشفرة أخرى؟",
        'available_coins': "🔹 إليك العملات المشفرة المتاحة:",
        'handle_text': "🤖 يرجى استخدام الأزرار أدناه لتحديد عملة مشفرة:",
        'language_set': "تم تعيين اللغة إلى {}",
        'ai_header': "🤖 <b>تقرير تحليل الذكاء الاصطناعي</b>\n",
        'analysis_section': "\n📊 <b>تحليل السوق:</b>\n{}",
        'recommendation_section': "\n\n💡 <b>التوصية التجارية:</b>\n🔹 الإجراء: <b>{}</b>\n🔹 السعر المستهدف: <b>${:.2f}</b>\n🔹 التاريخ المستهدف: <b>{}</b>",
        'donation_thanks': "⭐ شكرا لدعمك!\n\n💝 تبرعك يساعدنا في الحفاظ على هذا البوت وتحسينه.\n\nيمكنك دعمنا بنجوم تيليجرام:",
        'donation_success': "🎉 شكرا لتبرعك السخي!\n\n💖 دعمك يعني الكثير بالنسبة لنا!",
        'donation_cancelled': "لا مشكلة! يمكنك التبرع في أي وقت باستخدام الأمر /donate.",
    }
}

language_full = {
    'en': 'English',
    'fa': 'Persian',
    'ar': 'Arabic'
}

# Mapping of crypto names to Binance symbols (without emojis)
BINANCE_SYMBOLS = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Ethereum (ETH)": "ETHUSDT", 
    "Binance Coin (BNB)": "BNBUSDT",
    "Ripple (XRP)": "XRPUSDT",
    "Cardano (ADA)": "ADAUSDT",
    "Solana (SOL)": "SOLUSDT",
    "Polkadot (DOT)": "DOTUSDT",
    "Dogecoin (DOGE)": "DOGEUSDT",
    "Avalanche (AVAX)": "AVAXUSDT",
    "Chainlink (LINK)": "LINKUSDT",
    "Litecoin (LTC)": "LTCUSDT",
    "Polygon (MATIC)": "MATICUSDT",
    "Cosmos (ATOM)": "ATOMUSDT",
    "Filecoin (FIL)": "FILUSDT",
    "Algorand (ALGO)": "ALGOUSDT",
    "Stellar (XLM)": "XLMUSDT",
    "Tron (TRX)": "TRXUSDT",
    "Monero (XMR)": "XMRUSDT",
    "Ethereum Classic (ETC)": "ETCUSDT",
    "VeChain (VET)": "VETUSDT",
    "Hedera (HBAR)": "HBARUSDT",
    "Internet Computer (ICP)": "ICPUSDT",
    "Uniswap (UNI)": "UNIUSDT",
    "Aptos (APT)": "APTUSDT",
    "Arbitrum (ARB)": "ARBUSDT",
    "Optimism (OP)": "OPUSDT",
    "Near Protocol (NEAR)": "NEARUSDT",
    "Stacks (STX)": "STXUSDT",
    "Immutable (IMX)": "IMXUSDT",
    "Cronos (CRO)": "CROUSDT",
    "Kaspa (KAS)": "KASUSDT",
    "Quant (QNT)": "QNTUSDT",
    "Render (RNDR)": "RNDRUSDT",
    "Injective (INJ)": "INJUSDT",
    "Sui (SUI)": "SUIUSDT",
    "The Graph (GRT)": "GRTUSDT",
    "Theta Network (THETA)": "THETAUSDT",
    "Maker (MKR)": "MKRUSDT",
    "Synthetix (SNX)": "SNXUSDT",
    "Aave (AAVE)": "AAVEUSDT",
    "EOS (EOS)": "EOSUSDT",
    "Axie Infinity (AXS)": "AXSUSDT",
    "The Sandbox (SAND)": "SANDUSDT",
    "Decentraland (MANA)": "MANAUSDT",
    "Tezos (XTZ)": "XTZUSDT",
    "Flow (FLOW)": "FLOWUSDT",
    "Fantom (FTM)": "FTMUSDT",
    "Kava (KAVA)": "KAVAUSDT",
    "IOTA (IOTA)": "IOTAUSDT",
    "Zilliqa (ZIL)": "ZILUSDT",
    "Enjin Coin (ENJ)": "ENJUSDT",
    "Gala (GALA)": "GALAUSDT",
    "Chiliz (CHZ)": "CHZUSDT",
    "1inch (1INCH)": "1INCHUSDT",
    "Compound (COMP)": "COMPUSDT",
    "Curve DAO (CRV)": "CRVUSDT",
    "Sushi (SUSHI)": "SUSHIUSDT",
    "Pancakeswap (CAKE)": "CAKEUSDT",
    "Loopring (LRC)": "LRCUSDT",
    "Gnosis (GNO)": "GNOUSDT",
    "Zcash (ZEC)": "ZECUSDT",
    "Dash (DASH)": "DASHUSDT",
    "Waves (WAVES)": "WAVESUSDT",
    "Qtum (QTUM)": "QTUMUSDT",
    "Arweave (AR)": "ARUSDT",
    "Basic Attention (BAT)": "BATUSDT",
    "Harmony (ONE)": "ONEUSDT",
    "Celo (CELO)": "CELOUSD",
    "Ankr (ANKR)": "ANKRUSDT",
    "Fetch.ai (FET)": "FETUSDT",
    "Ocean Protocol (OCEAN)": "OCEANUSDT",
    "Band Protocol (BAND)": "BANDUSDT",
    "Storj (STORJ)": "STORJUSDT",
    "NEM (XEM)": "XEMUSDT",
    "Ravencoin (RVN)": "RVNUSDT",
    "ICON (ICX)": "ICXUSDT",
    "OMG Network (OMG)": "OMGUSDT",
    "Ontology (ONT)": "ONTUSDT",
    "WOO Network (WOO)": "WOOUSDT",
    "Skale (SKL)": "SKLUSDT",
    "Coti (COTI)": "COTIUSDT",
    "Amp (AMP)": "AMPUSDT",
    "Civic (CVC)": "CVCUSDT",
    "Status (SNT)": "SNTUSDT",
    "Golem (GLM)": "GLMUSDT",
    "Request (REQ)": "REQUSDT",
    "Power Ledger (POWR)": "POWRUSDT",
    "Mask Network (MASK)": "MASKUSDT",
    "My Neighbor Alice (ALICE)": "ALICEUSDT",
    "Dent (DENT)": "DENTUSDT",
    "Voyager (VGX)": "VGXUSDT",
    "Kyber Network (KNC)": "KNCUSDT",
    "Perpetual Protocol (PERP)": "PERPUSDT",
    "Numeraire (NMR)": "NMRUSDT",
    "Spell Token (SPELL)": "SPELLUSDT",
    "Balancer (BAL)": "BALUSDT",
    "Convex Finance (CVX)": "CVXUSDT",
    "Yearn.finance (YFI)": "YFIUSDT",
    "UMA (UMA)": "UMAUSDT",
    "Livepeer (LPT)": "LPTUSDT"
}

# List of 100 crypto coins with emojis
CRYPTO_COINS = [
    "₿ Bitcoin (BTC)", "⧫ Ethereum (ETH)", "🔶 Binance Coin (BNB)", "✕ Ripple (XRP)",
    "₳ Cardano (ADA)", "◉ Solana (SOL)", "● Polkadot (DOT)", "Ð Dogecoin (DOGE)",
    "🔺 Avalanche (AVAX)", "🔗 Chainlink (LINK)", "Ł Litecoin (LTC)", "🔷 Polygon (MATIC)",
    "⚛ Cosmos (ATOM)", "💾 Filecoin (FIL)", "◆ Algorand (ALGO)", "★ Stellar (XLM)",
    "🔴 Tron (TRX)", "🔒 Monero (XMR)", "⧫ Ethereum Classic (ETC)", "✓ VeChain (VET)",
    "ℏ Hedera (HBAR)", "∞ Internet Computer (ICP)", "🦄 Uniswap (UNI)", "🅰 Aptos (APT)",
    "🔵 Arbitrum (ARB)", "🔴 Optimism (OP)", "⭕ Near Protocol (NEAR)", "📚 Stacks (STX)",
    "⚔ Immutable (IMX)", "🔷 Cronos (CRO)", "💎 Kaspa (KAS)", "🔢 Quant (QNT)",
    "🎨 Render (RNR)", "💉 Injective (INJ)", "🌊 Sui (SUI)", "📊 The Graph (GRT)",
    "θ Theta Network (THETA)", "🏛 Maker (MKR)", "⚡ Synthetix (SNX)", "👻 Aave (AAVE)",
    "📱 EOS (EOS)", "🎮 Axie Infinity (AXS)", "🏖 The Sandbox (SAND)", "🌐 Decentraland (MANA)",
    "🔷 Tezos (XTZ)", "🌊 Flow (FLOW)", "👻 Fantom (FTM)", "🔶 Kava (KAVA)",
    "🔗 IOTA (IOTA)", "⚡ Zilliqa (ZIL)", "🎮 Enjin Coin (ENJ)", "🎪 Gala (GALA)",
    "🌶 Chiliz (CHZ)", "1️⃣ 1inch (1INCH)", "🏦 Compound (COMP)", "📈 Curve DAO (CRV)",
    "🍣 Sushi (SUSHI)", "🥞 Pancakeswap (CAKE)", "🔁 Loopring (LRC)", "🦉 Gnosis (GNO)",
    "🛡 Zcash (ZEC)", "💨 Dash (DASH)", "🌊 Waves (WAVES)", "Q Qtum (QTUM)",
    "📦 Arweave (AR)", "🦁 Basic Attention (BAT)", "1️⃣ Harmony (ONE)", "💚 Celo (CELO)",
    "⚓ Ankr (ANKR)", "🤖 Fetch.ai (FET)", "🌊 Ocean Protocol (OCEAN)", "🎵 Band Protocol (BAND)",
    "☁ Storj (STORJ)", "💎 NEM (XEM)", "🐦 Ravencoin (RVN)", "🔷 ICON (ICX)",
    "⚡ OMG Network (OMG)", "🔷 Ontology (ONT)", "🔥 WOO Network (WOO)", "⚡ Skale (SKL)",
    "💠 Coti (COTI)", "🔊 Amp (AMP)", "🔑 Civic (CVC)", "💬 Status (SNT)",
    "🤖 Golem (GLM)", "📨 Request (REQ)", "⚡ Power Ledger (POWR)", "😷 Mask Network (MASK)",
    "🏰 My Neighbor Alice (ALICE)", "🦷 Dent (DENT)", "🚀 Voyager (VGX)", "🔷 Kyber Network (KNC)",
    "♾ Perpetual Protocol (PERP)", "🔢 Numeraire (NMR)", "✨ Spell Token (SPELL)", "⚖ Balancer (BAL)",
    "🔺 Convex Finance (CVX)", "💰 Yearn.finance (YFI)", "📊 UMA (UMA)", "📹 Livepeer (LPT)"
]

def get_binance_ohlc(symbol, interval, limit):
    """Fetch OHLCV data from Binance API"""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df
    except Exception as e:
        print(f"Error fetching OHLC: {e}")
        return None

def get_current_data(symbol):
    """Fetch current price and 24h change from Binance"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            'last_price': float(data['lastPrice']),
            'price_change_percent': float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error fetching current data: {e}")
        return None

def plot_candlestick(df, coin_name, timeframe, interval):
    """Plot candlestick chart with volume and SMA using matplotlib"""
    
    # Calculate interval in minutes for width
    if interval.endswith('m'):
        min_interval = int(interval[:-1])
    elif interval.endswith('h'):
        min_interval = int(interval[:-1]) * 60
    else:
        min_interval = 1  # default
    
    width = (min_interval / 1440.0) * 0.8  # width in days
    width2 = width / 10.0  # thin wick
    
    up = df[df.close >= df.open]
    down = df[df.close < df.open]
    
    col_up = 'green'
    col_down = 'red'
    
    fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(10, 8), sharex=True)
    
    # Candlestick bodies
    ax1.bar(up['open_time'], up['close'] - up['open'], width, bottom=up['open'], color=col_up)
    ax1.bar(down['open_time'], down['open'] - down['close'], width, bottom=down['close'], color=col_down)
    
    # Candlestick wicks
    ax1.bar(up['open_time'], up['high'] - up['close'], width2, bottom=up['close'], color=col_up)
    ax1.bar(up['open_time'], up['open'] - up['low'], width2, bottom=up['low'], color=col_up)
    ax1.bar(down['open_time'], down['high'] - down['open'], width2, bottom=down['open'], color=col_down)
    ax1.bar(down['open_time'], down['close'] - down['low'], width2, bottom=down['low'], color=col_down)
    
    # Simple Moving Average (SMA 20)
    if len(df) >= 20:
        sma = df['close'].rolling(window=20).mean()
        ax1.plot(df['open_time'], sma, color='orange', label='SMA 20')
        ax1.legend()
    
    ax1.set_title(f"{coin_name} Candlestick Chart ({timeframe})")
    ax1.set_ylabel("Price (USD)")
    ax1.grid(True)
    
    # Volume
    ax2.bar(df['open_time'], df['volume'], width, color=[col_up if c >= o else col_down for o, c in zip(df['open'], df['close'])])
    ax2.set_ylabel("Volume")
    ax2.grid(True)
    
    # X-axis formatting
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    
    return buf

def get_crypto_chart(coin_full_name, timeframe):
    """Main function to get chart: fetch data, plot, and return buffer"""
    symbol = BINANCE_SYMBOLS.get(coin_full_name)
    if not symbol:
        return None
    
    timeframe_params = {
        '1h': {'interval': '1m', 'limit': 60},
        '1w': {'interval': '1h', 'limit': 168},
        '1m': {'interval': '1h', 'limit': 720}
    }
    
    params = timeframe_params.get(timeframe)
    if not params:
        return None
    
    df = get_binance_ohlc(symbol, params['interval'], params['limit'])
    if df is None or df.empty:
        return None
    
    chart_buf = plot_candlestick(df, coin_full_name, timeframe, params['interval'])
    
    return chart_buf

def create_donation_keyboard():
    """Create inline keyboard with donation options using Telegram Stars"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Donation buttons with different star amounts
    button_1 = types.InlineKeyboardButton(text="⭐ 1 Star", callback_data="donate_1")
    button_5 = types.InlineKeyboardButton(text="⭐ 5 Stars", callback_data="donate_5")
    button_10 = types.InlineKeyboardButton(text="⭐ 10 Stars", callback_data="donate_10")
    button_25 = types.InlineKeyboardButton(text="⭐ 25 Stars", callback_data="donate_25")
    button_50 = types.InlineKeyboardButton(text="⭐ 50 Stars", callback_data="donate_50")
    button_100 = types.InlineKeyboardButton(text="⭐ 100 Stars", callback_data="donate_100")
    
    keyboard.add(button_1, button_5)
    keyboard.add(button_10, button_25)
    keyboard.add(button_50, button_100)
    
    return keyboard

def create_main_menu_keyboard(lang='en'):
    """Create main menu keyboard with donation button"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    coins_button = types.InlineKeyboardButton(
        text="📊 View Coins" if lang == 'en' else "📊 مشاهده کوین‌ها" if lang == 'fa' else "📊 عرض العملات",
        callback_data="show_coins"
    )
    donate_button = types.InlineKeyboardButton(
        text="⭐ Donate" if lang == 'en' else "⭐ حمایت مالی" if lang == 'fa' else "⭐ تبرع",
        callback_data="show_donation"
    )
    
    keyboard.add(coins_button, donate_button)
    
    return keyboard

def create_crypto_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    for i in range(0, len(CRYPTO_COINS), 2):
        row = []
        for j in range(i, min(i + 2, len(CRYPTO_COINS))):
            coin = CRYPTO_COINS[j]
            button = types.InlineKeyboardButton(text=coin, callback_data=f"coin_{j}")
            row.append(button)
        keyboard.add(*row)
    
    return keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    for i in range(0, len(CRYPTO_COINS), 2):
        row = []
        for j in range(i, min(i + 2, len(CRYPTO_COINS))):
            coin = CRYPTO_COINS[j]
            button = types.InlineKeyboardButton(text=coin, callback_data=f"coin_{j}")
            row.append(button)
        keyboard.add(*row)
    
    return keyboard

def create_timeframe_keyboard(coin_name):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    button_1h = types.InlineKeyboardButton(text="🕐 1 Hour", callback_data=f"timeframe_{coin_name}_1h")
    button_1w = types.InlineKeyboardButton(text="📅 1 Week", callback_data=f"timeframe_{coin_name}_1w")
    button_1m = types.InlineKeyboardButton(text="🗓️ 1 Month", callback_data=f"timeframe_{coin_name}_1m")
    button_ai = types.InlineKeyboardButton(text="🤖 AI Analysis", callback_data=f"ai_{coin_name}")
    
    keyboard.add(button_1h, button_1w)
    keyboard.add(button_1m, button_ai)
    return keyboard

def send_long_message(chat_id, text, parse_mode=None):
    """Send long message by splitting into parts"""
    max_length = 4096
    while len(text) > max_length:
        part = text[:max_length]
        bot.send_message(chat_id, part, parse_mode=parse_mode)
        text = text[max_length:]
    if text:
        bot.send_message(chat_id, text, parse_mode=parse_mode)

def create_language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    button_en = types.InlineKeyboardButton("English", callback_data="lang_en")
    button_fa = types.InlineKeyboardButton("فارسی", callback_data="lang_fa")
    button_ar = types.InlineKeyboardButton("العربية", callback_data="lang_ar")
    keyboard.add(button_en, button_fa, button_ar)
    return keyboard

def create_google_calendar_link(coin_name, recommendation, price, dt_str, analysis):
    """Create a Google Calendar link"""
    # Format date for Google Calendar (YYYYMMDDTHHmmss)
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    start_time = dt.strftime("%Y%m%dT%H%M%S")
    
    # Add 1 hour for end time
    from datetime import timedelta
    end_dt = dt + timedelta(hours=1)
    end_time = end_dt.strftime("%Y%m%dT%H%M%S")
    
    # Create event title
    title = f"{recommendation.upper()} {coin_name} at ${price}"
    
    # Create description (truncated for URL length)
    description = f"AI Trading Recommendation\n\nAction: {recommendation.upper()}\nTarget Price: ${price}\n\nAnalysis Summary: {analysis[:200]}..."
    
    # URL encode the parameters
    calendar_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(title)}"
        f"&dates={start_time}/{end_time}"
        f"&details={quote(description)}"
        f"&sf=true&output=xml"
    )
    
    return calendar_url

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    lang = user_languages.get(chat_id, 'en')
    bot.reply_to(message, texts[lang]['select_language'], reply_markup=create_language_keyboard())

@bot.message_handler(commands=['donate'])
def send_donation(message):
    chat_id = message.chat.id
    lang = user_languages.get(chat_id, 'en')
    bot.reply_to(
        message,
        texts[lang]['donation_thanks'],
        reply_markup=create_donation_keyboard(),
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    lang = user_languages.get(chat_id, 'en')
    
    if call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        user_languages[chat_id] = new_lang
        bot.answer_callback_query(call.id, texts[new_lang]['language_set'].format(language_full[new_lang]))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts[new_lang]['welcome'],
            reply_markup=create_crypto_keyboard()
        )
        return
    
    lang = user_languages.get(chat_id, 'en')
    
    if call.data.startswith("coin_"):
        coin_index = int(call.data.split("_")[1])
        selected_coin = CRYPTO_COINS[coin_index]
        clean_coin_name = selected_coin.split(' ', 1)[1]
        
        bot.answer_callback_query(
            call.id, 
            f"🎯 Selected: {clean_coin_name}",
            show_alert=False
        )
        
        timeframe_keyboard = create_timeframe_keyboard(clean_coin_name)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts[lang]['selected'].format(clean_coin_name),
            reply_markup=timeframe_keyboard,
            parse_mode='HTML'
        )
    
    elif call.data.startswith("timeframe_"):
        parts = call.data.split("_", 2)
        coin_full_name = parts[1]
        timeframe = parts[2]
        
        symbol = BINANCE_SYMBOLS.get(coin_full_name)
        
        if not symbol:
            print(f"Coin not found in mapping: {coin_full_name}")
            bot.answer_callback_query(
                call.id,
                "❌ Sorry, this coin is not available",
                show_alert=True
            )
            return
        
        timeframe_map = {
            '1h': '🕐 1 Hour',
            '1w': '📅 1 Week', 
            '1m': '🗓️ 1 Month'
        }
        
        readable_timeframe = timeframe_map.get(timeframe, timeframe)
        
        processing_msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts[lang]['loading_chart'].format(coin_full_name, readable_timeframe),
            parse_mode='HTML'
        )
        
        try:
            chart_buf = get_crypto_chart(coin_full_name, timeframe)
            
            current_data = get_current_data(symbol)
            
            if chart_buf:
                caption = texts[lang]['chart_caption'].format(coin_full_name, readable_timeframe, current_data['last_price'], current_data['price_change_percent'])
                
                bot.send_photo(
                    call.message.chat.id,
                    chart_buf,
                    caption=caption,
                    parse_mode='HTML'
                )
                
                try:
                    bot.delete_message(call.message.chat.id, processing_msg.message_id)
                except:
                    pass
                
                bot.send_message(
                    call.message.chat.id,
                    texts[lang]['another_coin'],
                    reply_markup=create_crypto_keyboard()
                )
                
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=processing_msg.message_id,
                    text=texts[lang]['error_chart'].format(coin_full_name, readable_timeframe),
                    parse_mode='HTML'
                )
                
        except Exception as e:
            print(f"Error in timeframe handler: {e}")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=processing_msg.message_id,
                text=texts[lang]['error_general'],
                parse_mode='HTML'
            )
    
    elif call.data.startswith("ai_"):
        coin_full_name = call.data.split("_", 1)[1]
        
        symbol = BINANCE_SYMBOLS.get(coin_full_name)
        
        if not symbol:
            print(f"Coin not found in mapping: {coin_full_name}")
            bot.answer_callback_query(
                call.id,
                "❌ Sorry, this coin is not available",
                show_alert=True
            )
            return
        
        processing_msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts[lang]['loading_ai'].format(coin_full_name),
            parse_mode='HTML'
        )
        
        try:
            # Generate charts for all timeframes
            chart_1h = get_crypto_chart(coin_full_name, '1h')
            chart_1w = get_crypto_chart(coin_full_name, '1w')
            chart_1m = get_crypto_chart(coin_full_name, '1m')
            
            if not all([chart_1h, chart_1w, chart_1m]):
                raise Exception("Failed to generate one or more charts")
            
            # Prepare Gemini parts - convert images to PIL Image objects
            from PIL import Image as PILImage
            
            img_1h = PILImage.open(chart_1h)
            img_1w = PILImage.open(chart_1w)
            img_1m = PILImage.open(chart_1m)
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            lang_full_name = language_full[lang]
            
            prompt = f"""Analyze these candlestick charts for {coin_full_name} (with volume and SMA20):
            First image: 1 hour timeframe
            Second image: 1 week timeframe
            Third image: 1 month timeframe
            
            Provide a very detailed analysis in {lang_full_name} explaining:
            - Key observations from each timeframe (candlestick patterns, volume trends, SMA20 crossovers, etc.)
            - The reasoning for your trading recommendation, referencing specific indicators and timeframes used
            - How the different timeframes influenced your decision
            
            Then give a trading recommendation: buy or sell, with a target price, and a suggested datetime in the near future.
            
            Output strictly in JSON format: 
            {{"analysis": "detailed analysis text without markdown bullet points or special formatting",
            "recommendation": "buy" or "sell", 
            "price": float, 
            "datetime": "YYYY-MM-DD HH:MM:SS"}}
            Do not include any other text or markdown formatting in the analysis field."""
            
            response = model.generate_content([prompt, img_1h, img_1w, img_1m])
            
            # Parse JSON
            try:
                # Clean up response text
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                signal = json.loads(response_text)
                analysis = signal['analysis']
                rec = signal['recommendation'].capitalize()
                price = signal['price']
                dt_str = signal['datetime']
                
                # Format the beautiful message
                analysis_text = texts[lang]['ai_header']
                analysis_text += "─" * 30 + "\n"
                analysis_text += texts[lang]['analysis_section'].format(analysis)
                analysis_text += "\n" + "─" * 30
                analysis_text += texts[lang]['recommendation_section'].format(rec, price, dt_str)
                analysis_text += "\n" + "─" * 30
                
                # Create keyboard with Google Calendar button
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                
                # Create Google Calendar link
                calendar_link = create_google_calendar_link(coin_full_name, rec, price, dt_str, analysis)
                calendar_button = types.InlineKeyboardButton(
                    text="📅 Add to Google Calendar",
                    url=calendar_link
                )
                keyboard.add(calendar_button)
                
                # Add "Check Another Coin" button
                another_coin_button = types.InlineKeyboardButton(
                    text="🔍 Check Another Coin",
                    callback_data="show_coins"
                )
                keyboard.add(another_coin_button)
                
                # Add donation button
                donate_button = types.InlineKeyboardButton(
                    text="⭐ Support Us" if lang == 'en' else "⭐ حمایت از ما" if lang == 'fa' else "⭐ ادعمنا",
                    callback_data="show_donation"
                )
                keyboard.add(donate_button)
                
            except Exception as parse_e:
                print(f"JSON parse error: {parse_e}")
                analysis_text = f"<b>AI Analysis:</b>\n\n{response.text}"
                keyboard = create_crypto_keyboard()
            
            # Send analysis
            send_long_message(call.message.chat.id, analysis_text, parse_mode='HTML')
            
            # Send keyboard
            bot.send_message(
                call.message.chat.id,
                texts[lang]['another_coin'],
                reply_markup=keyboard
            )
            
            try:
                bot.delete_message(call.message.chat.id, processing_msg.message_id)
            except:
                pass
            
        except Exception as e:
            print(f"Error in AI handler: {e}")
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=processing_msg.message_id,
                text=texts[lang]['error_ai'],
                parse_mode='HTML'
            )
    
    elif call.data == "show_coins":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts[lang]['available_coins'],
            reply_markup=create_crypto_keyboard()
        )
    
    elif call.data == "show_donation":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=texts[lang]['donation_thanks'],
            reply_markup=create_donation_keyboard(),
            parse_mode='HTML'
        )
    
    elif call.data.startswith("donate_"):
        # Extract star amount
        star_amount = int(call.data.split("_")[1])
        
        try:
            # Create invoice for Telegram Stars
            prices = [types.LabeledPrice(label=f"{star_amount} Telegram Stars", amount=star_amount)]
            
            bot.send_invoice(
                chat_id=call.message.chat.id,
                title=f"Support Crypto Tracker Bot",
                description=f"Thank you for supporting our bot with {star_amount} Telegram Stars! Your contribution helps us maintain and improve the service.",
                invoice_payload=f"donate_{star_amount}_stars",
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",  # Telegram Stars currency code
                prices=prices,
                start_parameter="donate"
            )
            
            bot.answer_callback_query(
                call.id,
                f"⭐ Payment request sent for {star_amount} stars!",
                show_alert=False
            )
            
        except Exception as e:
            print(f"Error creating invoice: {e}")
            bot.answer_callback_query(
                call.id,
                "❌ Sorry, there was an error processing your donation request.",
                show_alert=True
            )

@bot.message_handler(commands=['coins'])
def show_coins(message):
    chat_id = message.chat.id
    lang = user_languages.get(chat_id, 'en')
    bot.reply_to(
        message, 
        texts[lang]['available_coins'],
        reply_markup=create_crypto_keyboard()
    )

# Handle successful payment
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Something went wrong. Please try again later."
    )

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    lang = user_languages.get(chat_id, 'en')
    
    # Extract star amount from invoice payload
    payload = message.successful_payment.invoice_payload
    
    bot.send_message(
        chat_id,
        texts[lang]['donation_success'],
        reply_markup=create_main_menu_keyboard(lang),
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    lang = user_languages.get(chat_id, 'en')
    bot.reply_to(
        message,
        texts[lang]['handle_text'],
        reply_markup=create_crypto_keyboard()
    )

bot.infinity_polling()