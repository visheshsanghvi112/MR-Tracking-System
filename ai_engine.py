"""
MR Bot AI Response Engine
Comprehensive AI system combining Gemini, ML/DL, and intelligent responses
"""
import os
import sys
import json
import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class MRAIEngine:
    """Central AI engine for MR Bot with advanced capabilities"""
    
    def __init__(self):
        self.gemini_available = False
        self.context_engine = None
        self.parser = None
        self.analytics = None
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize all AI components"""
        try:
            # Initialize context engine
            from mr_context import mr_context
            self.context_engine = mr_context
            
            # Initialize parsers
            from gemini_parser import gemini_parser
            self.parser = gemini_parser
            
            # Initialize analytics
            from ml_analytics import ml_analytics
            self.analytics = ml_analytics
            
            # Check Gemini availability
            try:
                import google.generativeai as genai
                api_key = os.getenv('GEMINI_API_KEY', '')
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_available = True
                    logger.info("MR AI Engine initialized with Gemini")
                else:
                    logger.warning("Gemini API key not found - using fallback methods")
            except ImportError:
                logger.warning("google-generativeai not available - using rule-based parsing")
                
        except Exception as e:
            logger.error(f"AI Engine initialization error: {e}")
            
    async def process_visit_entry(self, user_id: int, text: str, visit_type: str = "regular") -> Dict[str, Any]:
        """Process visit entry with full AI pipeline"""
        try:
            logger.info(f"Processing visit entry for user {user_id}: {text[:50]}...")
            
            # 1. Parse with AI/ML
            if self.gemini_available and self.parser:
                parsed_data = await self.parser.parse_visit_smart(user_id, text, visit_type)
            else:
                parsed_data = self.fallback_visit_parsing(text, visit_type)
                
            # 2. Detect anomalies
            anomalies = []
            if self.analytics:
                anomalies = self.analytics.detect_anomalies(parsed_data, "visit")
                
            # 3. Generate intelligent response
            response_text = await self.generate_visit_response(parsed_data, anomalies)
            
            # 4. Add ML insights
            ml_insights = self.get_ml_insights(parsed_data, "visit")
            
            return {
                "parsed_data": parsed_data,
                "response_text": response_text,
                "anomalies": anomalies,
                "ml_insights": ml_insights,
                "processing_status": "success"
            }
            
        except Exception as e:
            logger.error(f"Visit processing error: {e}")
            return {
                "parsed_data": {"error": str(e)},
                "response_text": f"❌ Error processing visit: {e}",
                "processing_status": "error"
            }
            
    async def process_expense_entry(self, user_id: int, text: str) -> Dict[str, Any]:
        """Process expense entry with full AI pipeline"""
        try:
            logger.info(f"Processing expense entry for user {user_id}: {text[:50]}...")
            
            # 1. Parse with AI/ML
            if self.gemini_available and self.parser:
                parsed_data = await self.parser.parse_expense_smart(user_id, text)
            else:
                parsed_data = self.fallback_expense_parsing(text)
                
            # 2. Detect anomalies
            anomalies = []
            if self.analytics:
                anomalies = self.analytics.detect_anomalies(parsed_data, "expense")
                
            # 3. Generate response
            response_text = await self.generate_expense_response(parsed_data, anomalies)
            
            # 4. Add insights
            ml_insights = self.get_ml_insights(parsed_data, "expense")
            
            return {
                "parsed_data": parsed_data,
                "response_text": response_text,
                "anomalies": anomalies,
                "ml_insights": ml_insights,
                "processing_status": "success"
            }
            
        except Exception as e:
            logger.error(f"Expense processing error: {e}")
            return {
                "parsed_data": {"error": str(e)},
                "response_text": f"❌ Error processing expense: {e}",
                "processing_status": "error"
            }
            
    async def generate_visit_response(self, parsed_data: Dict, anomalies: List[str]) -> str:
        """Generate intelligent visit confirmation response"""
        try:
            if not parsed_data or "contact" not in parsed_data:
                return "✅ Visit logged successfully!"
                
            contact = parsed_data["contact"]
            orders = parsed_data.get("orders", [])
            assessment = parsed_data.get("assessment", {})
            
            # Build response
            response = "🏥 **Visit Logged Successfully**\n\n"
            
            # Contact info
            response += f"👨‍⚕️ **Doctor:** {contact.get('name', 'Unknown')}\n"
            if contact.get("specialty"):
                response += f"🩺 **Specialty:** {contact['specialty']}\n"
            if contact.get("location"):
                response += f"🏥 **Location:** {contact['location']}\n"
                
            # Orders summary
            if orders:
                total_items = sum(order.get("quantity", 0) for order in orders)
                response += f"\n📦 **Orders:** {len(orders)} products, {total_items} total items\n"
                
                for order in orders:
                    product = order.get("product", "Product")
                    quantity = order.get("quantity", 0)
                    unit = order.get("unit", "units")
                    response += f"• {product}: {quantity} {unit}\n"
                    
            # AI Assessment
            quality = assessment.get("visit_quality", 0)
            potential = assessment.get("business_potential", "medium")
            
            if quality > 0.8:
                response += f"\n⭐ **Excellent visit quality** (Score: {quality:.2f})"
            elif quality < 0.5:
                response += f"\n📈 **Room for improvement** (Score: {quality:.2f})"
                
            if potential == "high":
                response += f"\n💰 **High business potential identified!**"
                
            # Anomalies
            if anomalies:
                response += f"\n\n⚠️ **Alerts:**\n"
                for anomaly in anomalies:
                    response += f"• {anomaly}\n"
                    
            # Next steps
            follow_up = assessment.get("next_visit", "")
            if follow_up:
                response += f"\n📅 **Next visit:** {follow_up}"
                
            return response
            
        except Exception as e:
            return f"✅ Visit logged (response generation issue: {e})"
            
    async def generate_expense_response(self, parsed_data: Dict, anomalies: List[str]) -> str:
        """Generate intelligent expense confirmation response"""
        try:
            if not parsed_data or "expense" not in parsed_data:
                return "💰 Expense logged successfully!"
                
            expense = parsed_data["expense"]
            compliance = parsed_data.get("compliance", {})
            analysis = parsed_data.get("analysis", {})
            
            response = "💰 **Expense Logged Successfully**\n\n"
            
            # Expense details
            response += f"🏷️ **Category:** {expense.get('category', 'Other')}\n"
            response += f"💵 **Amount:** ₹{expense.get('amount', 0):.2f}\n"
            response += f"📝 **Description:** {expense.get('description', 'No description')}\n"
            
            # Compliance status
            if compliance.get("tax_deductible"):
                response += f"\n✅ **Tax deductible**"
            if compliance.get("reimbursable"):
                response += f"\n💸 **Reimbursable**"
            if compliance.get("receipt_required"):
                response += f"\n📄 **Receipt required**"
                
            # ML Analysis
            reasonableness = analysis.get("reasonableness", "")
            if reasonableness == "high":
                response += f"\n⚠️ **High amount detected** - review recommended"
            elif reasonableness == "appropriate":
                response += f"\n✅ **Amount appears reasonable**"
                
            # Anomalies
            if anomalies:
                response += f"\n\n🔍 **Analysis Alerts:**\n"
                for anomaly in anomalies:
                    response += f"• {anomaly}\n"
                    
            return response
            
        except Exception as e:
            return f"💰 Expense logged (response issue: {e})"
            
    def get_ml_insights(self, parsed_data: Dict, data_type: str) -> List[str]:
        """Get ML insights for parsed data"""
        insights = []
        
        try:
            # Confidence analysis
            if data_type == "visit":
                contact_confidence = parsed_data.get("contact", {}).get("confidence", 0)
                if contact_confidence > 0.9:
                    insights.append("High confidence contact identification")
                elif contact_confidence < 0.5:
                    insights.append("Contact identification needs verification")
                    
                orders = parsed_data.get("orders", [])
                if orders:
                    avg_confidence = sum(o.get("confidence", 0) for o in orders) / len(orders)
                    if avg_confidence > 0.8:
                        insights.append("Orders parsed with high confidence")
                        
            elif data_type == "expense":
                amount = parsed_data.get("expense", {}).get("amount", 0)
                if amount > 1000:
                    insights.append("High-value expense logged")
                    
            # Pattern matching insights
            parsing_method = parsed_data.get("parsing_method", "")
            if parsing_method == "ai_enhanced":
                insights.append("AI-enhanced parsing applied")
            elif parsing_method == "rule_based":
                insights.append("Basic parsing used - consider adding more details")
                
        except Exception as e:
            insights.append(f"Insight generation error: {e}")
            
        return insights
        
    def fallback_visit_parsing(self, text: str, visit_type: str) -> Dict[str, Any]:
        """Enhanced fallback parsing with ML patterns"""
        try:
            # Smart text splitting
            delimiters = ["|", ",", "\n", " - ", " : "]
            parts = [text]
            
            for delimiter in delimiters:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(delimiter))
                parts = [p.strip() for p in new_parts if p.strip()]
                if len(parts) >= 3:  # Good split found
                    break
                    
            # Extract information intelligently
            contact_name = parts[0] if parts else "Unknown Contact"
            
            # Enhance doctor name
            if not any(title in contact_name.lower() for title in ["dr", "doctor"]):
                contact_name = f"Dr. {contact_name}"
                
            # Extract products and quantities
            orders = []
            for part in parts[1:]:
                # Look for quantity patterns
                qty_matches = re.findall(r'(\d+)\s*(\w+)', part)
                for qty_match in qty_matches:
                    product_name = re.sub(r'\d+\s*\w+', '', part).strip()
                    if product_name:
                        orders.append({
                            "product": product_name,
                            "quantity": int(qty_match[0]),
                            "unit": qty_match[1],
                            "confidence": 0.7
                        })
                        
            return {
                "contact": {
                    "name": contact_name,
                    "specialty": "",
                    "location": "",
                    "confidence": 0.6
                },
                "orders": orders,
                "discussion": {
                    "topics": [],
                    "remarks": text
                },
                "assessment": {
                    "visit_quality": 0.6,
                    "business_potential": "medium",
                    "next_visit": "follow up in 1 week"
                },
                "parsing_method": "enhanced_fallback",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fallback parsing error: {e}")
            return {"error": str(e), "parsing_method": "failed"}
            
    def fallback_expense_parsing(self, text: str) -> Dict[str, Any]:
        """Enhanced fallback expense parsing"""
        try:
            # Extract amount with various formats
            amount_patterns = [
                r'₹\s*(\d+(?:\.\d{2})?)',  # ₹500.00
                r'(\d+(?:\.\d{2})?)\s*rupees?',  # 500 rupees
                r'(\d+(?:\.\d{2})?)\s*rs?',  # 500 rs
                r'(\d+(?:\.\d{2})?)'  # Just number
            ]
            
            amount = 0.0
            for pattern in amount_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount = float(match.group(1))
                    break
                    
            # Smart categorization
            text_lower = text.lower()
            category_keywords = {
                "fuel": ["fuel", "petrol", "diesel", "gas"],
                "meals": ["meal", "lunch", "dinner", "food", "eat", "restaurant"],
                "travel": ["travel", "taxi", "auto", "bus", "train", "parking", "toll"],
                "communication": ["phone", "call", "mobile", "internet", "data"],
                "accommodation": ["hotel", "lodge", "stay", "room"],
                "marketing": ["gift", "sample", "promotional", "marketing"]
            }
            
            category = "other"
            for cat, keywords in category_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    category = cat
                    break
                    
            # Business purpose inference
            purpose_map = {
                "fuel": "Field travel and transportation",
                "meals": "Client meeting and field work nutrition",
                "travel": "Transportation for doctor visits",
                "communication": "Field communication and coordination",
                "accommodation": "Outstation field work accommodation",
                "marketing": "Doctor relationship building and promotion"
            }
            
            business_purpose = purpose_map.get(category, "Field work related expense")
            
            return {
                "expense": {
                    "category": category,
                    "amount": amount,
                    "description": text,
                    "business_purpose": business_purpose
                },
                "compliance": {
                    "tax_deductible": category in ["fuel", "travel", "communication", "marketing"],
                    "reimbursable": True,
                    "receipt_required": amount > 500,
                    "policy_compliant": amount < 5000  # Basic policy check
                },
                "analysis": {
                    "reasonableness": "high" if amount > 2000 else "appropriate",
                    "category_confidence": 0.8 if category != "other" else 0.5,
                    "auto_approved": amount < 1000 and category in ["fuel", "meals", "travel"]
                },
                "parsing_method": "enhanced_fallback",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Expense parsing error: {e}")
            return {"error": str(e), "parsing_method": "failed"}
            
    async def generate_performance_report(self, user_id: int, timeframe_days: int = 30) -> str:
        """Generate comprehensive performance report with AI insights"""
        try:
            # Get analytics
            if self.analytics:
                analysis = self.analytics.analyze_visit_patterns(user_id, timeframe_days)
            else:
                analysis = {"error": "Analytics not available"}
                
            # Build report
            report = f"📊 **MR Performance Report ({timeframe_days} days)**\n\n"
            
            # Visit frequency
            freq_data = analysis.get("visit_frequency", {})
            if freq_data:
                report += f"📈 **Visit Summary:**\n"
                report += f"• Total visits: {freq_data.get('total', 0)}\n"
                report += f"• Active days: {freq_data.get('active_days', 0)}\n"
                report += f"• Daily average: {freq_data.get('daily_average', 0)}\n"
                report += f"• Trend: {freq_data.get('trend', 'stable')}\n\n"
                
            # Doctor engagement
            engagement = analysis.get("doctor_engagement", {})
            if engagement:
                top_doctors = sorted(engagement.items(), key=lambda x: x[1].get("engagement_score", 0), reverse=True)[:3]
                if top_doctors:
                    report += f"🤝 **Top Engaged Doctors:**\n"
                    for doctor, stats in top_doctors:
                        score = stats.get("engagement_score", 0)
                        visits = stats.get("visit_count", 0)
                        report += f"• {doctor}: {score:.2f} score ({visits} visits)\n"
                    report += "\n"
                    
            # Product performance
            products = analysis.get("product_performance", {})
            if products:
                top_products = sorted(products.items(), key=lambda x: x[1].get("total_quantity", 0), reverse=True)[:3]
                if top_products:
                    report += f"🥇 **Top Products:**\n"
                    for product, stats in top_products:
                        quantity = stats.get("total_quantity", 0)
                        doctors = stats.get("doctor_adoption", 0)
                        report += f"• {product}: {quantity} units ({doctors} doctors)\n"
                    report += "\n"
                    
            # ML insights
            insights = analysis.get("ml_insights", [])
            if insights:
                report += f"🧠 **AI Insights:**\n"
                for insight in insights:
                    report += f"• {insight}\n"
                report += "\n"
                
            # Recommendations
            recommendations = analysis.get("recommendations", [])
            if recommendations:
                report += f"💡 **AI Recommendations:**\n"
                for rec in recommendations:
                    report += f"• {rec}\n"
                    
            return report
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return f"📊 Report generation failed: {e}"
            
    async def get_smart_suggestions(self, user_id: int, context: str) -> List[str]:
        """Get smart suggestions based on context"""
        try:
            suggestions = []
            
            if "visit" in context.lower():
                suggestions.extend([
                    "🏥 Log a doctor visit: /visit",
                    "📍 Check current location: /location", 
                    "📊 View visit analytics: /analytics"
                ])
                
            elif "expense" in context.lower():
                suggestions.extend([
                    "💰 Log an expense: /expense",
                    "📈 View expense summary: /expenses",
                    "🧾 Check reimbursement status: /reimbursement"
                ])
                
            else:
                # General suggestions based on recent activity
                suggestions.extend([
                    "🏥 Start location session: /start",
                    "📊 View performance report: /report",
                    "💡 Get AI insights: /insights",
                    "❓ Show help menu: /help"
                ])
                
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation error: {e}")
            return ["❓ Show help: /help"]
            
    async def analyze_conversation_context(self, message_history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation context for intelligent responses"""
        try:
            if not message_history:
                return {"context": "new_conversation", "suggestions": []}
                
            recent_messages = message_history[-5:]  # Last 5 messages
            
            # Extract patterns
            keywords = []
            for msg in recent_messages:
                text = msg.get("text", "").lower()
                keywords.extend(text.split())
                
            keyword_freq = {}
            for word in keywords:
                if len(word) > 3:  # Ignore short words
                    keyword_freq[word] = keyword_freq.get(word, 0) + 1
                    
            # Determine context
            context_indicators = {
                "visit_focused": ["doctor", "hospital", "visit", "order", "medicine"],
                "expense_focused": ["expense", "fuel", "meal", "money", "cost"],
                "analytics_focused": ["report", "analysis", "performance", "trend"],
                "location_focused": ["location", "gps", "where", "place"]
            }
            
            context_scores = {}
            for context_type, indicators in context_indicators.items():
                score = sum(keyword_freq.get(indicator, 0) for indicator in indicators)
                context_scores[context_type] = score
                
            # Determine primary context
            primary_context = max(context_scores.items(), key=lambda x: x[1])[0] if context_scores else "general"
            
            # Generate contextual suggestions
            suggestions = await self.get_smart_suggestions(None, primary_context)
            
            return {
                "context": primary_context,
                "confidence": max(context_scores.values()) / max(sum(context_scores.values()), 1),
                "keyword_frequency": keyword_freq,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Context analysis error: {e}")
            return {"context": "error", "suggestions": []}

# Global AI engine instance
mr_ai_engine = MRAIEngine()

# Export main functions
async def process_visit(user_id: int, text: str, visit_type: str = "regular") -> Dict[str, Any]:
    """Process visit entry with full AI pipeline"""
    return await mr_ai_engine.process_visit_entry(user_id, text, visit_type)

async def process_expense(user_id: int, text: str) -> Dict[str, Any]:
    """Process expense entry with full AI pipeline"""
    return await mr_ai_engine.process_expense_entry(user_id, text)

async def generate_report(user_id: int, days: int = 30) -> str:
    """Generate performance report"""
    return await mr_ai_engine.generate_performance_report(user_id, days)

async def get_suggestions(user_id: int, context: str = "") -> List[str]:
    """Get smart suggestions"""
    return await mr_ai_engine.get_smart_suggestions(user_id, context)

async def analyze_context(message_history: List[Dict]) -> Dict[str, Any]:
    """Analyze conversation context"""
    return await mr_ai_engine.analyze_conversation_context(message_history)
