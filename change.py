from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
import shutil
import json
import datetime

# ================= 휴지통 경로 =================
TRASH_DIR = os.path.join(os.path.expanduser("~"), ".folder_reorder_trash")
TRASH_META = os.path.join(TRASH_DIR, "meta.json")

def ensure_trash_dir():
    os.makedirs(TRASH_DIR, exist_ok=True)

def load_trash_meta():
    if os.path.exists(TRASH_META):
        with open(TRASH_META, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_trash_meta(meta):
    ensure_trash_dir()
    with open(TRASH_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

# ================= 폴더 목록 불러오기 =================
def load_folders():
    folder = filedialog.askdirectory(title="상위 폴더 선택")
    if not folder:
        return
    load_from_path(folder)

def load_from_path(folder):
    folder_path_var.set(folder)
    preview_listbox.delete(0, tk.END)
    folder_list.clear()

    entries = os.listdir(folder)
    pattern = re.compile(r'^(\d+)_(.*)')
    matched = []

    for entry in entries:
        full_path = os.path.join(folder, entry)
        if os.path.isdir(full_path):
            m = pattern.match(entry)
            if m:
                num = int(m.group(1))
                rest = m.group(2)
                matched.append((num, rest, entry, full_path))

    matched.sort(key=lambda x: x[0])

    # 중복 번호 감지
    num_count = {}
    for num, _, _, _ in matched:
        num_count[num] = num_count.get(num, 0) + 1
    dup_nums = {num for num, cnt in num_count.items() if cnt > 1}
    duplicate_set.clear()
    duplicate_set.update(dup_nums)

    # 시작번호는 첫 폴더 번호 기준, 이후 연속으로 재매핑 (빵꾸 전체 감지)
    start_num = matched[0][0] if matched else 1
    for new_num, (_, rest, entry, full_path) in enumerate(matched, start=start_num):
        folder_list.append((new_num, rest, entry, full_path))

    apply_search_filter()

    if dup_nums:
        dup_list = ", ".join(str(n) for n in sorted(dup_nums))
        status_label.config(
            text=f"⚠️ 중복 번호 감지: [{dup_list}]  — 중복 확인 버튼을 눌러 확인하세요",
            fg="red"
        )
        dup_btn.config(state="normal")
    else:
        status_label.config(text=f"✅ {len(matched)}개 폴더 불러옴 (중복 없음)", fg="blue")
        dup_btn.config(state="disabled")

    preview_btn.config(state="normal")
    update_delete_btn()

# ================= 드래그 앤 드롭 =================
def drop_folders(event):
    raw = event.data
    paths = root.tk.splitlist(raw)

    base_folder = os.path.dirname(paths[0])
    folder_path_var.set(base_folder)
    preview_listbox.delete(0, tk.END)
    folder_list.clear()

    pattern = re.compile(r'^(\d+)_(.*)')
    matched = []

    for full_path in paths:
        if os.path.isdir(full_path):
            entry = os.path.basename(full_path)
            m = pattern.match(entry)
            if m:
                num = int(m.group(1))
                rest = m.group(2)
                matched.append((num, rest, entry, full_path))

    matched.sort(key=lambda x: x[0])

    # 중복 번호 감지
    num_count = {}
    for num, _, _, _ in matched:
        num_count[num] = num_count.get(num, 0) + 1
    dup_nums = {num for num, cnt in num_count.items() if cnt > 1}
    duplicate_set.clear()
    duplicate_set.update(dup_nums)

    # 시작번호는 첫 폴더 번호 기준, 이후 연속으로 재매핑
    start_num = matched[0][0] if matched else 1
    for new_num, (_, rest, entry, full_path) in enumerate(matched, start=start_num):
        folder_list.append((new_num, rest, entry, full_path))

    apply_search_filter()

    if dup_nums:
        dup_list = ", ".join(str(n) for n in sorted(dup_nums))
        status_label.config(
            text=f"⚠️ 중복 번호 감지: [{dup_list}]  — 중복 확인 버튼을 눌러 확인하세요",
            fg="red"
        )
        dup_btn.config(state="normal")
    else:
        status_label.config(text=f"✅ {len(matched)}개 폴더 불러옴 (드래그, 중복 없음)", fg="blue")
        dup_btn.config(state="disabled")

    preview_btn.config(state="normal")
    update_delete_btn()

# ================= 검색 필터 =================
def on_search_change_with_count(*args):
    apply_search_filter()
    keyword = search_var.get().strip()
    if keyword:
        search_count_label.config(text=f"{listbox.size()}개 일치")
    else:
        search_count_label.config(text="")

def apply_search_filter():
    keyword = search_var.get().strip().lower()
    listbox.delete(0, tk.END)
    filtered_indices.clear()

    for i, item in enumerate(folder_list):
        if keyword == "" or keyword in item[2].lower():
            listbox.insert(tk.END, item[2])
            filtered_indices.append(i)
            # 중복 번호 항목 빨간색 강조
            if item[0] in duplicate_set:
                listbox.itemconfig(tk.END, fg="#e74c3c", selectforeground="white")

    update_delete_btn()

def clear_search():
    search_var.set("")

# ================= 삭제 버튼 상태 업데이트 =================
def update_delete_btn():
    sel = listbox.curselection()
    if sel and folder_list:
        delete_btn.config(state="normal")
    else:
        delete_btn.config(state="disabled")

# ================= 리스트박스 선택 이벤트 =================
def on_listbox_select(event):
    update_delete_btn()
    sel = listbox.curselection()
    if sel:
        real_idx = filtered_indices[sel[0]]
        item = folder_list[real_idx]
        status_label.config(
            text=f"📁 선택됨: {item[2]}  (삭제 버튼으로 제거 가능)",
            fg="purple"
        )

# ================= 선택 폴더 삭제 (휴지통으로) =================
def delete_selected():
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("경고", "삭제할 폴더를 선택하세요.")
        return

    listbox_idx = sel[0]
    real_idx = filtered_indices[listbox_idx]
    item = folder_list[real_idx]
    folder_name = item[2]
    full_path = item[3]

    if not os.path.exists(full_path):
        folder_list.pop(real_idx)
        apply_search_filter()
        auto_renumber()
        return

    answer = messagebox.askyesno(
        "폴더 삭제 확인",
        f"아래 폴더를 휴지통으로 이동하고 순번을 재정렬할까요?\n\n"
        f"  📁 {folder_name}\n\n"
        f"♻️  휴지통에서 복구할 수 있습니다.",
        icon="warning"
    )
    if not answer:
        return

    ensure_trash_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    trash_id = f"{timestamp}_{folder_name}"
    trash_dest = os.path.join(TRASH_DIR, trash_id)

    try:
        shutil.move(full_path, trash_dest)
    except Exception as e:
        messagebox.showerror("삭제 오류", f"폴더 이동 중 오류 발생:\n{e}")
        return

    meta = load_trash_meta()
    meta.append({
        "id": trash_id,
        "original_name": folder_name,
        "original_path": full_path,
        "deleted_at": timestamp,
        "base_folder": folder_path_var.get()
    })
    save_trash_meta(meta)

    folder_list.pop(real_idx)
    apply_search_filter()
    auto_renumber()

    status_label.config(
        text=f"🗑️ '{folder_name}' 휴지통으로 이동 — 순번 자동 재정렬됨",
        fg="green"
    )
    delete_btn.config(state="disabled")
    preview_listbox.delete(0, tk.END)

# ================= 순번 자동 재정렬 =================
def auto_renumber():
    if not folder_list:
        listbox.delete(0, tk.END)
        preview_listbox.delete(0, tk.END)
        status_label.config(text="폴더 목록이 비었습니다. 다시 불러오세요.", fg="gray")
        preview_btn.config(state="disabled")
        run_btn.config(state="disabled")
        return

    base_folder = folder_path_var.get()
    start_num = folder_list[0][0]  # 시작번호 유지, 이후 연속으로 빵꾸 채움
    errors = []
    updated_list = []

    temp_map = []
    for new_num, (_, rest, orig_name, full_path) in enumerate(folder_list, start=start_num):
        new_name = f"{new_num}_{rest}"
        new_full_path = os.path.join(base_folder, new_name)

        if orig_name == new_name:
            updated_list.append((new_num, rest, new_name, full_path))
            continue

        temp_name = f"__TEMP_{new_num}_{rest}"
        temp_path = os.path.join(base_folder, temp_name)
        try:
            os.rename(full_path, temp_path)
            temp_map.append((temp_path, new_full_path, new_num, rest, new_name))
        except Exception as e:
            errors.append(f"{orig_name}: {e}")
            updated_list.append((new_num, rest, orig_name, full_path))

    for temp_path, final_path, new_num, rest, new_name in temp_map:
        try:
            os.rename(temp_path, final_path)
            updated_list.append((new_num, rest, new_name, final_path))
        except Exception as e:
            errors.append(f"{os.path.basename(temp_path)}: {e}")

    updated_list.sort(key=lambda x: x[0])
    folder_list.clear()
    folder_list.extend(updated_list)

    apply_search_filter()

    if errors:
        messagebox.showerror("재정렬 오류", "\n".join(errors))

# ================= 중복 번호 확인 창 =================
def open_dup_window():
    if not duplicate_set:
        messagebox.showinfo("중복 없음", "중복된 번호가 없습니다.")
        return

    win = tk.Toplevel(root)
    win.title("⚠️ 중복 번호 확인")
    win.geometry("620x420")
    win.grab_set()

    tk.Label(win, text="⚠️ 중복 번호 목록", font=("Arial", 14, "bold"), fg="red").pack(pady=8)
    tk.Label(win,
             text="아래 폴더들은 같은 순번을 가지고 있습니다.\n삭제 또는 재정렬로 해결하세요.",
             fg="gray").pack()

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=15, pady=8)

    cols = ("순번", "폴더명", "전체 경로")
    tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
    tree.heading("순번", text="순번")
    tree.heading("폴더명", text="폴더명")
    tree.heading("전체 경로", text="전체 경로")
    tree.column("순번", width=60, anchor="center")
    tree.column("폴더명", width=200)
    tree.column("전체 경로", width=300)

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    # 중복 번호에 해당하는 항목만 표시 (원본 matched 기준)
    base_folder = folder_path_var.get()
    import re as _re
    pattern = _re.compile(r'^(\d+)_(.*)')
    dup_items = []
    try:
        for entry in os.listdir(base_folder):
            fp = os.path.join(base_folder, entry)
            if os.path.isdir(fp):
                m = pattern.match(entry)
                if m and int(m.group(1)) in duplicate_set:
                    dup_items.append((int(m.group(1)), entry, fp))
    except Exception:
        pass
    dup_items.sort(key=lambda x: (x[0], x[1]))

    for num, name, path in dup_items:
        iid = tree.insert("", "end", values=(num, name, path))
        tree.item(iid, tags=("dup",))
    tree.tag_configure("dup", foreground="#e74c3c")

    tk.Label(win, text=f"총 {len(dup_items)}개 항목에서 {len(duplicate_set)}개 번호 중복",
             fg="red", font=("Arial", 10, "bold")).pack(pady=4)
    tk.Button(win, text="닫기", width=10, command=win.destroy).pack(pady=4)

# ================= 휴지통 창 =================
def open_trash_window():
    meta = load_trash_meta()

    win = tk.Toplevel(root)
    win.title("🗑️ 휴지통 — 복구 / 영구 삭제")
    win.geometry("720x480")
    win.grab_set()

    tk.Label(win, text="휴지통", font=("Arial", 14, "bold")).pack(pady=8)
    tk.Label(win, text="삭제된 폴더 목록입니다. 선택 후 복구하거나 영구 삭제할 수 있습니다.", fg="gray").pack()

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=15, pady=8)

    cols = ("원본 폴더명", "삭제 일시", "원본 경로")
    tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
    tree.heading("원본 폴더명", text="원본 폴더명")
    tree.heading("삭제 일시", text="삭제 일시")
    tree.heading("원본 경로", text="원본 경로")
    tree.column("원본 폴더명", width=180)
    tree.column("삭제 일시", width=140)
    tree.column("원본 경로", width=340)

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def refresh_tree():
        tree.delete(*tree.get_children())
        for item in meta:
            dt = item["deleted_at"]
            try:
                dt_fmt = datetime.datetime.strptime(dt, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                dt_fmt = dt
            tree.insert("", "end", iid=item["id"],
                        values=(item["original_name"], dt_fmt, item["original_path"]))

    refresh_tree()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=8)

    def restore_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("경고", "복구할 항목을 선택하세요.", parent=win)
            return

        restored, failed = [], []

        for trash_id in selected:
            entry = next((m for m in meta if m["id"] == trash_id), None)
            if not entry:
                continue
            trash_path = os.path.join(TRASH_DIR, trash_id)
            original_path = entry["original_path"]

            if not os.path.exists(trash_path):
                failed.append(f"{entry['original_name']}: 휴지통 파일 없음")
                continue
            if os.path.exists(original_path):
                failed.append(f"{entry['original_name']}: 원본 경로에 이미 같은 이름 존재")
                continue
            try:
                shutil.move(trash_path, original_path)
                meta.remove(entry)
                restored.append(entry["original_name"])
            except Exception as e:
                failed.append(f"{entry['original_name']}: {e}")

        save_trash_meta(meta)
        refresh_tree()

        msg = ""
        if restored:
            msg += "✅ 복구 완료:\n" + "\n".join(f"  • {n}" for n in restored)
        if failed:
            msg += ("\n\n" if msg else "") + "❌ 실패:\n" + "\n".join(f"  • {n}" for n in failed)
        messagebox.showinfo("복구 결과", msg.strip(), parent=win)

        if restored:
            base = folder_path_var.get()
            if base:
                load_from_path(base)
            status_label.config(text=f"♻️ {len(restored)}개 폴더 복구됨 — 목록 새로고침됨", fg="blue")

    def permanent_delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 항목을 선택하세요.", parent=win)
            return

        names = [next((m["original_name"] for m in meta if m["id"] == tid), tid)
                 for tid in selected]

        answer = messagebox.askyesno(
            "영구 삭제 확인",
            f"선택한 {len(names)}개 폴더를 영구 삭제할까요?\n\n"
            + "\n".join(f"  • {n}" for n in names)
            + "\n\n⚠️ 이 작업은 되돌릴 수 없습니다.",
            icon="warning", parent=win
        )
        if not answer:
            return

        for trash_id in selected:
            entry = next((m for m in meta if m["id"] == trash_id), None)
            if not entry:
                continue
            trash_path = os.path.join(TRASH_DIR, trash_id)
            if os.path.exists(trash_path):
                shutil.rmtree(trash_path, ignore_errors=True)
            meta.remove(entry)

        save_trash_meta(meta)
        refresh_tree()
        messagebox.showinfo("완료", f"{len(names)}개 폴더 영구 삭제 완료.", parent=win)

    def clear_all_trash():
        if not meta:
            messagebox.showinfo("알림", "휴지통이 이미 비어 있습니다.", parent=win)
            return
        answer = messagebox.askyesno(
            "휴지통 비우기",
            f"휴지통의 모든 항목({len(meta)}개)을 영구 삭제할까요?\n⚠️ 되돌릴 수 없습니다.",
            icon="warning", parent=win
        )
        if not answer:
            return
        for entry in meta:
            trash_path = os.path.join(TRASH_DIR, entry["id"])
            if os.path.exists(trash_path):
                shutil.rmtree(trash_path, ignore_errors=True)
        meta.clear()
        save_trash_meta(meta)
        refresh_tree()
        messagebox.showinfo("완료", "휴지통을 비웠습니다.", parent=win)

    tk.Button(btn_frame, text="♻️ 선택 복구", width=14, command=restore_selected,
              bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=6)
    tk.Button(btn_frame, text="🗑️ 영구 삭제", width=14, command=permanent_delete_selected,
              bg="#e74c3c", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=6)
    tk.Button(btn_frame, text="🧹 휴지통 비우기", width=14, command=clear_all_trash,
              bg="#888", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=6)
    tk.Button(btn_frame, text="닫기", width=8, command=win.destroy).pack(side="left", padx=6)

# ================= 미리보기 =================
def preview():
    preview_listbox.delete(0, tk.END)

    if not folder_list:
        messagebox.showwarning("경고", "폴더를 먼저 불러오세요.")
        return

    changed_count = 0
    start_num = folder_list[0][0]
    for new_num, (_, rest, orig_name, _full) in enumerate(folder_list, start=start_num):
        new_name = f"{new_num}_{rest}"
        if orig_name == new_name:
            preview_listbox.insert(tk.END, f"  {orig_name}")
            preview_listbox.itemconfig(tk.END, fg="gray")
        else:
            preview_listbox.insert(tk.END, f"  {orig_name}  →  {new_name}")
            preview_listbox.itemconfig(tk.END, fg="#e74c3c")
            changed_count += 1

    status_label.config(
        text=f"👁 미리보기 완료 — {changed_count}개 변경예정 / 확인 후 실행 버튼을 누르세요",
        fg="orange"
    )
    run_btn.config(state="normal")

# ================= 실행 =================
def run_reorder():
    if not folder_list:
        return

    base_folder = folder_path_var.get()
    errors = []
    start_num = folder_list[0][0]  # 시작번호 유지, 이후 연속으로 빵꾸 채움

    temp_map = []
    for new_num, (_, rest, orig_name, full_path) in enumerate(folder_list, start=start_num):
        new_name = f"{new_num}_{rest}"
        if orig_name == new_name:
            continue
        temp_name = f"__TEMP_{new_num}_{rest}"
        temp_path = os.path.join(base_folder, temp_name)
        try:
            os.rename(full_path, temp_path)
            temp_map.append((temp_path, os.path.join(base_folder, new_name)))
        except Exception as e:
            errors.append(f"{orig_name}: {e}")

    for temp_path, final_path in temp_map:
        try:
            os.rename(temp_path, final_path)
        except Exception as e:
            errors.append(f"{os.path.basename(temp_path)}: {e}")

    if errors:
        messagebox.showerror("오류 발생", "\n".join(errors))
    else:
        status_label.config(text="🔥 재정렬 완료!", fg="green")
        messagebox.showinfo("완료", "폴더 순번 재정렬이 완료되었습니다!")

    folder_list.clear()
    filtered_indices.clear()
    listbox.delete(0, tk.END)
    preview_listbox.delete(0, tk.END)
    run_btn.config(state="disabled")
    preview_btn.config(state="disabled")
    delete_btn.config(state="disabled")

# ================= GUI =================
root = TkinterDnD.Tk()
root.title("폴더 순번 재정렬기")
root.geometry("860x680")

folder_list = []
filtered_indices = []
duplicate_set = set()  # 중복 번호 추적
folder_path_var = tk.StringVar()
search_var = tk.StringVar()

# ── 타이틀 ──
tk.Label(root, text="폴더 순번 자동 재정렬기", font=("Arial", 16, "bold")).pack(pady=8)

# ── 폴더 경로 + 휴지통 버튼 ──
path_frame = tk.Frame(root)
path_frame.pack(fill="x", padx=15, pady=4)
tk.Label(path_frame, text="선택 폴더:").pack(side="left")
tk.Entry(path_frame, textvariable=folder_path_var, width=52, state="readonly").pack(side="left", padx=5)
tk.Button(path_frame, text="📂 폴더 선택", command=load_folders).pack(side="left")
tk.Button(path_frame, text="🗑️ 휴지통", command=open_trash_window,
          bg="#555", fg="white", font=("Arial", 9, "bold")).pack(side="right")
dup_btn = tk.Button(path_frame, text="⚠️ 중복확인", command=open_dup_window,
                    bg="#e67e22", fg="white", font=("Arial", 9, "bold"), state="disabled")
dup_btn.pack(side="right", padx=4)

# ── 검색바 ──
search_frame = tk.Frame(root)
search_frame.pack(fill="x", padx=15, pady=4)
tk.Label(search_frame, text="🔍 검색:").pack(side="left")
search_entry = tk.Entry(search_frame, textvariable=search_var, width=40, font=("Arial", 11))
search_entry.pack(side="left", padx=5)
tk.Button(search_frame, text="✕ 초기화", command=clear_search, bg="#bbb", font=("Arial", 9)).pack(side="left")
search_count_label = tk.Label(search_frame, text="", fg="gray")
search_count_label.pack(side="left", padx=10)

search_var.trace_add("write", on_search_change_with_count)

# ── 리스트 영역 ──
list_frame = tk.Frame(root)
list_frame.pack(fill="both", expand=True, padx=15, pady=4)

# 왼쪽
left_frame = tk.Frame(list_frame)
left_frame.pack(side="left", fill="both", expand=True)
tk.Label(left_frame, text="현재 폴더명 (드래그 가능)", font=("Arial", 11, "bold")).pack()

delete_btn = tk.Button(
    left_frame, text="🗑️ 선택 폴더 삭제 (휴지통으로)",
    width=35, command=delete_selected,
    bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), state="disabled"
)
delete_btn.pack(pady=(2, 4))

scrollbar_l = tk.Scrollbar(left_frame)
scrollbar_l.pack(side="right", fill="y")
listbox = tk.Listbox(
    left_frame, yscrollcommand=scrollbar_l.set, width=40,
    selectbackground="#e74c3c", selectforeground="white",
    activestyle="none", font=("Arial", 10)
)
listbox.pack(fill="both", expand=True)
scrollbar_l.config(command=listbox.yview)
listbox.bind("<<ListboxSelect>>", on_listbox_select)

listbox.drop_target_register(DND_FILES)
listbox.dnd_bind('<<Drop>>', drop_folders)

# 오른쪽
right_frame = tk.Frame(list_frame)
right_frame.pack(side="right", fill="both", expand=True)
tk.Label(right_frame, text="변경 미리보기", font=("Arial", 11, "bold")).pack()
tk.Label(right_frame, text="(미리보기 / 실행은 아래 버튼 사용)", fg="gray").pack(pady=(2, 4))

scrollbar_r = tk.Scrollbar(right_frame)
scrollbar_r.pack(side="right", fill="y")
preview_listbox = tk.Listbox(right_frame, yscrollcommand=scrollbar_r.set, width=55, font=("Arial", 10))
preview_listbox.pack(fill="both", expand=True)
scrollbar_r.config(command=preview_listbox.yview)

# ── 하단 버튼 ──
btn_frame = tk.Frame(root)
btn_frame.pack(pady=8)

preview_btn = tk.Button(btn_frame, text="👁 미리보기", width=15, command=preview, state="disabled")
preview_btn.pack(side="left", padx=10)

run_btn = tk.Button(btn_frame, text="🔥 재정렬 실행", width=15, command=run_reorder,
                    bg="tomato", fg="white", state="disabled")
run_btn.pack(side="left", padx=10)

# ── 상태 표시 ──
status_label = tk.Label(root, text="폴더를 선택하거나 왼쪽 목록에 드래그하세요.", fg="gray")
status_label.pack(pady=4)

root.mainloop()