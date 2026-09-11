# 專案開發 Prompt：廠商資料維護與匯入管理系統

## 1. 專案背景與架構概述
本系統為一套基於 Python 開發的廠商資料維護與管理解決方案，結合了 **CustomTkinter** 現代化圖形介面、**SQLite** 本地資料庫、**ttk.Treeview** 互動式表格以及 **Pandas** 數據處理與 Excel 匯入/匯出功能。系統主要分為桌面互動維護端 (`app.py`) 與批次資料初始化匯入腳本 (`import_data.py`)。

---

## 2. 資料庫綱要 (Database Schema)
系統使用 SQLite 資料庫（檔名：`vendors.db`），核心資料表 `vendors` 的結構與欄位定義如下：
* `id`: 唯一識別碼（主鍵，自動遞增）
* `major_item`: 大項 (TEXT)
* `category`: 分類 (TEXT)
* `sub_item`: 細目 (TEXT)
* `notes`: 備註 (TEXT)
* `vendor_name`: 廠商姓名（NOT NULL，必填欄位）
* `contact1`, `phone1`: 聯絡人 1 與電話 1 (TEXT)
* `fax`: 傳真 (TEXT)
* `contact2`, `phone2`: 聯絡人 2 與電話 2 (TEXT)
* `contact3`, `phone3`: 聯絡人 3 與電話 3 (TEXT)
* `score`: 評分（REAL，預設 0.0）
* `updated_at`: 最後更新時間戳記 (TEXT)

---

## 3. 核心模組一：廠商資料維護應用程式 (`app.py`)
此模組為桌面 GUI 應用程式，提供視覺化的完整 CRUD 與高效互動操作：
* **介面佈局與設計**：
  * **左側表單面板**：寬度設定為 360px，支援收合與展開切換（`toggle_sidebar`）。表單內部以卡片式區塊分群：
    1. *📌 基本與分類資訊*：廠商姓名*、大項、分類、細目。
    2. *📞 聯絡人與通訊*：傳真、聯絡人 1、電話 1、聯絡人 2、電話 2（第 3 組聯絡資訊在表單隱藏，但後端預設帶空值）。
    3. *⭐ 評分與備註*：評分 (0-100)、備註。
  * **操作按鈕區**：於表單底部設置單列並排的 4 個等寬精簡按鈕：新增、更新、刪除、清除。
  * **右側查詢與表格面板**：包含收合按鈕、全欄位關鍵字搜尋框、「查詢」、「顯示全部」以及經典綠色識別的「匯出 Excel」按鈕。
  * **資料表格 (`ttk.Treeview`)**：完整顯示包含 ID、廠商姓名、各項分類、備註、聯絡人 1~3、電話 1~3、傳真與評分的所有欄位。
* **互動編輯功能**：
  * 支援**雙擊儲存格直接編輯**（`on_double_click`），除 ID 欄位外，使用者直接在表格上雙擊任意儲存格即可跳出輸入框修改，按下 `Enter` 鍵或失去焦點（`FocusOut`）時自動驗證、即時寫入 SQLite 資料庫並刷新介面。
* **Excel 匯出功能**：
  * 點擊「匯出 Excel」可透過系統檔案對話框選擇儲存路徑，將當前畫面的表格資料透過 `pandas` 快速匯出為 `.xlsx` 檔案。

---

## 4. 核心模組二：批次初始化匯入工具 (`import_data.py`)
此模組為獨立的資料初始化腳本，用於批次將外部試算表匯入系統中：
* **完全重置機制 (Wipe-and-Reload)**：執行時會自動清空 `vendors` 表格中的所有舊資料，並重置 SQLite 的流水號計數器（`sqlite_sequence`），確保匯入後的 ID 從 1 開始重新計算。
* **資料解析與防呆**：支援讀取 `.xlsx` 或 `.csv` 檔案（例如 `vendors_data.xlsx`）。逐列檢查「廠商姓名」是否存在，若無則自動略過；其餘欄位（大項、分類、細目、備註、聯絡人 1~3、電話 1~3、評分）進行安全轉型後批次寫入資料庫。

---

## 5. 後續開發與維護指引 (Developer Instructions)
* **欄位擴充考量**：未來若需將 `contact3` 與 `phone3` 放回左側 UI 表單中，僅需調整 `create_widgets()` 中的 `fields_card2` 陣列，並確保 `add_vendor`、`update_vendor` 與 `on_select_row` 的 SQL 查詢對應正確。
* **打包與部署**：若需將本系統打包為獨立的 `.exe` 執行檔供無 Python 環境的使用者執行，建議使用 PyInstaller 並帶入以下參數以完整打包依賴套件：
  ```bash
  pyinstaller --noconsole --onefile --collect-all customtkinter --collect-all pandas --collect-all openpyxl app.py
  ```
