import { useLocalDoneSet } from "../hooks.js";

const CAMP_STEPS = [
  ["循環與台詞大腦", "while 循環 + history：agent 的心臟", "step-01-loop.md"],
  ["協議", "讓大腦會說 toolcall，並寫出解析器", "step-02-protocol.md"],
  ["工具執行", "工具箱 + 永不拋異常的執行器", "step-03-tools.md"],
  ["路徑守衛與讀寫", "第一道安全閘：不許逃出工作區", "step-04-guard-files.md"],
  ["自我修復", "把解析錯誤喂回大腦，循環自己癒合", "step-05-repair.md"],
  ["上下文預算", "成對裁剪歷史，保護最新觀察", "step-06-context.md"],
  ["迷你評測", "同一套任務，誰來考都同分", "step-07-eval.md"],
  ["🎓 畢業考", "規則大腦驅動整機，寫出 TODO 報告", "step-08-graduation.md"],
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
        每道工序都連到實際規格、提示與常見問題。勾選是保存在這個瀏覽器的
        自行記錄；實作是否通過，請在本機執行動手營檢查器。
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

              </label>
              <a className="camp-ref" href={`https://github.com/f0909172434/miniharness/blob/main/tutorial/steps/${ref}`}>工序教材 ↗</a>
            </li>
          );
        })}
      </ol>

      <p className="camp-progress" aria-live="polite">
        自行記錄 {doneCount}/8
        {doneCount === 8
          ? " —— 已全部勾選；尚需執行檢查器確認實作。"
          : ` —— 剩 ${8 - doneCount} 道；勾選只存在你的瀏覽器裡。`}
      </p>

      <div className="terminal-block" role="figure" aria-label="常用命令">
        <div><span className="c">$</span> git clone https://github.com/f0909172434/miniharness.git <span className="c">&&</span> cd miniharness</div>
        <div><span className="c">$</span> python3 tutorial/check.py <span className="c"># 動手營：進度總覽 / 逐步驗收</span></div>
        <div><span className="c">$</span> python3 demos/demo_from_zero.py <span className="c"># 沒有模型，也有 agent</span></div>
        <div><span className="c">$</span> python3 tools/academy.py map <span className="c"># 你的學習地圖與進度</span></div>
        <div><span className="c">$</span> python3 tools/academy.py gaps <span className="r"># 隨時掃描：哪裡還有洞</span></div>
      </div>

      <p style={{ color: "var(--ink-soft)", maxWidth: 680 }}>
        後續練習方向包括：完成動手營檢查、復現一個小型實驗、寫出可重現的技術報告，
        以及參與一次開源貢獻。這些是練習目標；職涯能力仍需要持續實作與外部回饋。
      </p>
    </section>
  );
}
