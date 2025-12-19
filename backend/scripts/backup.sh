#!/bin/bash
# PostgreSQL Backup Script
# Runs daily backups and removes old backups

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lifeai_backup_$TIMESTAMP.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "Starting backup at $(date)"
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
  -h postgres \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --format=custom \
  --compress=9 \
  --file="$BACKUP_FILE"

echo "Backup completed: $BACKUP_FILE"

# Remove old backups (keep last N days)
find "$BACKUP_DIR" -name "lifeai_backup_*.sql.gz" -type f -mtime +${BACKUP_KEEP_DAYS:-7} -delete

echo "Old backups removed (keeping last ${BACKUP_KEEP_DAYS:-7} days)"

# Sleep for 24 hours before next backup
sleep 86400

# Run script again (infinite loop for daily backups)
exec /backup.sh
