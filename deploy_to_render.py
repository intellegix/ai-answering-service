#!/usr/bin/env python3
"""
Render.com Deployment Script for AI Answering Service
Uses Render API to deploy all services with autodeploy from GitHub
Austin Kidwell | ASR Inc / Intellegix
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional

class RenderDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.services = {}

    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make a request to the Render API."""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            print(f"Response: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
            raise

    def get_github_repo_info(self) -> tuple[str, str]:
        """Get GitHub repository information."""
        print("\n📝 GitHub Repository Information")

        # Try to get from git remote
        try:
            import subprocess
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                repo_url = result.stdout.strip()
                if "github.com" in repo_url:
                    # Parse owner/repo from URL
                    if repo_url.endswith(".git"):
                        repo_url = repo_url[:-4]

                    if "github.com/" in repo_url:
                        parts = repo_url.split("github.com/")[1].split("/")
                        if len(parts) >= 2:
                            return parts[0], parts[1]
        except:
            pass

        # Manual input
        owner = input("Enter GitHub username/organization: ").strip()
        repo = input("Enter repository name [ai-answering-service]: ").strip() or "ai-answering-service"

        return owner, repo

    def create_database(self, name: str = "ai-answering-db") -> str:
        """Create PostgreSQL database."""
        print(f"\n🗄️ Creating PostgreSQL database: {name}")

        data = {
            "name": name,
            "databaseName": "ai_answering_service",
            "user": "ai_admin",
            "region": "oregon",
            "plan": "starter"  # Free tier
        }

        try:
            result = self.make_request("POST", "/postgres", data)
            database_id = result["id"]
            self.services["database"] = {
                "id": database_id,
                "name": name,
                "connection_string": result.get("connectionString", "")
            }

            print(f"✅ Database created successfully!")
            print(f"   ID: {database_id}")

            # Wait for database to be ready
            print("⏳ Waiting for database to initialize...")
            self.wait_for_service_ready(database_id, service_type="database")

            return database_id

        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            raise

    def create_backend_service(self, owner: str, repo: str, database_id: str) -> str:
        """Create Flask backend service."""
        print(f"\n🖥️ Creating Flask Backend Service")

        data = {
            "name": "ai-secretary-backend",
            "ownerId": owner,
            "repo": f"https://github.com/{owner}/{repo}",
            "branch": "main",
            "buildCommand": "cd backend && pip install -r requirements.txt",
            "startCommand": "cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app --timeout 120",
            "plan": "starter",  # $7/month
            "region": "oregon",
            "env": "python",
            "healthCheckPath": "/health",
            "autoDeploy": True,
            "serviceDetails": {
                "env": [
                    {"key": "FLASK_ENV", "value": "production"},
                    {"key": "LOG_LEVEL", "value": "INFO"},
                    {"key": "PORT", "value": "10000"}
                ],
                "envVars": [
                    {"key": "DATABASE_URL", "fromDatabase": {"name": "ai-answering-db", "property": "connectionString"}},
                    {"key": "ANTHROPIC_API_KEY", "value": ""},  # Will be set manually
                    {"key": "OPENAI_API_KEY", "value": ""},
                    {"key": "TWILIO_ACCOUNT_SID", "value": ""},
                    {"key": "TWILIO_AUTH_TOKEN", "value": ""},
                    {"key": "TWILIO_PHONE_NUMBER", "value": ""},
                    {"key": "PERPLEXITY_API_KEY", "value": ""}
                ]
            }
        }

        try:
            result = self.make_request("POST", "/services", data)
            service_id = result["id"]
            service_url = result["service"]["serviceDetails"]["url"]

            self.services["backend"] = {
                "id": service_id,
                "name": "ai-secretary-backend",
                "url": service_url
            }

            print(f"✅ Backend service created successfully!")
            print(f"   ID: {service_id}")
            print(f"   URL: {service_url}")

            return service_id

        except Exception as e:
            print(f"❌ Failed to create backend service: {e}")
            raise

    def create_conversation_relay_service(self, owner: str, repo: str) -> str:
        """Create Node.js conversation relay service."""
        print(f"\n🗣️ Creating Conversation Relay Service")

        data = {
            "name": "ai-conversation-relay",
            "ownerId": owner,
            "repo": f"https://github.com/{owner}/{repo}",
            "branch": "main",
            "buildCommand": "cd backend && npm install",
            "startCommand": "cd backend && node conversation_relay.js",
            "plan": "starter",  # $7/month
            "region": "oregon",
            "env": "node",
            "healthCheckPath": "/relay/health",
            "autoDeploy": True,
            "serviceDetails": {
                "env": [
                    {"key": "NODE_ENV", "value": "production"},
                    {"key": "RELAY_PORT", "value": "10000"}
                ],
                "envVars": [
                    {"key": "ANTHROPIC_API_KEY", "value": ""},  # Will be set manually
                    {"key": "OPENAI_API_KEY", "value": ""}
                ]
            }
        }

        try:
            result = self.make_request("POST", "/services", data)
            service_id = result["id"]
            service_url = result["service"]["serviceDetails"]["url"]

            self.services["relay"] = {
                "id": service_id,
                "name": "ai-conversation-relay",
                "url": service_url
            }

            print(f"✅ Conversation relay service created successfully!")
            print(f"   ID: {service_id}")
            print(f"   URL: {service_url}")

            return service_id

        except Exception as e:
            print(f"❌ Failed to create conversation relay service: {e}")
            raise

    def create_frontend_service(self, owner: str, repo: str, backend_url: str) -> str:
        """Create React frontend static site."""
        print(f"\n⚛️ Creating React Frontend Service")

        data = {
            "name": "ai-secretary-frontend",
            "ownerId": owner,
            "repo": f"https://github.com/{owner}/{repo}",
            "branch": "main",
            "buildCommand": "cd frontend && npm install && npm run build",
            "staticPublishPath": "./frontend/build",
            "region": "oregon",
            "autoDeploy": True,
            "serviceDetails": {
                "buildFilter": {
                    "paths": ["frontend/**"],
                    "ignoredPaths": ["backend/**"]
                },
                "headers": [
                    {"path": "/*", "name": "X-Frame-Options", "value": "DENY"},
                    {"path": "/*", "name": "X-Content-Type-Options", "value": "nosniff"},
                    {"path": "/*", "name": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                    {"path": "/static/*", "name": "Cache-Control", "value": "public, max-age=31536000, immutable"}
                ],
                "routes": [
                    {"type": "rewrite", "source": "/*", "destination": "/index.html"}
                ],
                "env": [
                    {"key": "REACT_APP_API_URL", "value": backend_url},
                    {"key": "NODE_ENV", "value": "production"}
                ]
            }
        }

        try:
            result = self.make_request("POST", "/static-sites", data)
            service_id = result["id"]
            service_url = result["staticSite"]["url"]

            self.services["frontend"] = {
                "id": service_id,
                "name": "ai-secretary-frontend",
                "url": service_url
            }

            print(f"✅ Frontend service created successfully!")
            print(f"   ID: {service_id}")
            print(f"   URL: {service_url}")

            return service_id

        except Exception as e:
            print(f"❌ Failed to create frontend service: {e}")
            raise

    def wait_for_service_ready(self, service_id: str, service_type: str = "service", timeout: int = 300):
        """Wait for service to be ready."""
        print(f"⏳ Waiting for {service_type} to be ready...")

        endpoint = f"/{service_type}s/{service_id}" if service_type == "database" else f"/services/{service_id}"

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = self.make_request("GET", endpoint)
                status = result.get("status", "unknown")

                if status in ["available", "running", "live"]:
                    print(f"✅ {service_type.capitalize()} is ready!")
                    return True

                print(f"   Status: {status}...")
                time.sleep(10)

            except Exception as e:
                print(f"   Checking status... ({str(e)[:50]})")
                time.sleep(10)

        print(f"⚠️ Timeout waiting for {service_type} to be ready")
        return False

    def set_environment_variables(self, service_id: str, env_vars: Dict[str, str]):
        """Set environment variables for a service."""
        print(f"🔧 Setting environment variables...")

        for key, value in env_vars.items():
            if value:  # Only set non-empty values
                try:
                    data = {"key": key, "value": value}
                    self.make_request("POST", f"/services/{service_id}/env-vars", data)
                    print(f"   ✅ Set {key}")
                except Exception as e:
                    print(f"   ❌ Failed to set {key}: {e}")

    def get_api_keys_from_user(self) -> Dict[str, str]:
        """Get API keys from user input."""
        print(f"\n🔑 API Keys Configuration")
        print("Please enter your API keys (leave blank to set later in Render dashboard):")

        api_keys = {}

        # Anthropic API Key
        anthropic_key = input("Anthropic API Key (sk-ant-...): ").strip()
        if anthropic_key:
            api_keys["ANTHROPIC_API_KEY"] = anthropic_key

        # OpenAI API Key
        openai_key = input("OpenAI API Key (sk-...): ").strip()
        if openai_key:
            api_keys["OPENAI_API_KEY"] = openai_key

        # Twilio credentials
        twilio_sid = input("Twilio Account SID (AC...): ").strip()
        if twilio_sid:
            api_keys["TWILIO_ACCOUNT_SID"] = twilio_sid

        twilio_token = input("Twilio Auth Token: ").strip()
        if twilio_token:
            api_keys["TWILIO_AUTH_TOKEN"] = twilio_token

        twilio_phone = input("Twilio Phone Number (+1...): ").strip()
        if twilio_phone:
            api_keys["TWILIO_PHONE_NUMBER"] = twilio_phone

        # Optional Perplexity API Key
        perplexity_key = input("Perplexity API Key (optional, ppl-...): ").strip()
        if perplexity_key:
            api_keys["PERPLEXITY_API_KEY"] = perplexity_key

        return api_keys

    def deploy_all_services(self):
        """Deploy all services for AI Answering Service."""
        print("🚀 AI Answering Service - Render Deployment")
        print("=" * 50)

        try:
            # Get GitHub repository info
            owner, repo = self.get_github_repo_info()
            print(f"📦 Repository: {owner}/{repo}")

            # Create database
            database_id = self.create_database()

            # Create backend service
            backend_id = self.create_backend_service(owner, repo, database_id)
            backend_url = self.services["backend"]["url"]

            # Create conversation relay service
            relay_id = self.create_conversation_relay_service(owner, repo)

            # Create frontend service
            frontend_id = self.create_frontend_service(owner, repo, backend_url)

            # Get API keys
            api_keys = self.get_api_keys_from_user()

            # Set environment variables for backend
            if api_keys:
                print(f"\n🔧 Configuring Backend Environment Variables")
                self.set_environment_variables(backend_id, api_keys)

                # Set environment variables for conversation relay
                print(f"\n🔧 Configuring Relay Environment Variables")
                relay_env = {
                    "ANTHROPIC_API_KEY": api_keys.get("ANTHROPIC_API_KEY", ""),
                    "OPENAI_API_KEY": api_keys.get("OPENAI_API_KEY", "")
                }
                self.set_environment_variables(relay_id, relay_env)

            # Display deployment summary
            self.print_deployment_summary()

            # Save deployment info
            self.save_deployment_info()

            return True

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False

    def print_deployment_summary(self):
        """Print deployment summary with URLs and next steps."""
        print(f"\n🎉 Deployment Complete!")
        print("=" * 50)

        print(f"📊 Services Created:")
        for service_type, info in self.services.items():
            print(f"   {service_type.capitalize()}: {info['name']}")
            if 'url' in info:
                print(f"   URL: {info['url']}")
            print(f"   ID: {info['id']}\n")

        print(f"🔗 Service URLs:")
        if 'backend' in self.services:
            print(f"   Backend API: {self.services['backend']['url']}")
            print(f"   Health Check: {self.services['backend']['url']}/health")

        if 'relay' in self.services:
            print(f"   Conversation Relay: {self.services['relay']['url']}")
            print(f"   Health Check: {self.services['relay']['url']}/relay/health")

        if 'frontend' in self.services:
            print(f"   Dashboard: {self.services['frontend']['url']}")

        print(f"\n📋 Next Steps:")
        print("1. ✅ Services are deploying automatically from GitHub")
        print("2. 🔑 Complete API key configuration in Render dashboard if needed")
        print("3. 📞 Configure Twilio webhooks:")

        if 'backend' in self.services:
            backend_url = self.services['backend']['url']
            print(f"   Incoming Call: {backend_url}/incoming-call")
            print(f"   Call Ended: {backend_url}/call-ended")

        print("4. 📱 Test your AI answering service!")
        print("5. 📈 Monitor services in Render dashboard")

    def save_deployment_info(self):
        """Save deployment information to a file."""
        deployment_info = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "services": self.services,
            "render_dashboard": "https://dashboard.render.com/",
            "status": "deployed"
        }

        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)

        print(f"\n💾 Deployment info saved to deployment_info.json")

def load_render_api_key() -> str:
    """Load Render API key from file or environment."""

    # Try environment variable first
    api_key = os.environ.get("RENDER_API_KEY")
    if api_key:
        return api_key

    # Try loading from the API key file
    api_key_file = Path("C:/Users/AustinKidwell/ASR Dropbox/Austin Kidwell/02.02_ApiKeys/Render/render api.txt")
    if api_key_file.exists():
        try:
            with open(api_key_file, 'r') as f:
                content = f.read().strip()
                # Extract the API key from "render api = key" format
                if "=" in content:
                    api_key = content.split("=")[1].strip()
                    return api_key
                return content
        except Exception as e:
            print(f"❌ Error reading API key file: {e}")

    # Manual input as fallback
    print("🔑 Render API Key not found in environment or file")
    print("You can get your API key from: https://dashboard.render.com/account/keys")
    api_key = input("Enter your Render API key: ").strip()

    return api_key

def verify_project_structure() -> bool:
    """Verify all required files are present."""
    required_files = [
        "backend/app.py",
        "backend/conversation_relay.js",
        "backend/requirements.txt",
        "backend/package.json",
        "frontend/src/App.jsx",
        "frontend/package.json",
        "README.md"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False

    return True

def main():
    """Main deployment function."""

    print("🚀 AI Answering Service - Render Deployment")
    print("Austin Kidwell | ASR Inc / Intellegix")
    print("=" * 50)

    # Verify project structure
    if not verify_project_structure():
        print("\n❌ Please ensure you're running this script from the project root directory.")
        sys.exit(1)

    # Load API key
    api_key = load_render_api_key()
    if not api_key:
        print("❌ Render API key is required for deployment.")
        sys.exit(1)

    print("✅ Render API key loaded successfully")

    # Create deployer and run deployment
    deployer = RenderDeployer(api_key)

    if deployer.deploy_all_services():
        print(f"\n🎉 AI Answering Service deployed successfully!")
        print("Check your Render dashboard for service status and logs.")
    else:
        print(f"\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()