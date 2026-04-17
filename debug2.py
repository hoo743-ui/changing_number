import os
import sys
from tkinter import filedialog, Tk

print(f"Python: {sys.version}")
print(f"OS: {sys.platform}")
print(f"파일시스템 인코딩: {sys.getfilesystemencoding()}")

root = Tk()
root.withdraw()
folder = filedialog.askdirectory(title="진단할 상위 폴더 선택")
root.destroy()

if not folder:
    print("폴더 선택 안 함")
    exit()

print(f"\n선택 폴더: {folder}")
print("=" * 70)

# 방법1: os.listdir
print("\n[방법1] os.listdir:")
try:
    entries = os.listdir(folder)
    print(f"  총 {len(entries)}개")
    for e in sorted(entries):
        print(f"  {repr(e)}")
except Exception as ex:
    print(f"  오류: {ex}")

# 방법2: os.scandir
print("\n[방법2] os.scandir:")
try:
    count = 0
    with os.scandir(folder) as it:
        for entry in it:
            count += 1
            print(f"  name={repr(entry.name)}  is_dir={entry.is_dir()}")
    print(f"  총 {count}개")
except Exception as ex:
    print(f"  오류: {ex}")

# 방법3: bytes 경로로 강제 읽기
print("\n[방법3] bytes 경로 강제 읽기:")
try:
    folder_bytes = folder.encode('utf-8') if isinstance(folder, str) else folder
    entries_b = os.listdir(folder_bytes)
    print(f"  총 {len(entries_b)}개")
    for e in sorted(entries_b):
        try:
            decoded = e.decode('utf-8')
        except Exception:
            decoded = repr(e)
        print(f"  raw={e}  decoded={decoded}")
except Exception as ex:
    print(f"  오류: {ex}")

input("\n완료. 엔터 누르면 종료...")