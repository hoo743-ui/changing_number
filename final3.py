import tkinter as tk
from tkinter import filedialog
import os
import time
from PyPDF2 import PdfReader, PdfWriter

rows = []
watch_folder = ""
seen_files = set()

# ================= 스크롤 영역 =================
def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scroll_frame

# ================= 파일 추가 =================
def add_files():
    files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for file_path in files:
        if file_path not in seen_files:
            seen_files.add(file_path)
            add_row(file_path)

# ================= 행 추가 =================
def add_row(file_path):
    row_frame = tk.Frame(table_frame)
    row_frame.pack(fill="x", pady=2)

    tk.Label(row_frame, text=os.path.basename(file_path), width=25, anchor="w").pack(side="left")

    name_entry = tk.Entry(row_frame, width=12)
    name_entry.pack(side="left", padx=5)

    id_entry = tk.Entry(row_frame, width=12)
    id_entry.pack(side="left", padx=5)

    def delete_row():
        row_frame.destroy()
        rows[:] = [r for r in rows if r[0] != row_frame]

    tk.Button(row_frame, text="삭제", command=delete_row).pack(side="left", padx=5)

    rows.append((row_frame, file_path, name_entry, id_entry))

    # 🔥 Enter 자동 이동
    def focus_next_row():
        for idx, r in enumerate(rows):
            if r[0] == row_frame:
                if idx + 1 < len(rows):
                    rows[idx + 1][2].focus()
                break

    name_entry.bind("<Return>", lambda e: id_entry.focus())
    id_entry.bind("<Return>", lambda e: focus_next_row())

    # 첫 행 자동 포커스
    if len(rows) == 1:
        name_entry.focus()

# ================= 스캔 폴더 선택 =================
def select_watch_folder():
    global watch_folder
    watch_folder = filedialog.askdirectory(title="스캔 폴더 선택")
    status_label.config(text=f"📡 감시중: {watch_folder}")

# ================= 폴더 자동 감시 =================
def watch_folder_loop():
    if watch_folder:
        try:
            files = os.listdir(watch_folder)
            for f in files:
                if f.lower().endswith(".pdf"):
                    full_path = os.path.join(watch_folder, f)

                    if full_path not in seen_files:
                        time.sleep(0.3)  # 파일 생성 안정화
                        seen_files.add(full_path)
                        add_row(full_path)
        except:
            pass

    root.after(2000, watch_folder_loop)

# ================= 자동 처리 =================
def process_pdf():
    base_folder = r"\\Gachonsemi8805\근로1\사업단 신청 스캔"
    delete_after = delete_var.get()

    try:
        for _, file_path, name_entry, id_entry in rows:
            name = name_entry.get().strip()
            student_id = id_entry.get().strip()

            if not name or not student_id:
                name_entry.config(bg="red")
                id_entry.config(bg="red")
                continue
            else:
                name_entry.config(bg="white")
                id_entry.config(bg="white")

            reader = PdfReader(file_path)
            total_pages = len(reader.pages)

            for i in range(0, total_pages, 3):  # 4 → 3
                folder_name = f"{student_id} {name}"
                new_folder = os.path.join(base_folder, folder_name)

                count = 1
                orig_folder = new_folder
                while os.path.exists(new_folder):
                    new_folder = f"{orig_folder}_{count}"
                    count += 1

                os.makedirs(new_folder)

                # 1p
                if i < total_pages:
                    writer1 = PdfWriter()
                    writer1.add_page(reader.pages[i])
                    with open(os.path.join(new_folder, "사업 참여 확인서.pdf"), "wb") as f:
                        writer1.write(f)

                # 2p
                if i+1 < total_pages:
                    writer2 = PdfWriter()
                    writer2.add_page(reader.pages[i+1])
                    with open(os.path.join(new_folder, "개인정보이용동의서(한국산업기술진흥원).pdf"), "wb") as f:
                        writer2.write(f)

                # 3p
                if i+2 < total_pages:
                    writer3 = PdfWriter()
                    writer3.add_page(reader.pages[i+2])
                    with open(os.path.join(new_folder, "개인정보활용동의서(가천대).pdf"), "wb") as f:
                        writer3.write(f)

            if delete_after:
                os.remove(file_path)

        status_label.config(text="🔥 전체 처리 완료!", fg="green")

    except Exception as e:
        status_label.config(text=f"오류 발생: {str(e)}", fg="red")
# ================= GUI =================
root = tk.Tk()
root.title("PDF 자동 분할기 (자동 스캔 감지)")
root.geometry("750x550")

tk.Label(root, text="PDF 자동 분할기", font=("Arial", 16, "bold")).pack(pady=10)

# 헤더
header = tk.Frame(root)
header.pack(fill="x", padx=10)

tk.Label(header, text="파일명", width=25).pack(side="left")
tk.Label(header, text="이름", width=12).pack(side="left")
tk.Label(header, text="학번", width=12).pack(side="left")

# 스크롤 테이블
table_container = tk.Frame(root)
table_container.pack(fill="both", expand=True, padx=10, pady=5)

table_frame = create_scrollable_frame(table_container)

# 버튼
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="PDF 추가", command=add_files).pack(side="left", padx=5)
tk.Button(btn_frame, text="📡 스캔폴더 선택", command=select_watch_folder).pack(side="left", padx=5)

delete_var = tk.BooleanVar()
tk.Checkbutton(btn_frame, text="처리 후 원본 삭제", variable=delete_var).pack(side="left", padx=10)

tk.Button(btn_frame, text="실행", width=15, height=2, command=process_pdf).pack(side="left", padx=5)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

# 🔥 폴더 감시 시작
watch_folder_loop()

root.mainloop()