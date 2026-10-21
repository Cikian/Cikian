# -*- coding: utf-8 -*-
"""
Derive README_zh-CN.md from README.md.

English stays the single source of truth: edit README.md, then run
    python scripts/make_zh.py
keeping this map in sync.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "README.md")
DST = os.path.join(ROOT, "README_zh-CN.md")

MAP = [
    # hero assets + alt
    ('srcset="assets/hero-dark.svg"', 'srcset="assets/hero-dark-zh.svg"'),
    ('srcset="assets/hero-light.svg"', 'srcset="assets/hero-light-zh.svg"'),
    ('<img src="assets/hero-light.svg" alt="Cikian Chen — Java backend engineer, full-stack developer, open source" width="100%" />',
     '<img src="assets/hero-light-zh.svg" alt="Cikian Chen — Java 后端工程师 / 全栈开发 / 开源" width="100%" />'),
    # language switch: flip the highlight
    ('<a href="./README.md"><img src="https://img.shields.io/badge/ENGLISH-22D3EE?style=flat-square&amp;labelColor=0D1224" alt="English" /></a>',
     '<a href="./README.md"><img src="https://img.shields.io/badge/ENGLISH-1B2540?style=flat-square&amp;labelColor=0D1224" alt="English" /></a>'),
    ('<a href="./README_zh-CN.md"><img src="https://img.shields.io/badge/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-1B2540?style=flat-square&amp;labelColor=0D1224" alt="简体中文" /></a>',
     '<a href="./README_zh-CN.md"><img src="https://img.shields.io/badge/%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-22D3EE?style=flat-square&amp;labelColor=0D1224" alt="简体中文" /></a>'),
    # sections
    ("## 🚀 What I'm building", "## 🚀 我在做什么"),
    ("<sub>Repositories I actually use — object storage, tunnels, Redis tooling and a bit of reverse engineering.</sub>",
     "<sub>我自己也在用的项目 —— 对象存储、内网穿透、Redis 工具，以及一点点逆向。</sub>"),
    ("## 🧰 Tech I work with", "## 🧰 技术栈"),
    ("<sub>Java is home base; everything else is a detour that turned useful.</sub>",
     "<sub>Java 是主场，其余都是「顺手学来却真用上了」的岔路。</sub>"),
    ("**Backend**", "**后端**"),
    ("**Frontend**", "**前端**"),
    ("**Data & Infra**", "**数据与基础设施**"),
    ("**Tools & Editors**", "**工具与编辑器**"),
    ("## 📈 By the numbers", "## 📈 数据一览"),
    ("<sub>Pulled live from the GraphQL API and redrawn every night by a workflow — no third-party card services, no broken images.</sub>",
     "<sub>数据实时取自 GraphQL API，每天由 workflow 重绘 —— 不依赖第三方卡片服务，也不会挂图。</sub>"),
    ('alt="GitHub statistics for Cikian — stars, commits, streaks and most used languages"',
     'alt="Cikian 的 GitHub 数据 —— 星标、提交、连续贡献与常用语言"'),
    ("## 🐍 Contribution graph", "## 🐍 贡献贪吃蛇"),
    ("<sub>A snake that eats my commit graph, redrawn every night.</sub>",
     "<sub>一条每晚重画的蛇，专门吃我的提交格子。</sub>"),
    ('alt="Contribution snake animation"', 'alt="贡献贪吃蛇动画"'),
    ("## 🤝 Say hi", "## 🤝 打个招呼"),
    ("<sub>Software engineering graduate of HBWE · currently shipping backend systems and small tools.</sub>",
     "<sub>河北水利电力学院软件工程专业 · 目前在做后端系统与各种小工具。</sub>"),
]


def main():
    src = io.open(SRC, encoding="utf-8").read()
    out = src
    missing = []
    for old, new in MAP:
        if old not in out:
            missing.append(old[:70])
        out = out.replace(old, new)
    if missing:
        sys.exit("map entries not found in README.md:\n  " + "\n  ".join(missing))
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", DST, len(out.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
