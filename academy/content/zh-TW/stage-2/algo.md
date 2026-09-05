# 演算法與複雜度入門

> 對應 Goal：`G2.12`, `G2.13`, `G2.14` ｜ 練習預估 6 小時（包含專案與反覆練習，不是閱讀時長）
> 前置：G1.6

## 為什麼學這個

資料量增加時，用操作數量理解程式為何變慢。

## 概念

大 O 描述輸入規模增加時的成長上界，不是實際秒數。排序後可用二分搜尋，把每輪剩餘範圍折半；set 查重的常見平均成本是 O(n)，但需要額外空間，雜湊也有最壞情況。

## 動手

從倉庫根目錄執行；獨立 Python 片段先存成練習檔再執行。帶有「你要交付」的命令是作業介面，需要先自己完成程式。

```python
def find_sorted(items, target):
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo < len(items) and items[lo] == target else -1

print(find_sorted([1, 3, 3, 8], 3))
print(find_sorted([], 3))
```

### 預期結果

輸出 1 與 -1；採半開區間 [lo,hi)，重複值回傳最左位置。

## 練習與驗收

實作 insertion sort 並用逆序與已排序輸入數比較次數。再將雙層迴圈找重複值改成 seen set，測空資料、重複與大量唯一值；記錄時間和操作數，分清 O(n²) 排序、O(log n) 搜尋及排序前置成本。

## 常見坑

不能把二分搜尋直接用在未排序的輸入。只測一個 n 的耗時無法支持成長率結論。

## 自測清單

- [ ] `G2.12` 能用大 O 描述常見操作的複雜度並解釋其含義。證據方式：`self`。
- [ ] `G2.13` 能實作二分搜尋與一種簡單排序並分析複雜度。證據方式：`self`。
- [ ] `G2.14` 能用 dict/set 把一個 O(n²) 的解法降到 O(n)。證據方式：`self`。

`ready` 表示教材可閱讀，並非你已完成目標。自動檢查只驗其明列契約，專案、外部回饋與人工解釋需留下真實證據。

## 下一步

回到 [課程總覽](../../../../README.md) 選下一課，或執行 `python3 tools/academy.py next`。

延伸閱讀：[原始文件](https://docs.python.org/3/library/bisect.html)。
