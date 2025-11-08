from smart_sheets import SmartMRSheetsManager

mgr = SmartMRSheetsManager()

print("=== Sheet Info ===")
print(f"Spreadsheet ID: {mgr.spreadsheet_id}")
print(f"Main Sheet: {mgr.main_sheet.title if mgr.main_sheet else 'None'}")

print("\n=== Raw Headers ===")
headers = mgr.main_sheet.row_values(1) if mgr.main_sheet else []
for i, h in enumerate(headers):
    print(f"{i}: '{h}'")

print("\n=== First Data Row (Raw) ===")
first_row = mgr.main_sheet.row_values(2) if mgr.main_sheet else []
for i, val in enumerate(first_row):
    print(f"{i} ({headers[i] if i < len(headers) else '?'}): {val}")

print("\n=== Using get_all_records() ===")
records = mgr.main_sheet.get_all_records()
if records:
    first_record = records[0]
    print("First record keys:", list(first_record.keys()))
    print("\nFirst record values:")
    for key, val in first_record.items():
        print(f"  {key}: {val}")

print("\n=== Comparing Local vs Production ===")
print("Local can read data: ✅")
print("Production returns empty: ❌")
print("\nThis means Vercel backend cannot access the spreadsheet properly!")
