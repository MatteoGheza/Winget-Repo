import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variable support with fallback to default paths
# This allows Docker and other deployment scenarios to override paths via env vars

# Default paths (maintaining backward compatibility)
_default_base_path = sys.path[0]

# Path configurations with environment variable support
# Use os.path.join for cross-platform compatibility
PATH_LOGOS = os.getenv('LOGOS_PATH', os.path.join(_default_base_path, "static", "images", "Logos"))
PATH_FILES = os.getenv('FILES_PATH', os.path.join(_default_base_path, "Files"))
PATH_DATABASE = os.getenv('APP_DATABASE_PATH', os.path.join(_default_base_path, "Modules", "Database", "Database.db"))
URL_PACKAGE_DOWNLOAD = os.getenv('URL_PACKAGE_DOWNLOAD', "DEFAULT")

PATH_WINGET_REPOSITORY = os.getenv('WINGET_REPOSITORY_PATH', os.path.join(_default_base_path, "Winget_DB"))
PATH_WINGET_REPOSITORY_DB = os.path.join(PATH_WINGET_REPOSITORY, "Public", "index.db")
URL_WINGET_REPOSITORY = os.getenv('URL_WINGET_REPOSITORY', "https://cdn.winget.microsoft.com/cache/")

# Keycloak Configuration
KEYCLOAK_ENABLED = os.getenv('KEYCLOAK_ENABLED', 'false').lower() == 'true'
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'http://localhost:8080')
KEYCLOAK_REALM_NAME = os.getenv('KEYCLOAK_REALM_NAME', 'winget-repo')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'winget-repo-client')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', '')
KEYCLOAK_REDIRECT_URI = os.getenv('KEYCLOAK_REDIRECT_URI', 'http://localhost:5000/keycloak/callback')
KEYCLOAK_POST_LOGOUT_REDIRECT_URI = os.getenv('KEYCLOAK_POST_LOGOUT_REDIRECT_URI', 'http://localhost:5000/')
KEYCLOAK_DEFAULT_GROUP = os.getenv('KEYCLOAK_DEFAULT_GROUP', '')  # Default admin group
