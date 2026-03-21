# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cdst_gui.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/cdst', 'cdst'),
    ],
    hiddenimports=[
        'customtkinter',
        'pandas',
        'numpy',
        'Bio',
        'Bio.SeqIO',
        'networkx',
        'scipy',
        'scipy.cluster',
        'scipy.cluster.hierarchy',
        'PIL',
        'PIL.Image',
        'packaging.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'matplotlib',
        'jinja2',
        'gi',
        'IPython',
        'notebook',
        'nbconvert',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CDST',
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
)
