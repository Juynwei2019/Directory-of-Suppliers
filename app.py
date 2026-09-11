from datetime import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class VendorApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("廠商資料維護系統 (專業版)")
    self.geometry("1300x750")

    self.init_db()
    self.create_widgets()
    self.load_data()

    self.is_collapsed = False  # 記錄左側表單是否收合

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

    # ================= 左側：一般框架面板 (無捲軸) =================
    self.left_frame = ctk.CTkFrame(self, width=380, corner_radius=0)
    self.left_frame.grid(
        row=0, column=0, sticky="nsew", padx=0, pady=0
    )
    self.left_frame.grid_propagate(False)  # 固定寬度不被內部元件擠壓

    # 標題
    title_label = ctk.CTkLabel(
        self.left_frame,
        text="廠商資料表單",
        font=("Microsoft JhengHei", 16, "bold"),
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
          font=("Microsoft JhengHei", 12, "bold"),
          text_color=("gray30", "gray70"),
      ).pack(anchor="w", padx=10, pady=(4, 2))
      return card

    # 卡片 1：基本與分類
    card1 = create_card("📌 基本與分類資訊")
    fields_card1 = [
        ("廠商姓名*", "vendor_name"),
        ("大項", "major_item"),
        ("分類", "category"),
        ("細目", "sub_item"),
    ]
    for label_text, key in fields_card1:
      row_f = ctk.CTkFrame(card1, fg_color="transparent")
      row_f.pack(fill="x", padx=10, pady=1)
      ctk.CTkLabel(
          row_f,
          text=label_text,
          font=("Microsoft JhengHei", 10),
          width=75,
          anchor="w",
      ).pack(side="left")
      entry = ctk.CTkEntry(row_f, height=26, corner_radius=4)
      entry.pack(side="right", fill="x", expand=True)
      self.entries[key] = entry

    # 卡片 2：聯絡人與通訊
    card2 = create_card("📞 聯絡人與通訊資訊")
    fields_card2 = [
        ("傳真", "fax"),
        ("聯絡人 1", "contact1"),
        ("電話 1", "phone1"),
        ("聯絡人 2", "contact2"),
        ("電話 2", "phone2"),
        ("聯絡人 3", "contact3"),
        ("電話 3", "phone3"),
    ]
    for label_text, key in fields_card2:
      row_f = ctk.CTkFrame(card2, fg_color="transparent")
      row_f.pack(fill="x", padx=10, pady=1)
      ctk.CTkLabel(
          row_f,
          text=label_text,
          font=("Microsoft JhengHei", 10),
          width=75,
          anchor="w",
      ).pack(side="left")
      entry = ctk.CTkEntry(row_f, height=26, corner_radius=4)
      entry.pack(side="right", fill="x", expand=True)
      self.entries[key] = entry

    # 卡片 3：評分與備註
    card3 = create_card("⭐ 評分與備註")
    fields_card3 = [("評分 (0-100)", "score"), ("備註", "notes")]
    for label_text, key in fields_card3:
      row_f = ctk.CTkFrame(card3, fg_color="transparent")
      row_f.pack(fill="x", padx=10, pady=1)
      ctk.CTkLabel(
          row_f,
          text=label_text,
          font=("Microsoft JhengHei", 10),
          width=75,
          anchor="w",
      ).pack(side="left")
      entry = ctk.CTkEntry(row_f, height=26, corner_radius=4)
      entry.pack(side="right", fill="x", expand=True)
      self.entries[key] = entry

    # 操作按鈕區 (2x2 網格排列)
    btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
    btn_frame.pack(fill="x", padx=8, pady=8)
    btn_frame.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkButton(
        btn_frame,
        text="新增資料",
        command=self.add_vendor,
        fg_color="#2b8a3e",
        hover_color="#237032",
        height=32,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=0, column=0, padx=2, pady=2, sticky="ew")

    ctk.CTkButton(
        btn_frame,
        text="更新資料",
        command=self.update_vendor,
        fg_color="#e67700",
        hover_color="#d97000",
        height=32,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

    ctk.CTkButton(
        btn_frame,
        text="刪除資料",
        command=self.delete_vendor,
        fg_color="#c92a2a",
        hover_color="#a61e1e",
        height=32,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=1, column=0, padx=2, pady=2, sticky="ew")

    ctk.CTkButton(
        btn_frame,
        text="清除重設",
        command=self.clear_form,
        fg_color="#868e96",
        hover_color="#495057",
        height=32,
        font=("Microsoft JhengHei", 11, "bold"),
    ).grid(row=1, column=1, padx=2, pady=2, sticky="ew")

    # ================= 右側：查詢與表格面板 =================
    self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.right_frame.grid(
        row=0, column=1, sticky="nsew", padx=15, pady=15
    )
    self.right_frame.grid_rowconfigure(1, weight=1)
    self.right_frame.grid_columnconfigure(0, weight=1)

    # 搜尋列框架
    search_card = ctk.CTkFrame(
        self.right_frame, fg_color=("gray92", "gray16"), corner_radius=8
    )
    search_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
    search_inner.pack(fill="x", padx=12, pady=10)

    # 表單收合/展開切換按鈕
    self.toggle_btn = ctk.CTkButton(
        search_inner,
        text="◀ 收合表單",
        width=100,
        height=36,
        fg_color="#343a40",
        hover_color="#212529",
        command=self.toggle_sidebar,
        font=("Microsoft JhengHei", 12, "bold"),
    )
    self.toggle_btn.pack(side="left", padx=(0, 10))

    self.search_entry = ctk.CTkEntry(
        search_inner,
        placeholder_text="輸入任意關鍵字搜尋全部欄位...",
        height=36,
        width=250,
    )
    self.search_entry.pack(side="left", padx=(0, 10))
    self.search_entry.bind("<Return>", lambda event: self.search_vendors())

    ctk.CTkButton(
        search_inner,
        text="查詢",
        width=80,
        height=36,
        command=self.search_vendors,
        font=("Microsoft JhengHei", 12),
    ).pack(side="left", padx=3)
    ctk.CTkButton(
        search_inner,
        text="顯示全部",
        width=80,
        height=36,
        fg_color="gray",
        hover_color="darkgray",
        command=lambda: self.load_data(""),
        font=("Microsoft JhengHei", 12),
    ).pack(side="left", padx=3)

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
        font=("Microsoft JhengHei", 11, "bold"),
        background="#f1f3f5",
        foreground="#212529",
    )
    style.configure(
        "Treeview",
        font=("Microsoft JhengHei", 10),
        rowheight=26,
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
    self.selected_id = None

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

  def add_vendor(self):
    data = {key: entry.get() for key, entry in self.entries.items()}
    if not data["vendor_name"]:
      messagebox.showerror("錯誤", "廠商姓名為必填欄位！")
      return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.cursor.execute(
        """INSERT INTO vendors (major_item, category, sub_item, notes, vendor_name, 
                                contact1, phone1, fax, contact2, phone2, contact3, phone3, score, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["major_item"],
            data["category"],
            data["sub_item"],
            data["notes"],
            data["vendor_name"],
            data["contact1"],
            data["phone1"],
            data["fax"],
            data["contact2"],
            data["phone2"],
            data["contact3"],
            data["phone3"],
            float(data["score"]) if data["score"] else 0.0,
            now,
        ),
    )
    self.conn.commit()
    self.load_data()
    self.clear_form()
    messagebox.showinfo("成功", "廠商資料已新增")

  def update_vendor(self):
    if not self.selected_id:
      messagebox.showwarning("警告", "請先從右側列表選擇要更新的廠商")
      return

    data = {key: entry.get() for key, entry in self.entries.items()}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    self.cursor.execute(
        """UPDATE vendors SET major_item=?, category=?, sub_item=?, notes=?, vendor_name=?, 
                              contact1=?, phone1=?, fax=?, contact2=?, phone2=?, contact3=?, phone3=?, score=?, updated_at=?
           WHERE id=?""",
        (
            data["major_item"],
            data["category"],
            data["sub_item"],
            data["notes"],
            data["vendor_name"],
            data["contact1"],
            data["phone1"],
            data["fax"],
            data["contact2"],
            data["phone2"],
            data["contact3"],
            data["phone3"],
            float(data["score"]) if data["score"] else 0.0,
            now,
            self.selected_id,
        ),
    )
    self.conn.commit()
    self.load_data()
    self.clear_form()
    messagebox.showinfo("成功", "廠商資料已更新")

  def delete_vendor(self):
    if not self.selected_id:
      messagebox.showwarning("警告", "請先從右側列表選擇要刪除的廠商")
      return

    if not messagebox.askyesno(
        "確認刪除", "確定要刪除這筆廠商資料嗎？此動作無法復原。"
    ):
      return

    self.cursor.execute("DELETE FROM vendors WHERE id=?", (self.selected_id,))
    self.conn.commit()
    self.load_data()
    self.clear_form()
    messagebox.showinfo("成功", "廠商資料已刪除")

  def on_select_row(self, event):
    selected_items = self.tree.selection()
    if not selected_items:
      return
    item = self.tree.item(selected_items[0])
    values = item["values"]

    self.selected_id = values[0]
    self.cursor.execute(
        """SELECT major_item, category, sub_item, notes, vendor_name, 
                  contact1, phone1, fax, contact2, phone2, contact3, phone3, score 
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
          "contact3",
          "phone3",
          "score",
      ]
      for key, val in zip(keys, row):
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