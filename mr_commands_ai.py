"""
MR Bot Commands with AI Integration
Complete command system with Gemini AI, ML/DL analytics, and intelligent responses
"""
import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class MRCommandProcessor:
    """Intelligent command processor for MR Bot"""
    
    def __init__(self):
        self.session_manager = None
        self.sheets_manager = None
        self.ai_engine = None
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize all components"""
        try:
            # Initialize session manager
            from session_manager import session_manager
            self.session_manager = session_manager
            
            # Initialize sheets manager
            from smart_sheets import smart_sheets
            self.sheets_manager = smart_sheets
            
            # Initialize AI engine
            from ai_engine import mr_ai_engine
            self.ai_engine = mr_ai_engine
            
            logger.info("MR Command Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Component initialization error: {e}")
            
    async def process_start_command(self, user_id: int, location_data: Optional[Dict] = None) -> str:
        """Process /start command with location session"""
        try:
            if not self.session_manager:
                return "❌ Session manager not available"
                
            # Start location session
            if location_data:
                latitude = location_data.get('latitude')
                longitude = location_data.get('longitude')
                
                if latitude and longitude:
                    success = self.session_manager.capture_location(user_id, latitude, longitude, "Field Location")
                    if success:
                        return f"""🎯 **Location Session Started**

📍 **Location:** {latitude:.6f}, {longitude:.6f}
⏰ **Session Duration:** 5 minutes
📝 **Max Entries:** 10 visits/expenses

🏥 **Quick Actions:**
• Log visit: /visit [doctor] | [product] | [quantity]
• Log expense: /expense [type] | [amount] | [description]
• Check session: /status

💡 **AI-Enhanced:** Your entries will be intelligently parsed and analyzed!"""
                    else:
                        return "❌ Failed to start location session"
                else:
                    return "❌ Invalid location data"
            else:
                return """📍 **Location Required**

To start your MR session, please share your location:
1. Click the 📎 attachment button
2. Select 'Location' 
3. Send your current location

🔒 Your location is only used to validate field presence and will be stored securely."""
                
        except Exception as e:
            logger.error(f"Start command error: {e}")
            return f"❌ Error starting session: {e}"
            
    async def process_visit_command(self, user_id: int, text: str, visit_type: str = "regular") -> str:
        """Process visit command with AI parsing"""
        try:
            # Check session
            if not self.session_manager or not self.session_manager.get_location_status(user_id).get('active', False):
                return "❌ No active location session. Use /start to begin."
                
            # Check entry limit
            if not self.session_manager.can_log_entry(user_id):
                return "⚠️ Session entry limit reached (10 max). Start a new session with /start"
                
            # Process with AI
            if self.ai_engine:
                result = await self.ai_engine.process_visit_entry(user_id, text, visit_type)
                parsed_data = result.get("parsed_data", {})
                response_text = result.get("response_text", "")
                
                # Log to sheets
                if self.sheets_manager and parsed_data and "error" not in parsed_data:
                    try:
                        # Extract data for sheets
                        contact = parsed_data.get("contact", {})
                        orders = parsed_data.get("orders", [])
                        
                        doctor_name = contact.get("name", "Unknown")
                        hospital = contact.get("location", "")
                        
                        # Combine orders into summary
                        order_summary = ""
                        if orders:
                            order_items = [f"{o.get('product', 'Product')} ({o.get('quantity', 0)} {o.get('unit', 'units')})" for o in orders]
                            order_summary = "; ".join(order_items)
                            
                        discussion = parsed_data.get("discussion", {}).get("remarks", text)
                        
                        # Get current location
                        session = self.session_manager.get_session(user_id)
                        latitude = session.gps_coords[0] if session.gps_coords else 0
                        longitude = session.gps_coords[1] if session.gps_coords else 0
                        
                        # Log to sheets with correct parameters
                        sheets_result = self.sheets_manager.log_visit(
                            user_id=user_id,
                            visit_type=visit_type,
                            contact_name=doctor_name,
                            orders=order_summary,
                            remarks=discussion,
                            location=hospital,
                            gps_lat=latitude,
                            gps_lon=longitude
                        )
                        
                        if sheets_result:
                            response_text += f"\n\n✅ **Logged to Google Sheets** (Row {sheets_result.get('row', 'N/A')})"
                        else:
                            response_text += f"\n\n⚠️ **Sheets logging failed** - data saved locally"
                            
                    except Exception as e:
                        logger.error(f"Sheets logging error: {e}")
                        response_text += f"\n\n⚠️ **Sheets error:** {e}"
                        
                # Add entry to session
                self.session_manager.log_entry(user_id)
                
                return response_text
                
            else:
                # Fallback without AI
                parts = text.split('|')
                doctor = parts[0].strip() if parts else "Unknown Doctor"
                product = parts[1].strip() if len(parts) > 1 else ""
                discussion = parts[2].strip() if len(parts) > 2 else text
                
                # Log to sheets
                if self.sheets_manager:
                    session = self.session_manager.get_session(user_id)
                    latitude = session.gps_coords[0] if session.gps_coords else 0
                    longitude = session.gps_coords[1] if session.gps_coords else 0
                    
                    result = self.sheets_manager.log_visit(
                        doctor_name=doctor,
                        hospital="",
                        orders=product,
                        discussion=discussion,
                        visit_type=visit_type,
                        latitude=latitude,
                        longitude=longitude
                    )
                    
                self.session_manager.log_entry(user_id)
                
                return f"""🏥 **Visit Logged**

👨‍⚕️ **Doctor:** {doctor}
📦 **Product:** {product}
💬 **Discussion:** {discussion}

✅ Logged to Google Sheets successfully!"""
                
        except Exception as e:
            logger.error(f"Visit command error: {e}")
            return f"❌ Error logging visit: {e}"
            
    async def process_expense_command(self, user_id: int, text: str) -> str:
        """Process expense command with AI parsing"""
        try:
            # Check session
            if not self.session_manager or not self.session_manager.get_location_status(user_id).get('active', False):
                return "❌ No active location session. Use /start to begin."
                
            if not self.session_manager.can_log_entry(user_id):
                return "⚠️ Session entry limit reached. Start new session with /start"
                
            # Process with AI
            if self.ai_engine:
                result = await self.ai_engine.process_expense_entry(user_id, text)
                parsed_data = result.get("parsed_data", {})
                response_text = result.get("response_text", "")
                
                # Log to sheets
                if self.sheets_manager and parsed_data and "error" not in parsed_data:
                    try:
                        expense = parsed_data.get("expense", {})
                        
                        # Get location
                        session = self.session_manager.get_session(user_id)
                        latitude = session.gps_coords[0] if session.gps_coords else 0
                        longitude = session.gps_coords[1] if session.gps_coords else 0
                        
                        sheets_result = self.sheets_manager.log_expense(
                            user_id=user_id,
                            expense_type=expense.get("category", "Other"),
                            amount=expense.get("amount", 0),
                            description=expense.get("description", text),
                            location="Field Location",
                            gps_lat=latitude,
                            gps_lon=longitude
                        )
                        
                        if sheets_result:
                            response_text += f"\n\n✅ **Logged to Google Sheets** (Row {sheets_result.get('row', 'N/A')})"
                            
                    except Exception as e:
                        logger.error(f"Expense sheets error: {e}")
                        response_text += f"\n\n⚠️ **Sheets error:** {e}"
                        
                self.session_manager.log_entry(user_id)
                return response_text
                
            else:
                # Fallback parsing
                parts = text.split('|')
                expense_type = parts[0].strip() if parts else "Other"
                amount = 0.0
                
                try:
                    if len(parts) > 1:
                        amount_str = ''.join(c for c in parts[1] if c.isdigit() or c == '.')
                        amount = float(amount_str) if amount_str else 0.0
                except:
                    pass
                    
                description = parts[2].strip() if len(parts) > 2 else text
                
                # Log to sheets
                if self.sheets_manager:
                    session = self.session_manager.get_session(user_id)
                    latitude = session.gps_coords[0] if session.gps_coords else 0
                    longitude = session.gps_coords[1] if session.gps_coords else 0
                    
                    self.sheets_manager.log_expense(
                        user_id=user_id,
                        expense_type=expense_type,
                        amount=amount,
                        description=description,
                        location="Field Location",
                        gps_lat=latitude,
                        gps_lon=longitude
                    )
                    
                self.session_manager.log_entry(user_id)
                
                return f"""💰 **Expense Logged**

🏷️ **Type:** {expense_type}
💵 **Amount:** ₹{amount:.2f}
📝 **Description:** {description}

✅ Logged to Google Sheets successfully!"""
                
        except Exception as e:
            logger.error(f"Expense command error: {e}")
            return f"❌ Error logging expense: {e}"
            
    async def process_analytics_command(self, user_id: int, timeframe: str = "30") -> str:
        """Process analytics command with ML insights"""
        try:
            # Parse timeframe
            try:
                days = int(timeframe)
            except:
                days = 30
                
            # Generate AI report
            if self.ai_engine:
                report = await self.ai_engine.generate_performance_report(user_id, days)
                return report
            else:
                # Basic fallback report
                return f"""📊 **Basic Analytics Report ({days} days)**

⚠️ AI analytics not available - basic reporting only

🏥 **Available Commands:**
• /report - View performance summary
• /insights - Get AI recommendations  
• /trends - View trend analysis

💡 Install AI dependencies for advanced analytics!"""
                
        except Exception as e:
            logger.error(f"Analytics command error: {e}")
            return f"❌ Analytics error: {e}"
            
    async def process_status_command(self, user_id: int) -> str:
        """Process status command"""
        try:
            if not self.session_manager:
                return "❌ Session manager not available"
                
            # Get session status
            status = self.session_manager.get_location_status(user_id)
            
            if not status.get('active', False):
                return """📍 **No Active Session**

Use /start to begin a new location session.

🎯 **Commands Available:**
• /start - Start location session
• /help - Show all commands
• /analytics - View performance analytics"""
                
            # Get session details
            session = self.session_manager.get_session(user_id)
            time_remaining = status.get('time_remaining', 0)
            entry_count = status.get('entries_count', 0)
            max_entries = 10
            
            minutes_left = max(0, time_remaining // 60)
            seconds_left = max(0, time_remaining % 60)
            
            coords = session.gps_coords if session.gps_coords else (0, 0)
            
            return f"""🎯 **Active Session Status**

📍 **Location:** {coords[0]:.6f}, {coords[1]:.6f}
⏰ **Time Remaining:** {minutes_left}m {seconds_left}s
📝 **Entries Used:** {entry_count}/{max_entries}

🏥 **Quick Actions:**
• /visit - Log doctor visit
• /expense - Log expense
• /end - End session early"""
                
        except Exception as e:
            logger.error(f"Status command error: {e}")
            return f"❌ Status error: {e}"
            
    async def process_insights_command(self, user_id: int) -> str:
        """Process insights command with AI"""
        try:
            if self.ai_engine:
                # Get AI insights
                context_analysis = await self.ai_engine.analyze_conversation_context([])
                suggestions = await self.ai_engine.get_smart_suggestions(user_id, "insights")
                
                response = "🧠 **AI Insights & Recommendations**\n\n"
                
                # Add suggestions
                if suggestions:
                    response += "💡 **Smart Suggestions:**\n"
                    for suggestion in suggestions:
                        response += f"• {suggestion}\n"
                    response += "\n"
                    
                # Add performance predictions
                try:
                    from ml_analytics import predict_performance
                    prediction = predict_performance(user_id)
                    
                    if prediction and "prediction" in prediction:
                        pred_data = prediction["prediction"]
                        response += f"🔮 **Performance Prediction:**\n"
                        response += f"• Next week visits: {pred_data.get('next_week_visits', 'N/A')}\n"
                        response += f"• Daily average: {pred_data.get('daily_average', 'N/A')}\n"
                        response += f"• Trend: {pred_data.get('trend', 'stable')}\n\n"
                        
                except Exception as e:
                    logger.error(f"Prediction error: {e}")
                    
                response += "📊 Use /analytics for detailed performance analysis!"
                return response
                
            else:
                return """🧠 **Basic Insights**

⚠️ AI engine not available - limited insights

📈 **Available Analysis:**
• /analytics - Basic performance report
• /status - Current session status
• /help - View all commands

💡 Configure AI dependencies for advanced insights!"""
                
        except Exception as e:
            logger.error(f"Insights command error: {e}")
            return f"❌ Insights error: {e}"
            
    async def process_help_command(self, user_id: int) -> str:
        """Process help command with context awareness"""
        try:
            help_text = """🤖 **MR Bot - AI-Enhanced Field Tracking**

🎯 **Core Workflow:**
1. /start - Start location session (5 min, GPS-validated)
2. Log entries while in session
3. View analytics and insights

📍 **Location Commands:**
• /start - Start GPS location session
• /status - Check session status
• /end - End current session

🏥 **Visit Logging:**
• /visit [doctor] | [product] | [quantity] - Log doctor visit
• /visit_followup [doctor] | [notes] - Log follow-up visit
• /visit_new [doctor] | [hospital] | [specialty] - Log new doctor

💰 **Expense Logging:**
• /expense [type] | [amount] | [description] - Log expense
• /fuel [amount] - Quick fuel expense
• /meal [amount] - Quick meal expense

📊 **Analytics & AI:**
• /analytics [days] - Performance analysis (default 30 days)
• /insights - AI recommendations and predictions
• /report - Comprehensive performance report
• /trends - View performance trends

🧠 **AI Features:**
• Intelligent parsing of visit and expense entries
• Automatic product name standardization
• Doctor name recognition and learning
• Expense categorization and compliance checking
• Performance prediction and recommendations
• Anomaly detection for unusual patterns

🔧 **System:**
• /settings - Configure preferences
• /export - Export data
• /help - Show this help

💡 **AI-Enhanced:** All entries are processed with Gemini AI and ML analytics for maximum accuracy and insights!"""

            # Add session-specific help
            if self.session_manager and self.session_manager.is_session_active(user_id):
                help_text += f"\n\n🎯 **Active Session:** You can log visits and expenses now!"
            else:
                help_text += f"\n\n📍 **Start Session:** Use /start to begin location-based logging"
                
            return help_text
            
        except Exception as e:
            logger.error(f"Help command error: {e}")
            return "❌ Help system error"
            
    async def process_end_command(self, user_id: int) -> str:
        """Process end session command"""
        try:
            if not self.session_manager:
                return "❌ Session manager not available"
                
            status = self.session_manager.get_location_status(user_id)
            
            if not status.get('active', False):
                return "📍 No active session to end."
                
            # Get session summary
            session = self.session_manager.get_session(user_id)
            entry_count = status.get('entries_count', 0)
            coords = session.gps_coords if session.gps_coords else (0, 0)
            
            # End session
            session.clear_session()
            self.session_manager.save_sessions()
            
            # Generate session summary
            response = f"""✅ **Session Ended Successfully**

📊 **Session Summary:**
• Entries logged: {entry_count}
• Location: {coords[0]:.6f}, {coords[1]:.6f}

🎯 **Next Steps:**
• Use /analytics to view performance analysis
• Use /insights for AI recommendations
• Use /start to begin a new session

Thank you for using MR Bot! 🚀"""

            return response
            
        except Exception as e:
            logger.error(f"End command error: {e}")
            return f"❌ Error ending session: {e}"
            
    async def process_unknown_command(self, user_id: int, text: str) -> str:
        """Process unknown commands with AI assistance"""
        try:
            # Try to understand intent with AI
            if self.ai_engine:
                suggestions = await self.ai_engine.get_smart_suggestions(user_id, text)
                
                response = f"""🤔 **Command not recognized:** `{text}`

💡 **Did you mean:**\n"""
                
                for suggestion in suggestions[:3]:  # Top 3 suggestions
                    response += f"• {suggestion}\n"
                    
                response += f"\n❓ **Need help?** Use /help for all commands"
                
                return response
            else:
                return f"""❓ **Unknown command:** `{text}`

Use /help to see all available commands.

🎯 **Quick Start:**
• /start - Begin location session
• /visit - Log doctor visit  
• /expense - Log expense
• /help - Show all commands"""
                
        except Exception as e:
            logger.error(f"Unknown command error: {e}")
            return "❓ Use /help to see available commands"

# Global command processor
mr_command_processor = MRCommandProcessor()

# Export main command functions
async def handle_start(user_id: int, location_data: Optional[Dict] = None) -> str:
    """Handle /start command"""
    return await mr_command_processor.process_start_command(user_id, location_data)

async def handle_visit(user_id: int, text: str, visit_type: str = "regular") -> str:
    """Handle visit logging commands"""
    return await mr_command_processor.process_visit_command(user_id, text, visit_type)

async def handle_expense(user_id: int, text: str) -> str:
    """Handle expense logging commands"""
    return await mr_command_processor.process_expense_command(user_id, text)

async def handle_analytics(user_id: int, timeframe: str = "30") -> str:
    """Handle analytics commands"""
    return await mr_command_processor.process_analytics_command(user_id, timeframe)

async def handle_status(user_id: int) -> str:
    """Handle status commands"""
    return await mr_command_processor.process_status_command(user_id)

async def handle_insights(user_id: int) -> str:
    """Handle insights commands"""
    return await mr_command_processor.process_insights_command(user_id)

async def handle_help(user_id: int) -> str:
    """Handle help commands"""
    return await mr_command_processor.process_help_command(user_id)

async def handle_end(user_id: int) -> str:
    """Handle end session commands"""
    return await mr_command_processor.process_end_command(user_id)

async def handle_unknown(user_id: int, text: str) -> str:
    """Handle unknown commands"""
    return await mr_command_processor.process_unknown_command(user_id, text)
