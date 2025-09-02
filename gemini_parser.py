"""
MR Bot Gemini AI Integration
Smart parsing and response system with ML enhancement
"""
import os
import sys
import json
import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Add parent directory for shared modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class GeminiMRParser:
    """Core Gemini parser for MR Bot with enhanced ML capabilities"""
    
    def __init__(self):
        self.api_key = None
        self.model = None
        self.ml_patterns = {}
        self.initialize_gemini()
        self.load_ml_patterns()
        
    def initialize_gemini(self):
        """Initialize Gemini API connection"""
        try:
            # Load API key from environment or config
            self.api_key = os.getenv('GEMINI_API_KEY', '')
            
            if not self.api_key:
                # Try loading from config file
                config_file = os.path.join(os.path.dirname(__file__), 'config.py')
                if os.path.exists(config_file):
                    sys.path.insert(0, os.path.dirname(config_file))
                    try:
                        import config
                        self.api_key = getattr(config, 'GEMINI_API_KEY', '')
                    except:
                        pass
                        
            if self.api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info("Gemini initialized successfully")
                except ImportError:
                    logger.warning("google-generativeai package not installed")
                    self.model = None
            else:
                logger.warning("No Gemini API key found")
                
        except Exception as e:
            logger.error(f"Gemini initialization error: {e}")
            
    def load_ml_patterns(self):
        """Load machine learning patterns"""
        try:
            patterns_file = os.path.join(os.path.dirname(__file__), 'data', 'ml_patterns.json')
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    self.ml_patterns = json.load(f)
            else:
                self.ml_patterns = {
                    "doctor_names": {},
                    "products": {},
                    "locations": {},
                    "expense_types": {},
                    "common_abbreviations": {
                        "dr": "doctor",
                        "hosp": "hospital",
                        "med": "medicine",
                        "qty": "quantity",
                        "pcs": "pieces"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error loading ML patterns: {e}")
            
    async def parse_visit_smart(self, user_id: int, text: str, visit_type: str) -> Dict[str, Any]:
        """Smart visit parsing with Gemini AI and ML"""
        try:
            # Import context engine
            from mr_context import mr_context
            
            # Get context
            context = mr_context.get_complete_context_for_gemini(user_id, "visit_parsing")
            
            # Apply ML preprocessing
            enhanced_text = self.enhance_text_with_ml(text, "visit")
            
            # Build intelligent prompt
            prompt = self.build_visit_parsing_prompt(context, enhanced_text, visit_type)
            
            # Call Gemini
            if self.model:
                response = await self.call_gemini(prompt)
                if response:
                    parsed = self.extract_structured_data(response)
                    if parsed:
                        # Apply ML post-processing
                        enhanced_parsed = self.enhance_parsed_data(parsed, text, "visit")
                        # Update ML patterns
                        self.update_ml_patterns(enhanced_parsed, text, "visit")
                        return enhanced_parsed
                        
            # Fallback to rule-based parsing
            return self.rule_based_visit_parsing(text, visit_type)
            
        except Exception as e:
            logger.error(f"Smart visit parsing error: {e}")
            return self.rule_based_visit_parsing(text, visit_type)
            
    async def parse_expense_smart(self, user_id: int, text: str) -> Dict[str, Any]:
        """Smart expense parsing with Gemini AI and ML"""
        try:
            from mr_context import mr_context
            
            context = mr_context.get_complete_context_for_gemini(user_id, "expense_parsing")
            enhanced_text = self.enhance_text_with_ml(text, "expense")
            
            prompt = self.build_expense_parsing_prompt(context, enhanced_text)
            
            if self.model:
                response = await self.call_gemini(prompt)
                if response:
                    parsed = self.extract_structured_data(response)
                    if parsed:
                        enhanced_parsed = self.enhance_parsed_data(parsed, text, "expense")
                        self.update_ml_patterns(enhanced_parsed, text, "expense")
                        return enhanced_parsed
                        
            return self.rule_based_expense_parsing(text)
            
        except Exception as e:
            logger.error(f"Smart expense parsing error: {e}")
            return self.rule_based_expense_parsing(text)
            
    def enhance_text_with_ml(self, text: str, data_type: str) -> str:
        """Enhance text using ML patterns"""
        try:
            enhanced = text
            
            # Apply common abbreviation expansions
            for abbrev, full_form in self.ml_patterns.get("common_abbreviations", {}).items():
                enhanced = re.sub(r'\b' + re.escape(abbrev) + r'\b', full_form, enhanced, flags=re.IGNORECASE)
                
            # Apply learned standardizations
            if data_type == "visit":
                for pattern, standard in self.ml_patterns.get("products", {}).items():
                    enhanced = re.sub(pattern, standard, enhanced, flags=re.IGNORECASE)
                    
            return enhanced
            
        except Exception as e:
            logger.error(f"Text enhancement error: {e}")
            return text
            
    def build_visit_parsing_prompt(self, context: str, text: str, visit_type: str) -> str:
        """Build intelligent visit parsing prompt"""
        return f"""
{context}

TASK: Parse MR visit entry with maximum intelligence and accuracy

INPUT TEXT: "{text}"
VISIT TYPE: {visit_type}

ENHANCED PARSING INSTRUCTIONS:
1. Extract contact information with medical context awareness
2. Identify all product orders with proper pharmaceutical naming
3. Parse discussion topics and medical outcomes
4. Detect competitive intelligence mentions
5. Assess visit quality and business impact

LEARNED PATTERNS TO CONSIDER:
{json.dumps(self.ml_patterns, indent=2)}

OUTPUT REQUIREMENTS:
- Return valid JSON only
- Include confidence scores for all extractions
- Standardize medical terminology
- Format pharmaceutical product names properly
- Provide business intelligence insights

JSON STRUCTURE:
{{
    "contact": {{
        "name": "Dr. [Full Name]",
        "specialty": "medical specialty",
        "location": "hospital/clinic name",
        "confidence": 0.95
    }},
    "orders": [
        {{
            "product": "standardized product name",
            "quantity": number,
            "unit": "boxes/strips/vials",
            "estimated_value": calculated_value,
            "confidence": 0.90
        }}
    ],
    "discussion": {{
        "medical_topics": ["topic1", "topic2"],
        "patient_cases": "summary",
        "concerns": ["concern1"],
        "outcomes": "visit result"
    }},
    "business_intelligence": {{
        "competitor_mentions": ["info"],
        "market_insights": ["insight1"],
        "follow_up_actions": ["action1"]
    }},
    "assessment": {{
        "visit_quality": 0.85,
        "business_potential": "high/medium/low",
        "next_visit": "timing suggestion"
    }}
}}

Parse with medical expertise and business intelligence. Return only JSON.
"""

    def build_expense_parsing_prompt(self, context: str, text: str) -> str:
        """Build intelligent expense parsing prompt"""
        return f"""
{context}

TASK: Parse MR expense entry with business intelligence

INPUT TEXT: "{text}"

ENHANCED EXPENSE ANALYSIS:
1. Categorize expense for tax compliance
2. Validate business purpose and necessity
3. Assess policy compliance
4. Estimate reimbursement eligibility

LEARNED PATTERNS:
{json.dumps(self.ml_patterns.get("expense_types", {}), indent=2)}

OUTPUT JSON:
{{
    "expense": {{
        "category": "standardized category",
        "amount": numeric_value,
        "description": "clear description",
        "business_purpose": "justification"
    }},
    "compliance": {{
        "tax_deductible": true/false,
        "reimbursable": true/false,
        "receipt_required": true/false,
        "policy_compliant": true/false
    }},
    "analysis": {{
        "reasonableness": "appropriate/high/questionable",
        "frequency_check": "normal/frequent/first_time",
        "approval_likelihood": 0.85
    }}
}}

Return only JSON with business intelligence.
"""

    async def call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API with error handling"""
        try:
            if not self.model:
                return None
                
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.8,
                    'max_output_tokens': 2048
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call error: {e}")
            return None
            
    def extract_structured_data(self, response: str) -> Optional[Dict]:
        """Extract JSON from Gemini response"""
        try:
            # Look for JSON in code blocks
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for JSON object directly
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return None
                    
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"JSON extraction error: {e}")
            return None
            
    def enhance_parsed_data(self, data: Dict, original_text: str, data_type: str) -> Dict:
        """Enhance parsed data with ML insights"""
        try:
            if not data:
                return data
                
            # Add ML metadata
            data["ml_enhanced"] = {
                "preprocessing_applied": True,
                "pattern_count": len(self.ml_patterns),
                "parsing_timestamp": datetime.now().isoformat(),
                "original_length": len(original_text),
                "enhancement_version": "1.0"
            }
            
            # Enhance confidence scores based on patterns
            if data_type == "visit" and "contact" in data:
                contact_name = data["contact"].get("name", "")
                if contact_name in self.ml_patterns.get("doctor_names", {}):
                    data["contact"]["confidence"] = min(data["contact"].get("confidence", 0.5) + 0.3, 1.0)
                    
            return data
            
        except Exception as e:
            logger.error(f"Data enhancement error: {e}")
            return data
            
    def update_ml_patterns(self, parsed_data: Dict, original_text: str, data_type: str):
        """Update ML patterns based on successful parsing"""
        try:
            if not parsed_data:
                return
                
            # Learn from successful parsing
            if data_type == "visit" and "contact" in parsed_data:
                contact_name = parsed_data["contact"].get("name", "")
                if contact_name:
                    # Learn name patterns
                    words = original_text.lower().split()
                    for word in words:
                        if len(word) > 2 and word.isalpha():
                            self.ml_patterns.setdefault("doctor_names", {})[word] = contact_name
                            
            # Learn product patterns
            if "orders" in parsed_data:
                for order in parsed_data["orders"]:
                    product = order.get("product", "")
                    if product:
                        words = original_text.lower().split()
                        for word in words:
                            if len(word) > 3 and word.isalpha():
                                self.ml_patterns.setdefault("products", {})[word] = product
                                
            # Save patterns asynchronously
            self.save_ml_patterns()
            
        except Exception as e:
            logger.error(f"ML pattern update error: {e}")
            
    def save_ml_patterns(self):
        """Save ML patterns to file"""
        try:
            patterns_file = os.path.join(os.path.dirname(__file__), 'data', 'ml_patterns.json')
            os.makedirs(os.path.dirname(patterns_file), exist_ok=True)
            
            with open(patterns_file, 'w') as f:
                json.dump(self.ml_patterns, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving ML patterns: {e}")
            
    def rule_based_visit_parsing(self, text: str, visit_type: str) -> Dict[str, Any]:
        """Fallback rule-based parsing"""
        try:
            # Split by common delimiters
            parts = re.split(r'[|,\n]', text)
            parts = [p.strip() for p in parts if p.strip()]
            
            # Extract basic information
            contact_name = parts[0] if parts else "Unknown Contact"
            if not contact_name.lower().startswith("dr"):
                contact_name = f"Dr. {contact_name}"
                
            # Extract orders if present
            orders = []
            for part in parts[1:]:
                # Look for quantity patterns
                qty_match = re.search(r'(\d+)\s*(\w+)', part)
                if qty_match:
                    orders.append({
                        "product": part.replace(qty_match.group(0), "").strip(),
                        "quantity": int(qty_match.group(1)),
                        "unit": qty_match.group(2),
                        "confidence": 0.6
                    })
                    
            return {
                "contact": {
                    "name": contact_name,
                    "specialty": "",
                    "location": "",
                    "confidence": 0.5
                },
                "orders": orders,
                "discussion": {
                    "topics": [],
                    "remarks": text
                },
                "assessment": {
                    "visit_quality": 0.6,
                    "business_potential": "medium"
                },
                "parsing_method": "rule_based"
            }
            
        except Exception as e:
            logger.error(f"Rule-based parsing error: {e}")
            return {"error": str(e), "parsing_method": "failed"}
            
    def rule_based_expense_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback expense parsing"""
        try:
            # Extract amount
            amount_match = re.search(r'[₹]?\s*(\d+(?:\.\d{2})?)', text)
            amount = float(amount_match.group(1)) if amount_match else 0.0
            
            # Categorize by keywords
            text_lower = text.lower()
            category = "other"
            
            if any(word in text_lower for word in ["fuel", "petrol", "diesel"]):
                category = "fuel"
            elif any(word in text_lower for word in ["meal", "lunch", "dinner", "food"]):
                category = "meals"
            elif any(word in text_lower for word in ["phone", "call", "mobile"]):
                category = "communication"
            elif any(word in text_lower for word in ["parking", "toll"]):
                category = "travel"
                
            return {
                "expense": {
                    "category": category,
                    "amount": amount,
                    "description": text,
                    "business_purpose": "Field work expense"
                },
                "compliance": {
                    "tax_deductible": True,
                    "reimbursable": True,
                    "receipt_required": amount > 500
                },
                "parsing_method": "rule_based"
            }
            
        except Exception as e:
            logger.error(f"Expense parsing error: {e}")
            return {"error": str(e), "parsing_method": "failed"}

# Smart response generator
class MRResponseGenerator:
    """Generate intelligent responses for MR interactions"""
    
    def __init__(self, parser: GeminiMRParser):
        self.parser = parser
        
    async def generate_visit_confirmation(self, parsed_data: Dict) -> str:
        """Generate intelligent visit confirmation"""
        try:
            if not parsed_data or "contact" not in parsed_data:
                return "✅ Visit logged successfully!"
                
            contact = parsed_data["contact"]
            orders = parsed_data.get("orders", [])
            
            response = f"🏥 **Visit Logged Successfully**\n\n"
            response += f"👨‍⚕️ **Contact:** {contact.get('name', 'Unknown')}\n"
            
            if contact.get("specialty"):
                response += f"🩺 **Specialty:** {contact['specialty']}\n"
                
            if contact.get("location"):
                response += f"🏥 **Location:** {contact['location']}\n"
                
            if orders:
                response += f"\n📦 **Orders ({len(orders)} items):**\n"
                for order in orders:
                    response += f"• {order.get('product', 'Product')} - {order.get('quantity', 0)} {order.get('unit', 'units')}\n"
                    
            # Add AI insights
            assessment = parsed_data.get("assessment", {})
            if assessment.get("business_potential") == "high":
                response += f"\n💰 **High business potential detected!**"
                
            return response
            
        except Exception as e:
            return f"✅ Visit logged (parsing issue: {e})"
            
    async def generate_expense_confirmation(self, parsed_data: Dict) -> str:
        """Generate intelligent expense confirmation"""
        try:
            if not parsed_data or "expense" not in parsed_data:
                return "💰 Expense logged successfully!"
                
            expense = parsed_data["expense"]
            compliance = parsed_data.get("compliance", {})
            
            response = f"💰 **Expense Logged Successfully**\n\n"
            response += f"🏷️ **Category:** {expense.get('category', 'Other')}\n"
            response += f"💵 **Amount:** ₹{expense.get('amount', 0):.2f}\n"
            response += f"📝 **Purpose:** {expense.get('business_purpose', 'Field work')}\n"
            
            # Add compliance info
            if compliance.get("receipt_required"):
                response += f"\n📄 **Receipt required** for this expense"
                
            if not compliance.get("policy_compliant"):
                response += f"\n⚠️ **Policy review needed**"
                
            return response
            
        except Exception as e:
            return f"💰 Expense logged (parsing issue: {e})"

# Global instances
gemini_parser = GeminiMRParser()
response_generator = MRResponseGenerator(gemini_parser)

# Export main functions
async def parse_visit(user_id: int, text: str, visit_type: str = "regular") -> Dict[str, Any]:
    """Main visit parsing function"""
    return await gemini_parser.parse_visit_smart(user_id, text, visit_type)

async def parse_expense(user_id: int, text: str) -> Dict[str, Any]:
    """Main expense parsing function"""
    return await gemini_parser.parse_expense_smart(user_id, text)

async def generate_visit_response(parsed_data: Dict) -> str:
    """Generate visit confirmation response"""
    return await response_generator.generate_visit_confirmation(parsed_data)

async def generate_expense_response(parsed_data: Dict) -> str:
    """Generate expense confirmation response"""
    return await response_generator.generate_expense_confirmation(parsed_data)
