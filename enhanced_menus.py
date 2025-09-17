"""
Enhanced Menu System for MR Bot
Dynamic, context-aware menus with smart functionality
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import logging
import config

logger = logging.getLogger(__name__)

class MRMenuManager:
    """Advanced menu manager with dynamic context-aware menus"""
    
    def __init__(self, session_manager=None):
        self.session_manager = session_manager
    
    def get_welcome_menu(self, user_id: str) -> InlineKeyboardMarkup:
        """Get welcome menu based on user role"""
        # Check if user is admin
        is_admin = int(user_id) == config.ADMIN_ID
        
        if is_admin:
            return self.get_admin_welcome_menu()
        else:
            return self.get_user_welcome_menu()
    
    def get_user_welcome_menu(self) -> InlineKeyboardMarkup:
        """Simplified menu for regular users"""
        keyboard = [
            [InlineKeyboardButton("📍 Start Field Session", callback_data="quick_location")],
            [InlineKeyboardButton("📊 My Status", callback_data="quick_status"),
             InlineKeyboardButton("💰 My Expenses", callback_data="menu_expense_view")],
            [InlineKeyboardButton("❓ Help & Support", callback_data="help_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_admin_welcome_menu(self) -> InlineKeyboardMarkup:
        """Extended menu for admin users"""
        keyboard = [
            [InlineKeyboardButton("📍 Start Field Session", callback_data="quick_location")],
            [InlineKeyboardButton("📊 View Status", callback_data="quick_status")],
            [InlineKeyboardButton("📈 Analytics", callback_data="analytics_daily")],
            [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")],
            [InlineKeyboardButton("❓ Help", callback_data="help_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_location_request_menu(self) -> ReplyKeyboardMarkup:
        """Request location using keyboard button (needed for location sharing)"""
        return ReplyKeyboardMarkup([
            [KeyboardButton("📍 Share Location", request_location=True)],
            [KeyboardButton("🔙 Back to Menu")]
        ], resize_keyboard=True, one_time_keyboard=True)
    
    def get_location_prompt_inline_menu(self) -> InlineKeyboardMarkup:
        """Inline menu to prompt for location sharing"""
        keyboard = [
            [InlineKeyboardButton("📍 I'll Share Location", callback_data="menu_main")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_active_session_menu(self, user_id: str) -> InlineKeyboardMarkup:
        """Simplified menu for active session"""
        # Check if user is admin
        is_admin = int(user_id) == config.ADMIN_ID
        
        # Core actions for everyone
        keyboard = [
            # Main actions - bigger buttons, clearer labels
            [InlineKeyboardButton("🏥 Log Doctor Visit", callback_data="menu_visit_types")],
            [InlineKeyboardButton("💰 Add Expense", callback_data="menu_expense_types")],
            
            # Quick actions
            [InlineKeyboardButton("📊 Session Status", callback_data="quick_status"),
             InlineKeyboardButton("💸 View Expenses", callback_data="menu_expense_view")],
        ]
        
        # Add admin features if admin
        if is_admin:
            keyboard.append([InlineKeyboardButton("📈 Analytics", callback_data="analytics_daily"),
                           InlineKeyboardButton("⚙️ Admin", callback_data="admin_panel")])
        
        # Help at bottom
        keyboard.append([InlineKeyboardButton("❓ Help", callback_data="help_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_visit_types_menu(self) -> InlineKeyboardMarkup:
        """Simplified menu for selecting visit type"""
        keyboard = [
            # Most common visit types first
            [InlineKeyboardButton("👨‍⚕️ Doctor Visit", callback_data="visit_doctor")],
            [InlineKeyboardButton("🏥 Hospital Visit", callback_data="visit_hospital")],
            [InlineKeyboardButton("🏪 Pharmacy Visit", callback_data="visit_pharmacy")],
            
            # Less common options
            [InlineKeyboardButton("📞 Phone Call", callback_data="visit_phone"),
             InlineKeyboardButton("🏢 Other Visit", callback_data="visit_other")],
            
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_expense_types_menu(self) -> InlineKeyboardMarkup:
        """Simplified menu for selecting expense type"""
        keyboard = [
            # Highlight the smart bulk entry option
            [InlineKeyboardButton("🚀 Smart Entry (Recommended)", callback_data="expense_bulk")],
            
            # Most common expenses
            [InlineKeyboardButton("⛽ Fuel", callback_data="expense_fuel"),
             InlineKeyboardButton("🍽️ Meals", callback_data="expense_food")],
            [InlineKeyboardButton("🚗 Travel", callback_data="expense_transport"),
             InlineKeyboardButton("🏨 Stay", callback_data="expense_stay")],
            
            # Other options
            [InlineKeyboardButton("📞 Communication", callback_data="expense_phone"),
             InlineKeyboardButton("📋 Other", callback_data="expense_other")],
            
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_expense_confirmation_menu(self) -> InlineKeyboardMarkup:
        """Menu for expense confirmation"""
        keyboard = [
            [InlineKeyboardButton("✅ Confirm & Save", callback_data="expense_confirm_ok"),
             InlineKeyboardButton("✏️ Edit/Modify", callback_data="expense_confirm_edit")],
            [InlineKeyboardButton("❌ Cancel", callback_data="expense_confirm_cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_expense_view_menu(self) -> InlineKeyboardMarkup:
        """Menu for viewing expenses"""
        keyboard = [
            [InlineKeyboardButton("📅 Today's Expenses", callback_data="expense_view_today"),
             InlineKeyboardButton("📊 This Month", callback_data="expense_view_month")],
            [InlineKeyboardButton("📈 This Week", callback_data="expense_view_week"),
             InlineKeyboardButton("📋 Full Analytics", callback_data="expense_view_analytics")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_expense_categories_menu(self) -> InlineKeyboardMarkup:
        """Menu for selecting expense category (alias for expense_types_menu)"""
        return self.get_expense_types_menu()
    
    def get_analytics_menu(self) -> InlineKeyboardMarkup:
        """Analytics menu (admin only)"""
        keyboard = [
            [InlineKeyboardButton("�️ Live Tracking Map", callback_data="tracking_map"),
             InlineKeyboardButton("📍 Route Blueprint", callback_data="route_blueprint")],
            [InlineKeyboardButton("�📊 Today's Summary", callback_data="analytics_today"),
             InlineKeyboardButton("📈 Weekly Report", callback_data="analytics_week")],
            [InlineKeyboardButton("📉 Monthly Stats", callback_data="analytics_month"),
             InlineKeyboardButton("📋 Custom Report", callback_data="analytics_custom")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_admin_panel_menu(self) -> InlineKeyboardMarkup:
        """Admin panel menu"""
        keyboard = [
            [InlineKeyboardButton("👥 User Management", callback_data="admin_users"),
             InlineKeyboardButton("📊 System Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("📝 Export Data", callback_data="admin_export"),
             InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_help_menu(self) -> InlineKeyboardMarkup:
        """Simplified help menu"""
        keyboard = [
            [InlineKeyboardButton("📍 Location Help", callback_data="help_location"),
             InlineKeyboardButton("📝 Visit Logging", callback_data="help_visits")],
            [InlineKeyboardButton("💰 Expense Logging", callback_data="help_expenses"),
             InlineKeyboardButton("📞 Support", callback_data="help_support")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
        
    def get_settings_menu(self, is_admin: bool = False) -> InlineKeyboardMarkup:
        """Settings menu"""
        keyboard = [
            [InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
             InlineKeyboardButton("📍 Location", callback_data="settings_location")],
            [InlineKeyboardButton("🌍 Language", callback_data="settings_language"),
             InlineKeyboardButton("🎨 Theme", callback_data="settings_theme")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

# Global menu manager instance
menu_manager = MRMenuManager()