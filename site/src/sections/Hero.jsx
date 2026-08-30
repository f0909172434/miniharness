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
        這是一條從零計算機基礎走到 AI 研究員的路線：6 個階段、110 條可驗證的
        Goal，以及一台你馬上就能通電的 agent 循環機器。紙上寫的、機器跑的，
        都是這個倉庫裡真實的東西。
      </p>

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
