import tkinter as tk
from tkinter import filedialog
import os
from PyPDF2 import PdfReader, PdfWriter

rows = []
seen_files = set()

# ================= PDF → 2페이지 단위 row 생성 =================
def add_pdf(file_path):
    if file_path in seen_files:
        return
    seen_files.add(file_path)
    
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    
    for i in range(0, total_pages, 2):
        row_frame = tk.Frame(table_frame)
        row_frame.pack(fill="x", pady=2)
        
        label_text = f"{os.path.basename(file_path)} ({i+1}-{min(i+2,total_pages)}p)"
        tk.Label(row_frame, text=label_text, width=40, anchor="w").pack(side="left")
        
        name_entry = tk.Entry(row_frame, width=20)
        name_entry.pack(side="left", padx=5)
        
        def delete_row():
            row_frame.destroy()
            rows[:] = [r for r in rows if r[0] != row_frame]
            
        tk.Button(row_frame, text="삭제", command=delete_row).pack(side="left", padx=5)
        
        rows.append((row_frame, file_path, i, name_entry))
        
        if len(rows) == 1:
            name_entry.focus()

# ================= 파일 선택 =================
def add_files():
    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for f in files:
        add_pdf(f)

# ================= PDF 처리 =================
def process_pdf():
    base_folder = r"\\Gachonsemi8805\근로1\사업단 신청 스캔"
    delete_after = delete_var.get()
    
    try:
        for _, file_path, start_page, name_entry in rows:
            name = name_entry.get().strip()
            
            if not name:
                name_entry.config(bg="red")
                continue
            else:
                name_entry.config(bg="white")
            
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            
            # 폴더 생성 (이름만)
            folder_name = f"{name}"
            new_folder = os.path.join(base_folder, folder_name)
            count = 1
            orig_folder = new_folder
            while os.path.exists(new_folder):
                new_folder = f"{orig_folder}_{count}"
                count += 1
            os.makedirs(new_folder)
            
            # 2페이지씩 PDF 생성
            writer = PdfWriter()
            writer.add_page(reader.pages[start_page])
            if start_page + 1 < total_pages:
                writer.add_page(reader.pages[start_page+1])
            
            save_path = os.path.join(new_folder, f"{start_page+1}_{min(start_page+2,total_pages)}.pdf")
            with open(save_path, "wb") as f:
                writer.write(f)
            
            if delete_after:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        status_label.config(text="🔥 2페이지 단위로 폴더 생성 완료!", fg="green")
    
    except Exception as e:
        status_label.config(text=f"오류 발생: {str(e)}", fg="red")

# ================= GUI =================
root = tk.Tk()
root.title("PDF 2페이지 단위 분할기 (이름만)")
root.geometry("700x500")

tk.Label(root, text="PDF 2페이지 단위 자동 분할기 (이름만)", font=("Arial", 16, "bold")).pack(pady=10)

header = tk.Frame(root)
header.pack(fill="x", padx=10)
tk.Label(header, text="파일 (페이지)", width=40).pack(side="left")
tk.Label(header, text="이름", width=20).pack(side="left")

table_container = tk.Frame(root)
table_container.pack(fill="both", expand=True, padx=10, pady=5)

# 스크롤 영역
canvas = tk.Canvas(table_container)
scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
table_frame = tk.Frame(canvas)
table_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0,0), window=table_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# 버튼
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="PDF 추가", command=add_files).pack(side="left", padx=5)

delete_var = tk.BooleanVar()
tk.Checkbutton(btn_frame, text="처리 후 원본 삭제", variable=delete_var).pack(side="left", padx=10)
tk.Button(btn_frame, text="실행", width=15, height=2, command=process_pdf).pack(side="left", padx=5)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()