# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Building and Distribution
- **Run application**: `python main.py` or use `main.bat` (launches with pythonw.exe)
- **Build executable**: `pyinstaller main.spec` (creates standalone .exe with all dependencies)
- **Install dependencies**: `pip install -r requirements.txt`

### No Testing/Linting Framework
This project does not use formal testing or linting frameworks. Code validation is done through manual testing and the application's built-in functionality.

## Architecture Overview

### Core Application Structure
This is a PyQt6-based desktop application for radiation oncology at USZ with three main purposes:
1. **Knowledge Database**: Tumor entity navigation with SOPs and contouring instructions
2. **Clinical Automation**: GUI automation scripts for KISIM (hospital information system)
3. **Tumorboard Management**: Digital workflow for tumor board sessions

### Main Application Flow
- **Entry Point**: `main.py` - Contains license validation, update checks, and main window setup
- **Navigation**: Left menu with 5 tabs: Tumor navigator, Tumorboards, KISIM Scripts, Backoffice, Developer Area
- **Page Management**: Uses QStackedWidget for navigation between different functional areas

### Key Components

#### 1. Tumor Navigator (`pages/tumorgroup_pages/`)
- **TumorGroupPage**: Main entry point showing tumor group tiles
- **Specific Group Pages**: e.g., `NeuroonkologiePage`, `GynPage` - show entities within each group
- **EntityPage**: Shows SOPs and contouring info for specific tumor entities
- **PdfReaderPage**: Integrated PDF viewer for SOP documents

#### 2. KISIM Automation (`scripts/` + `pages/kisim_page.py`)
- **KisimPage**: Shows tiles for available automation scripts
- **CmdScriptsPage**: Executes scripts and shows real-time output
- **UNIVERSAL.py**: Core automation library with common functions
- **Individual Scripts**: Each script automates specific clinical workflows using PyAutoGUI
- **Screenshot Dependencies**: Scripts rely on images in `scripts/screenshots pyautogui/`

#### 3. Tumorboard System
- **TumorboardsPage**: Weekly overview of tumor boards
- **SpecificTumorboardPage**: Individual board management
- **ExcelViewerPage**: Display and edit tumor board patient lists
- **TumorboardSessionPage**: Live session management for patient discussions

#### 4. Backoffice System (`pages/backoffice_*.py`)
- **BackofficePage**: Administrative overview with task aggregation
- **Task Management**: Tracks billing, consultations, and administrative tasks
- **Excel Integration**: Specialized viewers for completed tumor boards

### Data Management

#### Patient Data Storage
- **Location**: `%USERPROFILE%/patdata/` (outside application directory)
- **Format**: JSON files with patient-specific data
- **Persistence**: Survives application updates and reinstalls
- **Access**: Via `UNIVERSAL.load_json()` and similar functions

#### Tumorboard Data
- **Primary Path**: `K:\RAO_Projekte\App\tumorboards\` (network drive)
- **Fallback Path**: `{user_home}/tumorboards/` (local backup)
- **Automatic Backup**: SQLite database backups before major operations
- **Export Consistency**: Maintains data integrity between network and local storage

### Important Development Patterns

#### GUI Automation Scripts
- All automation scripts use `pyautogui` for GUI interaction
- Screenshots stored in `scripts/screenshots pyautogui/{script_name}/`
- `UNIVERSAL.py` provides common functions for window management, OCR, and patient data
- Scripts handle KISIM navigation and data entry workflows

#### Page Navigation
- Uses breadcrumb system for navigation history
- Session protection prevents data loss during navigation
- Dynamic page creation with lazy loading for performance

#### PDF Integration
- Custom PDF viewer using PyMuPDF (fitz)
- SOP search functionality across all PDF documents
- Integration with entity pages for contextual document access

#### Database Integration
- SQLite database for tumorboard data aggregation
- Automatic backup system before data modifications
- Export/import functionality for Excel integration

### Security and Access Control
- Monthly license validation system with RSA signature verification
- Password-protected access to Backoffice and Developer areas
- No sensitive data stored in repository (patient data external)

### Build and Distribution
- PyInstaller spec includes offline packages (Tesseract, EasyOCR models)
- Executable includes all assets and scripts
- Automatic update system with network-based distribution
- Windows-specific optimizations (AppUserModelID, monitor detection)

## Key Files and Directories

- `main.py`: Application entry point with license validation and window setup
- `pages/`: All UI page classes organized by functionality
- `scripts/`: Clinical automation scripts and UNIVERSAL.py library
- `assets/sop/`: PDF documents organized by tumor group and entity
- `utils/`: Database management and utility functions
- `components/`: Reusable UI components (search widgets, etc.)
- `tumorboards/`: Local tumorboard data storage and templates
- `requirements.txt`: Python dependencies
- `main.spec`: PyInstaller build configuration

## Development Notes

- Patient data is stored externally in `%USERPROFILE%/patdata/` for persistence
- Network paths use `K:\RAO_Projekte\App\` as primary with local fallbacks
- GUI automation requires screenshot maintenance when UI changes
- Application supports dual monitor setups with automatic positioning
- WebEngine components require special initialization workarounds