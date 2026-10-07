# 文献检索子 agent 的工作规则（硬规则）

先读 `5-ultimate-plan-20261007/work/PROJECT-BRIEF-for-agents.md`，弄清项目的模块、问题和记号，再开始检索。你的任务是为指定领域的指定子主题找出“对本项目某个模块或某个问题有可迁移原理”的论文，并逐篇核实。

## 核实标准（一篇都不能例外）

- 一篇论文只有在你本次真的用 WebFetch 打开了它的来源页（arXiv abs 页、DOI 出版社页、PubMed/PMC 页、官方会议页如 openaccess.thecvf.com / proceedings.neurips.cc / openreview.net / proceedings.mlr.press / aclanthology.org、期刊官网如 nature.com / elifesciences.org / journals.plos.org / frontiersin.org / sciencedirect.com / link.springer.com / ieeexplore.ieee.org、作者主页 PDF），并且页面上的标题、作者、年份和你写的对得上，才算“已核实”。
- 只凭记忆、只凭检索引擎摘录（snippet）、只凭 Semantic Scholar / Google Scholar 列表页，都不算核实；这种记录放进 unverified 文件。
- `what_it_says` 必须是来源页上真有的内容（摘要或正文里写的），不得添加来源没有的结论或数字。
- 优先打开能读到摘要或全文的页面（arXiv、PMC、PLOS、eLife、Frontiers、Nature、Springer、PMLR、OpenReview、CVF、NeurIPS、ACL Anthology）。被拦截（403、验证页、只看到 cookie 提示）就换一个来源页（例如换 arXiv 或 PubMed）；换了还打不开，就记进 unverified。
- 去重：同一作者同一内容的会议版和期刊版只算一篇；不要凑数。宁可少、不可假。
- 跨领域迁移要诚实：人类实验的结论迁移到网络设计只能写成类比启发，`transfer_risk` 里写明类比在哪一步可能不成立。

## 检索方法

- 工具：WebSearch（默认 mode "standard"，结果薄或过时时用 "extended"）找候选；WebFetch 打开来源页核实。若这两个工具没加载，先用 ToolSearch 加载（`select:WebSearch,WebFetch`）。
- 每个子主题先列 6 到 10 个检索词组合（英文），再按“经典奠基 + 近五年进展 + 直接贴近本项目”三层去找。
- 每核实 5 篇就把 JSON 文件整体重写一次存盘（防中断丢失）。
- 目标：每个 agent 至少 22 篇已核实，多多益善，上限 32 篇；不足 22 篇就继续换检索词找，直到够或已穷尽（穷尽要在 summary 里说明）。

## 输出文件（只写你自己的这两个文件，JSON 数组，UTF-8）

1. `5-ultimate-plan-20261007/04-cross-domain/registers/<domain>/<subtopic>.json`
2. `5-ultimate-plan-20261007/04-cross-domain/registers/<domain>/<subtopic>.unverified.json`（可以为空数组）

每条记录的字段（全部必填，字符串用中文写，标题作者原文保留）：

```json
{
  "id": "<domain>-<subtopic>-01",
  "domain": "<domain>",
  "subtopic": "<subtopic>",
  "title": "原题",
  "authors": "第一作者 等（或全列，不超过 6 人）",
  "year": 2021,
  "venue": "期刊或会议名",
  "url": "你实际打开并核实的那个页面 URL",
  "doi": "有就写，没有写空字符串",
  "verification": "读了摘要 | 读了全文 | 只读到检索摘录",
  "source_page_opened": true,
  "what_it_says": "一两句，来源里真有的内容",
  "target_module": "本项目哪个模块或问题（例如：笔的编码 / 意图绑定 / 范围头 / 难负样本 / 加删分治 / 损失标定 / 训练状态池 / 执行门槛 / 翻转增强 / 评测与统计 / 多轮纠错 / 远端补全）",
  "use_for_project": "能落成什么具体的网络结构、损失、训练策略或推理策略（一两句）",
  "transfer_risk": "迁移时的风险，类比在哪一步可能不成立（一两句）"
}
```

`verification` 为“只读到检索摘录”的记录必须放进 unverified 文件，不能放进主文件。`source_page_opened` 在主文件里必须为 true。

## 最后的汇报

完成后在最终回复里给出：已核实篇数、未核实篇数、用过的检索词、哪些方向没找到合适论文、你认为对本项目最有用的 3 篇和理由（一句话一篇）。不要把整份 JSON 贴进回复。

## 本次运行实测的网络情况（2026-10-07 07:00 UTC，curl 经代理）

能打开（HTTP 200）：arxiv.org（abs 和 pdf）、export.arxiv.org API、doi.org（跳转正常）、api.crossref.org、pubmed.ncbi.nlm.nih.gov、pmc.ncbi.nlm.nih.gov、eutils.ncbi.nlm.nih.gov、openreview.net、proceedings.neurips.cc、papers.nips.cc、openaccess.thecvf.com、link.springer.com、www.nature.com、aclanthology.org、journals.plos.org、elifesciences.org、www.frontiersin.org、dblp.org、paperswithcode.com、huggingface.co。
被拦（403/418/429，别反复试）：scholar.google.com、api.semanticscholar.org（限流）、www.biorxiv.org（限流）、ieeexplore.ieee.org、dl.acm.org、www.sciencedirect.com、onlinelibrary.wiley.com、www.pnas.org、www.science.org、psycnet.apa.org、www.jneurosci.org、journals.aps.org、www.tandfonline.com、www.mdpi.com、researchgate.net。

对策：
- IEEE、ACM、Elsevier、Wiley 的论文：找 arXiv 版（export.arxiv.org API 按标题搜很稳）、PubMed/PMC 版（心理学、神经科学、医学文献大多有 PubMed 条目，PubMed 摘要页算来源页）、或作者主页 PDF。
- 心理学、教育学经典期刊（Psychological Review、Cognition、Review of Educational Research 等）走 PubMed 摘要页或 doi.org 跳到 Springer/Nature/PLOS/Frontiers 时能打开；跳到 Wiley/Elsevier/APA 打不开就记 unverified，换一篇能打开的。
- Crossref API（https://api.crossref.org/works/<doi>）能核标题、作者、年份、期刊；但只有 Crossref 元数据、没有读到摘要或正文的，`verification` 写“只读到检索摘录”并放 unverified。
- 用 WebFetch 时 prompt 写短，让它返回：标题、作者（前三位）、年份、出处、摘要前三句、以及和你的问题相关的一两个要点。
- 仓库里已有的两份文献综述（`3-literature/literature-review.md` 的对应领域小节、`3-literature/attribution-methods-and-k-literature-20261007.md`）可以当候选来源，但必须本次重新打开来源页才算已核实。用 Grep 搜你领域的小节标题就行，不要整篇读（235 KB）。

## 存盘和效率

- 文件路径用绝对路径 `/home/user/honor-degree-intent-pet-ct-claude-research/5-ultimate-plan-20261007/04-cross-domain/registers/<domain>/<subtopic>.json`。
- 每核实 5 篇就用 Write 整体重写一次 JSON（有效的 JSON 数组）。不要运行 git。
- 一个子主题只写自己的两个文件，别碰别人的。

## 补充（07:30 UTC 实测，WebFetch 和 curl 行为不同，以下按 WebFetch 的实际表现写）

1. PubMed 文章页 `https://pubmed.ncbi.nlm.nih.gov/<PMID>/` 经 WebFetch 只返回 cookie 提示页，拿不到内容。改用两步：
   - 找 PMID：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<标题关键词，用+连接>[Title]&retmode=json`
   - 读记录：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=<PMID>&retmode=xml`（返回官方 PubMed 记录，含标题、作者、年份、期刊、DOI、完整摘要）。这算打开了来源记录，`verification` 写“读了摘要（eutils XML）”，`url` 写 `https://pubmed.ncbi.nlm.nih.gov/<PMID>/`，`doi` 填 XML 里的 DOI。
2. Europe PMC REST 能用且覆盖心理学、神经科学、教育学、医学：`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE:%22<标题>%22&format=json&resultType=core&pageSize=3`（返回标题、作者、年份、期刊、DOI、摘要）。`verification` 写“读了摘要（Europe PMC）”，`url` 写它返回的 DOI 链接或 PubMed 链接。Europe PMC 的网页版 europepmc.org 被拦，只能用 REST。
3. OpenAlex 按 DOI 查能用（`https://api.openalex.org/works/doi:<doi>`），按关键词搜索被限流。它只给元数据（标题、作者、年份、出处），没有摘要正文时不算核实，只能用来确认 DOI 和年份。
4. Nature、Springer（link.springer.com，含 PDF 直链）的文章页经 WebFetch 全部跳到 idp.nature.com / idp.springer.com 的 cookie 授权页，拿不到内容。这两家的论文改走：PubMed eutils（生物医学类几乎都有 PMID）、Europe PMC、PMC 全文页（`https://pmc.ncbi.nlm.nih.gov/articles/PMC<id>/` 能开）、arXiv 版本。都没有就记 unverified。
5. doi.org 经 WebFetch 返回“REDIRECT DETECTED”，把它给出的跳转 URL 再 WebFetch 一次即可（跳到 Nature/Springer 时按第 4 条处理）。
6. 另外确认能开：proceedings.mlr.press（ICML/AISTATS 等）、ojs.aaai.org、ijcai.org、www.cambridge.org/core（文章页含摘要，不需要登录）、psyarxiv.com 与 osf.io、jmlr.org、hal.science、core.ac.uk、openaccess.thecvf.com、journals.plos.org、elifesciences.org、frontiersin.org 文章页。确认被拦：jneurosci.org（Cloudflare 验证页）、psycnet.apa.org、academic.oup.com、direct.mit.edu、journals.sagepub.com、cell.com、annualreviews.org、royalsocietypublishing.org、sciencedirect.com、ieeexplore、dl.acm.org。
7. 统计脚本认 `verification` 以“读了摘要”或“读了全文”开头的记录，所以括号里的注释可以保留。

## 补充二（08:20 UTC）：WebSearch 配额可能中途耗尽，找候选的替代通道（都经 WebFetch 可用，返回 XML 或 JSON）

- arXiv API 按题名或关键词搜：`https://export.arxiv.org/api/query?search_query=ti:%22interactive%20segmentation%22+AND+all:scribble&max_results=20&sortBy=relevance`（返回标题、作者、年份、摘要、abs 链接；读到摘要即算核实，url 写 abs 页）。
- Crossref 按题名搜：`https://api.crossref.org/works?query.title=<题名关键词>&rows=5&select=DOI,title,author,issued,container-title`（只给元数据，用来拿 DOI 和出处，再去 Europe PMC / eutils / arXiv 读摘要）。
- Europe PMC 按关键词搜：`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<关键词>%20AND%20(SRC:MED%20OR%20SRC:PPR)&format=json&resultType=core&pageSize=10`（含摘要，覆盖 PubMed 和部分预印本）。
- PubMed 按关键词搜：eutils esearch（见补充一）再 efetch。
- dblp 搜计算机类会议论文：`https://dblp.org/search/publ/api?q=<关键词>&format=json&h=10`（元数据和 DOI/ee 链接，再去 arXiv 或会议页读摘要）。
- 会议论文集目录页能直接翻：proceedings.mlr.press/v<卷>/、openaccess.thecvf.com/<会议><年>、proceedings.neurips.cc/paper_files/paper/<年>、aclanthology.org/events/。
- 篇数上限从 32 放宽到 40；但宁缺毋滥，去重后再计数。
