import { useRef, useState } from "react";
import { useScrollProgress } from "../hooks.js";
import manifest from "../../../academy/manifest.json";
const SOURCE = "https://github.com/f0909172434/miniharness/blob/main/";
const STAGES = manifest.stages.map(stage => ({
  ...stage,
  hours: stage.modules.reduce((n, module) => n + module.hours, 0),
  ready: stage.modules.filter(module => module.status === "ready"),
}));
const TOTAL = STAGES.reduce((n, stage) => n + stage.modules.length, 0);
const READY = STAGES.reduce((n, stage) => n + stage.ready.length, 0);

/** 章壹：從路線走進教材抽屜；搜尋與展開均不改寫學習進度。 */
export default function PathSection() {
  const ref = useRef(null);
  const progress = useScrollProgress(ref);
  const [query, setQuery] = useState("");
  const needle = query.trim().toLocaleLowerCase();
  const match = module => !needle || [module.title[manifest.default_locale], module.title.en,
    module.id, ...module.goals].join(" ").toLocaleLowerCase().includes(needle);
  const matches = STAGES.reduce((n, stage) => n + stage.ready.filter(match).length, 0);

  return <section className="chapter wrap" id="path" ref={ref} aria-labelledby="path-title">
    <div className="chapter-head"><span className="chapter-no">章 · 壹</span><span className="chapter-sub" style={{ margin: 0 }}>六個階段，一課一個可檢查的成果</span></div>
    <h2 id="path-title">打開一課，動手留下結果。</h2>
    <p className="chapter-sub">{READY} / {TOTAL} 個模組已有繁體中文教材、練習與驗收指引。時數包含專案與反覆練習；教材可讀和學習者通過，是兩件需要各自確認的事。</p>
    <div className="lesson-search">
      <label htmlFor="lesson-search">找教材</label>
      <input id="lesson-search" type="search" placeholder="例如 Python、Transformer、G3.17" value={query} onChange={e => setQuery(e.target.value)} />
      <span role="status">{matches} 個模組</span>
    </div>
    <div className="path" style={{ "--draw": Math.min(1, progress * 1.6) }}>
      {STAGES.map((stage, index) => {
        const modules = stage.ready.filter(match);
        if (needle && !modules.length) return null;
        return <div key={stage.id} className={`path-stop${progress > (index + 0.5) / STAGES.length ? " lit" : ""}`}>
          <span className="path-dot" aria-hidden="true">{stage.id}</span>
          <span className="path-stage">STAGE {stage.id}</span>
          <h3>{stage.title[manifest.default_locale]}<span className="hours">練習約 {stage.hours}h</span></h3>
          <p>{stage.tagline[manifest.default_locale]}</p>
          <details className="stage-lessons" open={needle ? true : stage.id === 0}>
            <summary>{modules.length} 課教材 · 展開閱讀入口</summary>
            <div className="stage-lesson-list">{modules.map(module => <div className="lesson-entry" key={module.id}>
              <div><strong>{module.title[manifest.default_locale]}</strong><small>{module.goals.join(" · ")}</small></div>
              <a href={SOURCE + module.content[manifest.default_locale][0]} aria-label={`閱讀：${module.title[manifest.default_locale]}`}>閱讀教材 ↗</a>
              {module.content[manifest.default_locale].length > 1 && <details className="lesson-catalogue">
                <summary>完整 {module.content[manifest.default_locale].length} 份教材</summary>
                <ol>{module.content[manifest.default_locale].map(path => <li key={path}><a href={SOURCE + path}>{path.split("/").pop().replace(".md", "")} ↗</a></li>)}</ol>
              </details>}
            </div>)}</div>
          </details>
        </div>;
      })}
    </div>
    {matches === 0 && <p className="empty-lessons">沒有符合的教材。試試模組名稱或 Goal ID，或清除搜尋查看全部課程。</p>}
    <div className="lesson-tools"><a href={SOURCE + "academy/TOOLS.md"}>32 題自測與五類作業驗收 ↗</a><a href={SOURCE + "academy/ASSESSMENT.md"}>專案交付清單 ↗</a><a href={SOURCE + "academy/examples/README.md"}>小模型實際執行結果 ↗</a></div>
    <p className="path-end" aria-hidden="true">—— 線畫完了，下一頁：通電。</p>
  </section>;
}
