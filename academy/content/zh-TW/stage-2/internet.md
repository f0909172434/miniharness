# 網際網路如何工作

> 對應 Goal：`G2.1`, `G2.2`, `G2.3` ｜ 練習預估 5 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.20

## 為什麼學這個

把「網站壞了」拆成能逐層定位的請求問題。

## 概念

URL 指定協定、主機與路徑。DNS 找到主機位址，TCP 建連線，HTTPS 另用 TLS 驗證與加密，HTTP 才交換方法、headers、狀態碼和 body。200 是成功；404 是資源不存在；429 應遵守重試等待；5xx 是伺服器端錯誤，仍須保存請求條件。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
import json
from urllib.request import Request, urlopen
req = Request("https://api.github.com/repos/python/cpython",
              headers={"User-Agent": "miniacademy-lesson"})
with urlopen(req, timeout=10) as response:
    print(response.status, response.headers.get("Content-Type"))
    data = json.load(response)
print(data["full_name"])
```

### 預期結果

有網路且未受限時，輸出狀態 200、JSON 類型與 python/cpython。它是公開 API，離線或限流時失敗屬於要記錄的環境條件。

## 練習與驗收

畫出 URL→DNS→TCP/TLS→HTTP→JSON 流程。保留一次真實回應的時間與 headers；另以本機 fixture 測試解析器，避免測試依賴 GitHub 網路。區分 HTTPError、URLError 與 JSON 解析錯誤，給出不同訊息。

## 常見坑

設定 timeout 不代表所有失敗都適合重試；POST 等有副作用的動作需要額外設計。本課只讀公開資料，不需 token，也不要把 token 放進 URL。

## 自測清單

- [ ] `G2.1` 能畫圖解釋「瀏覽器輸入 URL 之後發生什麼」（DNS/TCP/HTTP 簡化版）。證據方式：`self`。
- [ ] `G2.2` 能用 curl 或 Python 的 urllib 讀取一個公開 API 的回應。證據方式：`self`。
- [ ] `G2.3` 能解釋請求/回應結構、常見狀態碼與 header 的含義。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)。
