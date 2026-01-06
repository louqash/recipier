#!/usr/bin/env python3
"""
Backend server entry point for Recipier.

This module provides a CLI command to start the FastAPI backend server.

Usage:
    recipier-backend [--port PORT] [--host HOST] [--reload]
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Start the Recipier backend API server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)",
    )
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload (production mode)")

    args = parser.parse_args()

    # Determine reload setting (default to True for development)
    reload = args.reload or not args.no_reload

    # Find project root (parent of recipier package)
    project_root = os.path.dirname(os.path.dirname(__file__))
    backend_dir = os.path.join(project_root, "backend")

    if not os.path.exists(backend_dir):
        print(f"✗ Error: Backend directory not found at {backend_dir}")
        sys.exit(1)

    # Change to project root so imports work correctly
    os.chdir(project_root)

    print("🚀 Starting Recipier Backend")
    print("=" * 50)
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {'enabled' if reload else 'disabled'}")
    print(f"   URL: http://{args.host}:{args.port}")
    print("=" * 50)

    # Import and run uvicorn from project root
    import uvicorn

    uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=reload)


if __name__ == "__main__":
    main()
