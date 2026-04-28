#!/usr/bin/env python3
"""
CDST GUI Application - Desktop interface for CoDing Sequence Typer

This is the main entry point for the CDST GUI application.
"""

import os
import sys

_app_config_dir = os.path.join(os.path.expanduser("~"), ".cdst")
_mpl_config_dir = os.path.join(_app_config_dir, "matplotlib")
_cache_dir = os.path.join(_app_config_dir, "cache")
try:
    os.makedirs(_mpl_config_dir, exist_ok=True)
    os.makedirs(_cache_dir, exist_ok=True)
    _test_path = os.path.join(_mpl_config_dir, ".write_test")
    with open(_test_path, "w") as _test_file:
        _test_file.write("ok")
    os.remove(_test_path)
    os.environ.setdefault("MPLCONFIGDIR", _mpl_config_dir)
    os.environ.setdefault("XDG_CACHE_HOME", _cache_dir)
except Exception:
    import tempfile
    _tmp_cache_dir = os.path.join(tempfile.gettempdir(), "cdst-cache")
    os.makedirs(os.path.join(_tmp_cache_dir, "matplotlib"), exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", os.path.join(_tmp_cache_dir, "matplotlib"))
    os.environ.setdefault("XDG_CACHE_HOME", _tmp_cache_dir)

# Add src directory to path for local development
_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, 'src')

# Handle PyInstaller bundled resources
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = sys._MEIPASS
    # Add the bundled cdst package to path
    cdst_bundle_path = os.path.join(bundle_dir, 'cdst')
    if os.path.exists(cdst_bundle_path):
        sys.path.insert(0, bundle_dir)
    # Also try looking in the same directory as the executable
    exe_dir = os.path.dirname(sys.executable)
    cdst_exe_path = os.path.join(exe_dir, 'cdst')
    if os.path.exists(cdst_exe_path) and exe_dir not in sys.path:
        sys.path.insert(0, exe_dir)
else:
    # Running from source - add src directory to path
    if os.path.exists(_src_dir) and _src_dir not in sys.path:
        sys.path.insert(0, _src_dir)

# Import and run the GUI
try:
    from cdst.gui.main_window import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing CDST GUI: {e}")
    print(f"Script directory: {_script_dir}")
    print(f"Src directory: {_src_dir}")
    print(f"Python path: {sys.path}")
    
    # List available directories
    if os.path.exists(_src_dir):
        print(f"\nContents of src directory: {os.listdir(_src_dir)}")
        cdst_path = os.path.join(_src_dir, 'cdst')
        if os.path.exists(cdst_path):
            print(f"Contents of cdst directory: {os.listdir(cdst_path)}")
            gui_path = os.path.join(cdst_path, 'gui')
            if os.path.exists(gui_path):
                print(f"Contents of gui directory: {os.listdir(gui_path)}")
    
    sys.exit(1)
