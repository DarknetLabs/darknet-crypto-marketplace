import PyInstaller.__main__
import os
import shutil

def build_clean_executable():
    """Build executable with antivirus-friendly settings"""
    
    print("Building clean executable to avoid virus detection...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller settings to reduce false positives
    args = [
        'main.py',
        '--onefile',
        '--noconsole',  # Remove console window
        '--name=DarknetTerminal',
        '--clean',  # Clean cache
        '--noconfirm',  # Overwrite existing files
        
        # Antivirus-friendly options
        '--noupx',  # Don't use UPX compression (triggers antivirus)
        '--strip',  # Strip debug symbols
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        
        # Add version info (helps with trust)
        # '--version-file=version_info.txt',  # Comment out for now
        
        # Exclude unnecessary modules that trigger detection
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=numpy.distutils',
        '--exclude-module=PIL.ImageTk',
        '--exclude-module=PIL._imagingtk',
        
        # Add icon (signed executables with icons are less suspicious)
        # '--icon=icon.ico',  # Comment out for now
        
        # Hidden imports (explicit is better than implicit)
        '--hidden-import=requests',
        '--hidden-import=websocket',
        '--hidden-import=cryptography',
        '--hidden-import=json',
        '--hidden-import=threading',
    ]
    
    print("Running PyInstaller with clean settings...")
    PyInstaller.__main__.run(args)
    
    print("✓ Clean executable built successfully!")
    print("Location: dist/DarknetTerminal.exe")
    
    # Show file info
    exe_path = "dist/DarknetTerminal.exe"
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"Size: {size:.1f} MB")

if __name__ == "__main__":
    build_clean_executable() 