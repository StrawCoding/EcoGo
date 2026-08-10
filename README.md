# EcoGo

台灣換電／加油站間隔路線規劃（開源）。

線上：https://ecogo.wastebase.xyz/

依 **Ionex 換電站**、**Gogoro 換電站**、**加油站** 與自訂間隔距離，用 **Google Maps Directions** 規劃最適停靠路線，並一鍵開啟／複製 Google Maps 導航連結。

## 功能

- 自選地址（Google Places Autocomplete）或地圖點選起終點
- 汽車／機車模式（機車：`avoidHighways` + `avoidTolls`，避開國道／收費快速道路）
- 各站類型獨立間隔（例：Ionex 每 40 km）
- 規劃後直開 Google Maps（含 waypoints）
- 站點資料：沿線示範站點，或優先 OpenStreetMap Overpass

## 使用

1. 開啟 https://ecogo.wastebase.xyz/
2. 貼上你的 Google Maps API Key → **載入**
3. 選汽車／機車，輸入起終點，設定間隔 → **用 Google Maps 規劃**
4. **開啟 Google Maps** 或 **複製 Maps 連結**

### API Key 需求

在 [Google Cloud Console](https://console.cloud.google.com/) 啟用：

- Maps JavaScript API
- Places API
- Directions API

建議將金鑰限制為 HTTP referrer：`https://ecogo.wastebase.xyz/*`（自架則改成你的網域）。

金鑰只存在瀏覽器 `localStorage`，不會上傳到 EcoGo 伺服器。

## 本機開啟

純靜態單檔，無需建置：

```bash
# 任選靜態伺服器
python3 -m http.server 8080
# 開啟 http://127.0.0.1:8080/
```

或直接用瀏覽器開啟 `index.html`（部分瀏覽器對 `file://` 載入 Maps API 有限制，建議用本機 HTTP）。

## 技術

| 項目 | 作法 |
|------|------|
| 路線 | Google Maps DirectionsService（DRIVING） |
| 地址 | Places Autocomplete + Geocoder |
| 機車 | avoidHighways + avoidTolls |
| 選站 | 沿路徑依間隔找最近站，再以 waypoints 精算 |
| 匯出 | Google Maps `/dir/` 深連結 |
| 站點備援 | OSM Overpass（可選）／內建沿線示範資料 |

## 授權

[MIT](LICENSE)

## 貢獻

Issue／PR 歡迎。請勿把 API Key 或密鑰提交進 repo。
