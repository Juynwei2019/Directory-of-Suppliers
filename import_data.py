from datetime import datetime
import sqlite3
import pandas as pd

# 1. 讀取現有資料檔案（支援 .xlsx 或 .csv）
file_path = "vendors_data.xlsx"  # 請確認您的檔案名稱是否正確

if file_path.endswith(".csv"):
  df = pd.read_csv(file_path)
else:
  df = pd.read_excel(file_path)

# 2. 連接 SQLite 資料庫
conn = sqlite3.connect("vendors.db")
cursor = conn.cursor()

# 確保資料表存在
cursor.execute("""
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

# 3. 清空舊資料並重設 ID 流水號（實現「完全重倒」）
cursor.execute("DELETE FROM vendors")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='vendors'")

# 4. 逐筆處理並寫入資料庫
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
success_count = 0

for index, row in df.iterrows():
  vendor_name = (
      str(row.get("廠商姓名", "")) if pd.notna(row.get("廠商姓名")) else ""
  )
  if not vendor_name:
    continue  # 若無廠商姓名則跳過

  major_item = str(row.get("大項", "")) if pd.notna(row.get("大項")) else ""
  category = str(row.get("分類", "")) if pd.notna(row.get("分類")) else ""
  sub_item = str(row.get("細目", "")) if pd.notna(row.get("細目")) else ""
  notes = str(row.get("備註", "")) if pd.notna(row.get("備註")) else ""
  contact1 = str(row.get("聯絡人1", "")) if pd.notna(row.get("聯絡人1")) else ""
  phone1 = str(row.get("電話1", "")) if pd.notna(row.get("電話1")) else ""
  fax = str(row.get("傳真", "")) if pd.notna(row.get("傳真")) else ""
  contact2 = str(row.get("聯絡人2", "")) if pd.notna(row.get("聯絡人2")) else ""
  phone2 = str(row.get("電話2", "")) if pd.notna(row.get("電話2")) else ""
  contact3 = str(row.get("聯絡人3", "")) if pd.notna(row.get("聯絡人3")) else ""
  phone3 = str(row.get("電話3", "")) if pd.notna(row.get("電話3")) else ""
  score = float(row.get("評分", 0.0)) if pd.notna(row.get("評分")) else 0.0

  cursor.execute(
      """INSERT INTO vendors (major_item, category, sub_item, notes, vendor_name, 
                              contact1, phone1, fax, contact2, phone2, contact3, phone3, score, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
      (
          major_item,
          category,
          sub_item,
          notes,
          vendor_name,
          contact1,
          phone1,
          fax,
          contact2,
          phone2,
          contact3,
          phone3,
          score,
          now,
      ),
  )
  success_count += 1

conn.commit()
conn.close()
print(f"成功清空舊資料並重新匯入 {success_count} 筆廠商資料！")