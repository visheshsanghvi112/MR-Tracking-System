"""
Thread-safe SQLite database for selfie checks
Prevents data loss from race conditions and file corruption
"""
import sqlite3
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SelfieDatabase:
    """Thread-safe SQLite database for selfie storage with automatic migration from JSON"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = Path('mr_bot') / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / 'selfie_checks.db')
        
        self.db_path = db_path
        self.json_backup_path = str(Path(db_path).parent / 'selfie_checks.json')
        
        # Initialize database
        self._init_database()
        
        # Migrate existing JSON data if present
        self._migrate_from_json()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create selfie_checks table with all necessary fields
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS selfie_checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        media_type TEXT NOT NULL,
                        file_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        verification_status TEXT DEFAULT 'Pending',
                        geofence_status TEXT DEFAULT 'Unknown',
                        distance_m REAL DEFAULT 0.0,
                        selfie_url TEXT DEFAULT '',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                    ON selfie_checks(user_id, timestamp DESC)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON selfie_checks(created_at DESC)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_file_id 
                    ON selfie_checks(file_id)
                ''')
                
                conn.commit()
                logger.info(f"Selfie database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize selfie database: {e}")
            raise
    
    def _migrate_from_json(self):
        """Migrate existing JSON data to SQLite (one-time operation)"""
        if not os.path.exists(self.json_backup_path):
            return
        
        try:
            # Check if we already have data in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM selfie_checks')
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info(f"Database already has {count} records, skipping JSON migration")
                    return
            
            # Read JSON data
            with open(self.json_backup_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not json_data:
                logger.info("No JSON data to migrate")
                return
            
            # Migrate to database
            migrated = 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for record in json_data:
                    try:
                        cursor.execute('''
                            INSERT INTO selfie_checks 
                            (user_id, media_type, file_id, timestamp)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            record.get('user_id'),
                            record.get('media_type'),
                            record.get('file_id'),
                            record.get('timestamp')
                        ))
                        migrated += 1
                    except Exception as e:
                        logger.warning(f"Failed to migrate record: {record}, error: {e}")
                
                conn.commit()
            
            logger.info(f"Successfully migrated {migrated} records from JSON to SQLite")
            
            # Backup the JSON file (don't delete, keep as backup)
            backup_path = f"{self.json_backup_path}.migrated.{int(datetime.now().timestamp())}"
            os.rename(self.json_backup_path, backup_path)
            logger.info(f"Original JSON backed up to {backup_path}")
            
        except Exception as e:
            logger.error(f"JSON migration failed: {e}")
    
    def add_selfie(
        self, 
        user_id: int, 
        media_type: str, 
        file_id: str,
        timestamp: str = None,
        verification_status: str = 'Pending',
        geofence_status: str = 'Unknown',
        distance_m: float = 0.0,
        selfie_url: str = ''
    ) -> int:
        """
        Add a new selfie record (thread-safe, ACID-compliant)
        Returns the ID of the inserted record
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO selfie_checks 
                    (user_id, media_type, file_id, timestamp, verification_status, 
                     geofence_status, distance_m, selfie_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, media_type, file_id, timestamp, 
                    verification_status, geofence_status, distance_m, selfie_url
                ))
                conn.commit()
                record_id = cursor.lastrowid
                
                logger.info(f"Selfie saved: user={user_id}, file_id={file_id}, id={record_id}")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to save selfie: {e}")
            raise
    
    def get_all_selfies(self, limit: int = None) -> List[Dict]:
        """Get all selfie records, optionally limited"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute('''
                        SELECT * FROM selfie_checks 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    ''', (limit,))
                else:
                    cursor.execute('SELECT * FROM selfie_checks ORDER BY created_at DESC')
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get selfies: {e}")
            return []
    
    def get_user_selfies(self, user_id: int, limit: int = None) -> List[Dict]:
        """Get selfies for a specific user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute('''
                        SELECT * FROM selfie_checks 
                        WHERE user_id = ?
                        ORDER BY created_at DESC 
                        LIMIT ?
                    ''', (user_id, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM selfie_checks 
                        WHERE user_id = ?
                        ORDER BY created_at DESC
                    ''', (user_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get user selfies: {e}")
            return []
    
    def get_selfie_by_file_id(self, file_id: str) -> Optional[Dict]:
        """Get a specific selfie by file_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM selfie_checks 
                    WHERE file_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (file_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Failed to get selfie by file_id: {e}")
            return None
    
    def export_to_json(self, output_path: str = None) -> str:
        """Export database to JSON format (for backward compatibility)"""
        if output_path is None:
            output_path = self.json_backup_path
        
        try:
            records = self.get_all_selfies()
            
            # Convert to simplified JSON format (matching old structure)
            simple_records = [
                {
                    'user_id': r['user_id'],
                    'media_type': r['media_type'],
                    'file_id': r['file_id'],
                    'timestamp': r['timestamp']
                }
                for r in records
            ]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(simple_records, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {len(simple_records)} records to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM selfie_checks')
                total = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT user_id) FROM selfie_checks')
                unique_users = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM selfie_checks
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    LIMIT 7
                ''')
                daily_counts = cursor.fetchall()
                
                return {
                    'total_selfies': total,
                    'unique_users': unique_users,
                    'daily_counts': [{'date': d[0], 'count': d[1]} for d in daily_counts]
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total_selfies': 0, 'unique_users': 0, 'daily_counts': []}


# Global instance
_selfie_db = None

def get_selfie_db() -> SelfieDatabase:
    """Get or create global selfie database instance"""
    global _selfie_db
    if _selfie_db is None:
        _selfie_db = SelfieDatabase()
    return _selfie_db
