# run.py
import uvicorn
import sys
import os

def setup_vendor_paths():
    """Add vendor packages to Python path."""
    backend_dir = os.path.dirname(__file__)
    vendor_dir = os.path.join(backend_dir, 'vendor')

    # Add neutts-air to path
    neutts_path = os.path.join(vendor_dir, 'neutts-air')
    if os.path.exists(neutts_path) and neutts_path not in sys.path:
        sys.path.insert(0, neutts_path)
        print(f"✅ Added neutts-air to Python path: {neutts_path}")
    else:
        print(f"⚠️  neutts-air not found at: {neutts_path}")


if __name__ == "__main__":
    setup_vendor_paths()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
