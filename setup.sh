#!/bin/bash
echo "Installing dependencies..."
pip install requests aiohttp 2>/dev/null || pip3 install requests aiohttp
echo "Done! Run with: python3 myjio.py"
