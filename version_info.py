import datetime

version = datetime.datetime.now().strftime("%Y.%m.%d")
version_tuple = tuple(map(int, datetime.datetime.now().strftime("%Y,%m,%d,0").split(',')))

content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'SoundSync'),
        StringStruct('FileDescription', 'SoundSync Centralized Audio Management'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'SoundSync'),
        StringStruct('LegalCopyright', 'Copyright (c) 2026 Gavin Gonçalves'),
        StringStruct('OriginalFilename', 'SoundSync.exe'),
        StringStruct('ProductName', 'SoundSync'),
        StringStruct('ProductVersion', '{version}')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""

with open("version_info.txt", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Version info generated: {version}")
