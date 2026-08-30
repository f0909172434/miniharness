// sim/harness.js —— 教程算法（tutorial/solutions/my_harness_full.py）的忠实 JS 移植。
// 网站上那台“循环机器”跑的就是这套真实逻辑：协议解析、工具执行、自我修复，
// 不是预设动画。
//
// 安全说明：这里的“工具”是進程內的純函數，全部登記在一張固定分發表
// TOOL_IMPLS 裡——名稱只在表中查找，沒有動態求值、沒有 shell、
// 沒有子進程、沒有網絡請求；進入回執文本的名稱一律經白名單清洗。

const FENCE_RE = /```toolcall\s*([\s\S]*?)\s*```/;
const MAX_CONTEXT = 24000;

export const SYSTEM_PROMPT = "你是一個運行在 my_harness 裡的 agent，用工具完成任務。";
export const TASK_PROMPT =
  "找出工作區裡所有包含 TODO 標記的 .py 文件，把清單寫入 REPORT.md（每行一條，含文件路徑）。";

// —— 虚拟工作区（与动手营毕业考同一份夹具）——
const FIXTURES = [
  [
    "app/core.py",
    '"""核心邏輯。"""\n\ndef scale(value, factor):\n    # TODO: 邊界值校驗\n    return value * factor\n',
  ],
  [
    "app/utils.py",
    "def slugify(text):\n    # TODO: 處理中文與空格\n    return text.lower().replace(\" \", \"-\")\n",
  ],
  [
    "scripts/pipeline.py",
    '"""示例流水線。"""\n\n# TODO: 接入日誌\nSTAGES = ["extract", "transform"]\n',
  ],
  ["notes.txt", "週末記得整理 TODO 清單（本文件不是 .py，不應被統計）\n"],
  ["README.md", "# 示例工作區\n"],
];

function makeWorkspace() {
  return new Map(FIXTURES);
}

function safeLabel(value) {
  // 白名單清洗：僅允許字母、數字、連字符與下劃線進入回執文本。
  const cleaned = String(value ?? "").replace(/[^A-Za-z0-9_-]/g, "");
  return cleaned.length > 0 ? cleaned.slice(0, 40) : "?";
}

// —— 固定分發表：兩個進程內純函數，鍵是唯一的合法工具名 ——
const TOOL_IMPLS = {
  search(files, args) {
    const pattern = String(args.pattern ?? "TODO").slice(0, 80);
    const suffix = String(args.glob ?? "*.py").replace("*", "");
    const hits = [];
    for (const [path, text] of [...files.entries()].sort()) {
      if (suffix && !path.endsWith(suffix)) continue;
      const lines = text.split("\n");
      for (let i = 0; i < lines.length; i += 1) {
        if (lines[i].includes(pattern)) {
          hits.push(path + ":" + (i + 1) + ": " + lines[i].trim());
        }
      }
    }
    return hits.length > 0 ? hits.slice(0, 100).join("\n") : "(無命中)";
  },
  write_file(files, args) {
    // 路徑清洗：反斜杠歸一、去掉 ..（防路徑穿越），截斷長度。
    const rel = String(args.path ?? "untitled.txt")
      .replace(/\\/g, "/")
      .replace(/\.\.+/g, ".")
      .slice(0, 120);
    const content = String(args.content ?? "");
    files.set(rel, content);
    return "OK：已寫入 " + rel + "（" + content.length + " 字符）";
  },
};

function applyTool(files, rawName, args) {
  const name = safeLabel(rawName);
  const impl = TOOL_IMPLS[name]; // 查表分發：name 不參與任何求值
  if (!impl) {
    return 'ERROR: 未知工具 "' + name + '"。可用：search, write_file';
  }
  return impl(files, args);
}

function formatToolcall(name, args) {
  return "```toolcall\n" + JSON.stringify({ tool: name, args }) + "\n```";
}

const SEARCH_CALL = formatToolcall("search", { pattern: "TODO", glob: "*.py" });
// 故障注入后的坏调用：args 键没有加引号，不是合法 JSON。
const BROKEN_CALL =
  'Thought: 我先搜尋 TODO。\n```toolcall\n{"tool": "search", "args": {pattern: TODO}}\n```';
const FINAL_TEXT =
  "Thought: 收工。\n\n最終回答：TODO 清單已寫入 REPORT.md；notes.txt 不是 .py，已正確排除。";

function parseReply(text) {
  const match = text.match(FENCE_RE);
  const thought = text.replace(/```toolcall\s*[\s\S]*?\s*```/g, "").trim();
  if (!match) return { thought, toolcall: null };
  let data;
  try {
    data = JSON.parse(match[1]);
  } catch (exc) {
    throw new Error("toolcall 不是合法 JSON：" + exc.message);
  }
  if (typeof data !== "object" || data === null || !("tool" in data)) {
    throw new Error('toolcall 必須是 {"tool": 名字, "args": {...}}');
  }
  const args = data.args ?? {};
  if (typeof args !== "object" || Array.isArray(args)) {
    throw new Error("args 必須是對象");
  }
  return { thought, toolcall: { name: String(data.tool), args } };
}

function composeReport(observation) {
  // 觀察行先經正則白名單（字母/數字/點/斜槓/連字符開頭的路徑）才進入報告。
  const paths = [];
  for (const line of observation.split("\n")) {
    if (/^(TOOL RESULT|ERROR|\[|\(無命中)/.test(line)) continue;
    const m = line.match(/^([\w./-]+):\d+:/);
    if (m && !paths.includes(m[1])) paths.push(m[1]);
  }
  const report = "# TODO 報告\n\n" + paths.map((p) => "- " + p).join("\n") + "\n";
  return formatToolcall("write_file", { path: "REPORT.md", content: report });
}

// —— 一次可步进的运行 ——
// step() 每次推进“一拍”（大脑发言 → 协议裁定 → 双手执行），返回事件数组。
export function createRun({ fault = false, maxSteps = 12 } = {}) {
  const files = makeWorkspace();
  const history = [
    { role: "system", content: SYSTEM_PROMPT },
    { role: "user", content: "任務：" + TASK_PROMPT },
  ];
  let steps = 0;
  let toolCalls = 0;
  let done = false;
  let faultArmed = fault; // 只影响本运行的第一次发言

  const lastUser = () => {
    for (let i = history.length - 1; i >= 0; i -= 1) {
      if (history[i].role === "user") return history[i].content;
    }
    return "";
  };

  function decide() {
    const obs = lastUser();
    if (faultArmed) {
      faultArmed = false;
      return BROKEN_CALL;
    }
    if (steps === 0) return SEARCH_CALL;
    if (obs.includes("ERROR")) return SEARCH_CALL; // 自我修复：修好格式后重试
    if (obs.includes("已寫入 REPORT")) return FINAL_TEXT;
    if (obs.includes("(無命中)")) return "最終回答：工作區裡沒有找到 TODO。";
    return composeReport(obs);
  }

  function contextChars() {
    return history.reduce((sum, m) => sum + m.content.length, 0);
  }

  function step() {
    if (done || steps >= maxSteps) return null;
    const events = [];
    const reply = decide();
    history.push({ role: "assistant", content: reply });
    steps += 1;
    events.push({
      kind: "reply",
      station: "brain",
      flow: "none>brain",
      card: { role: "大腦", text: reply },
      steps,
      toolCalls,
      context: contextChars(),
    });

    let parsed;
    try {
      parsed = parseReply(reply);
    } catch (exc) {
      const errObs =
        "TOOL RESULT (parse):\nERROR: " + exc.message + "\n請重新輸出一個合法的 toolcall。";
      history.push({ role: "user", content: errObs });
      events.push({
        kind: "parse-error",
        station: "protocol",
        flow: "brain>protocol",
        card: { role: "環境", text: errObs, error: true },
        steps,
        toolCalls,
        context: contextChars(),
      });
      return events;
    }

    const { toolcall } = parsed;
    if (!toolcall) {
      done = true;
      events.push({
        kind: "final",
        station: "brain",
        flow: "brain>out",
        final: parsed.thought || reply,
        steps,
        toolCalls,
        context: contextChars(),
      });
      return events;
    }

    const observation =
      "TOOL RESULT (" + safeLabel(toolcall.name) + "):\n" + applyTool(files, toolcall.name, toolcall.args);
    toolCalls += 1;
    history.push({ role: "user", content: observation });
    events.push({
      kind: "tool-result",
      station: "hands",
      flow: "brain>protocol>hands",
      card: { role: "環境", text: observation },
      tool: safeLabel(toolcall.name),
      steps,
      toolCalls,
      context: contextChars(),
    });
    return events;
  }

  return {
    step,
    history: () => history.map((m) => ({ ...m })),
    contextChars,
    isDone: () => done,
    stepsSoFar: () => steps,
  };
}
