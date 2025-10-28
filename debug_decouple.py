#!/usr/bin/env python
"""Debug script to test decouple import"""

import sys
import os

print("=== Decouple Import Debug ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\n--- Testing decouple import ---")

# Test 1: Try importing decouple module
try:
    import decouple
    print(f"✓ Successfully imported decouple module")
    print(f"  Module location: {decouple.__file__}")
    print(f"  Module type: {type(decouple)}")
    print(f"  Module attributes: {[attr for attr in dir(decouple) if not attr.startswith('_')]}")
except ImportError as e:
    print(f"✗ Failed to import decouple: {e}")

# Test 2: Try importing config from decouple
try:
    from decouple import config
    print(f"✓ Successfully imported config from decouple")
    print(f"  Config type: {type(config)}")
except ImportError as e:
    print(f"✗ Failed to import config from decouple: {e}")

# Test 3: Check if there's a local decouple.py file
current_dir = os.getcwd()
for root, dirs, files in os.walk(current_dir):
    if 'decouple.py' in files:
        print(f"⚠️  Found decouple.py file at: {os.path.join(root, 'decouple.py')}")

# Test 4: Check pip installed packages
print("\n--- Checking pip packages ---")
try:
    import subprocess
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
    if 'decouple' in result.stdout.lower():
        print("✓ python-decouple found in pip packages")
        for line in result.stdout.split('\n'):
            if 'decouple' in line.lower():
                print(f"  {line}")
    else:
        print("✗ python-decouple not found in pip packages")
        print("Available packages containing 'decouple':")
        for line in result.stdout.split('\n'):
            if 'decouple' in line.lower():
                print(f"  {line}")
except Exception as e:
    print(f"Could not check pip packages: {e}")

print("\n=== End Debug ===")