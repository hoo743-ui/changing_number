import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class NameOnlyMatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 이름만 비교 (B2부터)")
        self.root.geometry("700x450")

        self.excel_paths = []
        self.folder_paths = []

        # 버튼 영역
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", pady=5)

        tk.Button(btn_frame, text="📂 엑셀 여러 개 선택", command=self.add_excels).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📁 상위 폴더 선택", command=self.add_parent_folder).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 초기화", command=self.clear_all).pack(side="left", padx=5)

        # 리스트 영역
        list_frame = tk.Frame(root)
        list_frame.pack(fill="both", expand=True)

        self.excel_list = tk.Listbox(list_frame)
        self.excel_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.folder_list = tk.Listbox(list_frame)
        self.folder_list.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # 실행 버튼
        tk.Button(root, text="🚀 실행", bg="green", fg="white", height=2, command=self.run).pack(fill="x", padx=10, pady=5)

        # 진행바
        self.progress = ttk.Progressbar(root)
        self.progress.pack(fill="x", padx=10)

        # 상태 메시지
        self.status = tk.Label(root, text="대기 중", anchor="w")
        self.status.pack(fill="x", padx=10)

        # 로그
        log_frame = tk.LabelFrame(root, text="로그")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log = tk.Text(log_frame, height=8)
        self.log.pack(fill="both", expand=True)

    # 로그 출력
    def write_log(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()

    # 엑셀 추가
    def add_excels(self):
        files = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx")])
        for f in files:
            if f not in self.excel_paths:
                self.excel_paths.append(f)
                self.excel_list.insert(tk.END, os.path.basename(f))

    # 상위 폴더 선택 → 하위 폴더 전부 수집
    def add_parent_folder(self):
        parent = filedialog.askdirectory(title="상위 폴더 선택")
        if not parent:
            return

        count = 0
        for name in os.listdir(parent):
            full_path = os.path.join(parent, name)
            if os.path.isdir(full_path) and full_path not in self.folder_paths:
                self.folder_paths.append(full_path)
                self.folder_list.insert(tk.END, name)
                count += 1

        self.status.config(text=f"폴더 {count}개 추가됨")

    # 초기화
    def clear_all(self):
        self.excel_paths = []
        self.folder_paths = []
        self.excel_list.delete(0, tk.END)
        self.folder_list.delete(0, tk.END)
        self.status.config(text="초기화 완료")
        self.log.delete("1.0", tk.END)

    # 실행
    def run(self):
        if not self.excel_paths or not self.folder_paths:
            messagebox.showerror("오류", "엑셀과 폴더를 선택하세요")
            return

        try:
            self.write_log("폴더 이름 수집 중...")

            # 폴더 이름에서 이름만 추출
            folder_names = set()
            for folder in self.folder_paths:
                name = os.path.basename(folder).strip().split()[-1]  # 마지막 단어 = 이름
                folder_names.add(name)

            self.write_log(f"폴더 이름 {len(folder_names)}개 수집 완료")

            self.progress["maximum"] = len(self.excel_paths)

            for i, excel in enumerate(self.excel_paths):
                self.status.config(text=f"처리 중: {os.path.basename(excel)}")
                self.root.update()

                # 2행을 헤더로 읽고 B열 이름만 가져오기
                df = pd.read_excel(excel, header=1, usecols=[1])  # B열
                df.columns = ['이름']  # 컬럼 이름 강제 지정

                # 이름 존재 여부 확인
                df['존재여부'] = df['이름'].apply(lambda x: "있음" if str(x).strip() in folder_names else "없음")

                out = excel.replace(".xlsx", "_결과.xlsx")
                df.to_excel(out, index=False)

                self.progress["value"] = i + 1
                self.write_log(f"✅ 완료: {out}")

            self.status.config(text="🎉 모든 파일 처리 완료!")
            messagebox.showinfo("완료", "끝!")

        except Exception as e:
            messagebox.showerror("에러", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = NameOnlyMatcher(root)
    root.mainloop()