#!/usr/bin/env python3
"""
Frontend development server entry point for Recipier.

This module provides a CLI command to start the React/Vite frontend.

Usage:
    recipier-frontend [dev|build|preview]
"""

import argparse
import os
import sys
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description='Manage the Recipier frontend'
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='dev',
        choices=['dev', 'build', 'preview'],
        help='Command to run: dev (start dev server), build (production build), preview (preview build)'
    )

    args = parser.parse_args()

    # Find frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    if not os.path.exists(frontend_dir):
        print(f"✗ Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)

    # Check if npm is available
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Error: npm is not installed or not in PATH")
        print("   Please install Node.js and npm: https://nodejs.org/")
        sys.exit(1)

    # Check if node_modules exists
    node_modules = os.path.join(frontend_dir, 'node_modules')
    if not os.path.exists(node_modules):
        print("📦 Installing frontend dependencies...")
        result = subprocess.run(['npm', 'install'], cwd=frontend_dir)
        if result.returncode != 0:
            print("✗ Error: Failed to install dependencies")
            sys.exit(1)

    print("🎨 Starting Recipier Frontend")
    print("=" * 50)
    print(f"   Command: npm run {args.command}")
    print(f"   Directory: {frontend_dir}")
    if args.command == 'dev':
        print(f"   URL: http://localhost:5173 (default Vite port)")
    print("=" * 50)

    # Run the npm command
    result = subprocess.run(['npm', 'run', args.command], cwd=frontend_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
