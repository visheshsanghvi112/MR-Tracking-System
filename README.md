# MR Bot - Medical Representative Field Tracking System

## 🎯 Overview
AI-powered Telegram bot for Medical Representatives with location-based entry logging, session management, and comprehensive analytics.

## ✨ Key Features

### 🔒 Location-First Security
- **Mandatory GPS capture** before any entry logging
- **5-minute location sessions** with auto-expiry
- **Real-time location validation** for field authenticity

### 📝 Smart Visit Tracking
- Doctor visits, Hospital visits, Pharmacy visits
- Vendor meetings, Phone calls, Email follow-ups  
- **AI-powered parsing** with Gemini integration
- **Enhanced analytics** with 22 data points per visit

### 💰 Expense Management
- Location-tagged expense tracking
- **20 analytics columns** for deep insights
- Currency formatting and categorization
- Reimbursement status tracking

### 📊 Advanced Analytics
- **3 specialized sheets**: Daily Log, Expenses, Location Sessions
- Real user names (not just IDs)
- Territory analysis, performance metrics
- ML-ready data structure

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/visheshsanghvi112/MR-Tracking-System.git
cd MR-Tracking-System
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file with your values:
```env
# Telegram Bot Configuration
MR_BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_telegram_user_id

# Google Sheets Configuration
MR_SPREADSHEET_ID=your_google_sheet_id
GOOGLE_SHEETS_CREDENTIALS=path_to_service_account.json

# Authorized Users (comma-separated Telegram user IDs)
AUTHORIZED_MR_IDS=1201911108,987654321

# AI Configuration (optional)
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Setup Google Sheets
1. Create a Google Service Account
2. Download the JSON credentials file
3. Create a new Google Spreadsheet
4. Share the spreadsheet with the service account email
5. Copy the Spreadsheet ID from URL

### 5. Run Bot
```bash
python main.py
```

## 📱 Bot Commands

- `/start` - Start location session
- `/status` - Check session status  
- `/visit` - Log field visit (AI-enhanced)
- `/expense` - Log expense
- `/analytics` - View performance analytics
- `/help` - Show all commands

## 🏗️ Architecture

### Core Components
- `main.py` - Bot entry point and Telegram handlers
- `smart_sheets.py` - Google Sheets integration with 3 specialized sheets
- `session_manager.py` - Location session management and validation
- `mr_commands.py` - Command processing and business logic
- `gemini_parser.py` - AI-powered text parsing with Gemini
- `ai_engine.py` - Advanced AI analytics and insights
- `config.py` - Configuration management

### Data Structure
- **MR_Daily_Log**: 22 columns for visit tracking with analytics
- **MR_Expenses**: 20 columns for expense management  
- **Location_Log**: 12 columns for session tracking

## 🛡️ Security Features
- Authorized user whitelist
- GPS coordinate validation
- Session-based authentication
- Time-bound location sessions
- Real-time field presence verification

## 🔧 Configuration Options
- `LOCATION_SESSION_DURATION` - Session timeout (default: 15 minutes)
- `MAX_ENTRIES_PER_SESSION` - Entry limit (default: 10)
- `GPS_REQUIRED` - Enforce GPS capture (default: true)
- `LOG_LEVEL` - Logging level (default: INFO)

## 📊 Analytics Capabilities
- **Location-based**: Territory performance, route optimization
- **Time-based**: Visit patterns, peak performance hours
- **Performance-based**: Doctor engagement scores, outcome tracking  
- **Expense-based**: Category analysis, budget utilization

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License
This project is licensed under the MIT License.

---

**Built with AI-powered parsing and comprehensive analytics for modern MR field operations.**
