"""
MR Bot Main Entry Point
Telegram bot for Medical Representatives field tracking
"""
import asyncio
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path to access shared modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes
)

# Import MR Bot modules
from session_manager import session_manager
from mr_commands import commands_handler
import config

# Set up enhanced business logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

# Reduce noise from external libraries
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('googleapiclient').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class MRBot:
    """Main MR Bot class"""
    
    def __init__(self):
        self.application = None
        self.setup_application()
        
    def setup_application(self):
        """Set up Telegram bot application"""
        if not config.TELEGRAM_BOT_TOKEN:
            raise ValueError("MR_BOT_TOKEN not found in environment variables")
            
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", commands_handler.start_command))
        self.application.add_handler(CommandHandler("location", commands_handler.capture_location_command))
        self.application.add_handler(CommandHandler("visit", commands_handler.log_visit_command))
        
        # Add message handlers
        self.application.add_handler(MessageHandler(filters.LOCATION, commands_handler.handle_location))
        self.application.add_handler(MessageHandler(filters.TEXT, self.handle_text_message))
        
        logger.info("MR Bot application configured successfully")
        
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Route text messages based on content"""
        text = update.message.text.strip()
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Unknown"
        
        logger.info(f"MESSAGE_RECEIVED: User {user_name} ({user_id}) sent: '{text[:50]}...'")
        
        # Check authorization
        if user_id not in config.AUTHORIZED_MR_IDS:
            logger.warning(f"UNAUTHORIZED_ACCESS: User {user_name} ({user_id}) denied access")
            await update.message.reply_text("❌ Access denied.")
            return
            
        logger.info(f"USER_AUTHORIZED: Processing command for {user_name}")
        
        # Route based on message content
        if text == "📍 Capture Location":
            logger.info(f"COMMAND: {user_name} requested location capture")
            await commands_handler.capture_location_command(update, context)
            
        elif text == "📝 Log Visit":
            logger.info(f"COMMAND: {user_name} requested visit logging")
            await commands_handler.log_visit_command(update, context)
            
        elif text in ["👨‍⚕️ Doctor Visit", "🏥 Hospital Visit", "🏪 Pharmacy Visit", 
                     "🏢 Vendor Visit", "📞 Phone Call", "📧 Email Follow-up"]:
            logger.info(f"VISIT_TYPE_SELECTED: {user_name} selected {text}")
            await commands_handler.handle_visit_type(update, context, text)
            
        elif text == "💰 Log Expense":
            logger.info(f"COMMAND: {user_name} requested expense logging")
            await self.handle_expense_command(update, context)
            
        elif text == "📍 Refresh Location":
            logger.info(f"COMMAND: {user_name} requested location refresh")
            await commands_handler.capture_location_command(update, context)
            
        elif text == "📊 View Status":
            logger.info(f"COMMAND: {user_name} requested status check")
            await self.handle_status_command(update, context)
            
        elif text == "📈 Daily Summary":
            logger.info(f"COMMAND: {user_name} requested daily summary")
            await self.handle_summary_command(update, context)
            
        elif text == "🔙 Back" or text == "🔙 Back to Main Menu":
            logger.info(f"NAVIGATION: {user_name} went back to main menu")
            await commands_handler.start_command(update, context)
            
        else:
            # Check if user is in middle of logging a visit
            if context.user_data.get('visit_type'):
                logger.info(f"VISIT_ENTRY: Processing visit details from {user_name}")
                await commands_handler.handle_visit_entry(update, context)
                # Clear visit type after processing
                context.user_data.pop('visit_type', None)
            else:
                logger.warning(f"UNKNOWN_COMMAND: {user_name} sent unrecognized command: '{text}'")
                await update.message.reply_text(
                    "🤔 I didn't understand that command.\n"
                    "Use /start to see available options."
                )
                
    async def handle_expense_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle expense logging"""
        user_id = update.effective_user.id
        
        if not session_manager.can_log_entry(user_id):
            await update.message.reply_text(
                "❌ Location required to log expenses.\n"
                "Capture your location first."
            )
            return
            
        await update.message.reply_text(
            "💰 **Log Expense**\n\n"
            "Format: Type | Amount | Description\n"
            "Example: Fuel | 500 | Travel to hospital\n\n"
            "Common types: Fuel, Meal, Parking, Phone, Other"
        )
        
        context.user_data['logging_expense'] = True
        
    async def handle_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle status check"""
        user_id = update.effective_user.id
        status = session_manager.get_location_status(user_id)
        
        if status['active']:
            remaining_mins = status['time_remaining'] // 60
            remaining_secs = status['time_remaining'] % 60
            
            await update.message.reply_text(
                f"📊 **Current Status**\n\n"
                f"🟢 Location: Active\n"
                f"📍 Address: {status['address']}\n"
                f"⏰ Time Remaining: {remaining_mins}m {remaining_secs}s\n"
                f"📝 Entries Logged: {status['entries_count']}/10\n"
                f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}"
            )
        else:
            await update.message.reply_text(
                f"📊 **Current Status**\n\n"
                f"🔴 Location: Inactive\n"
                f"📍 Please capture location to start logging\n"
                f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}"
            )
            
    async def handle_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle daily summary request"""
        user_id = update.effective_user.id
        
        try:
            summary = commands_handler.sheets.get_daily_summary(user_id)
            if summary:
                await update.message.reply_text(
                    f"📈 **Daily Summary - {summary['date']}**\n\n"
                    f"📝 Visits Logged: {summary['visits_count']}\n"
                    f"💰 Expenses: ₹{summary['total_expenses']:.2f}\n"
                    f"🏪 Expense Entries: {summary['expenses_count']}\n\n"
                    f"Great work today! 👏"
                )
            else:
                await update.message.reply_text(
                    "📈 **Daily Summary**\n\n"
                    "No data found for today.\n"
                    "Start logging visits to see your summary!"
                )
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            await update.message.reply_text(
                "❌ Error getting daily summary. Please try again."
            )
            
    async def cleanup_expired_sessions(self):
        """Background task to clean expired sessions"""
        while True:
            try:
                session_manager.clear_expired_sessions()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)
                
    def run(self):
        """Run the MR Bot"""
        logger.info("Starting MR Bot...")
        
        # Run the bot with proper async handling
        self.application.run_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True
        )
        
    async def start_bot_async(self):
        """Start bot with async cleanup task"""
        # Start background cleanup task
        cleanup_task = asyncio.create_task(self.cleanup_expired_sessions())
        
        try:
            # This would be for async bot running, but we'll use polling instead
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            cleanup_task.cancel()
            logger.info("Bot stopped by user")

if __name__ == "__main__":
    try:
        bot = MRBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("MR Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running MR Bot: {e}")
        raise
