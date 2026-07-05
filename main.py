#!/usr/bin/env python3
"""
JARVIS - Personal Offline AI Assistant
Main Application Entry Point

A futuristic AI assistant inspired by Iron Man's JARVIS
with voice commands, AI responses, and a sleek HUD interface.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from ui.jarvis_app import JARVISApplication
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    logger.info("=" * 60)
    logger.info("🤖 JARVIS APPLICATION STARTING...")
    logger.info("=" * 60)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("JARVIS")
        app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        jarvis = JARVISApplication()
        jarvis.show()
        
        logger.info("JARVIS is ready. Entering main event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
