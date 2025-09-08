"""
Smart MR Sheets Manager
Automatically creates sheets and handles all data operations
"""
import os
import sys
import time
from datetime import datetime
import logging

# Add parent directory for shared utilities
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class SmartMRSheetsManager:
    """Automatically manages MR Bot Google Sheets"""
    
    def __init__(self):
        self.spreadsheet_id = None
        self.client = None
        self.spreadsheet = None
        self.main_sheet = None
        self.init_connection()
        
    def init_connection(self):
        """Initialize Google Sheets and auto-create required structure"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Get configuration
            self.spreadsheet_id = os.getenv('MR_SPREADSHEET_ID', '')
            creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'pharmagiftapp-60fb5a6a3ca9.json')
            
            if not self.spreadsheet_id or self.spreadsheet_id == 'PASTE_YOUR_NEW_SPREADSHEET_ID_HERE':
                logger.error("MR_SPREADSHEET_ID not configured")
                return False
                
            # Connect to Google Sheets
            import gspread
            from google.oauth2.service_account import Credentials
            
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = Credentials.from_service_account_file(creds_file, scopes=scope)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            # Auto-create required sheet structure
            self.setup_sheets()
            
            logger.info("MR Sheets initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MR sheets: {e}")
            return False
            
    def setup_sheets(self):
        """Automatically create 3 MR tracking sheets"""
        try:
            # Delete any extra sheets (keep only our 3 main sheets)
            self.cleanup_extra_sheets()
            
            # Setup main daily log sheet
            self.setup_daily_log_sheet()
            # Setup expenses sheet  
            self.setup_expenses_sheet()
            # Setup location tracking sheet
            self.setup_location_log_sheet()
            
            logger.info("Successfully set up exactly 3 sheets: MR_Daily_Log, MR_Expenses, and Location_Log")
            
        except Exception as e:
            logger.error(f"Error setting up sheets: {e}")
            
    def cleanup_extra_sheets(self):
        """Remove any sheets other than our 3 main sheets"""
        try:
            keep_sheets = ["MR_Daily_Log", "MR_Expenses", "Location_Log"]
            current_sheets = self.spreadsheet.worksheets()
            
            for sheet in current_sheets:
                if sheet.title not in keep_sheets:
                    logger.info(f"Removing extra sheet: {sheet.title}")
                    self.spreadsheet.del_worksheet(sheet)
                    
        except Exception as e:
            logger.warning(f"Could not cleanup extra sheets: {e}")
            
    def setup_daily_log_sheet(self):
        """Create MR Daily Log sheet"""
        try:
            sheet_name = "MR_Daily_Log"
            
            # Check if exists
            try:
                self.main_sheet = self.spreadsheet.worksheet(sheet_name)
                logger.info(f"Found existing sheet: {sheet_name}")
                return
            except:
                pass
                
            # Delete default Sheet1 if empty
            try:
                default_sheet = self.spreadsheet.worksheet("Sheet1")
                if not default_sheet.get_all_values():
                    self.spreadsheet.del_worksheet(default_sheet)
            except:
                pass
                
            # Create daily log sheet
            self.main_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=2000, cols=22
            )
            
            # Daily log headers (enhanced for deep analytics)
            headers = [
                "Timestamp", "Date", "Time", "MR_ID", "MR_Name",
                "Visit_Type", "Contact_Name", "Orders", 
                "Remarks", "Location", "GPS_Lat", "GPS_Lon", "Session_ID",
                "Visit_Duration", "Weather_Condition", "Area_Type", "Outcome_Score",
                "Follow_Up_Required", "Competition_Mentioned", "Product_Interest_Level",
                "Doctor_Specialty", "Hospital_Tier", "Territory_Zone"
            ]
            
            self.main_sheet.insert_row(headers, 1)
            
            # Format headers
            self.main_sheet.format("A1:V1", {
                "backgroundColor": {"red": 0.1, "green": 0.4, "blue": 0.8},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })
            
            logger.info(f"Created daily log sheet with {len(headers)} columns")
            
        except Exception as e:
            logger.error(f"Error creating daily log sheet: {e}")
            
    def setup_expenses_sheet(self):
        """Create MR Expenses sheet"""
        try:
            sheet_name = "MR_Expenses"
            
            # Check if exists
            try:
                self.expenses_sheet = self.spreadsheet.worksheet(sheet_name)
                logger.info(f"Found existing sheet: {sheet_name}")
                return
            except:
                pass
                
            # Create expenses sheet
            self.expenses_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=20
            )
            
            # Expense-specific headers (enhanced for analytics)
            headers = [
                "Timestamp", "Date", "Time", "MR_ID", "MR_Name", 
                "Expense_Type", "Amount", "Description", "Receipt_URL",
                "Location", "GPS_Lat", "GPS_Lon", "Session_ID",
                "Vendor_Name", "Bill_Number", "Payment_Mode", "Approval_Status",
                "Category", "Tax_Amount", "Reimbursement_Status"
            ]
            
            self.expenses_sheet.insert_row(headers, 1)
            
            # Format headers
            self.expenses_sheet.format("A1:T1", {
                "backgroundColor": {"red": 0.8, "green": 0.4, "blue": 0.1},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })
            
            logger.info(f"Created expenses sheet with {len(headers)} columns")
            
        except Exception as e:
            logger.error(f"Error creating expenses sheet: {e}")
            
    def setup_location_log_sheet(self):
        """Create Location Log sheet for session tracking"""
        try:
            sheet_name = "Location_Log"
            
            # Check if exists
            try:
                self.location_sheet = self.spreadsheet.worksheet(sheet_name)
                logger.info(f"Found existing sheet: {sheet_name}")
                return
            except:
                pass
                
            # Create location log sheet
            self.location_sheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=1000, cols=12
            )
            
            # Location log headers
            headers = [
                "Timestamp", "Date", "Time", "MR_ID", "MR_Name",
                "GPS_Lat", "GPS_Lon", "Address", 
                "Session_Started", "Session_Expired", "Entries_Count", "Session_ID"
            ]
            
            self.location_sheet.insert_row(headers, 1)
            
            # Format headers (green theme for location)
            self.location_sheet.format("A1:L1", {
                "backgroundColor": {"red": 0.1, "green": 0.6, "blue": 0.2},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })
            
            logger.info(f"Created location log sheet with {len(headers)} columns")
            
        except Exception as e:
            logger.error(f"Error creating location log sheet: {e}")
            
    def log_action(self, user_id: int, action_type: str, user_data: dict = None, **kwargs):
        """Universal logging method for all MR actions with real user name"""
        try:
            if not self.main_sheet:
                logger.error(f"CRITICAL: Main sheet not initialized for user {user_id}")
                return False
                
            now = datetime.now()
            session_id = f"session_{user_id}_{now.strftime('%Y-%m-%d')}"
            
            # Get actual user name
            from utils import get_mr_name
            mr_name = get_mr_name(user_id, user_data)
            
            logger.info(f"BUSINESS_LOG: User {mr_name} ({user_id}) performing {action_type}")
            logger.info(f"LOCATION_DATA: Lat={kwargs.get('gps_lat', 'N/A')}, Lon={kwargs.get('gps_lon', 'N/A')}, Address={kwargs.get('location', 'N/A')}")
            
            if action_type == "VISIT":
                logger.info(f"VISIT_DETAILS: Type={kwargs.get('visit_type', 'N/A')}, Contact={kwargs.get('contact_name', 'N/A')}, Orders={kwargs.get('orders', 'N/A')}")
            elif action_type == "EXPENSE":
                logger.info(f"EXPENSE_DETAILS: Type={kwargs.get('expense_type', 'N/A')}, Amount={kwargs.get('amount', 'N/A')}")
            
            # Base row data (enhanced for analytics)
            row_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                now.strftime("%Y-%m-%d"),           # Date
                now.strftime("%H:%M:%S"),           # Time
                user_id,                            # MR_ID
                mr_name,                            # MR_Name (ACTUAL NAME)
                kwargs.get('visit_type', ''),       # Visit_Type
                kwargs.get('contact_name', ''),     # Contact_Name
                kwargs.get('orders', ''),           # Orders
                kwargs.get('remarks', ''),          # Remarks
                kwargs.get('location', ''),         # Location
                kwargs.get('gps_lat', ''),          # GPS_Lat
                kwargs.get('gps_lon', ''),          # GPS_Lon
                session_id,                         # Session_ID
                kwargs.get('visit_duration', ''),   # Visit_Duration
                kwargs.get('weather', ''),          # Weather_Condition
                kwargs.get('area_type', ''),        # Area_Type
                kwargs.get('outcome_score', ''),    # Outcome_Score
                kwargs.get('follow_up', ''),        # Follow_Up_Required
                kwargs.get('competition', ''),      # Competition_Mentioned
                kwargs.get('interest_level', ''),   # Product_Interest_Level
                kwargs.get('specialty', ''),        # Doctor_Specialty
                kwargs.get('hospital_tier', ''),    # Hospital_Tier
                kwargs.get('territory', ''),        # Territory_Zone
            ]
            
            # Append to sheet
            self.main_sheet.append_row(row_data)
            logger.info(f"SUCCESS: Data logged to sheet for {mr_name} - Row added successfully")
            return True
            
        except Exception as e:
            logger.error(f"SHEET_ERROR: Failed to log {action_type} for user {user_id}: {str(e)}")
            logger.error(f"ERROR_DETAILS: Location={kwargs.get('location', 'N/A')}, Data={kwargs}")
            return False
            
    def log_location_capture(self, user_id: int, lat: float, lon: float, address: str, user_data: dict = None):
        """Log location capture event to both Daily Log and Location Log"""
        try:
            # Log to main daily log
            success1 = self.log_action(
                user_id=user_id,
                action_type="LOCATION_CAPTURE",
                user_data=user_data,
                location=address,
                gps_lat=lat,
                gps_lon=lon,
                remarks="Field session started"
            )
            
            # Also log to dedicated Location_Log sheet
            success2 = self.log_location_session(user_id, lat, lon, address, user_data)
            
            return success1 and success2
            
        except Exception as e:
            logger.error(f"Error logging location capture: {e}")
            return False
            
    def log_location_session(self, user_id: int, lat: float, lon: float, address: str, user_data: dict = None):
        """Log location session to Location_Log sheet"""
        try:
            if not hasattr(self, 'location_sheet') or not self.location_sheet:
                logger.warning("Location sheet not initialized")
                return False
                
            now = datetime.now()
            session_id = f"session_{user_id}_{now.strftime('%Y-%m-%d')}"
            
            # Get actual user name
            from utils import get_mr_name
            mr_name = get_mr_name(user_id, user_data)
            
            row_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                now.strftime("%Y-%m-%d"),           # Date
                now.strftime("%H:%M:%S"),           # Time
                user_id,                            # MR_ID
                mr_name,                            # MR_Name (ACTUAL NAME)
                lat,                                # GPS_Lat
                lon,                                # GPS_Lon
                address,                            # Address
                "Yes",                              # Session_Started
                "No",                               # Session_Expired
                0,                                  # Entries_Count (will be updated)
                session_id                          # Session_ID
            ]
            
            self.location_sheet.append_row(row_data)
            logger.info(f"Logged location session for {mr_name}: {address}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging location session: {e}")
            return False
        
    def log_visit(self, user_id: int, visit_type: str, contact_name: str, 
                  orders: str, remarks: str, location: str, gps_lat: float, gps_lon: float, user_data: dict = None):
        """Log visit entry"""
        return self.log_action(
            user_id=user_id,
            action_type="VISIT",
            user_data=user_data,
            visit_type=visit_type,
            contact_name=contact_name,
            orders=orders,
            remarks=remarks,
            location=location,
            gps_lat=gps_lat,
            gps_lon=gps_lon
        )
        
    def log_expense(self, user_id: int, expense_type: str, amount: float,
                   description: str, location: str, gps_lat: float, gps_lon: float, expense_data: dict = None):
        """Log expense entry to dedicated MR_Expenses sheet"""
        try:
            from datetime import datetime
            
            # Get current timestamp
            now = datetime.now()
            timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            # Get user info
            from utils import get_mr_name
            user_name = get_mr_name(user_id)
            
            # Prepare expense data for the MR_Expenses sheet
            if expense_data:
                # Smart expense with detailed breakdown
                category_breakdown = {}
                items_list = []
                
                for item in expense_data.get('items', []):
                    category = item.get('category', 'other')
                    amount_item = item.get('amount', 0)
                    description_item = item.get('item', '')
                    
                    if category not in category_breakdown:
                        category_breakdown[category] = 0
                    category_breakdown[category] += amount_item
                    
                    items_list.append(f"{category.title()}: {description_item} (₹{amount_item})")
                
                # Create detailed description
                detailed_description = "; ".join(items_list)
                category_summary = ", ".join([f"{k.title()}: ₹{v}" for k, v in category_breakdown.items()])
                
                # For multiple categories, use "Mixed" as primary type
                if len(category_breakdown) > 1:
                    primary_type = "Mixed"
                else:
                    primary_type = list(category_breakdown.keys())[0].title()
                
            else:
                # Simple expense
                detailed_description = description
                category_summary = f"{expense_type}: ₹{amount}"
                primary_type = expense_type
            
            # Generate session ID
            session_id = f"session_{user_id}_{date_str}"
            
            # Prepare row data for MR_Expenses sheet
            # Headers: Timestamp, Date, Time, MR_ID, MR_Name, Expense_Type, Amount, Description, 
            #         Category_Breakdown, Location, GPS_Lat, GPS_Lon, Session_ID, Receipt_URL, 
            #         Approval_Status, Approved_By, Comments, Created_At, Updated_At
            expense_row = [
                timestamp_str,           # Timestamp
                date_str,               # Date  
                time_str,               # Time
                user_id,                # MR_ID
                user_name,              # MR_Name
                primary_type,           # Expense_Type
                amount,                 # Amount
                detailed_description,   # Description
                category_summary,       # Category_Breakdown
                location,               # Location
                gps_lat,               # GPS_Lat
                gps_lon,               # GPS_Lon
                session_id,            # Session_ID
                "",                    # Receipt_URL (empty for now)
                "Pending",             # Approval_Status
                "",                    # Approved_By (empty)
                f"Smart parsed: {len(expense_data.get('items', []))} items" if expense_data else "Manual entry",  # Comments
                timestamp_str,         # Created_At
                timestamp_str          # Updated_At
            ]
            
            # Log to MR_Expenses sheet
            self.expenses_sheet.append_row(expense_row)
            
            # Also log a summary to main sheet for session tracking
            self.log_action(
                user_id=user_id,
                action_type="EXPENSE_LOGGED",
                remarks=f"Expense logged: {primary_type} Rs{amount}",
                location=location,
                gps_lat=gps_lat,
                gps_lon=gps_lon
            )
            
            logger.info(f"EXPENSE_SAVED: User {user_id} - {primary_type} - Rs{amount} - {len(expense_data.get('items', []))} items")
            return True
            
        except Exception as e:
            logger.error(f"Error logging expense: {e}")
            return False
        
    def log_session_end(self, user_id: int, location: str, total_entries: int):
        """Log session end event"""
        return self.log_action(
            user_id=user_id,
            action_type="SESSION_END",
            location=location,
            remarks=f"Session ended with {total_entries} entries"
        )
        
    def get_daily_summary(self, user_id: int, date: str = None):
        """Get daily summary for MR from single sheet"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
                
            # Get all records for the date
            all_records = self.main_sheet.get_all_records()
            
            # Filter for specific MR and date
            user_records = [
                record for record in all_records
                if str(record.get('MR_ID')) == str(user_id) and record.get('Date') == date
            ]
            
            # Separate by action type
            visits = [r for r in user_records if r.get('Action_Type') == 'VISIT']
            expenses = [r for r in user_records if r.get('Action_Type') == 'EXPENSE']
            locations = [r for r in user_records if r.get('Action_Type') == 'LOCATION_CAPTURE']
            
            total_expenses = sum(float(r.get('Amount', 0)) for r in expenses if r.get('Amount'))
            
            return {
                'date': date,
                'visits_count': len(visits),
                'expenses_count': len(expenses),
                'total_expenses': total_expenses,
                'locations_captured': len(locations),
                'total_entries': len(user_records)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return None
    
    def get_expense_summary(self, user_id: int, period: str = "today"):
        """Get expense summary for different periods from MR_Expenses sheet"""
        try:
            from datetime import datetime, timedelta
            
            today = datetime.now()
            
            if period == "today":
                start_date = today.strftime("%Y-%m-%d")
                end_date = start_date
                period_name = "Today"
            elif period == "month":
                start_date = today.replace(day=1).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                period_name = f"{today.strftime('%B %Y')}"
            elif period == "week":
                start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                period_name = "This Week"
            else:
                return None
            
            # Get all records from MR_Expenses sheet
            expense_records_raw = self.expenses_sheet.get_all_records()
            
            # Filter expense records for user and date range
            expense_records = []
            for record in expense_records_raw:
                if (str(record.get('MR_ID')) == str(user_id)):
                    record_date = record.get('Date', '')
                    if start_date <= record_date <= end_date:
                        expense_records.append(record)
            
            # Calculate totals by category
            category_totals = {}
            total_amount = 0
            expense_items = []
            
            for record in expense_records:
                # Clean amount string - remove currency symbols and commas
                amount_str = str(record.get('Amount', 0))
                amount_cleaned = amount_str.replace('₹', '').replace(',', '').strip()
                try:
                    amount = float(amount_cleaned) if amount_cleaned else 0.0
                except ValueError:
                    amount = 0.0
                    
                expense_type = record.get('Expense_Type', 'Other')
                description = record.get('Description', 'No description')
                date = record.get('Date', '')
                time = record.get('Time', '')
                category_breakdown = record.get('Category_Breakdown', '')
                
                total_amount += amount
                
                if expense_type not in category_totals:
                    category_totals[expense_type] = 0
                category_totals[expense_type] += amount
                
                expense_items.append({
                    'date': date,
                    'time': time,
                    'expense_type': expense_type,
                    'amount': amount,
                    'description': description,
                    'category_breakdown': category_breakdown,
                    'location': record.get('Location', 'Unknown')
                })
            
            # Sort items by date (newest first)
            expense_items.sort(key=lambda x: (x['date'], x['time']), reverse=True)
            
            return {
                'period': period_name,
                'total_amount': total_amount,
                'expense_count': len(expense_records),
                'category_totals': category_totals,
                'items': expense_items,
                'start_date': start_date,
                'end_date': end_date
            }
            
        except Exception as e:
            logger.error(f"Error getting expense summary for {period}: {e}")
            return None
    
    def get_expense_analytics(self, user_id: int):
        """Get comprehensive expense analytics"""
        try:
            from datetime import datetime, timedelta
            
            today = datetime.now()
            
            # Get different period summaries
            today_summary = self.get_expense_summary(user_id, "today")
            week_summary = self.get_expense_summary(user_id, "week")
            month_summary = self.get_expense_summary(user_id, "month")
            
            # Get top categories this month
            top_categories = []
            if month_summary and month_summary['category_totals']:
                top_categories = sorted(
                    month_summary['category_totals'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]  # Top 5 categories
            
            # Calculate daily average for the month
            days_in_month = today.day
            daily_average = month_summary['total_amount'] / days_in_month if month_summary and days_in_month > 0 else 0
            
            return {
                'today': today_summary,
                'week': week_summary,
                'month': month_summary,
                'top_categories': top_categories,
                'daily_average': daily_average,
                'analytics_date': today.strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            logger.error(f"Error getting expense analytics: {e}")
            return None
    
    def get_all_mrs(self):
        """Get list of all unique MRs from the sheets with correct GPS coordinates"""
        try:
            if not self.main_sheet:
                return []
                
            # Get all records
            records = self.main_sheet.get_all_records()
            
            # Extract unique MRs with CORRECT GPS mapping based on actual sheet structure
            mrs = {}
            for record in records:
                mr_id = record.get('MR_ID')
                mr_name = record.get('MR_Name', f'MR {mr_id}')
                
                if mr_id and mr_id not in mrs:
                    # ACTUAL GPS coordinate mapping from sheet structure:
                    # Location field = latitude, GPS_Lat field = longitude
                    location_field = record.get('Location', '')  # Contains latitude
                    gps_lat_field = record.get('GPS_Lat', '')    # Contains longitude
                    remarks = record.get('Remarks', '')          # Might contain proper coordinates
                    timestamp = record.get('Timestamp', '')
                    
                    # Parse coordinates properly
                    try:
                        lat = float(location_field) if location_field and location_field != '' else 0
                        lon = float(gps_lat_field) if gps_lat_field and gps_lat_field != '' else 0
                        
                        # If still no coordinates, try parsing from Remarks field
                        if (lat == 0 or lon == 0) and remarks:
                            # Parse format like "Lat: 18.947962, Lon: 72.829974"
                            if "Lat:" in remarks and "Lon:" in remarks:
                                try:
                                    lat_str = remarks.split("Lat:")[1].split(",")[0].strip()
                                    lon_str = remarks.split("Lon:")[1].strip()
                                    lat = float(lat_str)
                                    lon = float(lon_str)
                                except:
                                    pass
                                    
                    except (ValueError, TypeError):
                        lat, lon = 0, 0
                    
                    # Get proper location address
                    location_address = remarks if remarks and "Lat:" not in remarks else f"{lat:.6f}, {lon:.6f}"
                    
                    mrs[mr_id] = {
                        'mr_id': str(mr_id),
                        'name': mr_name,
                        'status': 'active' if timestamp else 'inactive',
                        'last_location': {
                            'lat': lat,
                            'lng': lon,
                            'address': location_address
                        },
                        'last_activity': timestamp,
                        'total_visits': len([r for r in records if r.get('MR_ID') == mr_id])
                    }
            
            return list(mrs.values())
            
        except Exception as e:
            logger.error(f"Error getting MR list: {e}")
            return []
    
    def get_mr_route_data(self, mr_id: str, date: str = None):
        """Get route/location data for a specific MR on a specific date with correct GPS coordinates"""
        try:
            if not self.main_sheet:
                return []
                
            records = self.main_sheet.get_all_records()
            
            # Filter by MR and date
            route_data = []
            for record in records:
                if str(record.get('MR_ID')) == str(mr_id):
                    if date and record.get('Date') != date:
                        continue
                        
                    # ACTUAL GPS coordinate mapping:
                    # Location field = latitude, GPS_Lat field = longitude
                    location_field = record.get('Location', '')  # Contains latitude
                    gps_lat_field = record.get('GPS_Lat', '')    # Contains longitude
                    remarks = record.get('Remarks', '')          # Might contain proper coordinates
                    
                    # Parse coordinates safely
                    try:
                        lat = float(location_field) if location_field and location_field != '' else 0
                        lon = float(gps_lat_field) if gps_lat_field and gps_lat_field != '' else 0
                        
                        # If still no coordinates, try parsing from Remarks field
                        if (lat == 0 or lon == 0) and remarks:
                            # Parse format like "Lat: 18.947962, Lon: 72.829974"
                            if "Lat:" in remarks and "Lon:" in remarks:
                                try:
                                    lat_str = remarks.split("Lat:")[1].split(",")[0].strip()
                                    lon_str = remarks.split("Lon:")[1].strip()
                                    lat = float(lat_str)
                                    lon = float(lon_str)
                                except:
                                    pass
                                    
                    except (ValueError, TypeError):
                        lat, lon = 0, 0
                    
                    if lat and lon and -90 <= lat <= 90 and -180 <= lon <= 180:
                        # Get proper location name
                        location_name = remarks if remarks and "Lat:" not in remarks else f"{lat:.6f}, {lon:.6f}"
                        
                        route_data.append({
                            'timestamp': record.get('Timestamp', ''),
                            'lat': lat,
                            'lng': lon,
                            'location': location_name,
                            'visit_type': record.get('Visit_Type', ''),
                            'contact_name': record.get('Contact_Name', ''),
                            'orders': record.get('Orders', 0)
                        })
            
            # Sort by timestamp
            route_data.sort(key=lambda x: x['timestamp'])
            return route_data
            
        except Exception as e:
            logger.error(f"Error getting route data for MR {mr_id}: {e}")
            return []

    def get_dashboard_stats(self):
        """Get dashboard statistics from sheets data"""
        try:
            if not self.main_sheet:
                return None
                
            records = self.main_sheet.get_all_records()
            
            # Calculate stats
            unique_mrs = set()
            today_date = datetime.now().strftime('%Y-%m-%d')
            active_today = set()
            total_visits = 0
            total_distance = 0
            
            for record in records:
                mr_id = record.get('MR_ID')
                date = record.get('Date', '')
                
                if mr_id:
                    unique_mrs.add(mr_id)
                    
                    if date == today_date:
                        active_today.add(mr_id)
                        
                    if record.get('Visit_Type'):
                        total_visits += 1
            
            return {
                'total_mrs': len(unique_mrs),
                'active_today': len(active_today),
                'live_sessions': len(active_today),  # Approximate
                'avg_distance': round(total_distance / max(len(unique_mrs), 1), 1),
                'total_visits': total_visits,
                'total_distance': total_distance
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return None
    
    def get_activity_feed(self, limit: int = 10):
        """Get recent activity feed from sheets"""
        try:
            if not self.main_sheet:
                return []
                
            records = self.main_sheet.get_all_records()
            
            # Sort by timestamp descending and take latest
            records.sort(key=lambda x: x.get('Timestamp', ''), reverse=True)
            
            activities = []
            for record in records[:limit]:
                mr_name = record.get('MR_Name', f"MR {record.get('MR_ID')}")
                action = record.get('Orders', record.get('Action_Type', 'Activity'))
                timestamp = record.get('Timestamp', '')
                
                activities.append({
                    'id': f"{record.get('MR_ID')}_{timestamp}",
                    'mr_name': mr_name,
                    'action': action,
                    'timestamp': timestamp,
                    'location': record.get('Remarks', '')
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting activity feed: {e}")
            return []
    
    def get_all_visit_records_with_gps(self):
        """Get all visit records with real GPS coordinates for analytics"""
        try:
            if not self.main_sheet:
                return []
                
            records = self.main_sheet.get_all_records()
            visit_records = []
            
            for record in records:
                # CORRECT GPS coordinate mapping based on actual sheet structure
                # From test: Location=lat, GPS_Lat=lon, GPS_Lon=session_id
                location_field = record.get('Location', '')  # This contains latitude
                gps_lat_field = record.get('GPS_Lat', '')    # This contains longitude  
                remarks = record.get('Remarks', '')          # This might contain coordinates
                
                # Parse coordinates safely - Location field has latitude, GPS_Lat has longitude
                try:
                    lat = float(location_field) if location_field and location_field != '' else 0
                    lon = float(gps_lat_field) if gps_lat_field and gps_lat_field != '' else 0
                    
                    # If still no coordinates, try parsing from Remarks field
                    if (lat == 0 or lon == 0) and remarks:
                        # Parse format like "Lat: 18.947962, Lon: 72.829974"
                        if "Lat:" in remarks and "Lon:" in remarks:
                            try:
                                lat_str = remarks.split("Lat:")[1].split(",")[0].strip()
                                lon_str = remarks.split("Lon:")[1].strip()
                                lat = float(lat_str)
                                lon = float(lon_str)
                            except:
                                pass
                                
                except (ValueError, TypeError):
                    lat, lon = 0, 0
                
                # Only include records with valid GPS coordinates
                if lat != 0 and lon != 0 and -90 <= lat <= 90 and -180 <= lon <= 180:
                    # Get proper location name from remarks or use coordinates
                    location_name = remarks if remarks and "Lat:" not in remarks else f"{lat:.6f}, {lon:.6f}"
                    
                    visit_records.append({
                        'mr_id': str(record.get('MR_ID', '')),
                        'mr_name': record.get('MR_Name', 'Unknown'),
                        'timestamp': record.get('Timestamp', ''),
                        'date': record.get('Date', ''),
                        'time': record.get('Time', ''),
                        'location': location_name,
                        'gps_lat': lat,
                        'gps_lon': lon,
                        'visit_type': record.get('Visit_Type', 'Unknown'),
                        'contact_name': record.get('Contact_Name', ''),
                        'session_id': record.get('GPS_Lon', '')  # Session ID is in GPS_Lon field
                    })
            
            return visit_records
            
        except Exception as e:
            logger.error(f"Error getting visit records with GPS: {e}")
            return []

    def fix_mr_coordinates(self):
        """Fix the coordinate mapping in get_all_mrs method"""
        try:
            if not self.main_sheet:
                return []
                
            # Get all records
            records = self.main_sheet.get_all_records()
            
            # Extract unique MRs with correct GPS mapping
            mrs = {}
            for record in records:
                mr_id = record.get('MR_ID')
                mr_name = record.get('MR_Name', f'MR {mr_id}')
                
                if mr_id and mr_id not in mrs:
                    # CORRECT GPS coordinate mapping
                    gps_lat = record.get('GPS_Lat', '')  # This is latitude
                    gps_lon = record.get('GPS_Lon', '')  # This is longitude
                    location = record.get('Location', '') # This is address/location name
                    timestamp = record.get('Timestamp', '')
                    
                    # Parse coordinates properly
                    try:
                        lat = float(gps_lat) if gps_lat and gps_lat != '' else 0
                        lon = float(gps_lon) if gps_lon and gps_lon != '' else 0
                    except (ValueError, TypeError):
                        lat, lon = 0, 0
                    
                    mrs[mr_id] = {
                        'mr_id': str(mr_id),
                        'name': mr_name,
                        'status': 'active' if timestamp else 'inactive',
                        'last_location': {
                            'lat': lat,
                            'lng': lon,
                            'address': location
                        },
                        'last_activity': timestamp,
                        'total_visits': len([r for r in records if r.get('MR_ID') == mr_id and r.get('GPS_Lat') and r.get('GPS_Lon')])
                    }
            
            return list(mrs.values())
            
        except Exception as e:
            logger.error(f"Error fixing MR coordinates: {e}")
            return []

# Global instance
smart_sheets = SmartMRSheetsManager()
