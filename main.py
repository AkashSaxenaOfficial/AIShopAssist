"""
AI Shop Assist - Main Entry Point

Combines both WebSocket and UI servers into a single application.
Provides a unified startup and shutdown process.

Author: AI Shop Assist Team
Version: 1.0.0
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import application components
from app import config
from app.server import websocket, ui

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    filename=config.LOG_FILE
)
logger = logging.getLogger(__name__)

class AIShopAssist:
    """Main application class combining WebSocket and UI servers"""
    
    def __init__(self):
        self.websocket_server = None
        self.app_server = None
        self.running = False
    
    def check_environment(self) -> bool:
        """Check environment variables and dependencies"""
        # Check API keys
        found_keys = [key for key, value in config.API_KEYS.items() if value]
        
        if found_keys:
            logger.info("✅ Found API keys:")
            for key in found_keys:
                logger.info(f"   • {key}")
        else:
            logger.warning("⚠️ No API keys found. The system will use mock responses.")
            logger.info("   Set API keys in .env file for full functionality")
        
        return True
    
    async def start_servers(self) -> bool:
        """Start both WebSocket and UI servers"""
        try:
            # Start WebSocket server
            self.websocket_server = websocket.WebSocketServer(
                host=config.WEBSOCKET_SERVER_HOST,
                port=config.WEBSOCKET_SERVER_PORT
            )
            if not await self.websocket_server.start():
                logger.error("❌ Failed to start WebSocket server")
                return False
            
            # Start UI server in a separate thread
            self.app_server = ui.AppServer(port=config.UI_SERVER_PORT)
            if not self.app_server.start():
                logger.error("❌ Failed to start UI server")
                await self.websocket_server.stop()
                return False
            
            self.running = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start servers: {e}")
            return False
    
    async def stop_servers(self) -> bool:
        """Stop both servers gracefully"""
        try:
            if self.websocket_server:
                await self.websocket_server.stop()
            
            # UI server will be stopped by the process
            self.running = False
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping servers: {e}")
            return False

async def main():
    """Main application entry point"""
    print("=" * 60)
    print(f"🚀 {config.APP_NAME} - Starting Application")
    print("=" * 60)
    
    # Create application instance
    app = AIShopAssist()
    
    # Check environment
    if not app.check_environment():
        print("❌ Environment check failed")
        return False
    
    print("\n📋 Startup Plan:")
    print(f"   1. Start WebSocket server (port {config.WEBSOCKET_SERVER_PORT})")
    print(f"   2. Start UI server (port {config.UI_SERVER_PORT})")
    print(f"   3. Open browser to http://{config.UI_SERVER_HOST}:{config.UI_SERVER_PORT}")
    
    # Start servers
    if not await app.start_servers():
        print("❌ Failed to start servers")
        return False
    
    print("\n🌟 Application started successfully!")
    print(f"📡 WebSocket server: ws://{config.WEBSOCKET_SERVER_HOST}:{config.WEBSOCKET_SERVER_PORT}")
    print(f"🌐 UI server: http://{config.UI_SERVER_HOST}:{config.UI_SERVER_PORT}")
    print("🔧 Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Keep application running
        while app.running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n📨 Keyboard interrupt received")
    finally:
        await app.stop_servers()
    
    return True

def run():
    """Run the application"""
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        success = asyncio.run(main())
        if not success:
            print("\n❌ Application failed to start")
            sys.exit(1)
        else:
            print("\n👋 Application stopped")
            
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run() 