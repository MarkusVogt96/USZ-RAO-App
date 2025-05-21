# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('offline_packages/tesseract/tesseract.exe', '.'),
        ('offline_packages/tesseract/*.dll', '.')
    ],
    datas=[
        ('offline_packages/tesseract/tessdata', 'tesseract/tessdata'),
        ('offline_packages/easyocr_models', 'easyocr_models'),
        ('assets', 'assets'),
        ('scripts', 'scripts')
    ],
    hiddenimports=[
        # Placeholder for future hidden imports
        'easyocr',
        'torch',
        'torchvision',
        'cv2', # opencv-python
        'skimage', # scikit-image
        'scipy',
        'PIL', # Pillow
        'numpy',
        'pytesseract',
        'pyautogui',
        'clipboard',
        'openpyxl',
        'cryptography',
        'pkg_resources.py2_warn', # Often needed to suppress warnings
        'fliesstexte' # Local script dependency
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/usz_logo_klein.ico'
)
