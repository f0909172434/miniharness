import { useLocalDoneSet } from "../hooks.js";

const CAMP_STEPS = [
  ["循環與台詞大腦", "while 循環 + history：agent 的心臟", "docs/01"],
  ["協議", "讓大腦會說 toolcall，並寫出解析器", "docs/02"],
  ["工具執行", "工具箱 + 永不拋異常的執行器", "docs/03"],
  ["路徑守衛與讀寫", "第一道安全閘：不許逃出工作區", "docs/06"],
  ["自我修復", "把解析錯誤喂回大腦，循環自己癒合", "docs/01"],
  ["上下文預算", "成對裁剪歷史，保護最新觀察", "docs/04"],
  ["迷你評測", "同一套任務，誰來考都同分", "docs/07"],
  ["🎓 畢業考", "規則大腦驅動整機，寫出 TODO 報告", "docs/09"],
];

const STORAGE_KEY = "mh-camp-steps-v1";

/** 章 D：工序單（可勾選，存在本機）+ 出口命令。 */
export default function CampSection() {
  const [checked, toggle] = useLocalDoneSet(STORAGE_KEY);
  const doneCount = CAMP_STEPS.filter((_, i) => checked.has(String(i))).length;

  return (
    <section className="chapter wrap" id="camp" aria-labelledby="camp-title">
      <div className="chapter-head">
        <span className="chapter-no">章 · 肆</span>
        <span className="chapter-sub" style={{ margin: 0 }}>
          八道工序，從空文件到你的 harness
        </span>
      </div>
      <h2 id="camp-title">動手營 · 工序單</h2>
      <p className="chapter-sub">
        這不是章節列表，是一張可以逐項打勾的作業指導書：每道工序在
        tutorial/steps/ 裡都有規格、提示與常見坑，檢查器逐項驗收。
        勾滿八格，你就寫出了自己的 my_harness.py。
      </p>

      <ol className="camp-list">
        {CAMP_STEPS.map(([title, line, ref], index) => {
          const key = String(index);
          const on = checked.has(key);
          return (
            <li key={key} className={`camp-row${on ? " done" : ""}`}>
              <label className="camp-check">
                <input type="checkbox" checked={on} onChange={() => toggle(key)} />
                <span className="camp-num">{String(index + 1).padStart(2, "0")}</span>
                <span className="camp-title">{title}</span>
                <span className="camp-line">{line}</span>
                <span className="camp-ref">{ref}</span>
              </label>
            </li>
          );
        })}
      </ol>

      <p className="camp-progress" aria-live="polite">
        工序 {doneCount}/8
        {doneCount === 8
          ? " —— 全部完成。G5.3 的驗收命令在下面，去跑它。"
          : ` —— 剩 ${8 - doneCount} 道；勾選只存在你的瀏覽器裡。`}
      </p>

      <div className="terminal-block" role="figure" aria-label="常用命令">
        <div><span className="c">$</span> git clone &lt;repo-url&gt; miniharness <span className="c">&&</span> cd miniharness</div>
        <div><span className="c">$</span> python3 tutorial/check.py <span className="c"># 動手營：進度總覽 / 逐步驗收</span></div>
        <div><span className="c">$</span> python3 demos/demo_from_zero.py <span className="c"># 沒有模型，也有 agent</span></div>
        <div><span className="c">$</span> python3 tools/academy.py map <span className="c"># 你的學習地圖與進度</span></div>
        <div><span className="c">$</span> python3 tools/academy.py gaps <span className="r"># 隨時掃描：哪裡還有洞</span></div>
      </div>

      <p style={{ color: "var(--ink-soft)", maxWidth: 680 }}>
        畢業標準寫在明處：G5.3（動手營 8/8）、G5.12（復現一篇論文的核心實驗）、
        G5.14（一份可復現的技術報告）、G5.15（一個被合併的 PR）。做到這四條，
        你就是這門課定義下的 AI 研究員。
      </p>
    </section>
  );
}
