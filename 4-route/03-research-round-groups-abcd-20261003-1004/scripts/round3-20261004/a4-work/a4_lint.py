# -*- coding: utf-8 -*-
"""Scan the A4 draft for banned words and banned sentence patterns (brief section 5 + global rules)."""
import re
from pathlib import Path

t = Path(__file__).resolve().parent.parent.joinpath("A4-local-evidence-draft.md").read_text(encoding="utf-8")
banned = ["席位", "写权", "读权", "承重", "落盘", "决策包", "不自决", "闸门", "派工单", "互盲", "真相源", "扇出",
          "写入者", "验收卡", "计划卡", "开工卡", "机器契约", "值得注意的是", "综上所述", "总的来说", "不难看出",
          "由此可见", "赋能", "抓手", "闭环", "颗粒度", "底层逻辑", "沉淀", "打通", "助力", "加持", "拥抱", "洞察",
          "范式", "重塑", "解锁", "全方位", "多维度", "至关重要", "不可或缺", "里程碑", "革命性", "显著提升", "——",
          "首先", "其次", "可以说", "对标", "无缝", "关卡", "纪律", "台账", "底稿", "收据", "首创", "没人做过"]
hits = {b: t.count(b) for b in banned if b in t}
print("banned hits:", hits or "none")
for pat in (r"不是.{1,12}而是", r"既.{1,8}又", r"一方面.{1,40}另一方面", r"(^|[，。；\n\s])(第一|第二|第三|最后)[，,、]"):
    found = [m.group(0) for m in re.finditer(pat, t, flags=re.M)]
    print(pat, "->", found or "none")
print("bytes", len(t.encode("utf-8")))
