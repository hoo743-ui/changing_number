import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
import os

source_files = []
target_files = []

def select_sources():
    global source_files
    paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if paths:
        source_files = list(paths)
        source_label.config(text=f"{len(source_files)}개 파일 선택 완료")
        status_label.config(text="원본 PDF 선택 완료")

def select_targets():
    global target_files
    paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if paths:
        target_files = list(paths)
        target_label.config(text=f"{len(target_files)}개 파일 선택 완료")
        status_label.config(text="대상 PDF 선택 완료")

def replace_pages_multi():
    if not source_files or not target_files:
        status_label.config(text="원본과 대상 PDF 파일을 모두 선택하세요")
        return

    if len(source_files) != len(target_files):
        status_label.config(text="원본과 대상 PDF 파일 수가 일치하지 않습니다")
        return

    try:
        src_page_num = int(source_page_entry.get()) - 1
        tgt_page_num = int(target_page_entry.get()) - 1
    except ValueError:
        status_label.config(text="페이지 번호는 숫자여야 합니다")
        return

    for s_file, t_file in zip(source_files, target_files):
        src_pdf = PdfReader(s_file)
        tgt_pdf = PdfReader(t_file)
        writer = PdfWriter()

        # 페이지 범위 체크
        if src_page_num >= len(src_pdf.pages) or src_page_num < 0:
            status_label.config(text=f"{os.path.basename(s_file)}: 원본 페이지 번호 범위 초과")
            continue
        if tgt_page_num >= len(tgt_pdf.pages) or tgt_page_num < 0:
            status_label.config(text=f"{os.path.basename(t_file)}: 대상 페이지 번호 범위 초과")
            continue

        # target 페이지 교체
        for i in range(len(tgt_pdf.pages)):
            if i == tgt_page_num:
                writer.add_page(src_pdf.pages[src_page_num])
            else:
                writer.add_page(tgt_pdf.pages[i])

        # 저장
        save_path = filedialog.asksaveasfilename(initialfile=os.path.basename(t_file),
                                                 defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if save_path:
            with open(save_path, "wb") as f:
                writer.write(f)
            status_label.config(text=f"{os.path.basename(t_file)} 저장 완료")
        else:
            status_label.config(text=f"{os.path.basename(t_file)} 저장 취소됨")

# ---------------- GUI ----------------
root = tk.Tk()
root.title("PDF 페이지 교체 툴 (다수 파일 처리)")
root.geometry("600x350")
root.resizable(False, False)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="PDF 페이지 교체 툴 (다수 파일 처리)", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0,15))

# Source PDF
tk.Label(frame, text="덮어쓸 PDF").grid(row=1, column=0, sticky="w")
source_label = tk.Label(frame, text="파일 선택 안됨", width=35, relief="sunken", anchor="w", bg="white")
source_label.grid(row=1, column=1, padx=5)
tk.Button(frame, text="선택", command=select_sources).grid(row=1, column=2)

tk.Label(frame, text="원본 페이지 번호").grid(row=2, column=0, sticky="w")
source_page_entry = tk.Entry(frame, width=10)
source_page_entry.grid(row=2, column=1, sticky="w")

# Target PDF
tk.Label(frame, text="대상 PDF").grid(row=3, column=0, sticky="w")
target_label = tk.Label(frame, text="파일 선택 안됨", width=35, relief="sunken", anchor="w", bg="white")
target_label.grid(row=3, column=1, padx=5)
tk.Button(frame, text="선택", command=select_targets).grid(row=3, column=2)

tk.Label(frame, text="대상 페이지 번호").grid(row=4, column=0, sticky="w")
target_page_entry = tk.Entry(frame, width=10)
target_page_entry.grid(row=4, column=1, sticky="w")

# 실행 버튼
tk.Button(frame, text="페이지 교체 실행 (다수 파일)", width=45, command=replace_pages_multi).grid(row=5, column=0, columnspan=3, pady=15)

# 상태 표시
status_label = tk.Label(frame, text="", fg="green")
status_label.grid(row=6, column=0, columnspan=3)

root.mainloop()