import { useRef } from "react";
import { useScrollProgress } from "../hooks.js";

import manifest from "../../../academy/manifest.json";
const SOURCE = "https://github.com/f0909172434/miniharness/blob/main/";
const STAGES = manifest.stages.map(stage => ({
  ...stage,
  hours: stage.modules.reduce((n, module) => n + module.hours, 0),
  ready: stage.modules.filter(module => module.status === "ready"),
}));

/** 章 A：路線坡道被滾動「畫」出來，最後一筆是通電。 */
export default function PathSection() {
  const ref = useRef(null);
  const progress = useScrollProgress(ref);

  return (
    <section className="chapter wrap" id="path" ref={ref} aria-labelledby="path-title">
      <div className="chapter-head">
        <span className="chapter-no">章 · 壹</span>
        <span className="chapter-sub" style={{ margin: 0 }}>
          六個階段，教材狀態公開
        </span>
      </div>
      <h2 id="path-title">先讀已完成的教材，再看路線規劃</h2>
      <p className="chapter-sub">目前 2 / 38 個模組有教材。其餘為規劃中的學習目標；時數是課程估計，現有正文以繁體中文提供。</p>
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
              {stage.title[manifest.default_locale]}
              <span className="hours">約 {stage.hours}h</span>
            </h3>
            <p>{stage.tagline[manifest.default_locale]}</p>
            <p className="module-status">{stage.ready.length} / {stage.modules.length} 個模組可讀 · {stage.modules.length - stage.ready.length} 個規劃中</p>
            {stage.ready.map(module => <div className="lesson-entry" key={module.id}>
              <strong>{module.title[manifest.default_locale]}</strong>
              {module.content[manifest.default_locale].map((path, i) => <a href={SOURCE + path} key={path}>閱讀教材{module.content[manifest.default_locale].length > 1 ? ` ${i + 1}` : ""} ↗</a>)}
            </div>)}
          </div>
        ))}
      </div>

      <p className="path-end" aria-hidden="true">
        —— 線畫完了，下一頁：通電。
      </p>
    </section>
  );
}
