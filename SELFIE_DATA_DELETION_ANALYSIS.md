# Selfie Data Deletion Investigation Report
**Date**: November 8, 2025  
**Issue**: Selfie entries mysteriously deleted from `selfie_checks.json`

---

## 🔍 CRITICAL FINDINGS

### 1. **RACE CONDITION VULNERABILITY** ⚠️
**Location**: `mr_commands.py` lines 120-132

```python
existing = []
if os.path.exists(store_path):
    with open(store_path, 'r', encoding='utf-8') as f:
        try:
            existing = json.load(f)
        except Exception:
            existing = []
existing.append(record)
with open(store_path, 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)
```

**THE PROBLEM**:
- When multiple selfies are submitted **simultaneously** (e.g., 2+ users at same time)
- Thread 1: Read file → Get existing array [A, B, C]
- Thread 2: Read file → Get existing array [A, B, C] (at same time)
- Thread 1: Append D → Write [A, B, C, D]
- Thread 2: Append E → Write [A, B, C, E] ❌ **OVERWRITES Thread 1's write!**
- Result: Entry D is **LOST FOREVER**

This is a **classic read-modify-write race condition** without file locking!

---

## 2. **SILENT ERROR HANDLING** ⚠️

```python
try:
    existing = json.load(f)
except Exception:
    existing = []  # Silently resets to empty if JSON is corrupted!
```

**THE PROBLEM**:
- If JSON file gets corrupted (incomplete write, disk error, etc.)
- Code silently creates an **empty array**
- All previous data is **lost** when file is rewritten
- No logging, no warning, no recovery attempt

---

## 3. **FILE WRITE WITHOUT ATOMIC OPERATIONS**

```python
with open(store_path, 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)
```

**THE PROBLEM**:
- Opens file in write mode ('w') - **immediately truncates file to 0 bytes**
- If script crashes/killed during `json.dump()`, file is left **empty or corrupted**
- No atomic write pattern (write to temp file → rename)
- No backup before overwrite

---

## 4. **LAST FILE MODIFICATION**
- Last modified: **November 4, 2025 at 17:37:36** (5:37 PM)
- File has **14 entries** currently
- All entries are from **November 4th** (10 AM - 12 PM timerange)
- **Data after November 4th 12:07 PM is missing**

---

## 📊 CURRENT FILE STATUS

**Entries Present**: 14 records
- User 999001: 1 test entry (9:31 AM)
- User 1201911108: 12 entries (9:56 AM - 12:04 PM)
- User 8254547957: 1 entry (12:07 PM)

**Potential Lost Data**:
- Any entries submitted after November 4th 12:07 PM
- Any entries lost to race conditions during concurrent submissions
- Any entries lost to JSON parse errors

---

## 🔧 ROOT CAUSES

### Primary Issues:
1. **No file locking mechanism** - Multiple processes can write simultaneously
2. **No atomic write operations** - File can be corrupted mid-write
3. **Silent error recovery** - Parse errors result in data loss without notification
4. **No transaction safety** - No rollback if write fails
5. **No backup strategy** - Data is overwritten with no recovery option

### Contributing Factors:
- Python's `json.dump()` is not atomic
- No use of file locking libraries (`fcntl` on Linux, `msvcrt` on Windows)
- No write-ahead logging or append-only structure
- Single file for all users (high contention)

---

## 💡 RECOMMENDED FIXES

### 🔴 CRITICAL (Implement Immediately):

#### 1. Add File Locking
```python
import fcntl  # Linux/Mac
import msvcrt  # Windows
import json
import os

def save_selfie_with_lock(store_path, record):
    """Thread-safe selfie saving with file locking"""
    lock_path = store_path + '.lock'
    
    # Create lock file
    with open(lock_path, 'w') as lock_file:
        try:
            # Acquire exclusive lock (blocks until available)
            if os.name == 'nt':  # Windows
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            else:  # Linux/Mac
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            
            # Now safely read-modify-write
            existing = []
            if os.path.exists(store_path):
                with open(store_path, 'r', encoding='utf-8') as f:
                    try:
                        existing = json.load(f)
                        if not isinstance(existing, list):
                            logger.error(f"SELFIE_DATA_CORRUPTED: Expected list, got {type(existing)}")
                            existing = []
                    except json.JSONDecodeError as e:
                        logger.error(f"SELFIE_JSON_PARSE_ERROR: {e}")
                        # Backup corrupted file before overwriting
                        backup_path = f"{store_path}.corrupted.{int(time.time())}"
                        os.rename(store_path, backup_path)
                        existing = []
            
            existing.append(record)
            
            # Atomic write: write to temp file, then rename
            temp_path = store_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            
            # Atomic rename (on same filesystem, this is guaranteed atomic)
            os.replace(temp_path, store_path)
            
        finally:
            # Release lock
            if os.name == 'nt':
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
```

#### 2. Use SQLite Database (Better Solution)
```python
import sqlite3
from datetime import datetime

def init_selfie_db():
    """Create SQLite database for selfies (ACID-compliant)"""
    conn = sqlite3.connect('mr_bot/data/selfie_checks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS selfie_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            file_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_timestamp ON selfie_checks(user_id, timestamp)')
    conn.commit()
    conn.close()

def save_selfie_db(user_id, media_type, file_id):
    """Save selfie to SQLite (thread-safe, ACID-compliant)"""
    conn = sqlite3.connect('mr_bot/data/selfie_checks.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO selfie_checks (user_id, media_type, file_id, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, media_type, file_id, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
```

**Why SQLite is better**:
- ✅ Built-in ACID transactions (no data loss)
- ✅ Concurrent writes handled automatically
- ✅ No file locking needed (SQLite handles it)
- ✅ Efficient queries and indexing
- ✅ Single file, no external dependencies
- ✅ Can still export to JSON for compatibility

---

### 🟡 HIGH PRIORITY (Implement Soon):

#### 3. Add Automatic Backups
```python
def backup_before_write(store_path):
    """Create timestamped backup before writing"""
    if os.path.exists(store_path):
        backup_dir = os.path.join('mr_bot', 'data', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'selfie_checks_{timestamp}.json')
        shutil.copy2(store_path, backup_path)
        
        # Keep only last 30 backups
        backups = sorted(os.listdir(backup_dir))
        if len(backups) > 30:
            for old_backup in backups[:-30]:
                os.remove(os.path.join(backup_dir, old_backup))
```

#### 4. Add Data Validation
```python
def validate_selfie_data(data):
    """Validate data structure before writing"""
    if not isinstance(data, list):
        raise ValueError(f"Expected list, got {type(data)}")
    
    for item in data:
        required_fields = ['user_id', 'media_type', 'file_id', 'timestamp']
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")
    
    return True
```

---

## 🔍 HOW TO RECOVER LOST DATA

### Check Git History (if committed)
```bash
git log --all -- "mr_bot/data/selfie_checks.json"
git show <commit_hash>:mr_bot/data/selfie_checks.json
```

### Check Google Sheets
- Selfie data is also logged to `Selfie_Verifications` sheet in Google Sheets
- This serves as a backup source
- Can reconstruct JSON from sheets data

### Check Application Logs
```bash
grep "SELFIE_MEDIA_DETECTED" mr_bot/data/mr_bot.log
```

### Reconstruct from Telegram File IDs
- File IDs are stored in Google Sheets
- Can query Telegram API to verify which files still exist
- Timestamps in sheets can rebuild timeline

---

## 📈 IMMEDIATE ACTION ITEMS

1. ✅ **[DONE]** Created backup: `selfie_checks.json.backup_20251108_*`
2. 🔴 **[URGENT]** Implement file locking OR migrate to SQLite
3. 🔴 **[URGENT]** Add proper error logging (replace silent `except Exception`)
4. 🟡 Add automated daily backups
5. 🟡 Add data validation before writes
6. 🟡 Set up monitoring/alerting for write failures
7. 🟢 Document recovery procedures
8. 🟢 Add unit tests for concurrent write scenarios

---

## 🎯 BEST SOLUTION: MIGRATE TO SQLITE

**Implementation Steps**:
1. Create migration script to convert JSON → SQLite
2. Update `mr_commands.py` to use SQLite functions
3. Keep JSON export function for backward compatibility
4. Test concurrent writes with stress test
5. Monitor for 1 week, then deprecate JSON file

**Estimated Time**: 2-3 hours
**Risk**: Low (SQLite is rock-solid)
**Benefit**: Eliminates ALL race condition issues permanently

---

## 📝 CONCLUSION

**Data loss is caused by**:
1. Race conditions during concurrent writes (PRIMARY)
2. Silent error handling that resets data (SECONDARY)
3. Non-atomic file operations (CONTRIBUTING)

**Fix Priority**:
- **Option A** (Quick): Add file locking (30 min implementation)
- **Option B** (Best): Migrate to SQLite (2-3 hours, permanent fix)

**Recommendation**: Go with **Option B (SQLite)** for production reliability.

---

**Analysis Completed By**: AI Inspector  
**Report Generated**: November 8, 2025
