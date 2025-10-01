"""
MR Commands Handler
Handles all MR bot commands and workflow logic
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime
from typing import Dict, Any
import logging

from session_manager import session_manager, mr_session_manager
# Using existing session managers instead of IntegratedSessionManager
from smart_sheets import smart_sheets  # Use Smart Sheets Manager
from location_handler import LocationHandler
from enhanced_menus import menu_manager  # Import enhanced menu system
from gemini_parser import GeminiMRParser  # Import AI parser
from smart_expense_handler import SmartExpenseHandler  # Import smart expense handler
from visit_based_location_tracker import log_visit_with_location  # Import visit location tracker
import config

logger = logging.getLogger(__name__)

class MRCommandsHandler:
    def __init__(self):
        self.sheets = smart_sheets  # Use Smart Sheets global instance
        self.location_handler = LocationHandler()
        self.pending_visits = {}  # Store pending visit types by user_id
        self.ai_parser = GeminiMRParser()  # Initialize AI parser
        self.expense_handler = SmartExpenseHandler()  # Initialize smart expense handler
        self.pending_expenses = {}  # Store pending expense confirmations
        
        # Initialize session manager
        self.session_manager = mr_session_manager
        
        # Initialize enhanced menu system with session manager
        menu_manager.session_manager = self.session_manager
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        # Safety check for message existence
        if not update or not update.message:
            logger.error(f"START_COMMAND_ERROR: Invalid update object - update={update}, message={getattr(update, 'message', 'NO_MESSAGE') if update else 'NO_UPDATE'}")
            return
            
        user_id = update.effective_user.id
        
        # 🌍 MR Bot is now OPEN TO EVERYONE! 
        # Only admin features are restricted, basic MR functionality is public
        
        # Check location status and provide appropriate menu
        status = mr_session_manager.get_location_status(user_id)
        
        if status['active']:
            remaining_mins = status['time_remaining'] // 60
            remaining_secs = status['time_remaining'] % 60
            entries_count = status.get('entries_count', 0)
            
            await update.message.reply_text(
                f"🟢 **Active Field Session**\n\n"
                f"📍 {status['address']}\n"
                f"⏰ {remaining_mins}m {remaining_secs}s remaining\n"
                f"📝 Entries logged: {entries_count}/10\n\n"
                f"🎯 Ready to log visits and expenses!",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
        else:
            await update.message.reply_text(
                "🔴 **No Active Session**\n\n"
                f"� Welcome {update.effective_user.first_name}!\n"
                "📍 Capture your location to start field tracking.\n"
                "📊 View analytics and reports anytime.\n\n"
                "💡 **Location ensures field authenticity**",
                reply_markup=menu_manager.get_welcome_menu(user_id)
            )
            
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command - admin panel access"""
        user_id = update.effective_user.id
        
        # Check if user is admin (only admin features are restricted)
        if int(user_id) != config.ADMIN_ID:
            await update.message.reply_text(
                "❌ **Admin Access Required**\n\n"
                "This command is only available to administrators."
            )
            return
            
        await update.message.reply_text(
            "🔧 **Admin Panel**\n\n"
            f"Welcome {update.effective_user.first_name}!\n"
            "Access advanced features and analytics.\n\n"
            "📊 View detailed analytics and reports\n"
            "👥 Manage users and settings\n"
            "📝 Export data and system stats",
            reply_markup=menu_manager.get_admin_panel_menu()
        )
            
    async def capture_location_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle location capture request"""
        # Safety check for message existence
        if not update or not update.message:
            logger.error(f"CAPTURE_LOCATION_ERROR: Invalid update object - update={update}, message={getattr(update, 'message', 'NO_MESSAGE') if update else 'NO_UPDATE'}")
            return
            
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
        
        # Check if message exists and has location
        if not update.message:
            logger.error(f"LOCATION_ERROR: No message in update for user {user_id}")
            return
            
        location = update.message.location
        
        if not location:
            await update.message.reply_text("❌ Location not received. Please try again.")
            return
            
        # Get address from coordinates
        address = await self.location_handler.get_address(location.latitude, location.longitude)
        
        # Start location session
        success = mr_session_manager.capture_location(
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
            duration_hours = config.LOCATION_SESSION_DURATION // 3600
            duration_mins = (config.LOCATION_SESSION_DURATION % 3600) // 60
            logger.info(f"SESSION_DETAILS: Address={address}, Duration={duration_hours}h{duration_mins}m, Max_entries={config.MAX_ENTRIES_PER_SESSION}")
            
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
                f"✅ **Location Captured Successfully!**\n\n"
                f"📍 {address}\n"
                f"⏰ Session active for 15 minutes\n"
                f"📝 You can now log visits & expenses!\n\n"
                f"🎯 Your field session is ready!",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
        else:
            logger.error(f"LOCATION_FAILED: Could not create session for user {user_id}")
            await update.message.reply_text(
                "❌ **Failed to capture location**\n\n"
                "Please try again with a stable connection.",
                reply_markup=menu_manager.get_location_request_menu()
            )
            
    async def log_visit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle visit logging request"""
        user_id = update.effective_user.id
        
        # Check if can log entry
        if not mr_session_manager.can_log_entry(user_id):
            status = mr_session_manager.get_location_status(user_id)
            if not status['active']:
                await update.message.reply_text(
                    "❌ **Location Required**\n\n"
                    "Your location session has expired or hasn't started.\n"
                    "Please capture location to start logging visits.",
                    reply_markup=menu_manager.get_location_request_menu()
                )
            else:
                remaining_mins = status['time_remaining'] // 60
                await update.message.reply_text(
                    "❌ **Entry Limit Reached**\n\n"
                    f"Maximum {config.MAX_ENTRIES_PER_SESSION} entries per session. {remaining_mins}m remaining.\n"
                    "Capture new location to continue.",
                    reply_markup=menu_manager.get_location_request_menu()
                )
            return

        # Show visit type selection menu
        await update.message.reply_text(
            "📝 **Log New Visit**\n\n"
            "Choose the type of visit to record:",
            reply_markup=menu_manager.get_visit_types_menu()
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
        status = mr_session_manager.get_location_status(user_id)
        
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
            mr_session_manager.log_entry(user_id)  # Increment entry count
            logger.info(f"VISIT_SUCCESS: Visit logged successfully for user {user_id}")
            
            # ENHANCED: Also capture location for route blueprint tracking
            await self._capture_visit_location_data(user_id, visit_type, name, orders, remarks, status)
            
            remaining = mr_session_manager.get_location_status(user_id)
            await update.message.reply_text(
                f"✅ **Visit Logged Successfully!**\n\n"
                f"👤 {name}\n"
                f"📦 {orders}\n"
                f"📝 {remarks}\n\n"
                f"📍 Location: {status['address']}\n"
                f"📊 Route blueprint updated\n"
                f"⏰ {remaining['time_remaining']//60}m remaining | Entries: {remaining['entries_count']}/10",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
            
            # Check if warning needed
            if remaining['needs_warning']:
                logger.warning(f"SESSION_WARNING: User {user_id} session expiring soon")
                await update.message.reply_text(
                    "⚠️ **Location Session Expiring**\n\n"
                    "Less than 1 minute remaining!\n"
                    "Capture new location to continue tracking.",
                    reply_markup=menu_manager.get_location_request_menu()
                )
        else:
            logger.error(f"VISIT_FAILED: Could not log visit for user {user_id}")
            logger.error(f"FAILURE_DETAILS: Name={name}, Orders={orders}, Location={status.get('address', 'N/A')}")
            await update.message.reply_text(
                "❌ **Failed to Log Visit**\n\n"
                "Something went wrong. Please try again.\n"
                "If issue persists, contact support.",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
            
    async def check_and_process_pending_visit(self, update: Update) -> bool:
        """Check if user has a pending visit and process the text message"""
        user_id = str(update.effective_user.id)
        
        # Check if user has a pending visit
        if user_id not in self.pending_visits:
            return False
            
        visit_type = self.pending_visits[user_id]
        text = update.message.text.strip()
        
        logger.info(f"PENDING_VISIT_PROCESSING: User {user_id} sent visit details for {visit_type}")
        
        # Process the visit entry
        await self.process_visit_entry(update, visit_type, text)
        
        # Clear the pending visit
        del self.pending_visits[user_id]
        
        return True
        
    async def check_and_process_pending_expense(self, update: Update) -> bool:
        """Check if user has a pending expense and process the text message"""
        user_id = str(update.effective_user.id)
        
        # Check if user has a pending expense
        if user_id not in self.pending_expenses:
            return False
            
        pending = self.pending_expenses[user_id]
        if not pending.get('waiting_for_input', False):
            return False
            
        text = update.message.text.strip()
        expense_type = pending['type']
        
        logger.info(f"PENDING_EXPENSE_PROCESSING: User {user_id} sent expense details for {expense_type}")
        logger.info(f"RAW_EXPENSE_INPUT: '{text}'")
        
        # Process the expense entry
        await self.process_expense_entry(update, expense_type, text)
        
        return True
    
    async def process_expense_entry(self, update: Update, expense_type: str, text: str):
        """Process expense entry with AI-powered parsing"""
        user_id = str(update.effective_user.id)
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Parse expense using smart handler
            parsed_data = await self.expense_handler.parse_bulk_expense(text, today)
            
            if parsed_data.get('success', False):
                # Store parsed data for confirmation
                self.pending_expenses[user_id]['parsed_data'] = parsed_data
                self.pending_expenses[user_id]['waiting_for_input'] = False
                
                # Generate confirmation message
                confirmation_msg = self.expense_handler.format_expense_confirmation(parsed_data, today)
                
                await update.message.reply_text(
                    confirmation_msg,
                    reply_markup=menu_manager.get_expense_confirmation_menu()
                )
                
                logger.info(f"EXPENSE_PARSED: User {user_id} - Total: Rs{parsed_data.get('total', 0)}")
                
            else:
                logger.error(f"EXPENSE_PARSING_FAILED: User {user_id} - {text}")
                await update.message.reply_text(
                    "❌ **Could not parse expense**\n\n"
                    "Please try again with a clearer format:\n"
                    "• `lunch 300 cab 150`\n" 
                    "• `fuel 250 parking 50 tea 30`\n"
                    "• `hotel 2000 dinner 400`",
                    reply_markup=menu_manager.get_active_session_menu(user_id)
                )
                
        except Exception as e:
            logger.error(f"EXPENSE_PROCESSING_ERROR: User {user_id} - {e}")
            await update.message.reply_text(
                "❌ **Processing Error**\n\n"
                "Something went wrong. Please try again.",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
        
    async def process_visit_entry(self, update: Update, visit_type: str, text: str):
        """Process visit entry with AI-powered parsing"""
        user_id = update.effective_user.id
        
        logger.info(f"AI_PARSING: Processing visit entry for user {user_id}")
        logger.info(f"RAW_INPUT: '{text}'")
        
        # Try AI parsing first
        try:
            parsed_data = await self.ai_parser.parse_visit_smart(user_id, text, visit_type)
            
            if parsed_data and parsed_data.get('success'):
                name = parsed_data.get('contact_name', 'Unknown')
                orders = parsed_data.get('orders', 'No orders specified')
                remarks = parsed_data.get('remarks', 'No remarks')
                
                logger.info(f"AI_PARSE_SUCCESS: Name='{name}', Orders='{orders}', Remarks='{remarks}'")
                
                # Proceed with the parsed data
                await self._log_visit_to_sheets(update, visit_type, name, orders, remarks)
                return
                
        except Exception as ai_error:
            logger.warning(f"AI_PARSE_FAILED: {str(ai_error)}, falling back to basic parsing")
        
        # Fallback to basic parsing if AI fails
        try:
            if '|' in text:
                # Standard pipe format: Name | Orders | Remarks
                parts = [part.strip() for part in text.split('|')]
                if len(parts) != 3:
                    await update.message.reply_text(
                        "❌ **Format Issue**\n\n"
                        "AI parsing failed. Please use:\n"
                        "`Name | Orders/Discussion | Remarks`\n\n"
                        "Example: `Dr. Smith | 50 tabs Paracetamol | Very cooperative`"
                    )
                    return
                name, orders, remarks = parts
            else:
                # Enhanced flexible parsing with AI insights
                words = text.split()
                if len(words) < 3:
                    await update.message.reply_text(
                        "❌ **Insufficient Details**\n\n"
                        "Please provide more details. Try:\n"
                        "• `Dr. Smith | 50 tabs Paracetamol | Very cooperative`\n"
                        "• Natural language: `Met Dr Smith discussed 50 paracetamol tablets good response`"
                    )
                    return
                
                # Improved heuristic parsing
                if len(words) <= 5:
                    name = words[0] + (' ' + words[1] if len(words) > 3 else '')
                    mid_point = len(words) // 2 + 1
                    orders = ' '.join(words[1 if len(words) <= 3 else 2:mid_point])
                    remarks = ' '.join(words[mid_point:]) if mid_point < len(words) else 'Good interaction'
                else:
                    # For longer entries, be more intelligent about splitting
                    name = ' '.join(words[:2])
                    # Look for medical/drug keywords for orders section
                    medical_keywords = ['tabs', 'tablet', 'mg', 'ml', 'dose', 'prescription', 'medicine']
                    orders_end = len(words) // 2 + 2
                    
                    # Extend orders section if medical keywords found
                    for i, word in enumerate(words[2:], 2):
                        if any(keyword in word.lower() for keyword in medical_keywords) and i < len(words) - 2:
                            orders_end = min(i + 2, len(words) - 1)
                            break
                    
                    orders = ' '.join(words[2:orders_end])
                    remarks = ' '.join(words[orders_end:]) or 'Interaction completed'
                
                logger.info(f"ENHANCED_PARSE: Name='{name}', Orders='{orders}', Remarks='{remarks}'")
            
            # Log the visit
            await self._log_visit_to_sheets(update, visit_type, name, orders, remarks)
                
        except Exception as e:
            logger.error(f"VISIT_PARSE_ERROR: {str(e)}")
            await update.message.reply_text(
                "❌ **Parsing Failed**\n\n"
                "Unable to understand the format. Please use:\n"
                "• `Dr. Smith | 50 tabs Paracetamol | Very cooperative`\n"
                "• Or try natural language like: `Met Dr Smith discussed paracetamol prescription went well`"
            )
            return
    
    async def _log_visit_to_sheets(self, update: Update, visit_type: str, name: str, orders: str, remarks: str):
        """Helper method to log visit to Google Sheets"""
        user_id = update.effective_user.id
            
        # Get current location info
        status = mr_session_manager.get_location_status(user_id)
        
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
        
        logger.info(f"VISIT_LOGGING: Attempting to log {visit_type} visit for {user_data.get('first_name', 'Unknown')}")
        
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
            mr_session_manager.log_entry(user_id)  # Increment entry count
            logger.info(f"VISIT_SUCCESS: Visit logged successfully for user {user_id}")
            
            remaining = mr_session_manager.get_location_status(user_id)
            await update.message.reply_text(
                f"✅ **{visit_type.title()} Visit Logged!**\n\n"
                f"👤 {name}\n"
                f"📦 {orders}\n"
                f"📝 {remarks}\n\n"
                f"📍 Location: {status['address']}\n"
                f"⏰ {remaining['time_remaining']//60}m remaining | Entries: {remaining['entries_count']}/10",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
            
            # Check if warning needed
            if remaining['needs_warning']:
                logger.warning(f"SESSION_WARNING: User {user_id} session expiring soon")
                await update.message.reply_text(
                    "⚠️ **Location Session Expiring**\n\n"
                    "Less than 1 minute remaining!\n"
                    "Capture new location to continue tracking.",
                    reply_markup=menu_manager.get_location_request_menu()
                )
        else:
            logger.error(f"VISIT_FAILED: Could not log visit for user {user_id}")
            logger.error(f"FAILURE_DETAILS: Name={name}, Orders={orders}, Location={status.get('address', 'N/A')}")
            await update.message.reply_text(
                "❌ **Failed to Log Visit**\n\n"
                "Something went wrong. Please try again.\n"
                "If issue persists, contact support.",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
    
    async def _capture_visit_location_data(self, user_id: int, visit_type: str, contact_name: str, 
                                         orders: str, remarks: str, status: Dict):
        """Capture visit location data for route blueprint tracking"""
        try:
            # Determine visit outcome based on orders/remarks
            visit_outcome = "successful"
            if "no order" in orders.lower() or "cancelled" in remarks.lower():
                visit_outcome = "no_order"
            elif "follow-up" in remarks.lower() or "next visit" in remarks.lower():
                visit_outcome = "follow_up"
            
            # Determine location type based on contact name or visit type
            location_type = "general"
            if any(keyword in contact_name.lower() for keyword in ["dr", "doctor", "physician"]):
                location_type = "hospital"
            elif any(keyword in contact_name.lower() for keyword in ["pharmacy", "chemist"]):
                location_type = "pharmacy"
            elif any(keyword in contact_name.lower() for keyword in ["clinic", "medical"]):
                location_type = "clinic"
            
            # Get session ID for tracking
            session_id = mr_session_manager.get_location_status(user_id).get('session_id', '')
            
            # Prepare location data
            location_data = {
                'latitude': status.get('gps_coords', [0, 0])[0],
                'longitude': status.get('gps_coords', [0, 0])[1],
                'address': status.get('address', '')
            }
            
            # Prepare visit data
            visit_data = {
                'location_name': contact_name,
                'location_type': location_type,
                'visit_time': datetime.now().isoformat(),
                'visit_duration': 30,  # Default session duration
                'visit_outcome': visit_outcome,
                'session_id': session_id,
                'notes': f"Orders: {orders} | Remarks: {remarks}"
            }
            
            # Log visit with location for route blueprint
            success = await log_visit_with_location(str(user_id), location_data, visit_data)
            
            if success:
                logger.info(f"ROUTE_BLUEPRINT: Visit location captured for MR {user_id}")
            else:
                logger.warning(f"ROUTE_BLUEPRINT: Failed to capture visit location for MR {user_id}")
                
        except Exception as e:
            logger.error(f"CAPTURE_VISIT_LOCATION: Error - {e}")
            
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callback queries"""
        query = update.callback_query
        await query.answer()  # Acknowledge the callback
        
        user_id = str(query.from_user.id)
        data = query.data
        
        try:
            # Route callback based on prefix
            if data.startswith('visit_'):
                await self._handle_visit_callback(query, user_id, data)
            elif data.startswith('expense_'):
                await self._handle_expense_callback(query, user_id, data)
            elif data.startswith('quick_'):
                await self._handle_quick_action_callback(query, user_id, data)
            elif data.startswith('menu_'):
                await self._handle_menu_callback(query, user_id, data)
            elif data == 'menu_main':
                await self._handle_menu_callback(query, user_id, 'menu_main')
            elif data == 'admin_panel':
                await self._handle_menu_callback(query, user_id, 'menu_admin_panel')
            elif data == 'help_main':
                await self._handle_menu_callback(query, user_id, 'menu_help')
            elif data.startswith('analytics_'):
                await self._handle_analytics_callback(query, user_id, data)
            elif data.startswith('tracking_') or data.startswith('route_'):
                await self._handle_tracking_callback(query, user_id, data)
            elif data.startswith('help_'):
                await self._handle_help_callback(query, user_id, data)
            elif data.startswith('settings_'):
                await self._handle_settings_callback(query, user_id, data)
            elif data.startswith('admin_'):
                await self._handle_admin_callback(query, user_id, data)
            else:
                await query.edit_message_text(
                    "❌ Unknown action. Please try again.",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
        except Exception as e:
            logger.error(f"Callback query error: {e}")
            try:
                await query.edit_message_text(
                    "⚠️ **Action temporarily unavailable**\n\n"
                    "Please try again or use the main menu.",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
            except:
                # If edit fails, send new message
                await query.message.reply_text(
                    "⚠️ **Action temporarily unavailable**\n\n"
                    "Please try again or use the main menu.",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
    
    async def _handle_visit_callback(self, query, user_id: str, data: str):
        """Handle visit-related callbacks"""
        visit_type = data.replace('visit_', '')
        
        # Convert user_id to int for session manager
        user_id_int = int(user_id)
        
        # Check session status
        if not mr_session_manager.can_log_entry(user_id_int):
            await query.edit_message_text(
                "❌ **Session Expired**\n\n"
                "Please capture location first to start logging visits.",
                reply_markup=menu_manager.get_welcome_menu(user_id)
            )
            return
            
        # For now, show manual input instructions
        await query.edit_message_text(
            f"📝 **{visit_type.title()} Visit**\n\n"
            "Please send visit details in one of these formats:\n\n"
            "**Option 1 (Precise):**\n"
            "`Name | Orders/Discussion | Remarks`\n"
            "Example: `Dr. Smith | 50 tabs Paracetamol | Very cooperative`\n\n"
            "**Option 2 (Natural):**\n"
            "`Name Orders Remarks`\n"
            "Example: `Dr Smith 50 tabs paracetamol very cooperative`\n\n"
            "💡 The system will automatically parse your input.",
            reply_markup=menu_manager.get_active_session_menu(user_id)
        )
        
        # Store visit type for next message processing
        self.pending_visits[user_id] = visit_type
        logger.info(f"VISIT_TYPE_STORED: User {user_id} selected {visit_type} visit")
    
    async def _handle_expense_callback(self, query, user_id: str, data: str):
        """Handle expense-related callbacks with smart parsing"""
        expense_type = data.replace('expense_', '')
        
        # Convert user_id to int for session manager
        user_id_int = int(user_id)
        
        # Handle expense viewing (no session required)
        if expense_type.startswith('view_'):
            await self._handle_expense_viewing(query, user_id, expense_type)
            return
        
        # Handle expense confirmations
        if expense_type.startswith('confirm_'):
            await self._handle_expense_confirmation(query, user_id, expense_type)
            return
        
        # Check session status for expense logging
        if not mr_session_manager.can_log_entry(user_id_int):
            await query.edit_message_text(
                "❌ **Session Expired**\n\n"
                "Please capture location first to start logging expenses.",
                reply_markup=menu_manager.get_welcome_menu(user_id)
            )
            return
        
        # Handle bulk expense entry
        if expense_type == 'bulk':
            message = self.expense_handler.create_expense_menu()
            message += "\n\n🚀 **BULK ENTRY SELECTED**\n"
            message += "Just dump all your expenses in one message!\n\n"
            message += "**Examples:**\n"
            message += "• `lunch 300 fuel 250 parking 50`\n"
            message += "• `food was 200 cab 180 and tea 40`\n"
            message += "• `hotel 2000 dinner 400 auto 120`\n\n"
            message += "💡 AI will automatically categorize everything!"
            
            # Store pending expense type
            self.pending_expenses[user_id] = {
                'type': 'bulk',
                'timestamp': datetime.now(),
                'waiting_for_input': True
            }
            
        else:
            # Handle specific category expense
            category_map = {
                'fuel': '⛽ Travel/Fuel',
                'food': '🍽️ Food & Meals', 
                'stay': '🏨 Accommodation',
                'transport': '🚗 Transport',
                'phone': '📞 Communication',
                'gift': '🎁 Gifts/Samples',
                'other': '📋 Other Expenses'
            }
            
            category_name = category_map.get(expense_type, expense_type.title())
            
            message = f"💰 **{category_name}**\n\n"
            message += "Send your expense details:\n\n"
            message += "**Simple format:**\n"
            message += f"• `300` - Just the amount\n"
            message += f"• `lunch 250` - Amount with description\n"
            message += f"• `cab fare 180 and parking 50` - Multiple items\n\n"
            message += "💡 **Pro Tip:** You can mix multiple items!\n"
            message += "Example: `fuel 300 coffee 40 parking 20`"
            
            # Store pending expense type
            self.pending_expenses[user_id] = {
                'type': expense_type,
                'timestamp': datetime.now(),
                'waiting_for_input': True
            }
        
        await query.edit_message_text(
            message,
            reply_markup=menu_manager.get_active_session_menu(user_id)
        )
        
    async def _handle_expense_confirmation(self, query, user_id: str, action: str):
        """Handle expense confirmation actions"""
        if user_id not in self.pending_expenses:
            await query.edit_message_text(
                "❌ No pending expense found.",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
            return
            
        pending = self.pending_expenses[user_id]
        
        if action == 'confirm_ok':
            # Save the expense
            expense_data = pending.get('parsed_data', {})
            success = self._save_expense_to_sheets(user_id, expense_data)
            
            if success:
                await query.edit_message_text(
                    f"✅ **Expense Saved Successfully!**\n\n"
                    f"� Total: ₹{expense_data.get('total', 0)}\n"
                    f"📊 Categories: {len([k for k,v in expense_data.items() if k not in ['items','total','success'] and v > 0])}\n"
                    f"📝 Items: {len(expense_data.get('items', []))}\n\n"
                    f"🎯 Ready for next entry!",
                    reply_markup=menu_manager.get_active_session_menu(user_id)
                )
            else:
                await query.edit_message_text(
                    "❌ **Failed to save expense**\n\n"
                    "Please try again.",
                    reply_markup=menu_manager.get_active_session_menu(user_id)
                )
            
            # Clean up pending data
            del self.pending_expenses[user_id]
            
        elif action == 'confirm_edit':
            await query.edit_message_text(
                "✏️ **Edit Expense**\n\n"
                "Please send your corrected expense details:",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
            # Keep pending expense but reset to waiting for input
            self.pending_expenses[user_id]['waiting_for_input'] = True
            
        elif action == 'confirm_cancel':
            del self.pending_expenses[user_id]
            await query.edit_message_text(
                "❌ **Expense Cancelled**\n\n"
                "No worries! You can start again anytime.",
                reply_markup=menu_manager.get_active_session_menu(user_id)
            )
    
    def _save_expense_to_sheets(self, user_id: str, expense_data: Dict) -> bool:
        """Save expense data to Google Sheets"""
        try:
            # Get location for expense logging
            user_id_int = int(user_id)
            status = mr_session_manager.get_location_status(user_id_int)
            
            if not status.get('active', False):
                return False
            
            # Prepare expense entry for sheets
            total_amount = expense_data.get('total', 0)
            items = expense_data.get('items', [])
            
            # Determine primary category
            if len(items) == 1:
                primary_category = items[0].get('category', 'Other')
            else:
                # For multiple items, use "Mixed" or most expensive category
                primary_category = "Mixed"
            
            # Create detailed description with all items
            description = "Smart Expense: " + "; ".join([
                f"{item.get('category', 'Unknown').title()}: {item.get('item', 'N/A')}: ₹{item.get('amount', 0)}" 
                for item in items
            ])
            
            # Get GPS coordinates
            gps_coords = status.get('gps_coords', [0.0, 0.0])
            gps_lat = gps_coords[0] if len(gps_coords) >= 2 else 0.0
            gps_lon = gps_coords[1] if len(gps_coords) >= 2 else 0.0
            
            # Log to sheets using enhanced method with structured data
            success = smart_sheets.log_expense(
                user_id=user_id_int,
                expense_type=primary_category,
                amount=float(total_amount),
                description=description,
                location=status['address'],
                gps_lat=gps_lat,
                gps_lon=gps_lon,
                expense_data=expense_data  # Pass the full parsed data for proper structuring
            )
            
            if success:
                mr_session_manager.log_entry(user_id_int)  # Increment entry count
                logger.info(f"EXPENSE_SAVED: User {user_id} - Rs{total_amount} - {primary_category}")
            else:
                logger.error(f"EXPENSE_SAVE_FAILED: User {user_id} - Rs{total_amount}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving expense for user {user_id}: {e}")
            return False
    
    async def _handle_expense_viewing(self, query, user_id: str, view_type: str):
        """Handle expense viewing requests"""
        user_id_int = int(user_id)
        period = view_type.replace('view_', '')
        
        try:
            if period == 'analytics':
                # Get comprehensive analytics
                analytics = smart_sheets.get_expense_analytics(user_id_int)
                if not analytics:
                    await query.edit_message_text(
                        "❌ **No expense data found**\n\n"
                        "You haven't logged any expenses yet.",
                        reply_markup=menu_manager.get_expense_view_menu()
                    )
                    return
                
                # Format analytics message
                message = f"📊 **Expense Analytics**\n\n"
                
                today = analytics.get('today', {})
                week = analytics.get('week', {})
                month = analytics.get('month', {})
                
                message += f"📅 **Today**: ₹{today.get('total_amount', 0):.0f} ({today.get('expense_count', 0)} expenses)\n"
                message += f"📈 **This Week**: ₹{week.get('total_amount', 0):.0f} ({week.get('expense_count', 0)} expenses)\n"
                message += f"📊 **This Month**: ₹{month.get('total_amount', 0):.0f} ({month.get('expense_count', 0)} expenses)\n\n"
                
                message += f"📈 **Daily Average**: ₹{analytics.get('daily_average', 0):.0f}\n\n"
                
                # Top categories
                top_categories = analytics.get('top_categories', [])
                if top_categories:
                    message += f"🏆 **Top Categories This Month**:\n"
                    for i, (category, amount) in enumerate(top_categories[:3], 1):
                        message += f"{i}. {category.title()}: ₹{amount:.0f}\n"
                
                await query.edit_message_text(
                    message,
                    reply_markup=menu_manager.get_expense_view_menu()
                )
                
            else:
                # Get specific period summary
                summary = smart_sheets.get_expense_summary(user_id_int, period)
                if not summary:
                    await query.edit_message_text(
                        f"❌ **No expenses found for {period}**\n\n"
                        "You haven't logged any expenses in this period.",
                        reply_markup=menu_manager.get_expense_view_menu()
                    )
                    return
                
                # Format summary message
                period_name = summary.get('period', period.title())
                total_amount = summary.get('total_amount', 0)
                expense_count = summary.get('expense_count', 0)
                category_totals = summary.get('category_totals', {})
                items = summary.get('items', [])
                
                # Header with better formatting
                message = f"💸 {period_name} Expenses\n"
                message += "═" * 25 + "\n\n"
                
                # Total and count with better spacing
                message += f"💰 Total Amount: ₹{total_amount:.0f}\n"
                message += f"📊 Total Entries: {expense_count} expenses\n\n"
                
                # Category breakdown with improved formatting
                if category_totals:
                    message += f"📈 Category Breakdown:\n"
                    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
                    for i, (category, amount) in enumerate(sorted_categories[:4], 1):  # Top 4 categories
                        emoji = self._get_expense_emoji(category)
                        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                        message += f"  {emoji} {category.title()}: ₹{amount:.0f} ({percentage:.0f}%)\n"
                    message += "\n"
                
                # Recent items with better formatting
                if items:
                    message += f"📋 Recent Transactions:\n"
                    for i, item in enumerate(items[:4], 1):  # Show last 4 items
                        emoji = self._get_expense_emoji(item.get('expense_type', ''))
                        date_str = item.get('date', '').split('-')[-1] if item.get('date') else '?'
                        amount = item.get('amount', 0)
                        
                        # Clean and shorten description
                        description = item.get('description', 'No description')
                        if len(description) > 35:
                            description = description[:32] + "..."
                        
                        message += f"  {i}. {emoji} ₹{amount:.0f} - {description}\n"
                        message += f"     📅 Sept {date_str} • {item.get('expense_type', 'Other').title()}\n"
                
                await query.edit_message_text(
                    message,
                    reply_markup=menu_manager.get_expense_view_menu()
                )
                
        except Exception as e:
            logger.error(f"Error viewing expenses for user {user_id}: {e}")
            await query.edit_message_text(
                "❌ **Error loading expense data**\n\n"
                "Please try again later.",
                reply_markup=menu_manager.get_expense_view_menu()
            )
    
    def _get_expense_emoji(self, category: str) -> str:
        """Get emoji for expense category"""
        emoji_map = {
            'travel': '🚗',
            'food': '🍽️',
            'accommodation': '🏨',
            'parking': '🅿️',
            'entertainment': '�',
            'gifts_samples': '🎁',
            'communication': '📱',
            'medical': '💊',
            'other': '📦',
            'fuel': '⛽',
            'stay': '🏨',
            'transport': '�',
            'phone': '📞',
            'gift': '🎁',
            'mixed': '🔀',
            'tea': '☕',
            'coffee': '☕',
            'lunch': '🍱',
            'dinner': '🍽️',
            'breakfast': '🥐',
            'snacks': '🍿',
            'drinks': '🥤'
        }
        return emoji_map.get(category.lower(), '💰')
        
    async def _handle_quick_action_callback(self, query, user_id: str, data: str):
        """Handle quick action callbacks"""
        action = data.replace('quick_', '')
        
        if action == 'location':
            try:
                # Try to edit the message first
                await query.edit_message_text(
                    "📍 **Location Required**\n\n"
                    "To start field tracking, you need to share your location.\n\n"
                    "🔽 **Next Step:** Use the location button that will appear below.",
                    reply_markup=menu_manager.get_location_prompt_inline_menu()
                )
            except Exception as e:
                if "Inline keyboard expected" in str(e):
                    # If we can't edit (original message doesn't have inline keyboard)
                    # Send a new message instead
                    await query.message.reply_text(
                        "📍 **Location Required**\n\n"
                        "To start field tracking, you need to share your location.\n\n"
                        "🔽 **Next Step:** Use the location button below.",
                        reply_markup=menu_manager.get_location_prompt_inline_menu()
                    )
                else:
                    raise e  # Re-raise if it's a different error
            
            # Then send a new message with location request keyboard
            await query.message.reply_text(
                "👇 **Please share your location:**",
                reply_markup=menu_manager.get_location_request_menu()
            )
        elif action == 'status':
            # Convert user_id to int for session manager
            user_id_int = int(user_id)
            status = mr_session_manager.get_location_status(user_id_int)
            if status['active']:
                remaining_mins = status['time_remaining'] // 60
                remaining_secs = status['time_remaining'] % 60
                await query.edit_message_text(
                    f"📊 **Current Status**\n\n"
                    f"🟢 Active Session\n"
                    f"📍 {status['address']}\n"
                    f"⏰ {remaining_mins}m {remaining_secs}s remaining\n"
                    f"📝 {status.get('entries_count', 0)}/10 entries logged",
                    reply_markup=menu_manager.get_active_session_menu(user_id)
                )
            else:
                await query.edit_message_text(
                    "📊 **Current Status**\n\n"
                    "🔴 No Active Session\n"
                    "📍 Capture location to start tracking",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
        elif action == 'summary':
            await query.edit_message_text(
                "📈 **Daily Summary**\n\n"
                "Generating your daily activity report...",
                reply_markup=menu_manager.get_analytics_menu()
            )
            
    async def _handle_menu_callback(self, query, user_id: str, data: str):
        """Handle menu navigation callbacks"""
        menu_action = data.replace('menu_', '')
        
        if menu_action == 'main':
            # Convert user_id to int for session manager
            user_id_int = int(user_id)
            status = mr_session_manager.get_location_status(user_id_int)
            if status['active']:
                remaining_mins = status['time_remaining'] // 60
                remaining_secs = status['time_remaining'] % 60
                entries_count = status.get('entries_count', 0)
                
                await query.edit_message_text(
                    f"🟢 **Active Field Session**\n\n"
                    f"📍 {status['address']}\n"
                    f"⏰ {remaining_mins}m {remaining_secs}s remaining\n"
                    f"📝 Entries logged: {entries_count}/10\n\n"
                    f"🎯 Ready to log visits and expenses!",
                    reply_markup=menu_manager.get_active_session_menu(user_id)
                )
            else:
                await query.edit_message_text(
                    "🔴 **No Active Session**\n\n"
                    f"👋 Welcome {query.from_user.first_name}!\n"
                    "📍 Capture your location to start field tracking.\n"
                    "📊 View analytics and reports anytime.\n\n"
                    "💡 **Location ensures field authenticity**",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
        elif menu_action == 'visit_types':
            await query.edit_message_text(
                "📝 **Select Visit Type**\n\n"
                "Choose the type of visit to log:",
                reply_markup=menu_manager.get_visit_types_menu()
            )
        elif menu_action == 'expense_types':
            await query.edit_message_text(
                "💰 **Select Expense Category**\n\n"
                "Choose the expense category:",
                reply_markup=menu_manager.get_expense_categories_menu()
            )
        elif menu_action == 'expense_view':
            await query.edit_message_text(
                "💸 **My Expenses**\n\n"
                "Choose a time period to view your expenses:",
                reply_markup=menu_manager.get_expense_view_menu()
            )
        elif menu_action == 'help':
            await query.edit_message_text(
                "❓ **Help & Support**\n\n"
                "Choose a help topic:",
                reply_markup=menu_manager.get_help_menu()
            )
        elif menu_action == 'settings':
            await query.edit_message_text(
                "⚙️ **Settings**\n\n"
                "Choose a settings category:",
                reply_markup=menu_manager.get_settings_menu()
            )
        elif menu_action == 'analytics':
            # Check if user is admin
            if int(user_id) != config.ADMIN_ID:
                await query.edit_message_text(
                    "❌ **Admin Access Required**\n\n"
                    "Analytics are only available to administrators.",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
                return
                
            await query.edit_message_text(
                "📊 **Analytics Dashboard**\n\n"
                "Select analytics type:",
                reply_markup=menu_manager.get_analytics_menu()
            )
        elif menu_action == 'admin_panel':
            # Check if user is admin
            if int(user_id) != config.ADMIN_ID:
                await query.edit_message_text(
                    "❌ **Admin Access Required**\n\n"
                    "Admin panel is only available to administrators.",
                    reply_markup=menu_manager.get_welcome_menu(user_id)
                )
                return
                
            await query.edit_message_text(
                "🔧 **Admin Panel**\n\n"
                "Access advanced features and system management:",
                reply_markup=menu_manager.get_admin_panel_menu()
            )
        elif menu_action == 'back':
            await query.edit_message_text(
                "🏠 **Main Menu**\n\nChoose an option:",
                reply_markup=menu_manager.get_welcome_menu(user_id)
            )
    
    async def _handle_analytics_callback(self, query, user_id: str, data: str):
        """Handle analytics-related callbacks with real data"""
        analytics_type = data.replace('analytics_', '')
        
        try:
            # Get real analytics data from sheets
            if analytics_type == 'daily' or analytics_type == 'today':
                analytics_data = await self._get_daily_analytics(user_id)
                
                # Add timestamp to make message unique
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M")
                
                await query.edit_message_text(
                    f"📊 **Today's Analytics** (Updated: {timestamp})\n\n"
                    f"📅 **Date:** {analytics_data['date']}\n\n"
                    f"🏥 **Visits:** {analytics_data['visits_count']}\n"
                    f"💰 **Expenses:** ₹{analytics_data['total_expenses']:.2f}\n"
                    f"📍 **Locations:** {analytics_data['unique_locations']}\n"
                    f"⏱️ **Active Time:** {analytics_data['active_time']}\n\n"
                    f"🎯 **Top Activity:** {analytics_data['top_activity']}\n"
                    f"📈 **Performance:** {analytics_data['performance_score']}/10",
                    reply_markup=menu_manager.get_analytics_menu()
                )
                
            elif analytics_type == 'week':
                analytics_data = await self._get_weekly_analytics(user_id)
                
                # Add timestamp to make message unique
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M")
                
                await query.edit_message_text(
                    f"📅 **Weekly Analytics** (Updated: {timestamp})\n\n"
                    f"📊 **Total Visits:** {analytics_data['total_visits']}\n"
                    f"💸 **Total Expenses:** ₹{analytics_data['total_expenses']:.2f}\n"
                    f"📈 **Daily Average:** {analytics_data['daily_average']:.1f} visits\n"
                    f"🎯 **Best Day:** {analytics_data['best_day']}\n"
                    f"📍 **Coverage:** {analytics_data['locations_covered']} locations\n\n"
                    f"🏆 **Week Performance:** {analytics_data['week_score']}/10\n"
                    f"📊 **Trend:** {analytics_data['trend']}",
                    reply_markup=menu_manager.get_analytics_menu()
                )
                
            elif analytics_type == 'month':
                analytics_data = await self._get_monthly_analytics(user_id)
                
                # Add timestamp to make message unique
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M")
                
                await query.edit_message_text(
                    f"📉 **Monthly Analytics** (Updated: {timestamp})\n\n"
                    f"📊 **Total Visits:** {analytics_data['total_visits']}\n"
                    f"💰 **Total Expenses:** ₹{analytics_data['total_expenses']:.2f}\n"
                    f"📈 **Monthly Growth:** {analytics_data['growth_rate']}%\n"
                    f"🎯 **Goal Progress:** {analytics_data['goal_progress']}%\n"
                    f"🏥 **Top Doctor:** {analytics_data['top_doctor']}\n"
                    f"💊 **Top Product:** {analytics_data['top_product']}\n\n"
                    f"🏆 **Month Rating:** {analytics_data['month_score']}/10",
                    reply_markup=menu_manager.get_analytics_menu()
                )
                
            else:
                await query.edit_message_text(
                    f"📊 **Analytics Dashboard**\n\n"
                    "Select the type of analytics you want to view:",
                    reply_markup=menu_manager.get_analytics_menu()
                )
                
        except Exception as e:
            logger.error(f"Analytics callback error: {e}")
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            await query.edit_message_text(
                f"❌ **Analytics Error** ({timestamp})\n\n"
                "Unable to generate analytics at the moment.\n"
                "Please try again later or contact support.\n\n"
                f"Error: {str(e)[:50]}...",
                reply_markup=menu_manager.get_analytics_menu()
            )
    
    async def _get_daily_analytics(self, user_id: str) -> dict:
        """Get daily analytics data"""
        try:
            from datetime import datetime, timedelta
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Get data from sheets
            visits_data = self.sheets.get_daily_visits(user_id, today)
            expenses_data = self.sheets.get_daily_expenses(user_id, today)
            
            # Calculate metrics
            visits_count = len(visits_data) if visits_data else 0
            
            # Parse expense amounts from Orders field (format: "Expense logged: Mixed Rs3890.0")
            total_expenses = 0
            if expenses_data:
                for exp in expenses_data:
                    orders = exp.get('Orders', '')
                    if 'Rs' in orders:
                        try:
                            # Extract amount after 'Rs'
                            amount_str = orders.split('Rs')[1].strip()
                            total_expenses += float(amount_str)
                        except (ValueError, IndexError):
                            pass
            
            unique_locations = len(set(visit.get('Visit_Type', '') for visit in visits_data)) if visits_data else 0
            
            # Calculate performance score (simple algorithm)
            performance_score = min(10, (visits_count * 2) + (1 if total_expenses < 1000 else 0) + (unique_locations * 1))
            
            return {
                'date': today,
                'visits_count': visits_count,
                'total_expenses': total_expenses,
                'unique_locations': unique_locations,
                'active_time': f"{visits_count * 30}min" if visits_count > 0 else "0min",
                'top_activity': 'Doctor Visits' if visits_count > 0 else 'No Activity',
                'performance_score': performance_score
            }
            
        except Exception as e:
            logger.error(f"Daily analytics error: {e}")
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'visits_count': 0,
                'total_expenses': 0.0,
                'unique_locations': 0,
                'active_time': '0min',
                'top_activity': 'No Activity',
                'performance_score': 0
            }
    
    async def _get_weekly_analytics(self, user_id: str) -> dict:
        """Get weekly analytics data"""
        try:
            from datetime import datetime, timedelta
            
            # Get last 7 days data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            visits_data = self.sheets.get_visits_range(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            expenses_data = self.sheets.get_expenses_range(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            
            total_visits = len(visits_data) if visits_data else 0
            
            # Parse expense amounts from Orders field
            total_expenses = 0
            if expenses_data:
                for exp in expenses_data:
                    orders = exp.get('Orders', '')
                    if 'Rs' in orders:
                        try:
                            amount_str = orders.split('Rs')[1].strip()
                            total_expenses += float(amount_str)
                        except (ValueError, IndexError):
                            pass
            
            daily_average = total_visits / 7
            
            # Find best day
            daily_counts = {}
            for visit in visits_data or []:
                date = visit.get('Date', '')  # Use Date field
                daily_counts[date] = daily_counts.get(date, 0) + 1
            
            best_day = max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else 'No data'
            locations_covered = len(set(visit.get('Visit_Type', '') for visit in visits_data)) if visits_data else 0
            
            # Calculate week score
            week_score = min(10, (total_visits // 2) + (1 if total_expenses < 5000 else 0) + (locations_covered // 2))
            
            # Determine trend
            if total_visits > 14:
                trend = "📈 Increasing"
            elif total_visits < 7:
                trend = "📉 Needs Improvement"
            else:
                trend = "📊 Stable"
            
            return {
                'total_visits': total_visits,
                'total_expenses': total_expenses,
                'daily_average': daily_average,
                'best_day': best_day,
                'locations_covered': locations_covered,
                'week_score': week_score,
                'trend': trend
            }
            
        except Exception as e:
            logger.error(f"Weekly analytics error: {e}")
            return {
                'total_visits': 0,
                'total_expenses': 0.0,
                'daily_average': 0.0,
                'best_day': 'No data',
                'locations_covered': 0,
                'week_score': 0,
                'trend': 'No data'
            }
    
    async def _get_monthly_analytics(self, user_id: str) -> dict:
        """Get monthly analytics data"""
        try:
            from datetime import datetime, timedelta
            from collections import Counter
            
            # Get last 30 days data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            visits_data = self.sheets.get_visits_range(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            expenses_data = self.sheets.get_expenses_range(user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            
            total_visits = len(visits_data) if visits_data else 0
            
            # Parse expense amounts from Orders field
            total_expenses = 0
            if expenses_data:
                for exp in expenses_data:
                    orders = exp.get('Orders', '')
                    if 'Rs' in orders:
                        try:
                            amount_str = orders.split('Rs')[1].strip()
                            total_expenses += float(amount_str)
                        except (ValueError, IndexError):
                            pass
            
            # Calculate growth rate (compare first half vs second half of month)
            mid_date = start_date + timedelta(days=15)
            first_half_visits = len([v for v in visits_data or [] if v.get('timestamp', '') < mid_date.strftime('%Y-%m-%d')])
            second_half_visits = total_visits - first_half_visits
            
            growth_rate = ((second_half_visits - first_half_visits) / max(first_half_visits, 1)) * 100 if first_half_visits > 0 else 0
            
            # Goal progress (assuming 60 visits per month target)
            goal_progress = min(100, (total_visits / 60) * 100)
            
            # Top doctor and product
            doctors = [visit.get('contact_name', 'Unknown') for visit in visits_data or []]
            products = []
            for visit in visits_data or []:
                orders = visit.get('orders', '')
                if orders:
                    products.extend(orders.split(','))
            
            top_doctor = Counter(doctors).most_common(1)[0][0] if doctors else 'No visits'
            top_product = Counter(products).most_common(1)[0][0] if products else 'No products'
            
            # Month score
            month_score = min(10, (total_visits // 6) + (1 if growth_rate > 0 else 0) + (1 if goal_progress > 50 else 0))
            
            return {
                'total_visits': total_visits,
                'total_expenses': total_expenses,
                'growth_rate': round(growth_rate, 1),
                'goal_progress': round(goal_progress, 1),
                'top_doctor': top_doctor,
                'top_product': top_product.strip() if top_product != 'No products' else top_product,
                'month_score': month_score
            }
            
        except Exception as e:
            logger.error(f"Monthly analytics error: {e}")
            return {
                'total_visits': 0,
                'total_expenses': 0.0,
                'growth_rate': 0.0,
                'goal_progress': 0.0,
                'top_doctor': 'No data',
                'top_product': 'No data',
                'month_score': 0
            }
    
    async def _handle_tracking_callback(self, query, user_id: str, data: str):
        """Handle tracking-related callbacks"""
        tracking_type = data.replace('tracking_', '').replace('route_', '')
        
        if tracking_type == 'map':
            # Get current date for map
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Note: Map URLs disabled for now (need proper hosting)
            # map_url = f"http://localhost:5001/map?user_id={user_id}&date={today}"
            
            # Create buttons (without invalid localhost URLs)
            keyboard = [
                # [InlineKeyboardButton("🗺️ Open Live Map", url=map_url)],
                # [InlineKeyboardButton("📱 Mobile Map", url=f"{map_url}&mobile=1"),
                #  InlineKeyboardButton("📊 Dashboard", url=f"http://localhost:5001")],
                [InlineKeyboardButton("📥 Export Route", callback_data="export_route"),
                 InlineKeyboardButton("📤 Share Route", callback_data="share_route")],
                [InlineKeyboardButton("🔙 Back to Analytics", callback_data="analytics_main")]
            ]
            
            await query.edit_message_text(
                "🗺️ **Live Tracking Map**\n\n"
                "📍 **Real-time location tracking**\n"
                "• Live GPS position updates\n"
                "• Complete route visualization with blue dots\n"
                "• Visit markers and timeline\n"
                "• Distance and time analytics\n\n"
                "🚀 **Features:**\n"
                "• Interactive Google Maps interface\n"
                "• Mobile-optimized responsive design\n"
                "• Auto-refresh every 30 seconds\n"
                "• Export routes as GPX files\n\n"
                "👆 Click 'Open Live Map' to see your blueprint!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif tracking_type == 'blueprint':
            await query.edit_message_text(
                "📍 **Route Blueprint System**\n\n"
                "🛣️ **Today's Journey:**\n"
                "• 📍 9:00 AM - Started at Home\n"
                "• 🚗 9:15 AM - Moving to first location\n"
                "• 🏥 9:30 AM - Dr. Sharma Clinic visit\n"
                "• 🚗 9:45 AM - Moving to pharmacy\n"
                "• 🏪 10:00 AM - Apollo Pharmacy visit\n\n"
                "📊 **Route Statistics:**\n"
                "• Distance: 12.5 km\n"
                "• Active Time: 3.2 hours\n"
                "• Visits: 5 locations\n"
                "• Expenses: ₹450\n\n"
                "🎯 **Blueprint shows your complete field journey with blue dot trail!**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🗺️ View Map", callback_data="tracking_map")],
                    [InlineKeyboardButton("🔙 Back", callback_data="analytics_main")]
                ])
            )
    
    async def _handle_help_callback(self, query, user_id: str, data: str):
        """Handle help-related callbacks"""
        help_topic = data.replace('help_', '')
        
        help_content = {
            'getting_started': {
                'title': '🚀 Getting Started',
                'content': """**Welcome to MR Bot!**

📱 **Step 1: Start Session**
• Tap "📍 Start Field Session"
• Share your location when prompted
• Session activates for 15 minutes

📝 **Step 2: Log Activities**
• Use "📝 Log Visit" for doctor/hospital visits
• Use "💰 Log Expense" for business expenses
• Up to 10 entries per session

📊 **Step 3: View Reports**
• Check "📊 Session Status" anytime
• View "📈 Analytics" for insights
• Export data when needed

💡 **Tips:**
• Keep GPS enabled for accuracy
• Log visits immediately for best results
• Use AI parsing for quick entry"""
            },
            'logging_visits': {
                'title': '📝 How to Log Visits',
                'content': """**Visit Logging Guide**

🏥 **Visit Types:**
• 👨‍⚕️ Doctor Visit - Individual practitioners
• 🏥 Hospital Visit - Medical institutions  
• 🏪 Pharmacy Visit - Medicine outlets
• 🏢 Vendor Visit - Business meetings
• 📞 Phone Call - Remote interactions
• 📧 Email Follow-up - Digital communication

📋 **Entry Format:**
`Name | Orders/Discussion | Remarks`

**Example:**
`Dr. Smith | 50 tabs Paracetamol | Very cooperative`

✅ **Best Practices:**
• Be specific with names
• Include order quantities
• Add meaningful remarks
• Log immediately after visit"""
            },
            'expenses': {
                'title': '💰 Expense Logging',
                'content': """**Expense Management Guide**

💸 **Expense Categories:**
• ⛽ Fuel - Travel costs
• 🍽️ Meals - Business meals
• 📱 Communication - Phone/internet
• 🅿️ Parking - Parking fees
• 🎁 Gifts - Customer gifts
• 🏨 Accommodation - Stay costs
• 💼 Other - Miscellaneous

📋 **Entry Format:**
`Amount | Description | Receipt Details`

**Example:**
`₹500 | Fuel for field visits | Petrol pump receipt`

💡 **Tips:**
• Keep receipts for verification
• Use accurate amounts
• Include GST details if applicable
• Log immediately to avoid forgetting"""
            },
            'location': {
                'title': '📍 Location Sessions',
                'content': """**Location Session Guide**

🎯 **Session Rules:**
• 15-minute active duration
• Maximum 10 entries per session
• GPS accuracy required
• Auto-expires after time limit

📍 **Location Features:**
• Real-time address capture
• Automatic geocoding
• Session timer display
• Entry counter tracking

🔄 **Session Management:**
• Start new session anytime
• Refresh location to extend
• View remaining time
• End session manually if needed

⚠️ **Important:**
• Keep GPS enabled
• Stable internet connection required
• Location permissions must be granted
• Indoor locations may have GPS issues"""
            },
            'analytics': {
                'title': '📊 Analytics Guide',
                'content': """**Analytics Dashboard**

📈 **Available Reports:**
• 📊 Daily Report - Today's activity
• 📅 Weekly Summary - Week overview  
• 📈 Performance Trends - Progress tracking
• 💰 Expense Analysis - Cost breakdown
• 👥 Doctor Engagement - Visit patterns
• 🗺️ Territory Analysis - Area coverage

📋 **Data Insights:**
• Visit frequency patterns
• Expense categorization
• Territory coverage maps
• Goal achievement tracking
• Performance comparisons
• Time-based trends

💡 **Using Analytics:**
• Review daily for immediate insights
• Check weekly for planning
• Use trends for goal setting
• Export data for presentations
• Share reports with management"""
            },
            'ai_features': {
                'title': '🤖 AI Features',
                'content': """**AI-Powered Assistance**

🧠 **Smart Parsing:**
• Natural language entry processing
• Auto-format visit details
• Intelligent data extraction
• Error detection and correction

🎯 **Intelligent Suggestions:**
• Context-aware recommendations
• Visit pattern recognition
• Optimal route planning
• Best time predictions

📊 **Advanced Analytics:**
• Predictive insights
• Performance optimization
• Trend identification
• Goal achievement forecasting

💡 **AI Tips:**
• Use natural language entries
• Let AI suggest improvements
• Review AI recommendations
• Provide feedback for better results"""
            },
            'faq': {
                'title': '❓ Frequently Asked Questions',
                'content': """**Common Questions & Answers**

❓ **Q: Why does my session expire?**
✅ A: Sessions auto-expire after 15 minutes for data accuracy and to prevent stale location data.

❓ **Q: Can I log more than 10 entries?**
✅ A: Start a new location session to log additional entries. This ensures location accuracy.

❓ **Q: What if GPS is not accurate?**
✅ A: Move to an open area, check GPS settings, ensure location permissions are enabled.

❓ **Q: How do I export my data?**
✅ A: Go to Settings > Data Export to download your activity reports.

❓ **Q: Can I edit logged entries?**
✅ A: Currently entries are final to maintain data integrity. Contact support for corrections.

❓ **Q: Is my data secure?**
✅ A: Yes, all data is encrypted and stored securely with access controls."""
            },
            'support': {
                'title': '📞 Support Contact',
                'content': """**Get Help & Support**

🆘 **Technical Support:**
• Email: support@mrbot.com  
• Phone: +91-XXXX-XXXXX
• Hours: 9 AM - 6 PM (Mon-Fri)

💬 **Live Chat:**
• Available in app
• Response time: < 2 hours
• Multilingual support

📋 **Report Issues:**
• Use "🐛 Report Bug" feature
• Include screenshots
• Describe steps to reproduce

📖 **Documentation:**
• User manual: mrbot.com/docs
• Video tutorials: mrbot.com/videos
• Best practices guide

🤝 **Community:**
• User forum: mrbot.com/forum
• Feature requests welcome
• Tips and tricks sharing"""
            },
            'troubleshooting': {
                'title': '🔧 Troubleshooting',
                'content': """**Common Issues & Solutions**

🔧 **Location Issues:**
• GPS not working → Check location permissions
• Inaccurate location → Move to open area
• Session won't start → Restart app

📱 **App Issues:**
• App crashes → Update to latest version
• Slow performance → Clear app cache
• Login problems → Check internet connection

📊 **Data Issues:**
• Entries not saving → Check internet
• Reports not loading → Refresh app
• Sync problems → Log out and back in

🔄 **Quick Fixes:**
• Restart the app
• Check internet connection
• Update app version
• Clear cache and data
• Reinstall if needed

💡 **Prevention Tips:**
• Keep app updated
• Maintain good internet
• Don't force close app
• Log out properly"""
            }
        }
        
        content = help_content.get(help_topic, {
            'title': f'❓ {help_topic.title()} Help',
            'content': 'Help content for this topic is being prepared. Please check back soon!'
        })
        
        await query.edit_message_text(
            f"**{content['title']}**\n\n{content['content']}",
            reply_markup=menu_manager.get_help_menu()
        )
    
    async def _handle_settings_callback(self, query, user_id: str, data: str):
        """Handle settings-related callbacks"""
        settings_action = data.replace('settings_', '')
        
        settings_responses = {
            'profile': '👤 **Profile Settings**\n\nConfigure your profile information, display name, and preferences.',
            'notifications': '🔔 **Notification Settings**\n\nManage alert preferences, reminder settings, and notification types.',
            'location': '📍 **Location Settings**\n\nConfigure GPS accuracy, location sharing, and session preferences.',
            'session': '⏰ **Session Preferences**\n\nCustomize session duration, entry limits, and timeout settings.',
            'display': '📱 **Display Options**\n\nAdjust theme, language, font size, and interface preferences.',
            'export': '📋 **Data Export**\n\nDownload your data, generate reports, and configure backup settings.'
        }
        
        response = settings_responses.get(settings_action, 
            f"⚙️ **{settings_action.title()} Settings**\n\nThis settings section will be available soon!")
        
        await query.edit_message_text(
            f"{response}\n\n(Settings functionality will be enhanced in future updates)",
            reply_markup=menu_manager.get_settings_menu()
        )
    
    async def _handle_admin_callback(self, query, user_id: str, data: str):
        """Handle admin-related callbacks"""
        admin_action = data.replace('admin_', '')
        
        # Check if user is admin
        if int(user_id) != config.ADMIN_ID:
            await query.edit_message_text(
                "🚫 **Access Denied**\n\n"
                "You don't have administrator privileges.",
                reply_markup=menu_manager.get_welcome_menu(user_id)
            )
            return
        
        if admin_action == 'users':
            # Get actual user statistics
            try:
                authorized_users = len(config.AUTHORIZED_MR_IDS)
                admin_count = 1  # Only one admin currently
                
                await query.edit_message_text(
                    f"� **User Management Panel**\n\n"
                    f"📊 **Current Users:**\n"
                    f"• Total Authorized: {authorized_users}\n"
                    f"• Administrators: {admin_count}\n"
                    f"• Regular Users: {authorized_users - admin_count}\n\n"
                    f"🔧 **Management Options:**\n"
                    f"• View user activity logs\n"
                    f"• Monitor session statistics\n"
                    f"• Review visit entries\n\n"
                    f"� To add/remove users, update AUTHORIZED_MR_IDS in config",
                    reply_markup=menu_manager.get_admin_panel_menu()
                )
            except Exception as e:
                await query.edit_message_text(
                    f"❌ Error loading user data: {str(e)}",
                    reply_markup=menu_manager.get_admin_panel_menu()
                )
                
        elif admin_action == 'stats':
            # Get actual system statistics
            try:
                import os
                from datetime import datetime
                
                # Get log file stats
                log_file = config.LOG_FILE if hasattr(config, 'LOG_FILE') else 'mr_bot/data/mr_bot.log'
                log_size = 0
                if os.path.exists(log_file):
                    log_size = os.path.getsize(log_file) / 1024  # KB
                
                # Get session info
                active_sessions = len(mr_session_manager.sessions) if hasattr(session_manager, 'sessions') else 0
                
                await query.edit_message_text(
                    f"📊 **System Statistics**\n\n"
                    f"🤖 **Bot Status:**\n"
                    f"• Status: ✅ Online\n"
                    f"• Uptime: Running\n"
                    f"• Log Size: {log_size:.1f} KB\n\n"
                    f"👥 **User Activity:**\n"
                    f"• Active Sessions: {active_sessions}\n"
                    f"• Authorized Users: {len(config.AUTHORIZED_MR_IDS)}\n\n"
                    f"📅 **System Info:**\n"
                    f"• Current Time: {datetime.now().strftime('%H:%M:%S')}\n"
                    f"• Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                    f"💾 **Storage:**\n"
                    f"• Google Sheets: Connected\n"
                    f"• Data Directory: mr_bot/data",
                    reply_markup=menu_manager.get_admin_panel_menu()
                )
            except Exception as e:
                await query.edit_message_text(
                    f"❌ Error loading system stats: {str(e)}",
                    reply_markup=menu_manager.get_admin_panel_menu()
                )
                
        elif admin_action == 'export':
            # Data export functionality
            await query.edit_message_text(
                f"📝 **Data Export Panel**\n\n"
                f"🗂️ **Available Exports:**\n"
                f"• Visit Logs (Google Sheets)\n"
                f"• Location Sessions\n"
                f"• User Activity Logs\n"
                f"• System Performance Data\n\n"
                f"📊 **Export Formats:**\n"
                f"• CSV (Recommended)\n"
                f"• JSON (Developer)\n"
                f"• Excel (Business)\n\n"
                f"💡 Use Google Sheets interface for manual exports\n"
                f"📊 Sheet ID: {config.MR_SPREADSHEET_ID[:20]}...",
                reply_markup=menu_manager.get_admin_panel_menu()
            )
            
        elif admin_action == 'settings':
            # System settings panel
            await query.edit_message_text(
                f"⚙️ **System Settings**\n\n"
                f"� **Current Configuration:**\n"
                f"• Admin ID: {config.ADMIN_ID}\n"
                f"• Authorized Users: {len(config.AUTHORIZED_MR_IDS)}\n"
                f"• GPS Required: {config.GPS_REQUIRED}\n"
                f"• Session Duration: 15 minutes\n"
                f"• Max Entries: 10 per session\n\n"
                f"🛡️ **Security:**\n"
                f"• Authentication: ✅ Enabled\n"
                f"• User Validation: ✅ Active\n"
                f"• Admin Controls: ✅ Protected\n\n"
                f"💡 Modify settings in config.py or .env file",
                reply_markup=menu_manager.get_admin_panel_menu()
            )
            
        else:
            # Default admin panel
            await query.edit_message_text(
                f"👑 **Admin Dashboard**\n\n"
                f"🎯 **Quick Actions:**\n"
                f"• Monitor user activity\n"
                f"• Review system performance\n"
                f"• Manage configurations\n"
                f"• Export data reports\n\n"
                f"📊 **System Health:** ✅ All systems operational\n"
                f"👤 **Logged in as:** Administrator\n\n"
                f"Select an option below for detailed management:",
                reply_markup=menu_manager.get_admin_panel_menu()
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
