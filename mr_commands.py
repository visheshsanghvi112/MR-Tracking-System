"""
MR Commands Handler
Handles all MR bot commands and workflow logic
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime
import logging

from session_manager import session_manager
from smart_sheets import smart_sheets  # Use Smart Sheets Manager
from location_handler import LocationHandler
import config

logger = logging.getLogger(__name__)

class MRCommandsHandler:
    def __init__(self):
        self.sheets = smart_sheets  # Use Smart Sheets global instance
        self.location_handler = LocationHandler()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        # Check if user is authorized MR
        if user_id not in config.AUTHORIZED_MR_IDS:
            await update.message.reply_text(
                "❌ Access denied. You are not authorized to use this MR Bot."
            )
            return
            
        # Check location status
        status = session_manager.get_location_status(user_id)
        
        if status['active']:
            remaining_mins = status['time_remaining'] // 60
            await update.message.reply_text(
                f"🟢 **Location Active**\n"
                f"📍 {status['address']}\n"
                f"⏰ {remaining_mins}m {status['time_remaining'] % 60}s remaining\n"
                f"📝 Entries logged: {status['entries_count']}/10\n\n"
                f"Ready to log visits!",
                reply_markup=self.get_main_menu()
            )
        else:
            await update.message.reply_text(
                "🔴 **Location Required**\n\n"
                "📍 You must capture your current location before logging visits.\n"
                "This ensures accurate field tracking.",
                reply_markup=self.get_location_menu()
            )
            
    async def capture_location_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle location capture request"""
        user_id = update.effective_user.id
        
        await update.message.reply_text(
            "📍 **Capture Location**\n\n"
            "Please share your current location to start field session.\n"
            "Use the 📍 Location button below or send location manually.",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("📍 Share Location", request_location=True)],
                [KeyboardButton("🔙 Back")]
            ], resize_keyboard=True)
        )
        
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process received location"""
        user_id = update.effective_user.id
        location = update.message.location
        
        if not location:
            await update.message.reply_text("❌ Location not received. Please try again.")
            return
            
        # Get address from coordinates
        address = await self.location_handler.get_address(location.latitude, location.longitude)
        
        # Start location session
        success = session_manager.capture_location(
            user_id, 
            location.latitude, 
            location.longitude, 
            address
        )
        
        if success:
            # Log location capture with user data
            user_data = {
                'first_name': update.effective_user.first_name,
                'last_name': update.effective_user.last_name,
                'username': update.effective_user.username
            }
            
            logger.info(f"LOCATION_SUCCESS: Session created for {user_data.get('first_name', 'Unknown')} ({user_id})")
            logger.info(f"SESSION_DETAILS: Address={address}, Duration=5min, Max_entries=10")
            
            try:
                self.sheets.log_location_capture(
                    user_id=user_id,
                    lat=location.latitude,
                    lon=location.longitude,
                    address=address,
                    user_data=user_data
                )
                logger.info(f"SHEET_SUCCESS: Location logged to Google Sheets")
            except Exception as e:
                logger.error(f"SHEET_ERROR: Failed to log location to sheets: {str(e)}")
            
            await update.message.reply_text(
                f"✅ **Location Captured**\n\n"
                f"📍 {address}\n"
                f"⏰ Session active for 5 minutes\n"
                f"📝 You can now log visits!",
                reply_markup=self.get_main_menu()
            )
        else:
            logger.error(f"LOCATION_FAILED: Could not create session for user {user_id}")
            await update.message.reply_text(
                "❌ Failed to capture location. Please try again."
            )
            
    async def log_visit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle visit logging request"""
        user_id = update.effective_user.id
        
        # Check if can log entry
        if not session_manager.can_log_entry(user_id):
            status = session_manager.get_location_status(user_id)
            if not status['active']:
                await update.message.reply_text(
                    "❌ **Location Expired**\n\n"
                    "Your location session has expired. Please capture location again.",
                    reply_markup=self.get_location_menu()
                )
            else:
                await update.message.reply_text(
                    "❌ **Entry Limit Reached**\n\n"
                    "Maximum 10 entries per location session. Capture new location to continue."
                )
            return
            
        # Show visit type menu
        await update.message.reply_text(
            "📝 **Log Visit**\n\n"
            "Select visit type:",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("👨‍⚕️ Doctor Visit"), KeyboardButton("🏥 Hospital Visit")],
                [KeyboardButton("🏪 Pharmacy Visit"), KeyboardButton("🏢 Vendor Visit")],
                [KeyboardButton("📞 Phone Call"), KeyboardButton("📧 Email Follow-up")],
                [KeyboardButton("🔙 Back to Main Menu")]
            ], resize_keyboard=True)
        )
        
    async def handle_visit_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, visit_type: str):
        """Handle visit type selection"""
        user_id = update.effective_user.id
        context.user_data['visit_type'] = visit_type
        
        await update.message.reply_text(
            f"📝 **{visit_type}**\n\n"
            f"Please provide visit details:\n"
            f"Format: Name | Orders/Discussion | Remarks\n\n"
            f"Example: Dr. Smith | 2 insulin pens, diabetes discussion | Follow-up next week"
        )
        
    async def handle_visit_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process visit entry details"""
        user_id = update.effective_user.id
        text = update.message.text
        visit_type = context.user_data.get('visit_type', 'General Visit')
        
        logger.info(f"VISIT_ENTRY: User {user_id} ({update.effective_user.first_name}) logging {visit_type}")
        logger.info(f"RAW_INPUT: {text}")
        
        # Parse entry (basic parsing, can be enhanced with Gemini later)
        parts = text.split('|')
        if len(parts) >= 2:
            name = parts[0].strip()
            orders = parts[1].strip()
            remarks = parts[2].strip() if len(parts) > 2 else ""
            logger.info(f"PARSED_DATA: Contact={name}, Orders={orders}, Remarks={remarks}")
        else:
            name = text.strip()
            orders = ""
            remarks = ""
            logger.warning(f"PARSING_FALLBACK: Using simple parsing for user {user_id}")
            
        # Get current location info
        status = session_manager.get_location_status(user_id)
        
        if not status.get('active', False):
            logger.error(f"VISIT_BLOCKED: User {user_id} has no active session")
            await update.message.reply_text(
                "❌ **Session Expired**\n\nYour location session has expired. Please capture location again."
            )
            return
            
        logger.info(f"SESSION_VALID: User {user_id} has active session with {status.get('entries_count', 0)} entries")
        
        # Log the visit with user data
        user_data = {
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'username': update.effective_user.username
        }
        
        logger.info(f"VISIT_LOGGING: Attempting to log visit for {user_data.get('first_name', 'Unknown')}")
        
        success = self.sheets.log_visit(
            user_id=user_id,
            visit_type=visit_type,
            contact_name=name,
            orders=orders,
            remarks=remarks,
            location=status['address'],
            gps_lat=status.get('gps_coords', [0, 0])[0],
            gps_lon=status.get('gps_coords', [0, 0])[1],
            user_data=user_data
        )
        
        if success:
            session_manager.log_entry(user_id)  # Increment entry count
            logger.info(f"VISIT_SUCCESS: Visit logged successfully for user {user_id}")
            
            remaining = session_manager.get_location_status(user_id)
            await update.message.reply_text(
                f"✅ **Visit Logged Successfully**\n\n"
                f"👤 {name}\n"
                f"📦 {orders}\n"
                f"📝 {remarks}\n\n"
                f"📍 Location: {status['address']}\n"
                f"⏰ {remaining['time_remaining']//60}m remaining | Entries: {remaining['entries_count']}/10",
                reply_markup=self.get_main_menu()
            )
            
            # Check if warning needed
            if remaining['needs_warning']:
                logger.warning(f"SESSION_WARNING: User {user_id} session expiring soon")
                await update.message.reply_text(
                    "⚠️ **Location Expiring Soon**\n"
                    "Less than 1 minute remaining. Capture new location to continue."
                )
        else:
            logger.error(f"VISIT_FAILED: Could not log visit for user {user_id}")
            logger.error(f"FAILURE_DETAILS: Name={name}, Orders={orders}, Location={status.get('address', 'N/A')}")
            await update.message.reply_text(
                "❌ Failed to log visit. Please try again."
            )
            
    def get_location_menu(self):
        """Get location capture menu"""
        return ReplyKeyboardMarkup([
            [KeyboardButton("📍 Capture Location")],
            [KeyboardButton("📊 View Status")]
        ], resize_keyboard=True)
        
    def get_main_menu(self):
        """Get main menu for active session"""
        return ReplyKeyboardMarkup([
            [KeyboardButton("📝 Log Visit"), KeyboardButton("💰 Log Expense")],
            [KeyboardButton("📍 Refresh Location"), KeyboardButton("📊 View Status")],
            [KeyboardButton("📈 Daily Summary"), KeyboardButton("⚙️ Settings")]
        ], resize_keyboard=True)

# Global handler instance
commands_handler = MRCommandsHandler()
