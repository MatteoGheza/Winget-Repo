#!/bin/bash
set -e

# Winget-Repo Docker Entrypoint Script

echo "Starting Winget-Repo Docker Container..."

# Create data directories if they don't exist
mkdir -p /app/data/Files
mkdir -p /app/data/static/images/Logos  
mkdir -p /app/data/Winget_DB/Public
mkdir -p /app/data/Modules/Database
mkdir -p /app/logs
mkdir -p /app/SSL

# Initialize database directory structure
DB_PATH="${APP_DATABASE_PATH:-/app/data/Modules/Database/Database.db}"
DB_DIR="$(dirname "$DB_PATH")"
mkdir -p "$DB_DIR"

# Copy initial database if it doesn't exist in the volume
if [ ! -f "$DB_PATH" ]; then
    echo "Initializing database from template..."
    if [ -f "/app/Modules/Database/Database.db" ]; then
        echo "Source database size: $(stat -c%s "/app/Modules/Database/Database.db" 2>/dev/null || echo "ERROR")"
        cp "/app/Modules/Database/Database.db" "$DB_PATH"
        chown appuser:appuser "$DB_PATH"
        echo "Database initialized successfully at: $DB_PATH"
        echo "Copied database size: $(stat -c%s "$DB_PATH" 2>/dev/null || echo "ERROR")"
    else
        echo "ERROR: No template database found at /app/Modules/Database/Database.db"
        echo "Available files in /app/Modules/Database/:"
        ls -la /app/Modules/Database/ || echo "Directory doesn't exist"
        exit 1
    fi
else
    echo "Database already exists at: $DB_PATH"
    echo "Existing database size: $(stat -c%s "$DB_PATH" 2>/dev/null || echo "ERROR")"
    # If existing database is empty, replace it
    if [ "$(stat -c%s "$DB_PATH" 2>/dev/null || echo "0")" = "0" ]; then
        echo "Existing database is empty, replacing with template..."
        if [ -f "/app/Modules/Database/Database.db" ]; then
            echo "Source database size: $(stat -c%s "/app/Modules/Database/Database.db" 2>/dev/null || echo "ERROR")"
            cp "/app/Modules/Database/Database.db" "$DB_PATH"
            chown appuser:appuser "$DB_PATH"
            echo "Database replaced successfully"
        fi
    fi
fi

# Generate SSL certificates for dev mode if SSL is enabled
if [ "${WINGET_SSL_ENABLED:-false}" = "true" ] || [ "${WINGET_DEV_MODE:-false}" = "true" ]; then
    if [ ! -f /app/SSL/cert.pem ] || [ ! -f /app/SSL/key.pem ]; then
        echo "Generating self-signed SSL certificates for development..."
        openssl req -x509 -newkey rsa:4096 -keyout /app/SSL/key.pem -out /app/SSL/cert.pem \
            -days 365 -nodes -subj "/C=US/ST=Docker/L=Container/O=Winget-Repo/CN=localhost"
        chmod 600 /app/SSL/key.pem /app/SSL/cert.pem
    fi
fi

# Create .env file from environment variables if Keycloak is enabled
if [ "${KEYCLOAK_ENABLED:-false}" = "true" ]; then
    echo "Configuring Keycloak from environment variables..."
    cat > /app/.env << EOF
KEYCLOAK_ENABLED=${KEYCLOAK_ENABLED}
KEYCLOAK_SERVER_URL=${KEYCLOAK_SERVER_URL}
KEYCLOAK_REALM_NAME=${KEYCLOAK_REALM_NAME}
KEYCLOAK_CLIENT_ID=${KEYCLOAK_CLIENT_ID}
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}
KEYCLOAK_REDIRECT_URI=${KEYCLOAK_REDIRECT_URI}
KEYCLOAK_POST_LOGOUT_REDIRECT_URI=${KEYCLOAK_POST_LOGOUT_REDIRECT_URI}
KEYCLOAK_DEFAULT_GROUP=${KEYCLOAK_DEFAULT_GROUP}
EOF
fi

# Set proper permissions
chown -R appuser:appuser /app/data /app/logs /app/SSL 2>/dev/null || true

echo "Winget-Repo Docker setup complete."
echo "Database path: $DB_PATH"
echo "Database exists: $([ -f "$DB_PATH" ] && echo "YES" || echo "NO")"
echo "Database file size: $(stat -c%s "$DB_PATH" 2>/dev/null || echo "ERROR")"
echo "Starting application as appuser with: $@"

# Execute the command as appuser
exec su appuser -c "cd /app && $*"
