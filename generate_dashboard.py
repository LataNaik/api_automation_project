#!/usr/bin/env python3
"""
Standalone script to generate the interactive test dashboard.
Run this script after test execution to create/update the dashboard.

Usage:
    python generate_dashboard.py
"""

from utils.dashboard_generator import generate_dashboard

if __name__ == "__main__":
    print("="*60)
    print("  Interactive Test Dashboard Generator")
    print("="*60)
    print()

    try:
        dashboard_path = generate_dashboard()
        print()
        print("="*60)
        print("✅ Success! Dashboard generated successfully.")
        print("="*60)
        print()
        print(f"📊 Open in browser: file://{dashboard_path}")
        print()
    except Exception as e:
        print()
        print("="*60)
        print("❌ Error generating dashboard")
        print("="*60)
        print(f"Error: {e}")
