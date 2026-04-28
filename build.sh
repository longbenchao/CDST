#!/bin/bash
# CDST Cross-Platform Build Script
# This script helps build CDST for Windows and macOS

set -e

echo "========================================="
echo "CDST Cross-Platform Build Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check current platform
PLATFORM=$(uname -s)
echo -e "${YELLOW}Current platform: $PLATFORM${NC}"
echo ""

# Function to build for current platform
build_current() {
    local app_name="CDST"
    local output_dir="dist"
    
    echo -e "${GREEN}Building for current platform ($PLATFORM)...${NC}"
    
    # Clean previous builds
    rm -rf build/ dist/ *.spec 2>/dev/null || true
    
    # Common PyInstaller arguments
    local common_args="--name $app_name --windowed --onefile"
    local hidden_imports="--hidden-import=tkinter --hidden-import=pandas --hidden-import=numpy --hidden-import=Bio --hidden-import=networkx --hidden-import=scipy --hidden-import=matplotlib --hidden-import=PIL --hidden-import=customtkinter --hidden-import=psutil --hidden-import=cdst --hidden-import=cdst.core --hidden-import=cdst.cli --hidden-import=cdst.gui --hidden-import=cdst.gui.main_window --hidden-import=cdst.gui.utils --hidden-import=cdst.gui.utils.config --hidden-import=cdst.gui.utils.logger --hidden-import=cdst.gui.utils.worker --hidden-import=cdst.gui.tabs --hidden-import=cdst.gui.tabs.quick_analysis --hidden-import=cdst.gui.tabs.step_by_step --hidden-import=cdst.gui.tabs.database_manager --hidden-import=cdst.gui.tabs.results_viewer --hidden-import=cdst.gui.tabs.settings --hidden-import=cdst.visualization"
    
    # Run PyInstaller
    if [[ "$PLATFORM" == "Darwin" ]]; then
        # macOS build
        python -m PyInstaller \
            $common_args \
            --add-data "src/cdst:cdst" \
            $hidden_imports \
            --osx-bundle-identifier=com.cdst.app \
            cdst_gui_new.py
        
        echo -e "${GREEN}macOS app created in dist/$app_name.app${NC}"
        
    elif [[ "$PLATFORM" == "Linux" ]]; then
        # Linux build
        python -m PyInstaller \
            $common_args \
            --add-data "src/cdst:cdst" \
            $hidden_imports \
            cdst_gui_new.py
        
        echo -e "${GREEN}Linux executable created in dist/$app_name${NC}"
        
    elif [[ "$PLATFORM" == MINGW* ]] || [[ "$PLATFORM" == CYGWIN* ]] || [[ "$PLATFORM" == MSYS* ]]; then
        # Windows build
        python -m PyInstaller \
            $common_args \
            --add-data "src/cdst;cdst" \
            $hidden_imports \
            cdst_gui_new.py
        
        echo -e "${GREEN}Windows executable created in dist/$app_name.exe${NC}"
    fi
}

# Function to show cross-platform build instructions
show_cross_platform_instructions() {
    echo -e "${YELLOW}=========================================${NC}"
    echo -e "${YELLOW}Cross-Platform Build Instructions${NC}"
    echo -e "${YELLOW}=========================================${NC}"
    echo ""
    echo "Since you're on $PLATFORM, you cannot directly build for other platforms."
    echo "Here are your options:"
    echo ""
    echo -e "${GREEN}Option 1: Use GitHub Actions (Recommended)${NC}"
    echo "  The repository includes a GitHub Actions workflow (.github/workflows/build.yml)"
    echo "  that automatically builds for Windows, macOS, and Linux on each release."
    echo ""
    echo "  Steps:"
    echo "  1. Commit and push your code to GitHub"
    echo "  2. Create a release tag: git tag v1.0.0 && git push origin v1.0.0"
    echo "  3. GitHub Actions will automatically build all platforms"
    echo "  4. Download the artifacts from the release page"
    echo ""
    echo -e "${GREEN}Option 2: Use CI/CD Services${NC}"
    echo "  - Azure Pipelines"
    echo "  - CircleCI"
    echo "  - GitLab CI"
    echo ""
    echo -e "${GREEN}Option 3: Manual Build on Each Platform${NC}"
    echo "  For Windows:"
    echo "    1. Set up a Windows environment (VM or physical machine)"
    echo "    2. Install Python and dependencies"
    echo "    3. Run: bash build.sh"
    echo ""
    echo "  For macOS:"
    echo "    1. Set up a macOS environment (VM or physical machine)"
    echo "    2. Install Python and dependencies"
    echo "    3. Run: bash build.sh"
    echo ""
    echo -e "${GREEN}Option 4: Use Cross-Compilation Tools${NC}"
    echo "  - For Windows from Linux: Use Wine + PyInstaller (limited support)"
    echo "  - For macOS from Linux: Not officially supported, use VM or CI"
    echo ""
}

# Main execution
case "${1:-}" in
    --current)
        build_current
        ;;
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --current    Build only for the current platform"
        echo "  --info       Show cross-platform build instructions"
        echo "  --help, -h   Show this help message"
        echo ""
        echo "If no options are provided, shows cross-platform build instructions."
        ;;
    --info|"")
        show_cross_platform_instructions
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo "Use --help for usage information."
        exit 1
        ;;
esac
