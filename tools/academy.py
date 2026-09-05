#!/usr/bin/env python3
"""MiniAcademy 课程引擎：让「随时找到漏洞」成为一条命令。

单一事实源是 academy/manifest.json（阶段 → 模块 → Goal），
本工具在其上提供六类操作：

    python3 tools/academy.py map                # 学习地图（含你的进度）
    python3 tools/academy.py goals --stage 1    # 列出某阶段的 Goal
    python3 tools/academy.py next               # 规划：现在该学什么
    python3 tools/academy.py gaps               # 漏洞扫描：结构/内容/翻译/学习
    python3 tools/academy.py i18n               # 多语言覆盖报告
    python3 tools/academy.py validate           # 结构校验（CI 也跑它）

进度记录在 academy/progress.json（默认被 git 忽略）：

    python3 tools/academy.py init               # 生成空白进度文件
    python3 tools/academy.py done G0.5 G0.6     # 勾选达成
    python3 tools/academy.py undo G0.6          # 撤销
    python3 tools/academy.py show               # 查看我的进度

全部实现只依赖标准库。manifest 的结构约束由 tests/test_academy.py 固化。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MANIFEST_PATH = ROOT / "academy" / "manifest.json"
PROGRESS_PATH = ROOT / "academy" / "progress.json"
STATUSES = ("ready", "draft", "planned")


def _c(text: str, code: str) -> str:
    import os
    if os.environ.get("NO_COLOR"):
        return text
    return f"\033[{code}m{text}\033[0m"


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_progress(path: Path = PROGRESS_PATH) -> dict:
    if not path.exists():
        return {"done": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_progress(progress: dict, path: Path = PROGRESS_PATH) -> None:
    import os
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".progress-", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(json.dumps(progress, ensure_ascii=False, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


# ----------------------------------------------------------- 索引与图

def goal_index(manifest: dict) -> dict:
    return {goal["id"]: goal for goal in manifest["goals"]}


def iter_modules(manifest: dict):
    for stage in manifest["stages"]:
        for module in stage["modules"]:
            yield stage, module


def goal_owner(manifest: dict) -> dict:
    """goal id -> 拥有它的 module dict。"""
    owners = {}
    for _stage, module in iter_modules(manifest):
        for gid in module["goals"]:
            owners[gid] = module
    return owners


def module_graph(manifest: dict) -> dict:
    """模块依赖图：经 prereq goal 归属到模块。"""
    owner = goal_owner(manifest)
    graph = {}
    for _stage, module in iter_modules(manifest):
        deps = set()
        for gid in module.get("prerequisites", []):
            if gid in owner and owner[gid] is not module:
                deps.add(id(owner[gid]))
        graph[id(module)] = deps
    return graph


def find_cycle(manifest: dict) -> list | None:
    graph = module_graph(manifest)
    state = {}  # id(module) -> 1 visiting / 2 done
    path: list = []
    ids = {id(module): module for _stage, module in iter_modules(manifest)}

    def visit(node) -> list | None:
        if state.get(node) == 1:
            cycle = path[path.index(node):] + [node]
            return [ids[n]["id"] for n in cycle]
        if state.get(node) == 2:
            return None
        state[node] = 1
        path.append(node)
        for dep in sorted(graph.get(node, ())):
            found = visit(dep)
            if found:
                return found
        path.pop()
        state[node] = 2
        return None

    for node in graph:
        found = visit(node)
        if found:
            return found
    return None


# ----------------------------------------------------------- 结构校验

def validate(manifest: dict) -> tuple[list, list]:
    """返回 (errors, warnings)。errors 非空时 validate 命令退出码非零。"""
    errors: list = []
    warnings: list = []
    locales = manifest.get("locales", [])
    default_locale = manifest.get("default_locale")
    if default_locale not in locales:
        errors.append(f"default_locale '{default_locale}' 不在 locales {locales} 中")

    goals = goal_index(manifest)
    if len(goals) != len(manifest["goals"]):
        errors.append("存在重复的 goal id")
    owner = goal_owner(manifest)

    seen_module_ids = set()
    for stage in manifest["stages"]:
        for module in stage["modules"]:
            mid = module["id"]
            if mid in seen_module_ids:
                errors.append(f"模块 id 重复：{mid}")
            seen_module_ids.add(mid)
            if module.get("status") not in STATUSES:
                errors.append(f"{mid}: status 应为 {STATUSES} 之一，得到 {module.get('status')!r}")
            if default_locale not in module.get("title", {}):
                errors.append(f"{mid}: title 缺少默认语言 {default_locale}")

            for gid in module["goals"]:
                if gid not in goals:
                    errors.append(f"{mid}: 引用了不存在的 goal '{gid}'")
            for gid in module.get("prerequisites", []):
                if gid not in goals:
                    errors.append(f"{mid}: 前置 goal '{gid}' 不存在")
                elif gid not in owner:
                    errors.append(f"{mid}: 前置 goal '{gid}' 没有归属模块")
                else:
                    dep_stage = None
                    for st in manifest["stages"]:
                        if owner[gid] in st["modules"]:
                            dep_stage = st["id"]
                            break
                    if dep_stage is not None and dep_stage > stage["id"]:
                        errors.append(
                            f"{mid}: 前置 goal '{gid}' 属于更晚的阶段 {dep_stage}（> {stage['id']}）")

            content = module.get("content", {})
            if module.get("status") == "ready":
                if not any(content.get(locale) for locale in locales):
                    errors.append(f"{mid}: status=ready 但没有任何语言的内容文件")
                for locale, paths in content.items():
                    if locale not in locales:
                        errors.append(f"{mid}: content 语言 '{locale}' 不在 locales 中")
                    for rel in paths:
                        if not (ROOT / rel).exists():
                            errors.append(f"{mid}: 内容文件缺失：{rel}")
            for locale, paths in content.items():
                for rel in paths:
                    if not (ROOT / rel).exists():
                        errors.append(f"{mid}: 内容文件缺失：{rel}")

    if len(owner) != len(goals):
        orphans = sorted(set(goals) - set(owner))
        warnings.append(f"未被任何模块引用的 goal：{', '.join(orphans)}")

    cycle = find_cycle(manifest)
    if cycle:
        errors.append(f"模块依赖图存在环：{' -> '.join(cycle)}")
    return errors, warnings


# ----------------------------------------------------------- 学习进度

def module_progress(module: dict, done: set) -> tuple:
    hit = sum(1 for gid in module["goals"] if gid in done)
    return hit, len(module["goals"])


def module_available(module: dict, goals: dict, done: set) -> tuple:
    """(是否可学, 未满足的前置 goal 列表)——保留旧签名以兼容外部调用。"""
    missing = [gid for gid in module.get("prerequisites", []) if gid not in done]
    return (not missing), missing


def learning_queue(manifest: dict, done: set) -> tuple:
    """返回 (candidates, blocked)，只看「第一个还有未完成模块的阶段」。

    这是课程规划的核心规则：严格按阶段推进——前面的阶段没走完，
    后面再诱人的模块也不会进入推荐队列（想跳级请显式 done 前置 Goal）。
    """
    for stage in manifest["stages"]:
        candidates = []
        blocked = []
        for module in stage["modules"]:
            hit, total = module_progress(module, done)
            if hit == total:
                continue
            missing = [gid for gid in module.get("prerequisites", []) if gid not in done]
            entry = (stage["id"], not missing, missing, stage, module)
            (candidates if not missing else blocked).append(entry)
        if candidates or blocked:
            return candidates, blocked
    return [], []


def cmd_next(manifest: dict, args) -> int:
    done = set(load_progress(args.progress)["done"])
    candidates, blocked = learning_queue(manifest, done)
    print("== MiniAcademy · 现在该学什么 ==\n")
    for index, (stage_id, _ok, _missing, _stage, module) in enumerate(candidates[:3]):
        hit, total = module_progress(module, done)
        title = module["title"][manifest["default_locale"]]
        mark = "★" if index == 0 else " "
        status = module["status"]
        note = "" if status == "ready" else _c(f"(内容撰写中：{status}，可先按 Goal 自学)", "33")
        print(f"{mark} 阶段 {stage_id} · {title}  [进度 {hit}/{total}] {note}")
        for gid in module["goals"]:
            done_mark = _c("x", "32") if gid in done else " "
            goal = goal_index(manifest)[gid]
            print(f"     [{done_mark}] {gid}  {goal['statement']}")
        print()
    if not candidates and not blocked:
        print("（全部阶段完成——去做 G5.14 那样的公开作品吧）")
    if blocked:
        stage_id, _ok, missing, _stage, module = blocked[0]
        title = module["title"][manifest["default_locale"]]
        print(f"被前置挡住（举例）：阶段 {stage_id} · {title} —— 还差 {', '.join(missing)}")
    return 0


def cmd_done(manifest: dict, args) -> int:
    goals = goal_index(manifest)
    progress = load_progress(args.progress)
    done = set(progress["done"])
    unknown = [gid for gid in args.goals if gid not in goals]
    if unknown:
        print(_c(f"未知的 goal id：{', '.join(unknown)}", "31"))
        return 1
    progress["done"] = sorted(done | set(args.goals))
    save_progress(progress, args.progress)
    print(f"已记录 {len(args.goals)} 项；总进度 {len(progress['done'])}/{len(goals)}")
    return 0


def cmd_undo(manifest: dict, args) -> int:
    progress = load_progress(args.progress)
    progress["done"] = sorted(set(progress["done"]) - set(args.goals))
    save_progress(progress, args.progress)
    print(f"已撤销 {len(args.goals)} 项；总进度 {len(progress['done'])}")
    return 0


def cmd_show(manifest: dict, args) -> int:
    done = set(load_progress(args.progress)["done"])
    goals = goal_index(manifest)
    total = sum(1 for gid in goals if gid in done)
    print(f"进度：{total}/{len(goals)} 条 Goal 达成\n")
    for stage in manifest["stages"]:
        stage_goal_ids = [gid for module in stage["modules"] for gid in module["goals"]]
        stage_hit = sum(1 for gid in set(stage_goal_ids) if gid in done)
        print(f"  阶段 {stage['id']} {stage['title'][manifest['default_locale']]}"
              f"  {stage_hit}/{len(set(stage_goal_ids))}")
    return 0


def cmd_init(manifest: dict, args) -> int:
    if args.progress.exists() and not args.force:
        print("进度文件已存在（--force 覆盖）")
        return 1
    save_progress({"done": []}, args.progress)
    print(f"已创建 {args.progress}")
    return 0


# ----------------------------------------------------------- 地图与 Goal

def cmd_map(manifest: dict, args) -> int:
    done = set(load_progress(args.progress)["done"])
    goals = goal_index(manifest)
    default_locale = manifest["default_locale"]
    print("== MiniAcademy · 学习地图 ==\n")
    grand_total = grand_hit = 0
    for stage in manifest["stages"]:
        hours = sum(m["hours"] for m in stage["modules"])
        stage_goal_ids = [gid for m in stage["modules"] for gid in m["goals"]]
        stage_hit = sum(1 for gid in stage_goal_ids if gid in done)
        grand_hit += stage_hit
        grand_total += len(stage_goal_ids)
        print(f"阶段 {stage['id']} · {stage['title'][default_locale]}  "
              f"[{hours}h, {len(stage_goal_ids)} goals]  "
              f"{_c(f'{stage_hit}/{len(stage_goal_ids)}', '32' if stage_hit == len(stage_goal_ids) else '2')}")
        for module in stage["modules"]:
            hit, total = module_progress(module, done)
            mark = _c("✓", "32") if hit == total else ("·" if hit == 0 else _c("◐", "33"))
            status_mark = {"ready": _c("ready", "32"), "draft": _c("draft", "33"),
                           "planned": _c("planned", "2")}[module["status"]]
            print(f"   {mark} {module['id']:<14} {module['title'][default_locale]:<26}"
                  f" [{module['hours']:>2}h] {status_mark:<8} {hit}/{total}")
        print()
    print(f"总计：{grand_hit}/{grand_total} 条 Goal，"
          f"{sum(m['hours'] for s in manifest['stages'] for m in s['modules'])} 小时全部内容")
    return 0


def cmd_goals(manifest: dict, args) -> int:
    done = set(load_progress(args.progress)["done"])
    goals = goal_index(manifest)
    owner = goal_owner(manifest)
    stage_of = {}
    for stage in manifest["stages"]:
        for module in stage["modules"]:
            for gid in module["goals"]:
                stage_of[gid] = stage["id"]
    count = 0
    for gid, goal in goals.items():
        if args.stage is not None and stage_of.get(gid) != args.stage:
            continue
        if args.todo and gid in done:
            continue
        if args.done and gid not in done:
            continue
        mark = _c("x", "32") if gid in done else " "
        module = owner.get(gid)
        mid = module["id"] if module else "?"
        print(f"[{mark}] {gid:<6} ({goal['level']:<5} {goal['evidence']:<9}) {mid:<14} {goal['statement']}")
        count += 1
    print(f"\n共 {count} 条")
    return 0


# ----------------------------------------------------------- 漏洞扫描

def cmd_gaps(manifest: dict, args) -> int:
    done = set(load_progress(args.progress)["done"])
    errors, warnings = validate(manifest)
    default_locale = manifest["default_locale"]

    print("== MiniAcademy · 漏洞扫描 ==\n")

    print("一、结构漏洞（manifest 自身）")
    if not errors and not warnings:
        print("  ✓ 无")
    for err in errors:
        print("  " + _c(f"✗ {err}", "31"))
    for warn in warnings:
        print("  " + _c(f"△ {warn}", "33"))

    print("\n二、内容漏洞（有 Goal 没有正文）")
    empty = []
    for stage, module in iter_modules(manifest):
        if module["status"] != "ready" and not any(module.get("content", {}).values()):
            empty.append(f"阶段 {stage['id']} · {module['title'][default_locale]}")
    if not empty:
        print("  ✓ 无")
    for item in empty:
        print(f"  △ {item}")

    print("\n三、翻译漏洞")
    i18n_lines = i18n_report(manifest)
    for line in i18n_lines:
        print(f"  {line}")

    print("\n四、学习漏洞（基于 progress.json）")
    candidates, blocked = learning_queue(manifest, done)
    if not done:
        print("  △ 进度为空——先跑 python3 tools/academy.py init，再 done 记录已达成的 Goal")
    if candidates:
        stage_id, _ok, _missing, _stage, module = candidates[0]
        print(f"  ✓ 当前可学：阶段 {stage_id} · {module['title'][default_locale]}"
              f" 共 {len(candidates)} 个模块（用 next 查看完整队列）")
    if blocked:
        missing_total = sum(len(entry[2]) for entry in blocked)
        print(f"  △ 同阶段有 {len(blocked)} 个模块被前置挡住，涉及 {missing_total} 条未达成的前置 Goal")
    if not candidates and not blocked:
        print("  ✓ 全部达成？恭喜——去做 G5.14 那样的公开作品吧")
    print()
    return 1 if errors else 0


# ----------------------------------------------------------- 多语言

def i18n_report(manifest: dict) -> list:
    default_locale = manifest["default_locale"]
    locales = manifest["locales"]
    modules = [m for _s, m in iter_modules(manifest)]
    lines = []
    for locale in locales:
        titled = sum(1 for m in modules if locale in m.get("title", {}))
        ready = [m for m in modules if m["status"] == "ready"]
        with_content = sum(1 for m in ready if any(m.get("content", {}).get(locale) or []))
        mark = "✓" if titled == len(modules) else "△"
        lines.append(f"{mark} {locale}: 标题覆盖 {titled}/{len(modules)}，"
                     f"ready 模块正文覆盖 {with_content}/{len(ready)}"
                     + ("（默认语言）" if locale == default_locale else ""))
    return lines


def cmd_i18n(manifest: dict, args) -> int:
    print("== MiniAcademy · 多语言覆盖 ==\n")
    for line in i18n_report(manifest):
        print(line)
    print("\n说明：goal statement 目前以默认语言书写；逐条翻译列为 ROADMAP P2。")
    print("新增语言的步骤：manifest.locales 加代码 → 为模块补 title →")
    print("在 academy/content/<locale>/ 下放置对应正文 → 跑本命令看覆盖。")
    return 0


def cmd_validate(manifest: dict, args) -> int:
    errors, warnings = validate(manifest)
    for err in errors:
        print(_c(f"✗ {err}", "31"))
    for warn in warnings:
        print(_c(f"△ {warn}", "33"))
    if errors:
        print(f"\n{len(errors)} 个结构错误（{len(warnings)} 个警告）")
        return 1
    print(_c(f"✓ manifest 结构完好（{len(warnings)} 个警告）", "32"))
    return 0


# ----------------------------------------------------------- 測驗、驗收與可攜進度

def quiz_questions(manifest, stage=None):
    rows = json.loads((ROOT / 'academy/quizzes.json').read_text(encoding='utf-8'))['questions']
    allowed = {g['id'] for g in manifest['goals'] if g['level'] == 'know'}
    return [q for q in rows if q['goal'] in allowed and
            (stage is None or q['goal'].startswith(f'G{stage}.'))]


def cmd_quiz(manifest, args):
    questions = quiz_questions(manifest, args.stage)
    if not questions:
        raise ValueError('此範圍沒有測驗題目')
    answers = None
    if args.answers:
        answers = json.loads(Path(args.answers).read_text(encoding='utf-8'))
        if not isinstance(answers, dict) or set(answers) - {q['goal'] for q in questions}:
            raise ValueError('答案應為本次題目的 Goal → 1/2/3 JSON 物件')
        if any(type(v) is not int or not 1 <= v <= 3 for v in answers.values()):
            raise ValueError('答案只能是整數 1、2 或 3')
    correct = 0
    for q in questions:
        print(f"\n{q['goal']} {q['question']}")
        for index, choice in enumerate(q['choices'], 1):
            print(f'  {index}. {choice}')
        if args.list:
            continue
        if answers is not None:
            answer = answers.get(q['goal'])
        else:
            try:
                raw = input('答案 1–3（Enter 略過）：').strip()
                answer = int(raw) if raw else None
            except (EOFError, ValueError):
                answer = None
        passed = answer == q['answer'] + 1
        correct += passed
        print(('✓' if passed else '△') + ' ' + q['explanation'])
    if args.list:
        return 0
    print(f'\n自測 {correct}/{len(questions)}。未更改學習進度；請另以自己的例子解釋。')
    return 0 if correct == len(questions) else 1


def cmd_verify(manifest, args):
    import subprocess
    from tools.academy_checks import CHECKERS
    requested = args.goal or [g['id'] for g in manifest['goals'] if g['evidence'] == 'checker']
    if not requested or any(gid not in CHECKERS for gid in requested):
        raise ValueError('沒有對應的固定檢查器：' + ', '.join(requested))
    failed = []
    print('參考實作自檢；不代表學習者完成。' if args.reference else '驗收學習者作業；不會自動修改進度。', flush=True)
    for gid in requested:
        command = [sys.executable, str(ROOT/'tools/academy_checks.py'), gid]
        if args.reference:
            command.append('--reference')
        try:
            result = subprocess.run(command, cwd=ROOT, timeout=120, check=False)
            if result.returncode:
                failed.append(gid)
        except subprocess.TimeoutExpired:
            print(f'{gid}: 超過驗收時間')
            failed.append(gid)
    print(f'驗收 {len(requested)-len(failed)}/{len(requested)}；未通過：{", ".join(failed) or "無"}')
    return 1 if failed else 0


def progress_snapshot(manifest, data):
    if not isinstance(data, dict) or not isinstance(data.get('done'), list):
        raise ValueError('進度必須含 done 陣列')
    done = data['done']
    if any(not isinstance(gid, str) or gid not in goal_index(manifest) for gid in done):
        raise ValueError('進度含未知 Goal 或錯誤型別')
    if len(done) != len(set(done)):
        raise ValueError('進度含重複 Goal')
    return {'format': 'miniacademy-progress/v1', 'manifest_version': manifest['version'], 'done': sorted(done)}


def cmd_export(manifest, args):
    target = Path(args.file)
    if target.resolve() == args.progress.resolve():
        raise ValueError('匯出檔不可覆寫目前進度')
    if target.exists():
        raise ValueError('匯出檔已存在，請使用新的檔名')
    snapshot = progress_snapshot(manifest, load_progress(args.progress))
    save_progress(snapshot, target)
    print(f'已匯出 {len(snapshot["done"])} 個自評標記至 {target}')
    return 0


def cmd_import(manifest, args):
    path = Path(args.file)
    if path.stat().st_size > 262144:
        raise ValueError('匯入檔超過 256 KiB')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'format','manifest_version','done'}:
        raise ValueError('匯入格式不符 miniacademy-progress/v1')
    if data['format'] != 'miniacademy-progress/v1' or data['manifest_version'] != manifest['version']:
        raise ValueError('進度格式或課程版本不同，請先核對目標')
    incoming = progress_snapshot(manifest, data)
    current = progress_snapshot(manifest, load_progress(args.progress))
    merged = {'done': sorted(set(current['done']) | set(incoming['done']))}
    save_progress(merged, args.progress)
    print(f'已合併為 {len(merged["done"])} 個自評標記；保留既有進度。')
    return 0


# ----------------------------------------------------------- CLI

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="MiniAcademy 课程引擎")
    parser.add_argument("--progress", default=str(PROGRESS_PATH),
                        help="进度文件路径（默认 academy/progress.json）")
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    sub = parser.add_subparsers(dest="command", required=True)

    def _register(name, help_text):
        sub_parser = sub.add_parser(name, help=help_text)
        # 允许把全局参数写在子命令后面（SUPPRESS 避免覆盖主解析器的值）
        sub_parser.add_argument("--progress", default=argparse.SUPPRESS)
        sub_parser.add_argument("--manifest", default=argparse.SUPPRESS)
        return sub_parser

    _register("map", "学习地图")
    _register("show", "我的进度摘要")
    _register("validate", "结构校验（CI 用）")
    _register("i18n", "多语言覆盖报告")
    _register("gaps", "漏洞扫描：结构/内容/翻译/学习")
    init_parser = _register("init", "创建空白进度文件")
    init_parser.add_argument("--force", action="store_true")

    goals_parser = _register("goals", "列出 Goal")
    goals_parser.add_argument("--stage", type=int, default=None)
    goals_parser.add_argument("--todo", action="store_true")
    goals_parser.add_argument("--done", action="store_true")

    _register("next", "现在该学什么")
    done_parser = _register("done", "记录达成的 Goal")
    done_parser.add_argument("goals", nargs="+")
    undo_parser = _register("undo", "撤销记录")
    undo_parser.add_argument("goals", nargs="+")

    quiz = _register("quiz", "32 個概念目標自測")
    quiz.add_argument("--stage", type=int, choices=range(6))
    quiz.add_argument("--answers", help="Goal 到選項 1/2/3 的 JSON 檔")
    quiz.add_argument("--list", action="store_true", help="只列出題目")
    verify = _register("verify", "聚合固定的作業檢查器")
    verify.add_argument("--goal", action="append")
    verify.add_argument("--reference", action="store_true", help="驗證參考實作，與學習者作業分開")
    export = _register("export", "匯出自評進度 JSON")
    export.add_argument("file")
    importer = _register("import", "驗證並合併自評進度 JSON")
    importer.add_argument("file")

    args = parser.parse_args(argv)
    manifest = load_manifest(Path(args.manifest))
    args.progress = Path(args.progress)
    handlers = {
        "map": cmd_map, "show": cmd_show, "validate": cmd_validate,
        "i18n": cmd_i18n, "gaps": cmd_gaps, "init": cmd_init,
        "quiz": cmd_quiz, "verify": cmd_verify, "export": cmd_export, "import": cmd_import,
        "goals": cmd_goals, "next": cmd_next, "done": cmd_done, "undo": cmd_undo,
    }
    try:
        return handlers[args.command](manifest, args)
    except (OSError, ValueError, TypeError) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
