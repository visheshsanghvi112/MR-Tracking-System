"""
Smart Expense Handler - Multiple Input Methods
Handles both quick expense dumps and detailed categorization
Now uses centralized gemini_handler for robust fallback
"""
import re
import json
from typing import Dict, List, Any

# Import centralized Gemini handler
try:
    from gemini_handler import gemini, generate, generate_json
    GEMINI_HANDLER_AVAILABLE = True
except ImportError:
    GEMINI_HANDLER_AVAILABLE = False

class SmartExpenseHandler:
    """Smart expense parsing and handling"""
    
    def __init__(self):
        self.expense_categories = {
            'travel': ['travel', 'cab', 'taxi', 'auto', 'bus', 'train', 'fuel', 'petrol', 'diesel', 'uber', 'ola'],
            'food': ['food', 'lunch', 'breakfast', 'dinner', 'tea', 'coffee', 'snacks', 'meal'],
            'accommodation': ['hotel', 'stay', 'room', 'accommodation', 'lodge'],
            'parking': ['parking', 'park'],
            'entertainment': ['entertainment', 'drinks', 'alcohol', 'bar', 'club'],
            'gifts': ['gift', 'sample', 'promotional', 'freebie'],
            'communication': ['phone', 'call', 'internet', 'data'],
            'medical': ['medicine', 'doctor', 'hospital', 'clinic'],
            'other': ['other', 'misc', 'miscellaneous']
        }
        self.handler_available = GEMINI_HANDLER_AVAILABLE
    
    async def parse_bulk_expense(self, expense_text: str, date: str = None) -> Dict[str, Any]:
        """Parse bulk expense text using AI"""
        if not self.handler_available:
            return self._parse_expense_manual(expense_text)
        
        prompt = f"""You are an expert expense parser for Medical Representatives. Parse this expense entry and categorize it properly.

Expense Entry: "{expense_text}"
Date: {date or 'Today'}

Extract and return ONLY a JSON object with these categories:
{{
    "travel": amount_in_rs,
    "food": amount_in_rs,
    "accommodation": amount_in_rs,
    "parking": amount_in_rs,
    "entertainment": amount_in_rs,
    "gifts_samples": amount_in_rs,
    "communication": amount_in_rs,
    "medical": amount_in_rs,
    "other": amount_in_rs,
    "total": total_amount_in_rs,
    "items": [
        {{"category": "category_name", "item": "description", "amount": amount}}
    ],
    "success": true/false
}}

Categories guide:
- travel: cab, taxi, auto, bus, train, fuel, petrol, diesel, uber, ola
- food: lunch, breakfast, dinner, tea, coffee, snacks, meals
- accommodation: hotel, stay, room
- parking: parking fees
- entertainment: drinks, alcohol, entertainment
- gifts_samples: samples, promotional items, gifts
- communication: phone calls, internet
- medical: medicines, doctor fees
- other: anything else

Rules:
1. Extract all amounts (rs/rupees/₹ mentions)
2. Categorize based on item description
3. Calculate correct total
4. List individual items with categories
5. Return valid JSON only

Parse the expenses now:"""

        try:
            # Use centralized Gemini handler
            parsed_data = await generate_json(prompt)
            if parsed_data:
                return parsed_data
            else:
                return self._parse_expense_manual(expense_text)
        except Exception as e:
            print(f"AI parsing failed: {e}")
            return self._parse_expense_manual(expense_text)
    
    def _parse_expense_manual(self, expense_text: str) -> Dict[str, Any]:
        """Manual expense parsing as fallback"""
        amounts = re.findall(r'(\d+)', expense_text.lower())
        amounts = [int(x) for x in amounts if int(x) > 0]
        
        categories = {cat: 0 for cat in self.expense_categories.keys()}
        categories['other'] = 0
        
        items = []
        text_lower = expense_text.lower()
        
        # Simple keyword matching
        for amount in amounts:
            found_category = 'other'
            for category, keywords in self.expense_categories.items():
                if any(keyword in text_lower for keyword in keywords):
                    found_category = category
                    break
            
            categories[found_category] += amount
            items.append({
                'category': found_category,
                'item': f"Amount {amount}",
                'amount': amount
            })
        
        return {
            **categories,
            'total': sum(amounts),
            'items': items,
            'success': True
        }
    
    def format_expense_confirmation(self, parsed_expenses: Dict[str, Any], date: str) -> str:
        """Format expense confirmation message"""
        if not parsed_expenses.get('success'):
            return "❌ Could not parse expenses. Please try again."
        
        total = parsed_expenses.get('total', 0)
        items = parsed_expenses.get('items', [])
        
        message = f"💰 **Expense Summary for {date}**\n"
        message += f"📊 **Total: ₹{total}**\n\n"
        
        # Category breakdown
        message += "**Category Breakdown:**\n"
        for category, amount in parsed_expenses.items():
            if category not in ['items', 'total', 'success'] and amount > 0:
                emoji = self._get_category_emoji(category)
                message += f"{emoji} {category.title()}: ₹{amount}\n"
        
        message += "\n**Item Details:**\n"
        for item in items:
            emoji = self._get_category_emoji(item['category'])
            message += f"{emoji} {item['item']}: ₹{item['amount']}\n"
        
        message += "\n❓ **Is this correct?**\n"
        message += "✅ Send 'OK' to confirm\n"
        message += "✏️ Send 'EDIT' to modify\n"
        message += "❌ Send 'CANCEL' to discard"
        
        return message
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for expense category"""
        emoji_map = {
            'travel': '🚗',
            'food': '🍽️',
            'accommodation': '🏨',
            'parking': '🅿️',
            'entertainment': '🍻',
            'gifts_samples': '🎁',
            'communication': '📱',
            'medical': '💊',
            'other': '📦'
        }
        return emoji_map.get(category, '💰')
    
    def create_expense_menu(self) -> str:
        """Create expense input menu"""
        menu = "💰 **EXPENSE ENTRY OPTIONS**\n\n"
        menu += "Choose your preferred method:\n\n"
        
        menu += "🚀 **Quick Options:**\n"
        menu += "1️⃣ **Bulk Entry** - Dump all expenses in one go\n"
        menu += "   Example: 'food 300 fuel 150 parking 50'\n\n"
        
        menu += "📝 **Detailed Options:**\n"
        menu += "2️⃣ **Travel** - Cab, fuel, transport\n"
        menu += "3️⃣ **Food** - Meals, tea, snacks\n"
        menu += "4️⃣ **Accommodation** - Hotel, stay\n"
        menu += "5️⃣ **Other** - Miscellaneous expenses\n\n"
        
        menu += "💡 **Tips:**\n"
        menu += "• Bulk: 'lunch 200 cab 150 parking 50'\n"
        menu += "• Quick: Just type amounts with items\n"
        menu += "• Smart: AI will categorize automatically"
        
        return menu

# Test the expense parsing
async def test_expense_parsing():
    """Test expense parsing with various inputs"""
    handler = SmartExpenseHandler()
    
    test_cases = [
        "food 300 fuel 150 parking 50 tea 30",
        "lunch was 250 rupees cab fare 180 and parking 100",
        "hotel stay 2000 dinner 400 taxi 200",
        "today spent 500 on food 200 on travel and 100 parking",
        "breakfast 150 petrol 300 samples 500",
        "total expense lunch 200 auto 80 coffee 40 gift 100"
    ]
    
    print("🧪 Testing Smart Expense Parsing\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")
        result = await handler.parse_bulk_expense(test, "2025-09-03")
        
        if result.get('success'):
            print(f"✅ Total: ₹{result.get('total', 0)}")
            print(f"📊 Categories: {len([k for k, v in result.items() if k not in ['items', 'total', 'success'] and v > 0])}")
            print(f"📝 Items: {len(result.get('items', []))}")
        else:
            print("❌ Parsing failed")
        print("-" * 50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_expense_parsing())
