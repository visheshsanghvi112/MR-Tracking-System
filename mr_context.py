"""
MR Bot AI Context Engine
Provides comprehensive context to Gemini for intelligent parsing and insights
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class MRContextEngine:
    """Comprehensive context provider for MR Bot AI operations"""
    
    def __init__(self):
        self.sheets_manager = None
        self.context_cache = {}
        self.load_base_context()
        
    def load_base_context(self):
        """Load base context about MR operations and medical field"""
        self.base_context = {
            "system_type": "Medical Representative Field Tracking Bot",
            "primary_function": "Location-based visit and expense tracking for pharmaceutical field representatives",
            "business_domain": "Pharmaceutical/Medical Device Sales",
            "operational_context": {
                "field_work": "MRs visit doctors, hospitals, pharmacies, vendors across territories",
                "location_importance": "GPS validation ensures field presence authenticity",
                "session_management": "5-minute location sessions allow multiple entries per location",
                "data_integrity": "All entries require active location session for compliance"
            }
        }
        
    def get_medical_context(self) -> str:
        """Provide medical field context for Gemini"""
        return """
        MEDICAL REPRESENTATIVE CONTEXT:
        
        🏥 VISIT TYPES & PATTERNS:
        - Doctor Visits: Specialists (Cardiologist, Diabetologist, Neurologist, Oncologist, etc.)
        - Hospital Visits: Department heads, Purchase managers, Pharmacy heads
        - Pharmacy Visits: Retail pharmacies, Hospital pharmacies, Chain stores
        - Vendor Visits: Distributors, Wholesalers, Medical device suppliers
        
        🎯 COMMON MEDICAL SPECIALTIES:
        - Cardiology (heart), Endocrinology (diabetes), Neurology (brain/nerves)
        - Oncology (cancer), Orthopedics (bones), Gastroenterology (digestive)
        - Nephrology (kidney), Pulmonology (lungs), Dermatology (skin)
        
        💊 PHARMACEUTICAL PRODUCTS:
        - Medications: Tablets, Capsules, Injections, Syrups, Inhalers
        - Medical Devices: Glucometers, BP monitors, Thermometers, Stethoscopes
        - Consumables: Test strips, Syringes, Bandages, Surgical supplies
        
        📋 ORDER TERMINOLOGY:
        - Quantities: Strips, Boxes, Vials, Units, Packs, Bottles
        - Common orders: "2 boxes insulin", "50 strips glucose", "10 vials injection"
        - Sample requests: Product samples for patient trials
        
        🗣️ DISCUSSION TOPICS:
        - Patient compliance, Treatment outcomes, Side effects
        - New product launches, Clinical studies, Competitive products
        - Pricing negotiations, Volume discounts, Payment terms
        
        💰 EXPENSE CATEGORIES:
        - Travel: Fuel, Parking, Tolls, Public transport
        - Meals: Business lunches with doctors, Client entertainment
        - Communication: Phone bills, Internet charges
        - Marketing: Product samples, Literature, Promotional materials
        """
        
    def get_parsing_context(self) -> str:
        """Provide parsing guidelines for Gemini"""
        return """
        INTELLIGENT PARSING GUIDELINES:
        
        🧠 ORDER PARSING RULES:
        - Extract product names, quantities, and units
        - Standardize medical terminology (insulin pen = insulin injection pen)
        - Recognize abbreviations (BP = Blood Pressure, DM = Diabetes Mellitus)
        - Quantity patterns: "2 boxes", "50 units", "10 packs", "5 strips"
        
        👨‍⚕️ DOCTOR NAME STANDARDIZATION:
        - Format: "Dr. [First Name] [Last Name]"
        - Handle variations: "Dr Smith" → "Dr. Smith", "doctor john" → "Dr. John"
        - Preserve specializations: "Dr. Smith (Cardiologist)"
        - Hospital affiliations: "Dr. Patel - City Hospital"
        
        🏥 LOCATION INTELLIGENCE:
        - Hospital names: "City Hospital", "Apollo Hospital", "Max Healthcare"
        - Clinic patterns: "Dr. Smith Clinic", "Heart Care Center"
        - Pharmacy chains: "Apollo Pharmacy", "MedPlus", "Netmeds"
        
        💭 DISCUSSION EXTRACTION:
        - Patient outcomes: "Patient responding well", "Side effects reported"
        - Competitive mentions: "Competitor X offering lower prices"
        - Follow-up needs: "Arrange product demo", "Send clinical data"
        
        📊 STRUCTURED OUTPUT FORMAT:
        {
            "contact": {
                "name": "Dr. Smith",
                "title": "Cardiologist", 
                "location": "City Hospital"
            },
            "orders": [
                {"product": "Insulin Pens", "quantity": 2, "unit": "boxes"},
                {"product": "Glucose Strips", "quantity": 50, "unit": "pieces"}
            ],
            "discussion": {
                "topics": ["patient_compliance", "new_product_interest"],
                "competitor_mentions": [],
                "follow_up_required": ["send_clinical_data"]
            },
            "visit_category": "routine_visit",
            "priority": "medium"
        }
        """
        
    def get_user_context(self, user_id: int) -> str:
        """Get personalized context for specific MR"""
        try:
            # Get recent activity for pattern recognition
            if self.sheets_manager:
                recent_data = self.get_recent_mr_activity(user_id, days=7)
                
                context = f"""
                MR USER CONTEXT (ID: {user_id}):
                
                📊 RECENT ACTIVITY PATTERNS:
                - Total visits last 7 days: {recent_data.get('total_visits', 0)}
                - Most visited types: {', '.join(recent_data.get('top_visit_types', []))}
                - Common locations: {', '.join(recent_data.get('frequent_locations', []))}
                - Average daily visits: {recent_data.get('avg_daily_visits', 0):.1f}
                
                👥 FREQUENT CONTACTS:
                {self.format_frequent_contacts(recent_data.get('frequent_contacts', []))}
                
                🛍️ COMMON ORDERS:
                {self.format_common_orders(recent_data.get('frequent_orders', []))}
                
                💰 EXPENSE PATTERNS:
                - Average daily expenses: ₹{recent_data.get('avg_daily_expenses', 0):.2f}
                - Common expense types: {', '.join(recent_data.get('common_expenses', []))}
                """
                
                return context
                
        except Exception as e:
            pass
            
        return f"MR USER CONTEXT (ID: {user_id}): New user, building activity patterns..."
        
    def get_real_time_context(self, user_id: int) -> str:
        """Get real-time session and location context"""
        try:
            from session_manager import session_manager
            
            status = session_manager.get_location_status(user_id)
            session = session_manager.get_session(user_id)
            
            if status['active']:
                context = f"""
                REAL-TIME SESSION CONTEXT:
                
                📍 CURRENT LOCATION: {status['address']}
                ⏰ SESSION STATUS: Active ({status['time_remaining']}s remaining)
                📝 ENTRIES LOGGED: {status['entries_count']}/10 this session
                🕐 SESSION STARTED: {datetime.fromtimestamp(session.location_captured_at).strftime('%H:%M:%S')}
                
                🎯 CONTEXT FOR PARSING:
                - Location is verified and active
                - All entries will be tagged with current GPS coordinates
                - Session allows {10 - status['entries_count']} more entries
                - Parse with confidence in location authenticity
                """
            else:
                context = """
                REAL-TIME SESSION CONTEXT:
                
                🔴 NO ACTIVE LOCATION SESSION
                - MR must capture location before logging entries
                - Any parsing should prompt for location capture first
                - Cannot process visit or expense entries without location
                """
                
            return context
            
        except Exception as e:
            return "REAL-TIME CONTEXT: Session status unavailable"
            
    def get_business_intelligence_context(self) -> str:
        """Provide business intelligence context for smart parsing"""
        return """
        BUSINESS INTELLIGENCE CONTEXT:
        
        🎯 MR PERFORMANCE METRICS:
        - Visit frequency: Target 8-12 visits per day
        - Territory coverage: Geographic distribution analysis
        - Doctor engagement: Relationship building patterns
        - Order conversion: Visit to order conversion rates
        
        📈 SUCCESS INDICATORS:
        - High-value doctor relationships (repeat visits)
        - Consistent order patterns (product adoption)
        - Geographic efficiency (logical territory coverage)
        - Expense optimization (cost per visit analysis)
        
        ⚠️ RED FLAGS TO DETECT:
        - Unusually high expenses without proportional visits
        - Repetitive identical entries (possible fake data)
        - Geographic inconsistencies (impossible travel times)
        - Missing follow-up actions on important discussions
        
        🔍 COMPETITIVE INTELLIGENCE:
        - Competitor product mentions in discussions
        - Pricing pressure indicators in remarks
        - Market share threats or opportunities
        - New competitor activities in territory
        
        💡 OPTIMIZATION OPPORTUNITIES:
        - Route optimization suggestions based on location patterns
        - Visit timing optimization (best times for different doctor types)
        - Expense categorization for tax and reimbursement efficiency
        - Follow-up automation based on discussion content
        """
        
    def get_complete_context_for_gemini(self, user_id: int, operation_type: str = "general") -> str:
        """Generate complete context for Gemini AI operations"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        complete_context = f"""
        MR BOT AI CONTEXT - {timestamp}
        ======================================================
        
        SYSTEM OVERVIEW:
        {json.dumps(self.base_context, indent=2)}
        
        {self.get_medical_context()}
        
        {self.get_parsing_context()}
        
        {self.get_user_context(user_id)}
        
        {self.get_real_time_context(user_id)}
        
        {self.get_business_intelligence_context()}
        
        OPERATION TYPE: {operation_type.upper()}
        
        🎯 AI PROCESSING INSTRUCTIONS:
        - Use medical terminology expertise for accurate parsing
        - Apply business intelligence for context-aware insights
        - Leverage user patterns for personalized suggestions
        - Maintain data integrity and compliance standards
        - Provide actionable intelligence for field optimization
        
        ======================================================
        """
        
        return complete_context
        
    def get_recent_mr_activity(self, user_id: int, days: int = 7) -> Dict:
        """Analyze recent MR activity for pattern recognition"""
        try:
            # This would connect to sheets and analyze data
            # For now, return sample structure
            return {
                'total_visits': 0,
                'top_visit_types': [],
                'frequent_locations': [],
                'avg_daily_visits': 0.0,
                'frequent_contacts': [],
                'frequent_orders': [],
                'avg_daily_expenses': 0.0,
                'common_expenses': []
            }
        except Exception as e:
            return {}
            
    def format_frequent_contacts(self, contacts: List) -> str:
        """Format frequent contacts for context"""
        if not contacts:
            return "- Building contact patterns..."
        return "\n".join([f"- {contact}" for contact in contacts[:5]])
        
    def format_common_orders(self, orders: List) -> str:
        """Format common orders for context"""
        if not orders:
            return "- Learning order patterns..."
        return "\n".join([f"- {order}" for order in orders[:5]])

# Global context engine
mr_context = MRContextEngine()
