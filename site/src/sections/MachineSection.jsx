import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createRun, TASK_PROMPT } from "../sim/harness.js";
import { usePowerOn, usePrefersReducedMotion } from "../hooks.js";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const STEPS = {
  brain: { name: "大腦", sub: "MODEL" },
  protocol: { name: "協議", sub: "PARSE" },
  hands: { name: "雙手", sub: "TOOLS" },
};

/** 核心體驗裝置：循環機器。跑的是教程算法的 JS 移植，不是預設動畫。 */
export default function MachineSection() {
  const sectionRef = useRef(null);
  const railRef = useRef(null);
  const runIdRef = useRef(0);
  const busyRunRef = useRef(null);
  const [busy, setBusy] = useState(false);
  const reduced = usePrefersReducedMotion();
  const powered = usePowerOn(sectionRef, 0.35);

  const [cards, setCards] = useState([]);
  const [station, setStation] = useState(null);
  const [flowing, setFlowing] = useState(null);
  const [steps, setSteps] = useState(0);
  const [toolCalls, setToolCalls] = useState(0);
  const [context, setContext] = useState(0);
  const [done, setDone] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [fault, setFault] = useState(false);
  const [view, setView] = useState("both");
  const [runToken, setRunToken] = useState(0);

  const sim = useMemo(() => createRun({ fault }), [fault, runToken]);
  const autoPlayedRef = useRef(false);

  const reset = useCallback(
    (nextFault = fault) => {
      runIdRef.current += 1;
      busyRunRef.current = null;
      setBusy(false);
      setRunToken((t) => t + 1);
      setCards([]);
      setStation(null);
      setFlowing(null);
      setSteps(0);
      setToolCalls(0);
      setContext(0);
      setDone(false);
      setPlaying(false);
      setFault(nextFault);
      void nextFault;
    },
    [fault],
  );

  // 把一次 step() 的事件按節奏演出：站點脈衝 → 墨線流動 → 卡片蓋章。
  const perform = useCallback(
    async (events, myRun) => {
      for (const ev of events) {
        if (runIdRef.current !== myRun) return;
        if (ev.flow === "brain>protocol" || ev.kind === "reply") setFlowing("e1");
        if (ev.kind === "parse-error") setFlowing("e3");
        if (ev.kind === "tool-result") setFlowing("e2");
        if (ev.kind === "final") setFlowing("e1");
        setStation(ev.station);
        await sleep(reduced ? 0 : 420);
        if (runIdRef.current !== myRun) return;
        if (ev.card) setCards((prev) => [...prev, { id: myRun + "-" + ev.kind + "-" + prev.length, ...ev.card }]);
        if (ev.kind === "tool-result") {
          setToolCalls(ev.toolCalls);
          setContext(ev.context);
          setFlowing("e3"); // 觀察沿左弧回到大腦
          await sleep(reduced ? 0 : 520);
          if (runIdRef.current !== myRun) return;
          setFlowing(null);
        }
        setSteps(ev.steps ?? steps);
        if (ev.context !== undefined) setContext(ev.context);
        if (ev.kind === "final") {
          setDone(true);
          setPlaying(false);
          setFlowing(null);
          setStation(null);
          return;
        }
        await sleep(reduced ? 60 : 360);
      }
      setStation(null);
      setFlowing(null);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [reduced],
  );

  const stepOnce = useCallback(async () => {
    if (busyRunRef.current !== null) return;
    const myRun = runIdRef.current;
    const events = sim.step();
    if (!events) { setDone(true); return; }
    busyRunRef.current = myRun;
    setBusy(true);
    try {
      await perform(events, myRun);
    } finally {
      if (busyRunRef.current === myRun) {
        busyRunRef.current = null;
        setBusy(false);
      }
    }
  }, [sim, perform]);

  // 首次通電啟動同一個播放控制器；減少動態時由訪客手動開始。
  useEffect(() => {
    if (!powered || autoPlayedRef.current) return;
    autoPlayedRef.current = true;
    if (!reduced) setPlaying(true);
  }, [powered, reduced]);

  // 暫停在目前這一拍結束後生效。共用鎖避免單步與自動重疊。
  useEffect(() => {
    if (!playing || done) return undefined;
    let cancelled = false;
    const myRun = runIdRef.current;
    (async () => {
      while (!cancelled && runIdRef.current === myRun) {
        if (busyRunRef.current !== null) {
          await sleep(40);
          continue;
        }
        await stepOnce();
        if (sim.isDone()) break;
        await sleep(reduced ? 120 : 900);
      }
      if (!cancelled) setPlaying(false);
    })();
    return () => { cancelled = true; };
  }, [playing, done, stepOnce, sim, reduced]);

  const railRefScroll = useCallback(() => {
    const rail = railRef.current;
    if (rail) rail.scrollTop = rail.scrollHeight;
  }, []);
  useEffect(railRefScroll, [cards]);

  const onKeyDown = (event) => {
    const tag = event.target.tagName;
    if (tag === "INPUT" || tag === "BUTTON" || tag === "TEXTAREA") return;
    if (event.code === "Space") {
      event.preventDefault();
      setPlaying(false);
      void stepOnce();
    } else if (event.key === "r" || event.key === "R") {
      reset();
    } else if (event.key === "f" || event.key === "F") {
      reset(!fault);
    }
  };

  return (
    <section className="chapter wrap" id="machine" ref={sectionRef} aria-labelledby="machine-title">
      <div className="chapter-head">
        <span className="chapter-no">章 · 貳</span>
        <span className="chapter-sub" style={{ margin: 0 }}>
          核心裝置 · 通電
        </span>
      </div>
      <h2 id="machine-title">循環機器</h2>
      <p className="chapter-sub">
        這台機器跑的是動手營參考實現的移植版：{TASK_PROMPT} 每一拍都是
        「大腦 → 協議 → 雙手 → 觀察」。它可以壞，也可以自己修好。
      </p>

      <div className="machine-shell" data-power={powered} data-view={view}>
        <div className="machine-grid">
          <div>
            <svg
              className="machine-svg"
              viewBox="0 0 760 420"
              role="img"
              aria-label="循環機器示意圖：大腦、協議、雙手三個站點沿環形墨線相連"
            >
              {/* 邊：大腦→協議（右弧）、協議→雙手（下弧）、雙手→大腦（左弧）、出口 */}
              <path id="e1" className={`edge${flowing === "e1" ? " flowing" : ""}`} d="M 380 55 A 160 160 0 0 1 519 295" />
              <path id="e2" className={`edge${flowing === "e2" ? " flowing" : ""}`} d="M 519 295 A 160 160 0 0 1 241 295" />
              <path id="e3" className={`edge${flowing === "e3" ? " flowing" : ""}`} d="M 241 295 A 160 160 0 0 1 380 55" />
              <path className={`edge${flowing === "final" ? " flowing" : ""}`} d="M 380 55 L 380 14" />
              <text x="392" y="26" fontFamily="var(--mono)" fontSize="11" fill="var(--ink-soft)">
                最終回答
              </text>

              <g className="station model-part station-brain" data-active={station === "brain"}>
                <circle cx="380" cy="55" r="52" strokeWidth="2" />
                <text className="st-name" x="380" y="52" textAnchor="middle">大腦</text>
                <text className="st-sub" x="380" y="74" textAnchor="middle">MODEL</text>
              </g>
              <g className="station harness-part station-protocol" data-active={station === "protocol"}>
                <circle cx="519" cy="295" r="52" strokeWidth="2" />
                <text className="st-name" x="519" y="292" textAnchor="middle">協議</text>
                <text className="st-sub" x="519" y="314" textAnchor="middle">PARSE</text>
              </g>
              <g className="station harness-part station-hands" data-active={station === "hands"}>
                <circle cx="241" cy="295" r="52" strokeWidth="2" />
                <text className="st-name" x="241" y="292" textAnchor="middle">雙手</text>
                <text className="st-sub" x="241" y="314" textAnchor="middle">TOOLS</text>
              </g>
            </svg>

            <div className="controls" style={{ marginTop: 14 }}>
              <button
                type="button"
                className="btn primary"
                onClick={() => {
                  setPlaying(false);
                  void stepOnce();
                }}
                disabled={done || busy}
              >
                單步 ▸
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => setPlaying((v) => !v)}
                disabled={done}
              >
                {playing ? "暫停 ⏸" : "自動 ▶"}
              </button>
              <button type="button" className="btn" onClick={() => reset()}>
                重置 ↺
              </button>
              <label className="lever" title="切換後重新開始；第一拍會輸出壞 JSON，看循環如何自我修復">
                <input
                  type="checkbox"
                  checked={fault}
                  onChange={(e) => {
                    const next = e.target.checked;
                    reset(next);
                  }}
                />
                故障注入
              </label>
            </div>

            <div className="chip-row" style={{ marginTop: 12 }} role="group" aria-label="視角切換">
              <span>視角：</span>
              {[
                ["both", "全景"],
                ["model", "看模型"],
                ["harness", "看工程"],
              ].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  className="chip"
                  data-on={view === key}
                  onClick={() => setView(key)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="machine-aside">
            <div
              className="history"
              ref={railRef}
              role="log"
              aria-live="polite"
              aria-label="對話歷史軌跡"
            >
              {cards.length === 0 && (
                <p style={{ color: "var(--ink-soft)", fontFamily: "var(--mono)", fontSize: 12, margin: 4 }}>
                  （歷史為空——通電後每一拍都會蓋章留在這裡）
                </p>
              )}
              {cards.map((card) => (
                <div
                  key={card.id}
                  className={`card ${card.role === "大腦" ? "role-brain" : "role-env"}${card.error ? " error" : ""}`}
                >
                  <span className="role">{card.role}</span>
                  <pre>{card.text}</pre>
                </div>
              ))}
            </div>

            <div className="machine-meta">
              <span>步數 {steps}</span>
              <span>工具調用 {toolCalls}</span>
              <span style={{ flex: "1 1 100%", display: "flex", gap: 10, alignItems: "center" }}>
                上下文 {context.toLocaleString()} / 24,000 字符
                <span className="ctxbar" style={{ "--fill": Math.min(1, context / 24000) }} />
              </span>
              {done && (
                <span style={{ color: "var(--red)" }}>
                  ✓ 示範流程已結束 · 請查看上方對話與工具結果
                </span>
              )}
            </div>
          </div>
        </div>

        <p className="machine-caption">
          三個站點各司其職：<span className="m">大腦</span>只負責判斷下一步；{" "}
          <span className="h">協議</span>裁定它說的話合不合法；{" "}
          <span className="h">雙手</span>在固定分發表裡查表執行。
          換大腦不用改機器——所以它可以是你手寫的規則，也可以是真模型。
          「暫停」會在目前這一拍結束後停止。切換「故障注入」會重新開始：第一拍輸出壞 JSON，
          你會看到協議把錯誤喂回大腦，循環自己癒合。
        </p>
      </div>
    </section>
  );
}
