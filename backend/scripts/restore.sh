#!/bin/bash
# PostgreSQL Restore Script
# Usage: ./restore.sh <backup_file>

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file>"
  echo "Example: $0 /backups/lifeai_backup_20231219_120000.sql.gz"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring from backup: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

# Restore backup
PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
  -h postgres \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --clean \
  --if-exists \
  "$BACKUP_FILE"

echo "Restore completed successfully"
