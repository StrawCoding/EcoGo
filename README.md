# EcoGo

台灣換電／加油站間隔路線規劃（開源 · 完全免費）。

線上：https://ecogo.wastebase.xyz/

依 **Ionex 換電站**、**Gogoro 換電站**、**加油站** 與自訂間隔距離，用 **免費開源路線引擎** 規劃最適停靠路線，並一鍵開啟／複製 Google Maps 導航連結（無需 Google API Key）。

## 功能

- 自選地址（地標別名／座標／Photon＋Nominatim 並行／台灣門牌正規化與結構化查詢）或地圖點選起終點
- 汽車／機車模式（機車：Valhalla `motor_scooter`，排除國道／快速道路）
- 各站類型獨立間隔（例：Ionex 每 40 km）
- 規劃後直開 Google Maps（含 waypoints，免費深連結）
- 站點資料：預設 **Ionex 官方地圖快取**（`api.ionex.com.tw/location`，與 [map.ionex.com.tw](https://map.ionex.com.tw/) 同源）、可改 OSM Overpass，或沿線示範站點

## 使用

1. 開啟 https://ecogo.wastebase.xyz/
2. 選汽車／機車，輸入起終點（或地圖點選；瀏覽器會記住上次起終點文字）
3. 設定間隔 → **用開源路線規劃**
4. **開啟 Google Maps** 或 **複製 Maps 連結**

無需任何 API Key。

## 地址解析方案（免費）

1. **地標別名**：台北車站、左營高鐵、台大等常用點
2. **座標貼上**：`25.0478,121.5170`
3. **Photon + Nominatim 並行**，結果去重排序
4. **台灣門牌正規化**：全形數字、台/臺互換、`路名+門牌` 空白化，並用 Nominatim structured（street/city）補強
5. **失敗備援**：改用地名／路名，或地圖點選

說明：開源 OSM 對台灣「完整門牌號」覆蓋有限；地名／車站／路名通常最穩。若未來要 100% 門牌精度，可再接政府 TGOS／內政部地址 API（需申請，非純開源）。

## 本機開啟

純靜態單檔，無需建置：

```bash
python3 -m http.server 8080
# 開啟 http://127.0.0.1:8080/
```

### 更新 Ionex 站點快取

地圖站點來自 Ionex 公開 location API（與 [map.ionex.com.tw](https://map.ionex.com.tw/) 同源）。定期執行：

```bash
python3 scripts/sync_ionex_stations.py
# 產出 data/stations-ionex.json，並同步到部署目錄（若存在）
```

建議 cron 每日一次。Gogoro 暫無同等公開來源時，可併用 OSM 或示範站。

## 技術

| 項目 | 作法（免費開源） |
|------|------|
| 地圖 | Leaflet + OpenStreetMap tiles |
| 路線 | Valhalla（主）／OSRM（汽車備援） |
| 機車 | Valhalla `motor_scooter` + `use_highways:0` |
| 地址 | 別名／座標／Photon／Nominatim（含結構化） |
| 選站 | 沿路徑依間隔找最近站，再以 waypoints 精算 |
| 匯出 | Google Maps `/dir/` 深連結（免金鑰） |
| 站點 | Ionex 官方地圖預抓快取；OSM／示範站備援 |

公開服務來源：

- Valhalla：`valhalla1.openstreetmap.de`
- OSRM：`router.project-osrm.org`
- Photon：`photon.komoot.io`
- Nominatim：`nominatim.openstreetmap.org`
- Ionex 站點：`api.ionex.com.tw/location`（官網地圖同源）

請遵守各服務的使用規範與公平使用；重度自架建議自行部署 Valhalla／OSRM。

## 授權

[MIT](LICENSE)

## 貢獻

Issue／PR 歡迎。
