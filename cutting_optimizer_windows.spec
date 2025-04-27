block_cipher = None

a = Analysis(['cutting_optimizer_PRO_v3.py'],
             pathex=['.'],  # Używamy ścieżki względnej
             binaries=[],
             datas=[('logo.png', '.')],  # Dołączamy logo
             hiddenimports=['PIL', 'pulp', 'pandas', 'ezdxf', 'reportlab'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='AMIR Cutting Optimizer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='logo.png') 