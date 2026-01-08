"""
MR Bot Intelligent Gemini Parser
Advanced AI parsing with ML/DL techniques for MR field data
"""
import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class IntelligentMRParser:
    """AI-powered parser for MR field data using Gemini with ML/DL techniques"""
    
    def __init__(self):
        self.gemini_keys = []
        self.current_key_index = 0
        self.learning_data = {}
        self.pattern_cache = {}
        self.load_configuration()
        self.load_learning_patterns()
        
    def load_configuration(self):
        """Load Gemini API keys and configuration"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Load multiple Gemini keys for load balancing
            self.gemini_keys = [
                os.getenv('GEMINI_API_KEY', ''),
                os.getenv('GEMINI_API_KEY_2', ''),
                os.getenv('GEMINI_API_KEY_3', '')
            ]
            
            # Filter out empty keys
            self.gemini_keys = [key for key in self.gemini_keys if key]
            
            if not self.gemini_keys:
                logger.error("No Gemini API keys configured")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            
    def load_learning_patterns(self):
        """Load ML patterns from previous parsing sessions"""
        try:
            patterns_file = "data/ml_patterns.json"
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    self.learning_data = json.load(f)
                logger.info("Loaded ML patterns from previous sessions")
            else:
                self.learning_data = {
                    "doctor_name_patterns": {},
                    "product_standardization": {},
                    "location_aliases": {},
                    "expense_categorization": {},
                    "discussion_topics": [],
                    "competitive_mentions": []
                }
                
        except Exception as e:
            logger.error(f"Error loading learning patterns: {e}")
            self.learning_data = {}
            
    def save_learning_patterns(self):
        """Save learned patterns for future use (ML persistence)"""
        try:
            patterns_file = "data/ml_patterns.json"
            os.makedirs(os.path.dirname(patterns_file), exist_ok=True)
            
            with open(patterns_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving learning patterns: {e}")
            
    async def parse_visit_entry(self, user_id: int, raw_text: str, visit_type: str) -> Dict:
        """Parse visit entry with advanced AI and ML techniques"""
        try:
            from mr_context import mr_context
            
            # Get comprehensive context
            context = mr_context.get_complete_context_for_gemini(user_id, "visit_parsing")
            
            # Apply pre-processing using ML patterns
            preprocessed_text = self.apply_ml_preprocessing(raw_text, "visit")
            
            # Build Gemini prompt with context and ML insights
            prompt = f"""
            {context}
            
            VISIT ENTRY PARSING TASK:
            ========================
            
            Raw MR Input: "{preprocessed_text}"
            Visit Type: {visit_type}
            
            MACHINE LEARNING INSIGHTS:
            {self.get_ml_insights_for_parsing(raw_text, "visit")}
            
            PARSING REQUIREMENTS:
            1. Extract and standardize contact information
            2. Parse orders with quantities and units
            3. Identify discussion topics and outcomes
            4. Detect competitive intelligence
            5. Suggest follow-up actions
            6. Assess visit quality and importance
            
            OUTPUT FORMAT (JSON):
            {{
                "contact": {{
                    "name": "standardized doctor name",
                    "title": "medical specialty or role",
                    "location": "hospital/clinic name",
                    "confidence": 0.95
                }},
                "orders": [
                    {{
                        "product": "standardized product name",
                        "quantity": number,
                        "unit": "boxes/strips/vials/etc",
                        "value_estimate": "approximate order value",
                        "confidence": 0.90
                    }}
                ],
                "discussion": {{
                    "topics": ["topic1", "topic2"],
                    "patient_outcomes": "summary of patient discussion",
                    "concerns_raised": ["concern1", "concern2"],
                    "competitor_mentions": ["competitor info"],
                    "follow_up_needed": ["action1", "action2"]
                }},
                "visit_assessment": {{
                    "quality_score": 0.85,
                    "importance": "high/medium/low",
                    "outcome": "successful/neutral/challenging",
                    "next_visit_suggested": "timeframe suggestion"
                }},
                "ml_feedback": {{
                    "new_patterns_detected": ["pattern1", "pattern2"],
                    "confidence_level": 0.88,
                    "parsing_quality": "excellent/good/needs_improvement"
                }}
            }}
            
            Be extremely intelligent and context-aware. Use medical expertise and business intelligence.
            """
            
            # Call Gemini with advanced prompting
            result = await self.call_gemini_with_retry(prompt)
            
            if result:
                parsed_data = self.extract_json_from_response(result)
                
                # Apply post-processing with ML learning
                enhanced_data = self.apply_ml_postprocessing(parsed_data, raw_text, "visit")
                
                # Update ML patterns
                self.update_learning_patterns(enhanced_data, raw_text, "visit")
                
                return enhanced_data
                
        except Exception as e:
            logger.error(f"Error parsing visit: {e}")
            
        return self.fallback_visit_parsing(raw_text, visit_type)
        
    async def parse_expense_entry(self, user_id: int, raw_text: str) -> Dict:
        """Parse expense entry with AI and ML"""
        try:
            from mr_context import mr_context
            
            context = mr_context.get_complete_context_for_gemini(user_id, "expense_parsing")
            preprocessed_text = self.apply_ml_preprocessing(raw_text, "expense")
            
            prompt = f"""
            {context}
            
            EXPENSE ENTRY PARSING TASK:
            ==========================
            
            Raw MR Input: "{preprocessed_text}"
            
            MACHINE LEARNING INSIGHTS:
            {self.get_ml_insights_for_parsing(raw_text, "expense")}
            
            PARSE AND CATEGORIZE:
            1. Extract expense type and amount
            2. Categorize for tax/reimbursement
            3. Validate business purpose
            4. Detect policy compliance issues
            
            OUTPUT FORMAT (JSON):
            {{
                "expense": {{
                    "type": "standardized expense category",
                    "amount": numeric_value,
                    "description": "cleaned description",
                    "business_purpose": "clear business justification"
                }},
                "categorization": {{
                    "tax_category": "travel/meals/communication/marketing",
                    "reimbursable": true/false,
                    "requires_receipt": true/false,
                    "policy_compliant": true/false
                }},
                "ml_analysis": {{
                    "expense_pattern": "regular/unusual/suspicious",
                    "amount_reasonableness": "appropriate/high/low",
                    "category_confidence": 0.92
                }}
            }}
            """
            
            result = await self.call_gemini_with_retry(prompt)
            
            if result:
                parsed_data = self.extract_json_from_response(result)
                enhanced_data = self.apply_ml_postprocessing(parsed_data, raw_text, "expense")
                self.update_learning_patterns(enhanced_data, raw_text, "expense")
                return enhanced_data
                
        except Exception as e:
            logger.error(f"Error parsing expense: {e}")
            
        return self.fallback_expense_parsing(raw_text)
        
    def apply_ml_preprocessing(self, text: str, entry_type: str) -> str:
        """Apply ML-based text preprocessing"""
        try:
            # 1. Text normalization using learned patterns
            normalized_text = text.strip().lower()
            
            # 2. Apply learned abbreviation expansions
            if entry_type == "visit":
                for abbrev, full_form in self.learning_data.get("abbreviations", {}).items():
                    normalized_text = normalized_text.replace(abbrev.lower(), full_form)
                    
            # 3. Standardize product names using ML patterns
            for old_name, standard_name in self.learning_data.get("product_standardization", {}).items():
                normalized_text = normalized_text.replace(old_name.lower(), standard_name)
                
            # 4. Apply location aliases
            for alias, standard_location in self.learning_data.get("location_aliases", {}).items():
                normalized_text = normalized_text.replace(alias.lower(), standard_location)
                
            return normalized_text
            
        except Exception as e:
            logger.error(f"ML preprocessing error: {e}")
            return text
            
    def get_ml_insights_for_parsing(self, text: str, entry_type: str) -> str:
        """Generate ML insights to help Gemini parse better"""
        try:
            insights = []
            
            # Pattern recognition based on learned data
            if entry_type == "visit":
                # Check for known doctor patterns
                for pattern in self.learning_data.get("doctor_name_patterns", {}):
                    if pattern.lower() in text.lower():
                        insights.append(f"Doctor pattern detected: {pattern}")
                        
                # Check for product patterns
                for product in self.learning_data.get("product_standardization", {}):
                    if product.lower() in text.lower():
                        insights.append(f"Known product mentioned: {product}")
                        
            elif entry_type == "expense":
                # Check expense patterns
                for expense_type in self.learning_data.get("expense_categorization", {}):
                    if expense_type.lower() in text.lower():
                        insights.append(f"Expense category detected: {expense_type}")
                        
            # Text complexity analysis
            word_count = len(text.split())
            if word_count > 20:
                insights.append("Complex entry - likely contains multiple data points")
            elif word_count < 5:
                insights.append("Simple entry - may need clarification prompts")
                
            return "\n".join([f"- {insight}" for insight in insights]) if insights else "- No specific ML patterns detected"
            
        except Exception as e:
            return f"- ML insights unavailable: {e}"
            
    def apply_ml_postprocessing(self, parsed_data: Dict, original_text: str, entry_type: str) -> Dict:
        """Apply ML-based post-processing to improve parsed data"""
        try:
            if not parsed_data:
                return parsed_data
                
            # 1. Confidence scoring based on learned patterns
            if entry_type == "visit" and "contact" in parsed_data:
                contact_name = parsed_data["contact"].get("name", "")
                if contact_name in self.learning_data.get("doctor_name_patterns", {}):
                    parsed_data["contact"]["confidence"] = min(parsed_data["contact"].get("confidence", 0.5) + 0.2, 1.0)
                    
            # 2. Order value estimation using historical data
            if "orders" in parsed_data:
                for order in parsed_data["orders"]:
                    product = order.get("product", "")
                    quantity = order.get("quantity", 0)
                    # Add value estimation logic here
                    order["estimated_value"] = self.estimate_order_value(product, quantity)
                    
            # 3. Add ML confidence metrics
            parsed_data["ml_metrics"] = {
                "preprocessing_applied": True,
                "pattern_matches": len([p for p in self.learning_data.get("doctor_name_patterns", {}) if p.lower() in original_text.lower()]),
                "parsing_timestamp": datetime.now().isoformat(),
                "model_version": "gemini_2.5_flash_ml_enhanced"
            }
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"ML post-processing error: {e}")
            return parsed_data
            
    def update_learning_patterns(self, parsed_data: Dict, original_text: str, entry_type: str):
        """Update ML patterns based on successful parsing (Deep Learning approach)"""
        try:
            if not parsed_data:
                return
                
            # 1. Learn doctor name patterns
            if entry_type == "visit" and "contact" in parsed_data:
                contact_name = parsed_data["contact"].get("name", "")
                if contact_name:
                    # Extract name variations from original text
                    words = original_text.lower().split()
                    for i, word in enumerate(words):
                        if "dr" in word or "doctor" in word:
                            # Learn name patterns around doctor mentions
                            context_words = words[max(0, i-2):i+3]
                            pattern = " ".join(context_words)
                            self.learning_data.setdefault("doctor_name_patterns", {})[pattern] = contact_name
                            
            # 2. Learn product standardization
            if "orders" in parsed_data:
                for order in parsed_data["orders"]:
                    product = order.get("product", "")
                    # Find product mentions in original text and learn variations
                    original_words = original_text.lower().split()
                    for word in original_words:
                        if len(word) > 3 and word in product.lower():
                            self.learning_data.setdefault("product_standardization", {})[word] = product
                            
            # 3. Learn expense categorization patterns
            if entry_type == "expense" and "expense" in parsed_data:
                expense_type = parsed_data["expense"].get("type", "")
                # Learn keywords that indicate this expense type
                keywords = original_text.lower().split()
                for keyword in keywords:
                    if len(keyword) > 3:
                        self.learning_data.setdefault("expense_categorization", {})[keyword] = expense_type
                        
            # 4. Save learned patterns asynchronously
            asyncio.create_task(self.async_save_patterns())
            
        except Exception as e:
            logger.error(f"Error updating learning patterns: {e}")
            
    async def async_save_patterns(self):
        """Asynchronously save learning patterns"""
        try:
            await asyncio.sleep(0.1)  # Small delay to batch updates
            
            patterns_file = "data/ml_patterns.json"
            os.makedirs(os.path.dirname(patterns_file), exist_ok=True)
            
            with open(patterns_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")
            
    async def call_gemini_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Gemini API with load balancing and retry logic"""
        try:
            import google.generativeai as genai
            
            for attempt in range(max_retries):
                try:
                    # Use round-robin key selection for load balancing
                    api_key = self.gemini_keys[self.current_key_index % len(self.gemini_keys)]
                    self.current_key_index += 1
                    
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    
                    response = await model.generate_content_async(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,  # Low temperature for structured parsing
                            top_p=0.8,
                            top_k=40,
                            max_output_tokens=2048
                        )
                    )
                    
                    return response.text
                    
                except Exception as e:
                    logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(1)  # Wait before retry
                    
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
            
    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from Gemini response using regex and ML"""
        try:
            import re
            
            # 1. Try to find JSON block
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 2. Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return None
                    
            # 3. Parse JSON
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"JSON extraction error: {e}")
            return None
            
    def estimate_order_value(self, product: str, quantity: int) -> float:
        """Estimate order value using ML patterns"""
        try:
            # Simple value estimation based on product type and quantity
            # This could be enhanced with real pricing data
            
            product_lower = product.lower()
            base_value = 0
            
            # Basic product value estimation
            if "insulin" in product_lower:
                base_value = 500  # ₹500 per unit
            elif "strips" in product_lower or "glucose" in product_lower:
                base_value = 10   # ₹10 per strip
            elif "tablet" in product_lower or "capsule" in product_lower:
                base_value = 5    # ₹5 per tablet
            elif "injection" in product_lower:
                base_value = 200  # ₹200 per injection
            else:
                base_value = 50   # Default ₹50
                
            return base_value * quantity
            
        except Exception as e:
            return 0.0
            
    def fallback_visit_parsing(self, text: str, visit_type: str) -> Dict:
        """Fallback parsing when AI fails"""
        parts = text.split('|')
        
        return {
            "contact": {
                "name": parts[0].strip() if parts else text[:50],
                "title": "",
                "location": "",
                "confidence": 0.3
            },
            "orders": [
                {
                    "product": parts[1].strip() if len(parts) > 1 else "",
                    "quantity": 1,
                    "unit": "items",
                    "confidence": 0.3
                }
            ] if len(parts) > 1 else [],
            "discussion": {
                "topics": [],
                "remarks": parts[2].strip() if len(parts) > 2 else ""
            },
            "visit_assessment": {
                "quality_score": 0.5,
                "importance": "medium",
                "outcome": "logged"
            },
            "parsing_method": "fallback"
        }
        
    def fallback_expense_parsing(self, text: str) -> Dict:
        """Fallback expense parsing when AI fails"""
        parts = text.split('|')
        
        # Try to extract amount
        amount = 0.0
        try:
            if len(parts) > 1:
                amount_str = ''.join(c for c in parts[1] if c.isdigit() or c == '.')
                amount = float(amount_str) if amount_str else 0.0
        except:
            pass
            
        return {
            "expense": {
                "type": parts[0].strip() if parts else "Other",
                "amount": amount,
                "description": parts[2].strip() if len(parts) > 2 else text,
                "business_purpose": "Field work expense"
            },
            "categorization": {
                "tax_category": "other",
                "reimbursable": True,
                "requires_receipt": amount > 500
            },
            "parsing_method": "fallback"
        }
        
    def get_ml_insights_for_parsing(self, text: str, entry_type: str) -> str:
        """Generate ML insights to guide Gemini parsing"""
        try:
            insights = []
            
            # Frequency analysis
            words = text.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
            # Pattern matching insights
            if entry_type == "visit":
                # Check for medical terminology
                medical_terms = ["doctor", "dr", "hospital", "clinic", "patient", "medicine", "treatment"]
                found_terms = [term for term in medical_terms if term in text.lower()]
                if found_terms:
                    insights.append(f"Medical context detected: {', '.join(found_terms)}")
                    
                # Check for quantity patterns
                import re
                quantity_patterns = re.findall(r'\d+\s*(?:boxes?|strips?|units?|vials?|packs?)', text.lower())
                if quantity_patterns:
                    insights.append(f"Quantity patterns found: {', '.join(quantity_patterns)}")
                    
            elif entry_type == "expense":
                # Check for expense keywords
                expense_keywords = ["fuel", "petrol", "diesel", "meal", "lunch", "dinner", "phone", "parking"]
                found_keywords = [kw for kw in expense_keywords if kw in text.lower()]
                if found_keywords:
                    insights.append(f"Expense indicators: {', '.join(found_keywords)}")
                    
                # Check for amount patterns
                import re
                amounts = re.findall(r'₹?\s*\d+(?:\.\d{2})?', text)
                if amounts:
                    insights.append(f"Amount patterns detected: {', '.join(amounts)}")
                    
            return "\n".join([f"  {insight}" for insight in insights]) if insights else "  No specific patterns detected"
            
        except Exception as e:
            return f"  ML analysis error: {e}"

# Global intelligent parser
intelligent_parser = IntelligentMRParser()
