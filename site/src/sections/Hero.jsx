import { usePrefersReducedMotion } from "../hooks.js";

/** 首屏：一頁幾乎空白的手稿，一句命題，一個自己畫出自己的循環。 */
export default function Hero() {
  const reduced = usePrefersReducedMotion();
  return (
    <header className="hero wrap" id="top">
      <p className="hero-kicker">MINIACADEMY × MINIHARNESS · 手稿成機</p>
      <h1>
        <span className="model">智能在模型</span>，
        <br />
        工程在<span className="harness">harness</span>
        <span aria-hidden="true">。</span>
        <span className="cursor-block" aria-hidden="true" />
      </h1>
      <p className="hero-sub">
        先操作一台 agent 循環，再親手寫出自己的 harness。這裡有離線範例、
        十章概念文檔與八步動手營。延伸課程規劃了 38 個模組，目前 2 個已有教材、
        36 個仍在編寫。
      </p>

      <div className="start-links"><a href="#machine">操作循環機器 ↓</a><a href="#path">找到可讀教材 ↓</a><a href="https://github.com/f0909172434/miniharness">原始碼 ↗</a></div>

      <svg
        className={`hero-loop${reduced ? "" : " draw-on-load"}`}
        viewBox="0 0 200 200"
        role="img"
        aria-label="一個標著『機』字的循環箭頭，代表 agent loop"
      >
        <g className="spin-slow" style={reduced ? { animation: "none" } : undefined}>
          <circle
            className="loop-path"
            cx="100"
            cy="100"
            r="76"
            fill="none"
            style={{ transformOrigin: "100px 100px", rotate: reduced ? undefined : "0deg" }}
          />
          <polygon className="loop-arrow" points="100,16 112,38 88,38" />
        </g>
        <text className="loop-word" x="100" y="112" textAnchor="middle">
          機
        </text>
      </svg>

      <p className="scroll-cue">往下滾動 · 機器被畫出來</p>
    </header>
  );
}
