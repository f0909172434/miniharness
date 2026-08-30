import { useRef } from "react";
import { useScrollProgress } from "../hooks.js";

const STAGES = [
  { id: 0, title: "零基礎起步", hours: 9, line: "終端機、檔案、第一支程式——把電腦從黑箱變成方向盤。" },
  { id: 1, title: "Python 程式核心", hours: 36, line: "變量到工程：獨立交付一個命令行工具。" },
  { id: 2, title: "工程與系統基礎", hours: 40, line: "測試、打包、協作、呼叫 API：從會寫代碼到會做軟體。" },
  { id: 3, title: "數學與機器學習", hours: 60, line: "夠用的數學 + 一條端到端 ML 流水線。" },
  { id: 4, title: "深度學習與 LLM", hours: 80, line: "手推注意力，親手訓練自己的小模型。" },
  { id: 5, title: "Agent 工程與研究方法", hours: 80, line: "MiniHarness 全套 + 復現論文 + 公開作品。" },
];

/** 章 A：路線坡道被滾動「畫」出來，最後一筆是通電。 */
export default function PathSection() {
  const ref = useRef(null);
  const progress = useScrollProgress(ref);

  return (
    <section className="chapter wrap" id="path" ref={ref} aria-labelledby="path-title">
      <div className="chapter-head">
        <span className="chapter-no">章 · 壹</span>
        <span className="chapter-sub" style={{ margin: 0 }}>
          六個階段，一條被工程化的路
        </span>
      </div>
      <h2 id="path-title">從零到研究員，每一步都有驗收</h2>
      <hr className="rule" />

      <div className="path" style={{ "--draw": Math.min(1, progress * 1.6) }}>
        {STAGES.map((stage, index) => (
          <div
            key={stage.id}
            className={`path-stop${progress > (index + 0.5) / STAGES.length ? " lit" : ""}`}
          >
            <span className="path-dot" aria-hidden="true">{stage.id}</span>
            <span className="path-stage">STAGE {stage.id}</span>
            <h3>
              {stage.title}
              <span className="hours">{stage.hours}h</span>
            </h3>
            <p>{stage.line}</p>
          </div>
        ))}
      </div>

      <p className="path-end" aria-hidden="true">
        —— 線畫完了，下一頁：通電。
      </p>
    </section>
  );
}
