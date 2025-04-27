block_cipher = None

a = Analysis(['cutting_optimizer_PRO_v3.py'],
             pathex=['/Users/hubert/Developer/cuts-optimizer'],
             binaries=[],
             datas=[('logo.png', '.')],  # Include logo
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
          [],
          exclude_binaries=True,
          name='AMIR Cutting Optimizer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='logo.png')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='AMIR Cutting Optimizer')

app = BUNDLE(coll,
            name='AMIR Cutting Optimizer.app',
            icon='logo.png',
            bundle_identifier='com.amir.cuttingoptimizer',
            info_plist={
                'CFBundleShortVersionString': '4.0.0',
                'CFBundleVersion': '4.0.0',
                'NSHighResolutionCapable': 'True'
            }) 