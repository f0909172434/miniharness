import { useEffect, useMemo, useRef, useState } from "react";
import manifest from "../../../academy/manifest.json";
import { useLocalDoneSet } from "../hooks.js";

const STAGE_COLORS = ["#8a7a5c", "#75654a", "#665741", "#574837", "#493a2b", "#b3402a"];
const STORAGE_KEY = "mh-academy-progress-v1";

// —— 用真實 manifest 佈局星圖：模塊沿螺旋排開，Goal 環繞各自的模塊 ——
function buildLayout() {
  const modules = [];
  manifest.stages.forEach((stage) =>
    stage.modules.forEach((module) => modules.push({ stageId: stage.id, ...module })),
  );
  const nodes = new Map();
  modules.forEach((module, i) => {
    const t = modules.length > 1 ? i / (modules.length - 1) : 0;
    const angle = -Math.PI / 2 + t * Math.PI * 2 * 1.55;
    const radius = 0.36 + t * 0.58;
    module.goals.forEach((gid, j) => {
      const a = angle + (j - (module.goals.length - 1) / 2) * 0.17;
      const r = radius + 0.045;
      nodes.set(gid, {
        gid,
        x: Math.cos(a) * r,
        y: Math.sin(a) * r * 0.82,
        stageId: module.stageId,
      });
    });
  });
  const edges = [];
  modules.forEach((module) => {
    (module.prerequisites || []).forEach((pgid) => {
      const from = nodes.get(pgid);
      if (!from) return;
      module.goals.forEach((gid) => {
        const to = nodes.get(gid);
        if (to) edges.push([from, to]);
      });
    });
  });
  return { modules, nodes, edges };
}

export default function ConstellationSection() {
  const wrapRef = useRef(null);
  const canvasRef = useRef(null);
  const [size, setSize] = useState({ w: 900, h: 600 });
  const [hoverId, setHoverId] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [activeStage, setActiveStage] = useState(null);
  const [done, toggleDone] = useLocalDoneSet(STORAGE_KEY);
  const [hintShown, setHintShown] = useState(false);

  const layout = useMemo(() => buildLayout(), []);
  const goals = useMemo(() => {
    const map = new Map();
    manifest.goals.forEach((g) => map.set(g.id, g));
    return map;
  }, []);
  const goalList = useMemo(() => [...layout.nodes.values()], [layout]);

  // —— 佈局映射到畫布 ——
  const project = useMemo(() => {
    const { w, h } = size;
    const cx = w / 2;
    const cy = h / 2;
    const sx = w / 2 - 42;
    const sy = h / 2 - 34;
    return (p) => ({ px: cx + p.x * sx, py: cy + p.y * sy });
  }, [size]);

  // —— 畫 ——
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size.w * dpr;
    canvas.height = size.h * dpr;
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.w, size.h);

    const nodeR = Math.max(3.5, size.w / 260);

    // 邊：前置 Goal → 依賴模塊的 Goal
    layout.edges.forEach(([from, to]) => {
      const dim =
        activeStage !== null && from.stageId !== activeStage && to.stageId !== activeStage;
      ctx.strokeStyle = dim ? "rgba(32,27,18,0.04)" : "rgba(32,27,18,0.15)";
      ctx.lineWidth = 1;
      const a = project(from);
      const b = project(to);
      ctx.beginPath();
      ctx.moveTo(a.px, a.py);
      ctx.lineTo(b.px, b.py);
      ctx.stroke();
    });

    // 節點
    layout.nodes.forEach((node) => {
      const { px, py } = project(node);
      const dim = activeStage !== null && node.stageId !== activeStage;
      const color = STAGE_COLORS[node.stageId];
      ctx.globalAlpha = dim ? 0.14 : 1;
      if (done.has(node.gid)) {
        ctx.fillStyle = "#b3402a";
        ctx.beginPath();
        ctx.arc(px, py, nodeR + 0.8, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.fillStyle = color;
        ctx.globalAlpha = dim ? 0.14 : 0.78;
        ctx.beginPath();
        ctx.arc(px, py, nodeR, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "rgba(32,27,18,0.55)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      if (hoverId === node.gid || selectedId === node.gid) {
        ctx.strokeStyle = "#b3402a";
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.arc(px, py, nodeR + 4.5, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = "#b3402a";
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.fillText(node.gid, px + nodeR + 7, py - 6);
      }
      ctx.globalAlpha = 1;
    });
  }, [layout, size, hoverId, selectedId, activeStage, done, project]);

  // —— 尺寸自適應 ——
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return undefined;
    const ro = new ResizeObserver(() => {
      const w = el.clientWidth;
      setSize({ w, h: Math.max(380, Math.min(640, w * 0.64)) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // —— 拾取 ——
  const pick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const mx = event.clientX - rect.left;
    const my = event.clientY - rect.top;
    let best = null;
    let bestDist = 18;
    layout.nodes.forEach((node) => {
      if (activeStage !== null && node.stageId !== activeStage) return;
      const { px, py } = project(node);
      const d = Math.hypot(px - mx, py - my);
      if (d < bestDist) {
        bestDist = d;
        best = node;
      }
    });
    return best;
  };

  const selected = selectedId ? goals.get(selectedId) : null;
  const selectedModule = selected
    ? layout.modules.find((m) => m.goals.includes(selected.id))
    : null;

  return (
    <section className="chapter wrap" id="sky" aria-labelledby="sky-title">
      <div className="chapter-head">
        <span className="chapter-no">章 · 叁</span>
        <span className="chapter-sub" style={{ margin: 0 }}>
          學習路線本身，也是一件作品
        </span>
      </div>
      <h2 id="sky-title">一百一十顆星的星圖</h2>
      <p className="chapter-sub">
        每顆星是一個可對照教材的學習目標，連線表示前置依賴。選擇節點查看教材狀態與
        驗收方式；已有內容的模組提供直接入口。勾選只記錄你的自評，不會執行驗收。
      </p>

      <div className="sky-shell" ref={wrapRef}>
        <div className="sky-body">
          <div>
            <canvas
              ref={canvasRef}
              className="sky-canvas"
              style={{ height: size.h }}
              role="img"
              aria-label="110 條學習 Goal 構成的星圖，按六個階段排成螺旋"
              tabIndex={0}
              onMouseMove={(e) => {
                const node = pick(e);
                setHoverId(node ? node.gid : null);
              }}
              onMouseLeave={() => setHoverId(null)}
              onClick={(e) => {
                const node = pick(e);
                if (node) {
                  setSelectedId(node.gid);
                  setHintShown(true);
                }
              }}
              onDoubleClick={(e) => {
                const node = pick(e);
                if (node) toggleDone(node.gid);
              }}
              onKeyDown={(e) => {
                const ids = goalList.map((n) => n.gid);
                const at = ids.indexOf(selectedId ?? "");
                if (e.key === "ArrowRight" || e.key === "ArrowDown") {
                  e.preventDefault();
                  setSelectedId(ids[Math.min(ids.length - 1, at + 1)]);
                } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
                  e.preventDefault();
                  setSelectedId(ids[Math.max(0, at - 1)]);
                } else if (e.key === "Enter" && selectedId) {
                  toggleDone(selectedId);
                }
              }}
            />
            <div className="sky-legend" role="group" aria-label="階段篩選">
              <button
                type="button"
                className="chip stage-chip"
                data-on={activeStage === null}
                onClick={() => setActiveStage(null)}
              >
                全部
              </button>
              {manifest.stages.map((stage) => (
                <button
                  key={stage.id}
                  type="button"
                  className="chip stage-chip"
                  data-on={activeStage === stage.id}
                  onClick={() => setActiveStage(stage.id)}
                >
                  <span
                    aria-hidden="true"
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: STAGE_COLORS[stage.id],
                      marginRight: 6,
                    }}
                  />
                  {stage.title[manifest.default_locale]}
                </button>
              ))}
              <span style={{ marginLeft: "auto", fontFamily: "var(--mono)", fontSize: 12, display: "inline-flex", alignItems: "center", gap: 8 }}>
                <span
                  aria-hidden="true"
                  className="sky-ring"
                  style={{ "--p": `${Math.round((done.size / manifest.goals.length) * 100)}%` }}
                />
                {done.size}/{manifest.goals.length}
              </span>
            </div>
            <p className="sky-hint">
              懸停查看 · 點擊釘選 · 雙擊任意一顆星標記達成（存在本機）{hintShown ? "" : ""}
            </p>
          </div>

          <aside className="sky-panel" aria-live="polite">
            {selected ? (
              <>
                <span className="gid">{selected.id}</span>
                <p className="gmod">
                  {selected.level} · {selected.evidence} ·{" "}
                  階段 {layout.modules.find((m) => m.goals.includes(selected.id))?.stageId} ·{" "}
                  {selectedModule?.title[manifest.default_locale]}
                </p>
                <p className="module-status">{selectedModule?.status === "ready" ? "已有教材 · 繁體中文" : "規劃中 · 正文尚未完成"}</p>
                {selectedModule?.status === "ready" && selectedModule.content[manifest.default_locale].map(path => <a className="lesson-link" key={path} href={`https://github.com/f0909172434/miniharness/blob/main/${path}`}>閱讀模組教材 ↗</a>)}
                <p>{selected.statement}</p>
                {selected.verify && (
                  <p className="verify">$ {selected.verify}</p>
                )}
                <label className="sky-check">
                  <input
                    type="checkbox"
                    checked={done.has(selected.id)}
                    onChange={() => toggleDone(selected.id)}
                  />
                  自行標記為已練習
                </label>
              </>
            ) : (
              <p className="empty">
                （尚未釘選任何一顆星。點擊星圖上的任意節點——比如從
                G0.1「打開終端機」開始，查看已有教材與後續規劃。）
              </p>
            )}
          </aside>
        </div>
      </div>
    </section>
  );
}
