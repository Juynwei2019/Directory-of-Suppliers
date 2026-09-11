from datetime import datetime
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import pandas as pd

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class VendorApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("廠商資料維護系統 (專業版)")
    self.geometry("1400x800")

    self.init_db()
    self.create_widgets()
    self.load_data()

    self.is_collapsed = False

  def init_db(self):
    self.conn = sqlite3.connect("vendors.db")
    self.cursor = self.conn.cursor()
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                major_item TEXT,
                category TEXT,
                sub_item TEXT,
                notes TEXT,
                vendor_name TEXT NOT NULL,
                contact1 TEXT,
                phone1 TEXT,
                fax TEXT,
                contact2 TEXT,
                phone2 TEXT,
                contact3 TEXT,
                phone3 TEXT,
                score REAL DEFAULT 0.0,
                updated_at TEXT
            )
        """)
    self.conn.commit()

  def create_widgets(self):
    self.grid_columnconfigure(1, weight=1)
    self.grid_rowconfigure(0, weight=1)

    # ================= 左側：一般框架面板 =================
    self.left_frame = ctk.CTkFrame(self, width=360, corner_radius=0)
    self.left_frame.grid(
        row=0, column=0, sticky="nsew", padx=0, pady=0
    )
    self.left_frame.grid_propagate(False)

    title_label = ctk.CTkLabel(
        self.left_frame,
        text="廠商資料表單",
        font=("Microsoft JhengHei", 18, "bold"),
    )
    title_label.pack(anchor="w", padx=12, pady=(10, 5))

    self.entries = {}

    def create_card(title):
      card = ctk.CTkFrame(
          self.left_frame, fg_color=("gray92", "gray16"), corner_radius=6
      )
      card.pack(fill="x", padx=8, pady=3)
      ctk.CTkLabel(
          card,
          text=title,
          font=("Microsoft JhengHei", 13, "bold"),
          text_color=("gray30", "gray70"),
      ).pack(anchor="w", padx=10, pady=(4, 2))
      return card

    card1 = create_card("📌 基本與分類資訊")
    fields_card1 = [
        ("廠商姓名*", "vendor_name"),
        ("大項", "major_item"),
        ("分類", "category"),
        ("細目", "sub_item"),
    ]
    for label_text, key in fields_card1:
      row_f = ctk.CTkFrame(card1, fg_color="transparent")
      row_f.pack(fill="x", padx=8, pady=2)
      ctk.CTkLabel(
          row_f,
          text=label_text,
          font=("Microsoft JhengHei", 12),
          width=75,
          anchor="w",
      ).pack(side="left")
      entry = ctk.CTkEntry(
          row_f, height=32, corner_radius=4, font=("Microsoft JhengHei", 12)
      )
      entry.pack(side="right", fill="x", expand=True)
      self.entries[key] = entry

    card2 = create_card("📞 聯絡人與通訊")
    fields_card2 = [
        ("傳真", "fax"),
        ("聯絡人 1", "contact1"),
        ("電話 1", "phone1"),
        ("聯絡人 2", "contact2"),
        ("電話 2", "phone2"),
    ]
    for label_text, key in fields_card2:
      row_f = ctk.CTkFrame(card2, fg_color="transparent")
      row_f.pack(fill="x", padx=8, pady=2)
      ctk.CTkLabel(
          row_f,
          text=label_text,
          font=("Microsoft JhengHei", 12),
          width=75,
          anchor="w",
      ).pack(side="left")
      entry = ctk.CTkEntry(
          row_f, height=32, corner_radius=4, font=("Microsoft JhengHei", 12)
      )
      entry.pack(side="right", fill="x", expand=True)
      self.entries[key] = entry

    card3 = create_card("⭐ 評分與備註")
    fields_card3 = [("評分 (0-100)", "score"), ("備註", "notes")]
    for label_text, key in fields_card3:
      row_f = ctk.CTkFrame(card3, fg_color="transparent")
      row_f.pack(fill="x", padx=8, pady=2)
      ctk.CTkLabel(
          row_f,
          text=label_text,
          font=("Microsoft JhengHei", 12),
          width=75,
          anchor="w",
      ).pack(side="left")
      entry = ctk.CTkEntry(
          row_f, height=32, corner_radius=4, font=("Microsoft JhengHei", 12)
      )
      entry.pack(side="right", fill="x", expand=True)
      self.entries[key] = entry

    btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
    btn_frame.pack(fill="x", padx=8, pady=8)
    btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    ctk.CTkButton(
        btn_frame,
        text="新增",
        command=self.add_vendor,
        fg_color="#2b8a3e",
        hover_color="#237032",
        width=70,
        height=36,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=0, column=0, padx=1, pady=2)

    ctk.CTkButton(
        btn_frame,
        text="更新",
        command=self.update_vendor,
        fg_color="#e67700",
        hover_color="#d97000",
        width=70,
        height=36,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=0, column=1, padx=1, pady=2)

    ctk.CTkButton(
        btn_frame,
        text="刪除",
        command=self.delete_vendor,
        fg_color="#c92a2a",
        hover_color="#a61e1e",
        width=70,
        height=36,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=0, column=2, padx=1, pady=2)

    ctk.CTkButton(
        btn_frame,
        text="清除",
        command=self.clear_form,
        fg_color="#868e96",
        hover_color="#495057",
        width=70,
        height=36,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=0, column=3, padx=1, pady=2)

    # ================= 右側：查詢與表格面板 =================
    self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.right_frame.grid(
        row=0, column=1, sticky="nsew", padx=15, pady=15
    )
    self.right_frame.grid_rowconfigure(1, weight=1)
    self.right_frame.grid_columnconfigure(0, weight=1)

    search_card = ctk.CTkFrame(
        self.right_frame, fg_color=("gray92", "gray16"), corner_radius=8
    )
    search_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
    search_inner.pack(fill="x", padx=12, pady=10)

    self.toggle_btn = ctk.CTkButton(
        search_inner,
        text="◀ 收合表單",
        width=110,
        height=38,
        fg_color="#343a40",
        hover_color="#212529",
        command=self.toggle_sidebar,
        font=("Microsoft JhengHei", 13, "bold"),
    )
    self.toggle_btn.pack(side="left", padx=(0, 10))

    self.search_entry = ctk.CTkEntry(
        search_inner,
        placeholder_text="輸入任意關鍵字搜尋全部欄位...",
        height=38,
        width=260,
        font=("Microsoft JhengHei", 12),
    )
    self.search_entry.pack(side="left", padx=(0, 10))
    self.search_entry.bind("<Return>", lambda event: self.search_vendors())

    ctk.CTkButton(
        search_inner,
        text="查詢",
        width=80,
        height=38,
        command=self.search_vendors,
        font=("Microsoft JhengHei", 13, "bold"),
    ).pack(side="left", padx=4)

    ctk.CTkButton(
        search_inner,
        text="顯示全部",
        width=90,
        height=38,
        fg_color="gray",
        hover_color="darkgray",
        command=lambda: self.load_data(""),
        font=("Microsoft JhengHei", 13, "bold"),
    ).pack(side="left", padx=4)

    # 新增的「匯出 Excel」按鈕（採用 Excel 經典綠色識別）
    ctk.CTkButton(
        search_inner,
        text="匯出 Excel",
        width=100,
        height=38,
        fg_color="#107c41",
        hover_color="#0b5c30",
        command=self.export_excel,
        font=("Microsoft JhengHei", 13, "bold"),
    ).pack(side="left", padx=4)

    # 資料表格容器
    table_card = ctk.CTkFrame(
        self.right_frame, fg_color=("white", "gray13"), corner_radius=8
    )
    table_card.grid(row=1, column=0, sticky="nsew")
    table_card.grid_rowconfigure(0, weight=1)
    table_card.grid_columnconfigure(0, weight=1)

    columns = (
        "ID",
        "廠商姓名",
        "大項",
        "分類",
        "細目",
        "備註",
        "聯絡人1",
        "電話1",
        "傳真",
        "聯絡人2",
        "電話2",
        "聯絡人3",
        "電話3",
        "評分",
    )
    self.tree = ttk.Treeview(
        table_card, columns=columns, show="headings", selectmode="browse"
    )

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview.Heading",
        font=("Microsoft JhengHei", 12, "bold"),
        background="#f1f3f5",
        foreground="#212529",
    )
    style.configure(
        "Treeview",
        font=("Microsoft JhengHei", 11),
        rowheight=32,
        background="white",
        fieldbackground="white",
    )

    for col in columns:
      self.tree.heading(col, text=col)
      self.tree.column(col, width=100, anchor="center")

    tree_scroll_y = ttk.Scrollbar(
        table_card, orient="vertical", command=self.tree.yview
    )
    tree_scroll_x = ttk.Scrollbar(
        table_card, orient="horizontal", command=self.tree.xview
    )
    self.tree.configure(
        yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
    )

    self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    tree_scroll_y.grid(row=0, column=1, sticky="ns")
    tree_scroll_x.grid(row=1, column=0, sticky="ew")

    self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
    self.tree.bind("<Double-1>", self.on_double_click)
    self.selected_id = None

    self.col_mapping = {
        1: "vendor_name",
        2: "major_item",
        3: "category",
        4: "sub_item",
        5: "notes",
        6: "contact1",
        7: "phone1",
        8: "fax",
        9: "contact2",
        10: "phone2",
        11: "contact3",
        12: "phone3",
        13: "score",
    }

    if hasattr(self, "entry_edit") and self.entry_edit:
      try:
        self.entry_edit.destroy()
      except Exception:
        pass

  def toggle_sidebar(self):
    if self.is_collapsed:
      self.left_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
      self.toggle_btn.configure(text="◀ 收合表單")
      self.is_collapsed = False
    else:
      self.left_frame.grid_remove()
      self.toggle_btn.configure(text="▶ 展開表單")
      self.is_collapsed = True

  def load_data(self, query=""):
    for row in self.tree.get_children():
      self.tree.delete(row)

    if query:
      sql = """
                SELECT id, vendor_name, major_item, category, sub_item, notes, 
                      contact1, phone1, fax, contact2, phone2, contact3, phone3, score 
                FROM vendors 
                WHERE vendor_name LIKE ? OR major_item LIKE ? OR category LIKE ? 
                      OR sub_item LIKE ? OR notes LIKE ? OR contact1 LIKE ? 
                      OR phone1 LIKE ? OR fax LIKE ? OR contact2 LIKE ? 
                      OR phone2 LIKE ? OR contact3 LIKE ? OR phone3 LIKE ?
            """
      params = tuple([f"%{query}%"] * 12)
      self.cursor.execute(sql, params)
    else:
      self.cursor.execute("""
                SELECT id, vendor_name, major_item, category, sub_item, notes, 
                      contact1, phone1, fax, contact2, phone2, contact3, phone3, score 
                FROM vendors
            """)

    for row in self.cursor.fetchall():
      self.tree.insert("", "end", values=row)

  def export_excel(self):
    """匯出目前表格中的資料至 Excel 檔案"""
    try:
      file_path = filedialog.asksaveasfilename(
          defaultextension=".xlsx",
          filetypes=[("Excel 檔案", "*.xlsx")],
          initialfile=f"廠商資料_{datetime.now().strftime('%Y%m%d')}.xlsx",
      )
      if not file_path:
        return

      rows = []
      for item_id in self.tree.get_children():
        rows.append(self.tree.item(item_id, "values"))

      if not rows:
        messagebox.showwarning("警告", "目前沒有資料可供匯出！")
        return

      columns = [
          "ID",
          "廠商姓名",
          "大項",
          "分類",
          "細目",
          "備註",
          "聯絡人1",
          "電話1",
          "傳真",
          "聯絡人2",
          "電話2",
          "聯絡人3",
          "電話3",
          "評分",
      ]
      df = pd.DataFrame(rows, columns=columns)
      df.to_excel(file_path, index=False)
      messagebox.showinfo("成功", f"資料已成功匯出至：\n{file_path}")
    except Exception as e:
      messagebox.showerror("錯誤", f"匯出失敗：{str(e)}")

  def on_double_click(self, event):
    self.cancel_edit()

    region = self.tree.identify("region", event.x, event.y)
    if region != "cell":
      return

    item_id = self.tree.identify_row(event.y)
    column_id = self.tree.identify_column(event.x)
    if not item_id or not column_id:
      return

    col_idx = int(column_id.replace("#", "")) - 1
    if col_idx == 0:
      return

    bbox = self.tree.bbox(item_id, column_id)
    if not bbox:
      return
    x, y, width, height = bbox

    item_values = self.tree.item(item_id, "values")
    if len(item_values) <= col_idx:
      return
    cell_value = item_values[col_idx]

    self.entry_edit = tk.Entry(self.tree, font=("Microsoft JhengHei", 11))
    self.entry_edit.insert(0, cell_value if cell_value is not None else "")
    self.entry_edit.select_range(0, tk.END)
    self.entry_edit.focus()
    self.entry_edit.place(x=x, y=y, width=width, height=height)

    self.entry_edit.bind(
        "<Return>", lambda e, item=item_id, col=col_idx: self.save_edit(item, col)
    )
    self.entry_edit.bind("<FocusOut>", lambda e: self.cancel_edit())

  def save_edit(self, item_id, col_idx):
    if not hasattr(self, "entry_edit") or not self.entry_edit:
      return

    try:
      new_value = self.entry_edit.get().strip()
      self.cancel_edit()

      values = list(self.tree.item(item_id, "values"))
      if not values:
        return
      record_id = values[0]

      db_field = self.col_mapping.get(col_idx)
      if db_field == "score":
        if new_value:
          try:
            final_val = float(new_value)
          except ValueError:
            messagebox.showerror("格式錯誤", "評分欄位必須輸入有效的數字！")
            return
        else:
          final_val = 0.0
      else:
        final_val = new_value

      values[col_idx] = final_val if db_field != "score" else str(final_val)
      self.tree.item(item_id, values=values)

      if db_field:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            f"UPDATE vendors SET {db_field}=?, updated_at=? WHERE id=?",
            (final_val, now, record_id),
        )
        self.conn.commit()

        if self.selected_id == record_id:
          self.on_select_row(None)
    except Exception as e:
      messagebox.showerror("資料庫錯誤", f"即時更新失敗：{str(e)}")

  def cancel_edit(self):
    if hasattr(self, "entry_edit") and self.entry_edit:
      try:
        if self.entry_edit.winfo_exists():
          self.entry_edit.destroy()
      except Exception:
        pass
      self.entry_edit = None

  def add_vendor(self):
    data = {key: entry.get().strip() for key, entry in self.entries.items()}
    if not data.get("vendor_name"):
      messagebox.showerror("錯誤", "廠商姓名為必填欄位！")
      return

    try:
      now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.cursor.execute(
          """INSERT INTO vendors (major_item, category, sub_item, notes, vendor_name, 
                                  contact1, phone1, fax, contact2, phone2, contact3, phone3, score, updated_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
          (
              data.get("major_item", ""),
              data.get("category", ""),
              data.get("sub_item", ""),
              data.get("notes", ""),
              data.get("vendor_name", ""),
              data.get("contact1", ""),
              data.get("phone1", ""),
              data.get("fax", ""),
              data.get("contact2", ""),
              data.get("phone2", ""),
              "",
              "",
              float(data["score"]) if data.get("score") else 0.0,
              now,
          ),
      )
      self.conn.commit()
      self.load_data()
      self.clear_form()
      messagebox.showinfo("成功", "廠商資料已新增")
    except Exception as e:
      messagebox.showerror("資料庫錯誤", f"新增失敗：{str(e)}")

  def update_vendor(self):
    if not self.selected_id:
      messagebox.showwarning("警告", "請先從右側列表選擇要更新的廠商")
      return

    data = {key: entry.get().strip() for key, entry in self.entries.items()}
    try:
      now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      self.cursor.execute(
          """UPDATE vendors SET major_item=?, category=?, sub_item=?, notes=?, vendor_name=?, 
                                contact1=?, phone1=?, fax=?, contact2=?, phone2=?, score=?, updated_at=?
             WHERE id=?""",
          (
              data.get("major_item", ""),
              data.get("category", ""),
              data.get("sub_item", ""),
              data.get("notes", ""),
              data.get("vendor_name", ""),
              data.get("contact1", ""),
              data.get("phone1", ""),
              data.get("fax", ""),
              data.get("contact2", ""),
              data.get("phone2", ""),
              float(data["score"]) if data.get("score") else 0.0,
              now,
              self.selected_id,
          ),
      )
      self.conn.commit()
      self.load_data()
      self.clear_form()
      messagebox.showinfo("成功", "廠商資料已更新")
    except Exception as e:
      messagebox.showerror("資料庫錯誤", f"更新失敗：{str(e)}")

  def delete_vendor(self):
    if not self.selected_id:
      messagebox.showwarning("警告", "請先從右側列表選擇要刪除的廠商")
      return

    if not messagebox.askyesno(
        "確認刪除", "確定要刪除這筆廠商資料嗎？此動作無法復原。"
    ):
      return

    try:
      self.cursor.execute("DELETE FROM vendors WHERE id=?", (self.selected_id,))
      self.conn.commit()
      self.load_data()
      self.clear_form()
      messagebox.showinfo("成功", "廠商資料已刪除")
    except Exception as e:
      messagebox.showerror("資料庫錯誤", f"刪除失敗：{str(e)}")

  def on_select_row(self, event):
    selected_items = self.tree.selection()
    if not selected_items:
      return
    item = self.tree.item(selected_items[0])
    values = item["values"]
    if not values:
      return

    self.selected_id = values[0]
    self.cursor.execute(
        """SELECT major_item, category, sub_item, notes, vendor_name, 
                  contact1, phone1, fax, contact2, phone2, score 
           FROM vendors WHERE id=?""",
        (self.selected_id,),
    )
    row = self.cursor.fetchone()
    if row:
      keys = [
          "major_item",
          "category",
          "sub_item",
          "notes",
          "vendor_name",
          "contact1",
          "phone1",
          "fax",
          "contact2",
          "phone2",
          "score",
      ]
      for key, val in zip(keys, row):
        if key in self.entries:
          self.entries[key].delete(0, tk.END)
          self.entries[key].insert(0, str(val) if val is not None else "")

  def search_vendors(self):
    query = self.search_entry.get()
    self.load_data(query)

  def clear_form(self):
    self.selected_id = None
    for entry in self.entries.values():
      entry.delete(0, tk.END)


if __name__ == "__main__":
  app = VendorApp()
  app.mainloop()