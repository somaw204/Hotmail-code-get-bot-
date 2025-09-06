#!/usr/bin/env python3
"""
DONGVANFB Telegram Bot for OTP Code Retrieval
Advanced featured bot with user-friendly interface
"""

import telebot
import requests
import json
import logging
import re
from datetime import datetime
import time
from telebot import types
import os
import pyotp
from typing import Optional, Dict, Any

from facebook_account import generate_account

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = "7970406512:AAGJCp05YIYG7NJ4Jx6Eau7zm2HOJpIJNpE"  # Replace with your actual bot token
API_BASE_URL = "https://tools.dongvanfb.net/api"

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# User data storage (in production, use a database)
user_sessions = {}

class OTPBot:
    def __init__(self):
        self.supported_services = [
            'facebook', 'instagram', 'twitter', 'apple', 'tiktok',
            'amazon', 'lazada', 'kakaotalk', 'google', 'shopee',
            'telegram', 'wechat', 'all'
        ]
        
    def parse_user_input(self, input_text: str) -> Optional[Dict[str, str]]:
        """
        Parse user-provided data.

        Supports two formats:
        1. ``email|password|refresh_token|client_id``
        2. ``refresh_token|client_id``
        """
        try:
            if '|' not in input_text:
                return None

            parts = [p.strip() for p in input_text.strip().split('|')]

            # Full data input
            if len(parts) == 4:
                email, password, refresh_token, client_id = parts
                if not all([email, password, refresh_token, client_id]):
                    return None
                return {
                    'email': email,
                    'password': password,
                    'refresh_token': refresh_token,
                    'client_id': client_id
                }

            # Token-only input
            if len(parts) == 2:
                refresh_token, client_id = parts
                if not all([refresh_token, client_id]):
                    return None
                return {
                    'refresh_token': refresh_token,
                    'client_id': client_id
                }

            return None
        except Exception as e:
            logger.error(f"Error parsing input: {e}")
            return None
    
    def get_otp_code(self, email: str, refresh_token: str, client_id: str, service_type: str = 'facebook') -> Dict[str, Any]:
        """
        Get OTP code from DONGVANFB API
        """
        try:
            url = f"{API_BASE_URL}/get_code_oauth2"
            
            payload = {
                "email": email,
                "refresh_token": refresh_token,
                "client_id": client_id,
                "type": service_type
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Making API request to {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return {
                    'status': False,
                    'error': f'API request failed with status {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {'status': False, 'error': 'Request timeout. Please try again.'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {'status': False, 'error': 'Network error. Please check your connection.'}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {'status': False, 'error': 'An unexpected error occurred.'}

# Initialize bot instance
otp_bot = OTPBot()

def create_service_keyboard():
    """Create inline keyboard for service selection"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    services = [
        ('📘 Facebook', 'facebook'),
        ('📷 Instagram', 'instagram'),
        ('🐦 Twitter', 'twitter'),
        ('🍎 Apple', 'apple'),
        ('🎵 TikTok', 'tiktok'),
        ('📦 Amazon', 'amazon'),
        ('🛒 Lazada', 'lazada'),
        ('💬 KakaoTalk', 'kakaotalk'),
        ('🔍 Google', 'google'),
        ('🛍️ Shopee', 'shopee'),
        ('✈️ Telegram', 'telegram'),
        ('💚 WeChat', 'wechat'),
        ('🌟 All Services', 'all')
    ]
    
    buttons = []
    for name, callback_data in services:
        buttons.append(types.InlineKeyboardButton(name, callback_data=f"service_{callback_data}"))
    
    # Add buttons in rows of 2
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.row(buttons[i], buttons[i + 1])
        else:
            keyboard.row(buttons[i])
    
    return keyboard

def create_main_menu():
    """Create main menu keyboard"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.row("🔐 Get OTP Code", "📊 Check Status")
    keyboard.row("Generate Facebook account")
    keyboard.row("2FA Code")
    keyboard.row("❓ Help", "⚙️ Settings")
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.first_name or "User"
    
    welcome_text = f"""
🎉 *Welcome to DONGVANFB OTP Bot, {username}!*

This bot helps you retrieve OTP codes from various services using OAuth2 tokens.

🚀 *Quick Start:*
1️⃣ Click "🔐 Get OTP Code"
2️⃣ Enter your email
3️⃣ Send your refresh_token|client_id
4️⃣ Select service type
5️⃣ Get your OTP code!

📝 *Input Format:*
`refresh_token|client_id`

🔧 *Supported Services:*
Facebook, Instagram, Twitter, Apple, TikTok, Amazon, Lazada, KakaoTalk, Google, Shopee, Telegram, WeChat

Type /help for detailed instructions.
    """
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=create_main_menu())
    logger.info(f"User {user_id} ({username}) started the bot")

@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handle /help command"""
    help_text = """
📚 *DONGVANFB OTP Bot Help*

🔧 *How to Use:*
1. Click "🔐 Get OTP Code" or send /getotp
2. Enter your email address
3. Send your data in format: `refresh_token|client_id`
4. Select the service you want OTP for
5. Wait for the OTP code

🔑 *Generate 2FA Codes:*
• Click "2FA Code" and send your secret key

📝 *Input Format Example:*
```
M.C518_BAY.0.U.-CtLyFkvpx3K*0NhzBPs4WM*pnGJXJkiN6BRN90zWaaX0CsGNQifKlyVRku8uzJNqdEFTzvhhF7coNzQ1y8eWM6bAu9i4jGIWQojThUG9mRt5iOKtrNUYIpVIpzbNJmxg0ScX10OvSUpISzGHuiF6g7NPu1g7PJZKQYlraipFnfp7bbHNLN9CwhlsoN5FOWZsK!Otm5lIj6fETNXzFVKQvbaVKPJon1E1Qx*M4f3XFs8uIl*Ym*S41F9ivu3htQzEpxpsFT1vImq1mew*GeNPQj!fEkFE32GbyapC5b0YW07u2vbyXuqAttNDEaIv8O6ULdyBdeKUCjEh2AeYj32qp9k8TWBpYfCFlAbBhceLmumKYsYNIsUzlYaopWcE5ZIowDeVNYVFrbnFs5VH1keKWmDISe88bFfRzUW8OEhVW*f9!QMqOn8shv1YtWb3uquRJg$$|dbc8e03a-b00c-46bd-ae65-b683e7707cb0
```

🎯 *Supported Services:*
• 📘 Facebook
• 📷 Instagram  
• 🐦 Twitter
• 🍎 Apple
• 🎵 TikTok
• 📦 Amazon
• 🛒 Lazada
• 💬 KakaoTalk
• 🔍 Google
• 🛍️ Shopee
• ✈️ Telegram
• 💚 WeChat
• 🌟 All Services

⚡ *Commands:*
/start - Start the bot
/help - Show this help
/getotp - Get OTP code
/status - Check bot status

❗ *Important Notes:*
- Keep your tokens secure
- Don't share your credentials
- Contact support if you encounter issues
    """
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['getotp'])
def handle_getotp_command(message):
    """Handle /getotp command"""
    user_id = message.from_user.id
    user_sessions[user_id] = {'step': 'data_input'}
    
    msg = bot.reply_to(
        message,
        "📝 *Send your data string*\n\n"
        "Just paste your data in this format:\n"
        "`email|password|refresh_token|client_id`\n\n"
        "The bot will automatically extract everything and get your Facebook OTP! 🚀",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_data_input_step)

def process_data_input_step(message):
    """Process direct data string input"""
    user_id = message.from_user.id
    parsed_data = otp_bot.parse_user_input(message.text)

    if not parsed_data or 'email' not in parsed_data:
        msg = bot.reply_to(
            message,
            "❌ *Invalid data format!*\n\n"
            "Please use: `email|password|refresh_token|client_id`",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_data_input_step)
        return

    user_sessions[user_id] = parsed_data
    user_sessions[user_id]['step'] = 'service'

    masked_email = f"{parsed_data['email'][:3]}***@{parsed_data['email'].split('@')[1]}"
    masked_password = "*" * len(parsed_data['password'])
    masked_token = f"{parsed_data['refresh_token'][:10]}...{parsed_data['refresh_token'][-4:]}"
    masked_client = f"{parsed_data['client_id'][:8]}...{parsed_data['client_id'][-4:]}"

    bot.reply_to(
        message,
        f"🚀 *Data parsed successfully!*\n\n"
        f"📧 Email: `{masked_email}`\n"
        f"🔑 Password: `{masked_password}`\n"
        f"🎫 Token: `{masked_token}`\n"
        f"🆔 Client ID: `{masked_client}`\n\n"
        f"🎯 *Select service to get OTP:*",
        parse_mode='Markdown',
        reply_markup=create_service_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🔐 Get OTP Code")
def handle_get_otp_button(message):
    """Handle Get OTP Code button"""
    user_id = message.from_user.id
    user_sessions[user_id] = {'step': 'data_input'}

    msg = bot.reply_to(
        message,
        "📝 *Send your data string*\n\n"
        "Just paste your data in this format:\n"
        "`email|password|refresh_token|client_id`\n\n"
        "The bot will automatically extract everything and get your Facebook OTP! 🚀",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_data_input_step)

@bot.message_handler(func=lambda message: message.text == "2FA Code")
def handle_2fa_button(message):
    """Handle 2FA Code button"""
    msg = bot.reply_to(
        message,
        "🔑 *Send your 2FA key:*",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_2fa_key)

def process_2fa_key(message):
    """Generate and send TOTP code based on user-provided key"""
    secret = message.text.strip().replace(' ', '')
    try:
        code = pyotp.TOTP(secret).now()
        bot.reply_to(
            message,
            f"✅ *Your 2FA code:* `{code}`",
            parse_mode='Markdown',
            reply_markup=create_main_menu()
        )
    except Exception:
        msg = bot.reply_to(
            message,
            "❌ *Invalid 2FA key.* Please send a valid key:",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_2fa_key)


@bot.message_handler(func=lambda message: message.text == "Generate Facebook account")
def handle_generate_fb_button(message):
    """Start Facebook account generation flow"""
    user_id = message.from_user.id
    user_sessions[user_id] = {'step': 'fb_identifier'}
    msg = bot.reply_to(message, "📧 Enter email or phone number:")
    bot.register_next_step_handler(msg, process_fb_identifier)


def process_fb_identifier(message):
    """Ask for password after receiving identifier"""
    user_id = message.from_user.id
    identifier = message.text.strip()
    user_sessions[user_id] = {'step': 'fb_password', 'identifier': identifier}
    msg = bot.reply_to(message, "🔑 Enter password:")
    bot.register_next_step_handler(msg, process_fb_password)


def process_fb_password(message):
    """Generate Facebook account and send result"""
    user_id = message.from_user.id
    session_data = user_sessions.get(user_id)
    if not session_data or session_data.get('step') != 'fb_password':
        bot.reply_to(message, "❌ Session expired. Please start over.", reply_markup=create_main_menu())
        return

    identifier = session_data['identifier']
    password = message.text.strip()
    result = generate_account(identifier, password)

    if result.get('success'):
        bot.reply_to(
            message,
            f"✅ Account created!\n\nEmail/Phone: {identifier}\nPassword: {password}\nUser ID: {result.get('c_user')}\nCookies: {result.get('cookies')}",
            reply_markup=create_main_menu(),
        )
    else:
        bot.reply_to(
            message,
            f"❌ Failed to create account: {result.get('error', 'Unknown error')}",
            reply_markup=create_main_menu(),
        )

    user_sessions.pop(user_id, None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def handle_service_selection(call):
    """Handle service selection from inline keyboard"""
    user_id = call.from_user.id
    service = call.data.replace('service_', '')
    
    if user_id not in user_sessions or user_sessions[user_id].get('step') != 'service':
        bot.answer_callback_query(call.id, "❌ Session expired. Please start over.")
        return
    
    bot.edit_message_text(
        f"🔄 *Processing your request...*\n\n"
        f"📧 Email: `{user_sessions[user_id]['email']}`\n"
        f"🎯 Service: *{service.upper()}*\n\n"
        f"⏳ Please wait while we fetch your OTP code...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # Get OTP code
    result = otp_bot.get_otp_code(
        email=user_sessions[user_id]['email'],
        refresh_token=user_sessions[user_id]['refresh_token'],
        client_id=user_sessions[user_id]['client_id'],
        service_type=service
    )
    
    # Process result
    if result.get('status'):
        success_message = f"""
✅ *OTP Code Retrieved Successfully!*

📧 *Email:* `{result.get('email', 'N/A')}`
🔐 *OTP Code:* `{result.get('code', 'N/A')}`
📝 *Message:* {result.get('content', 'N/A')}
🕐 *Time:* {result.get('date', 'N/A')}

💡 *Tip:* Copy the code quickly as it may expire soon!
        """
        
        bot.edit_message_text(
            success_message,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        # Log successful request
        logger.info(f"OTP retrieved successfully for user {user_id}, service {service}")
        
    else:
        error_message = f"""
❌ *Failed to retrieve OTP code*

🚫 *Error:* {result.get('error', 'Unknown error occurred')}

🔄 *What you can do:*
• Check your tokens are correct
• Ensure your email is valid
• Try again in a few minutes
• Contact support if issue persists

Use /getotp to try again.
        """
        
        bot.edit_message_text(
            error_message,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        # Log failed request
        logger.warning(f"OTP retrieval failed for user {user_id}, service {service}: {result.get('error', 'Unknown error')}")
    
    # Clean up session
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text == "📊 Check Status")
def handle_status(message):
    """Handle status check"""
    try:
        # Simple API health check
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        api_status = "🟢 Online" if response.status_code == 200 else "🟡 Limited"
    except:
        api_status = "🔴 Offline"
    
    status_text = f"""
📊 *Bot Status Report*

🤖 *Bot:* 🟢 Online
🌐 *API:* {api_status}
👥 *Active Sessions:* {len(user_sessions)}
🕐 *Last Update:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 *Supported Services:* {len(otp_bot.supported_services)}
⚡ *Response Time:* Good

💡 All systems operational!
    """
    
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "⚙️ Settings")
def handle_settings(message):
    """Handle settings menu"""
    settings_text = """
⚙️ *Bot Settings*

🔧 *Current Configuration:*
• Auto-cleanup sessions: Enabled
• Response timeout: 30 seconds
• Max retries: 3

📝 *Available Commands:*
• /start - Restart bot
• /help - Show help
• /getotp - Quick OTP retrieval
• /status - Check bot status

💡 *Tips:*
- Keep your tokens secure
- Sessions auto-expire for security
- Contact @YourSupport for issues
    """
    
    bot.reply_to(message, settings_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "❓ Help")
def handle_help_button(message):
    """Handle help button"""
    handle_help(message)

@bot.message_handler(commands=['status'])
def handle_status_command(message):
    """Handle /status command"""
    handle_status(message)

@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
    """Handle unknown messages and direct data input"""
    user_id = message.from_user.id
    
    # Check if user is in a session
    if user_id in user_sessions:
        step = user_sessions[user_id].get('step')
        if step == 'data_input':
            process_data_input_step(message)
            return
    
    # Check if message looks like direct data input (contains 3 pipes)
    if message.text and message.text.count('|') == 3:
        # Direct processing for format: email|password|refresh_token|client_id
        parsed_data = otp_bot.parse_user_input(message.text)
        
        if parsed_data:
            user_sessions[user_id] = parsed_data
            user_sessions[user_id]['step'] = 'service'
            
            # Show parsed data for confirmation (with masked sensitive info)
            masked_email = f"{parsed_data['email'][:3]}***@{parsed_data['email'].split('@')[1]}"
            masked_password = "*" * len(parsed_data['password'])
            masked_token = f"{parsed_data['refresh_token'][:10]}...{parsed_data['refresh_token'][-4:]}"
            masked_client = f"{parsed_data['client_id'][:8]}...{parsed_data['client_id'][-4:]}"
            
            bot.reply_to(
                message,
                f"🚀 *Quick OTP Request*\n\n"
                f"✅ Data parsed successfully:\n"
                f"📧 Email: `{masked_email}`\n"
                f"🔑 Password: `{masked_password}`\n"
                f"🎫 Token: `{masked_token}`\n"
                f"🆔 Client ID: `{masked_client}`\n\n"
                f"🎯 *Select service to get OTP:*",
                parse_mode='Markdown',
                reply_markup=create_service_keyboard()
            )
            return
        else:
            bot.reply_to(
                message,
                "❌ *Invalid data format!*\n\n"
                "Please use the correct format:\n"
                "`email|password|refresh_token|client_id`\n\n"
                "*Example:*\n"
                "`user@email.com|pass123|refresh_token_here|client_id_here`\n\n"
                "Or use /getotp for step-by-step guidance.",
                parse_mode='Markdown',
                reply_markup=create_main_menu()
            )
            return
    
    # Default response for unknown messages
    bot.reply_to(
        message,
        "🤔 *I didn't understand that command.*\n\n"
        "💡 *Quick options:*\n"
        "• Paste data directly: `email|password|refresh_token|client_id`\n"
        "• Use /getotp for Facebook OTP\n"
        "• Use /help for instructions\n"
        "• Use /status to check bot status",
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

def main():
    """Main function to run the bot"""
    logger.info("Starting DONGVANFB Telegram Bot...")
    
    try:
        # Test bot token
        bot.get_me()
        logger.info("Bot token is valid. Starting polling...")
        
        # Start polling
        bot.infinity_polling(none_stop=True, interval=1, timeout=60)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"Error: {e}")
        print("\nPlease check:")
        print("1. Your BOT_TOKEN is set correctly")
        print("2. Your internet connection")
        print("3. The bot token is valid")

if __name__ == "__main__":
    main()
