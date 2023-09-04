# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\customtkinter', 'customtkinter/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\CTkMessagebox', 'CTkMessagebox/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\colorama', 'colorama/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\darkdetect', 'darkdetect/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\idna', 'idna/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\imageio', 'imageio/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\imageio_ffmpeg', 'imageio_ffmpeg/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\moviepy', 'moviepy/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\PIL', 'PIL/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\proglog', 'proglog/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\pytube', 'pytube/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\requests', 'requests/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\tqdm', 'tqdm/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\urllib3', 'urllib3/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\decorator.py', '.'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\eyed3', 'eyed3/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\filetype', 'filetype/'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\venv\\lib\\site-packages\\deprecation.py', '.'),
     ('C:\\Users\\pedro\\OneDrive\\Documentos\\pythonProject6\\icon.ico', '.')],
    hiddenimports = ['tkinter.font', 'typing_extensions', 'ctypes.wintypes', 'tkinter.ttk', 'CTkMessagebox', 'pytube', 'moviepy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Youber',
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
    icon=['icon.ico'],
)
