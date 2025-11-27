"""
Entry point for the Cricket Commentary Agent System.

This file provides a simple entry point to run the CLI.
For programmatic use, import from src.cli.main instead.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
