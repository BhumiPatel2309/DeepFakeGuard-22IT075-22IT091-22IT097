import os
import shutil
import sqlite3
from datetime import datetime
import json
import logging
from pathlib import Path
import hashlib

class BackupManager:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        # List of files and directories to exclude from backup
        self.exclude_patterns = [
            "__pycache__",
            "*.pyc",
            "backups/*",
            ".git/*",
            ".gitignore",
            "*.log",
            "*.tmp"
        ]
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename=os.path.join(self.backup_dir, 'backup.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def create_backup(self, backup_note=""):
        """Create a backup of the entire application"""
        try:
            # Create timestamp-based backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)

            # Get the root directory of the application
            app_root = os.path.dirname(os.path.abspath(__file__))
            app_root = os.path.dirname(app_root)  # Go up one level to get the project root

            # Initialize backup stats
            backup_stats = {
                "total_files": 0,
                "total_size": 0,
                "backed_up_items": []
            }

            # Walk through the application directory
            for root, dirs, files in os.walk(app_root, topdown=True):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(p.rstrip('/*') == d for p in self.exclude_patterns)]
                
                # Get relative path from app root
                rel_path = os.path.relpath(root, app_root)
                if rel_path == ".":
                    rel_path = ""

                # Create corresponding directory in backup
                backup_dir = os.path.join(backup_path, rel_path) if rel_path else backup_path
                os.makedirs(backup_dir, exist_ok=True)

                # Copy files
                for file in files:
                    # Skip excluded files
                    if any(self._matches_pattern(file, pattern) for pattern in self.exclude_patterns):
                        continue

                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(backup_dir, file)
                    
                    # Special handling for database files
                    if file.endswith('.db'):
                        self._backup_database(src_file, dst_file)
                    else:
                        shutil.copy2(src_file, dst_file)
                    
                    file_size = os.path.getsize(src_file)
                    backup_stats["total_files"] += 1
                    backup_stats["total_size"] += file_size
                    backup_stats["backed_up_items"].append({
                        "path": os.path.join(rel_path, file),
                        "size": file_size,
                        "hash": self._calculate_file_hash(dst_file)
                    })

            # Create backup metadata
            metadata = {
                "timestamp": timestamp,
                "note": backup_note,
                "stats": backup_stats,
                "version": "2.0"
            }
            
            with open(os.path.join(backup_path, "backup_metadata.json"), "w") as f:
                json.dump(metadata, f, indent=4)

            logging.info(f"Full application backup created successfully at {backup_path}")
            return True, backup_path

        except Exception as e:
            logging.error(f"Backup failed: {str(e)}")
            return False, str(e)

    def restore_backup(self, backup_timestamp=None):
        """Restore the entire application from a backup"""
        try:
            # Find the backup to restore
            if backup_timestamp:
                backup_path = os.path.join(self.backup_dir, f"backup_{backup_timestamp}")
            else:
                # Get the latest backup
                backups = [d for d in os.listdir(self.backup_dir) if d.startswith("backup_")]
                if not backups:
                    raise Exception("No backups found")
                latest_backup = sorted(backups)[-1]
                backup_path = os.path.join(self.backup_dir, latest_backup)

            if not os.path.exists(backup_path):
                raise Exception(f"Backup {backup_path} not found")

            # Load and verify backup metadata
            with open(os.path.join(backup_path, "backup_metadata.json"), "r") as f:
                metadata = json.load(f)

            # Get the application root directory
            app_root = os.path.dirname(os.path.abspath(__file__))
            app_root = os.path.dirname(app_root)

            # Create a pre-restore backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = os.path.join(self.backup_dir, f"pre_restore_{timestamp}")
            self.create_backup(backup_note="Automatic backup before restore")

            restored_items = []
            
            # Restore all files from backup
            for item in metadata["stats"]["backed_up_items"]:
                src_path = os.path.join(backup_path, item["path"])
                dst_path = os.path.join(app_root, item["path"])
                
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                
                # Special handling for database files
                if dst_path.endswith('.db'):
                    # Close any open database connections
                    if os.path.exists(dst_path):
                        try:
                            conn = sqlite3.connect(dst_path)
                            conn.close()
                        except:
                            pass
                
                # Copy the file
                shutil.copy2(src_path, dst_path)
                
                # Verify file hash
                current_hash = self._calculate_file_hash(dst_path)
                if current_hash != item["hash"]:
                    logging.warning(f"Hash mismatch for {item['path']}, file may be corrupted")
                
                restored_items.append(item["path"])

            logging.info(f"Application restored successfully from {backup_path}")
            return True, {
                "message": f"Restored from {backup_path}",
                "restored_items": restored_items,
                "pre_restore_backup": pre_restore_backup
            }

        except Exception as e:
            logging.error(f"Restore failed: {str(e)}")
            return False, str(e)

    def get_backup_details(self, backup_timestamp):
        """Get detailed information about a specific backup"""
        try:
            backup_path = os.path.join(self.backup_dir, f"backup_{backup_timestamp}")
            if not os.path.exists(backup_path):
                return None

            with open(os.path.join(backup_path, "backup_metadata.json"), "r") as f:
                metadata = json.load(f)

            # Add additional information
            metadata["backup_size"] = self._get_directory_size(backup_path)
            metadata["backup_path"] = backup_path
            return metadata

        except Exception as e:
            logging.error(f"Failed to get backup details: {str(e)}")
            return None

    def verify_backup_integrity(self, backup_timestamp):
        """Verify the integrity of a backup"""
        try:
            backup_path = os.path.join(self.backup_dir, f"backup_{backup_timestamp}")
            if not os.path.exists(backup_path):
                return False, "Backup not found"

            with open(os.path.join(backup_path, "backup_metadata.json"), "r") as f:
                metadata = json.load(f)

            total_files = len(metadata["stats"]["backed_up_items"])
            verified_files = 0
            corrupted_files = []

            for item in metadata["stats"]["backed_up_items"]:
                file_path = os.path.join(backup_path, item["path"])
                if os.path.exists(file_path):
                    current_hash = self._calculate_file_hash(file_path)
                    if current_hash == item["hash"]:
                        verified_files += 1
                    else:
                        corrupted_files.append(item["path"])

            if corrupted_files:
                return False, f"Backup integrity check failed. {len(corrupted_files)} files are corrupted."
            elif verified_files != total_files:
                return False, f"Backup integrity check failed. {total_files - verified_files} files are missing."
            else:
                return True, f"Backup integrity verified. All {total_files} files are intact."

        except Exception as e:
            logging.error(f"Backup verification failed: {str(e)}")
            return False, str(e)

    def _backup_database(self, src_file, dst_file):
        """Safely backup a database file"""
        try:
            # Create a connection to the source database
            src_conn = sqlite3.connect(src_file)
            
            # Create a backup of the database
            dst_conn = sqlite3.connect(dst_file)
            src_conn.backup(dst_conn)
            
            # Close connections
            src_conn.close()
            dst_conn.close()
            
        except Exception as e:
            logging.error(f"Database backup failed: {str(e)}")
            # If database backup fails, try simple file copy
            shutil.copy2(src_file, dst_file)

    def _calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_directory_size(self, directory):
        """Calculate total size of a directory in bytes"""
        total_size = 0
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

    def _matches_pattern(self, filename, pattern):
        """Check if a filename matches a glob pattern"""
        from fnmatch import fnmatch
        return fnmatch(filename, pattern) or fnmatch(os.path.join('*', filename), pattern)

    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            for backup_dir in os.listdir(self.backup_dir):
                if backup_dir.startswith("backup_"):
                    metadata_file = os.path.join(self.backup_dir, backup_dir, "backup_metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                            backups.append(metadata)
            return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logging.error(f"Failed to list backups: {str(e)}")
            return []
