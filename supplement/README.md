# 图与数值表（F1–F22）

> **2026-08-03 改版**：弱图全部重设计（一图一论点、效应量 ± 置信区间优先、全部直接标注），并新增
> F7（MCQ 格式虚高）与 F8（三轴构念效度总览）。改版同时修复了一个数据完整性问题 —— 此前所有
> PNG/PDF 渲染于 07-29，而 CSV 已在 08-02 重生成，且 `make_figures.py` 的脚注硬编码着修复前的
> "+0.54 pt"。现在**图内一切统计量都在渲染时从 CSV 计算**，不再有硬编码；四张需要统计量或曾缺失
> 的 CSV（`F6_2_forest` / `F7_mcq_inflation` / `F6_1c_shortcut_capture` / `F6_1b_trap_family`）
> 由新增的 `extract_figure_data.py` 从 `experiments/` 与 `eval.analysis.robustness` 现抽，可随时重跑。
> 旧的 `F2_tokens…` / `F3_accuracy…` / `F2_F3_combined`（slope 版）已删除，由 `F2_F3_protocol` 取代。

> ⚠️ **2026-07-29 重算**：`eval/engine.py` 的 `extract_code` 有一个未闭合代码围栏的边界缺陷，把
> 完整正确的解判成了失败（384 条 FAIL→PASS，几乎全在 DeepSeek-V4-flash）。本目录下的 **CSV 与图都已按修复后的数据重生成**（转录已移至 `docs/evidence/`）；机制、影响面与逐表前后对比见 commit `822575f`。
>
> **同日复核补记**：把全部 14 张 CSV 逐格重算后，发现两张漏掉了这次重生成 ——
> `F6_4_tolerance_sweep.csv`（DeepSeek-V4-flash 的 5/10/20% 三档为旧值，另两行有 `.5` 舍入偏差）
> 与 `F5b_three_axes.csv`（协议轴 +0.54 是修复前的均值，现为 +1.01），均已更正。两张都只有数值表、
> 无对应图，9 张已出图所依赖的 CSV 全部核对无误，无需重出图。
>
> **源数据 `outcome` 字段修复**：当初的离线重评更新了 `passed` / `details` / `num_attempts`，
> 但未重写 `attempts[].outcome`，致 4 057 条记录同时写着 `passed=True` 与 `outcome: ungradable`。
> 已用 `CodeProtocol.attempt()` 重放修正（4 947 处，134 个文件）；与修前备份逐字段比对，除 `outcome`
> 外零差异。该字段无任何分析模块读取，故已发表数字未变。`docs/evidence/` 中受影响的 9 处 `outcome` 已同步。

**先读**：[`../LOG_EXTRACTION_PREMISE_CHECK.md`](../LOG_EXTRACTION_PREMISE_CHECK.md) —— 需求单里有 **4 处前提与当前数据不符**，其中 R4 那处影响正文论点。抽 log 前先看那份。

所有内容直接从 `experiments/` 抽取或重算，**未摘要、未改写**；只有两处按需求单的窗口做了标注省略（见 R2 说明）。

---

### `figure_data/` —— 数值表（CSV）

| 文件 | 图 | 说明 |
|---|---|---|
| `F0_core_composition.csv` | F0 · F0b | 10 类别 × (总数 + low/medium/high + 可数值扰动数 + 涉及教材数，后者只入表不入图) + ALL 行；**直接读 `benchmark/core.json`**，不经 experiments |
| `F1_category_matrix.csv` + `F1_category_sizes.csv` | F1 | 16 配置 × 10 类别，每格 mean + SD，含 overall；类别按跨模型均值易→难排序 |
| `F2_F3_direct_vs_code.csv` | F2/F3 | 6 个两侧都跑过的配置：两模式准确率 ± SD、Δ、token、比值、† 标记 |
| `F4d_spend_hist.csv` · `F4d_spend_quantiles.csv`（新） | F2c · F4d | **逐题输出 token 的分布**：log10 空间直方图（宽 0.1，50→400k）+ 分位数 P10/P25/P50/P75/P90/P99、均值、P90/中位、均值/中位；code 与 direct 两个协议共用同一套分箱（`extract … spend_dist`）。存直方图而非 34,000 个原始值 |
| `F4c_token_bins.csv`（新） | F4c | 16 配置 × log₂ 输出 token 分箱：箱内题-轮数、通过数、准确率（`extract … token_bins`）；观测单位是**题-轮**（436 题 × 3 轮），token = response + reasoning 文本按 o200k 计 |
| `F4_token_accuracy.csv` | F4 · F4b | 16 配置的 (tokens, accuracy)、推理/非推理、**backbone 配对列**（箭头连线）、† 标记；F4b 复用同一张表，成本场为派生量、非额外测量 |
| `F5a_main_accuracy.csv` · `F5b_three_axes.csv` | F5 | 18 配置主结果（含两个 ClimateGPT，单列为 out-of-distribution 组）；三轴汇总（F8 现改从 F7/F2F3 CSV 现算，此表留作口径记录） |
| `F6_1_trap_gradient.csv` | F6.1a | core 准确率 vs Trap Gap（9 配置，含推理孪生配对）|
| `F6_1b_trap_family.csv` | F6.1b | 六个 trap family 的 pooled 解出率（`extract_figure_data.py trap_family`）|
| `F6_1c_shortcut_capture.csv` | F6.1c | **全向量口径**的捷径捕获数（`extract_figure_data.py trap_capture`）|
| `F6_1b_family_sizes.csv` | F6.1d | 每族陷阱数（列标签与分组用）；F6.1d 的判定数据取自 `F18_trap_matrix.csv` |
| `F6_1b_matrix.csv` | —（数值表） | 9 配置 × 6 族解出率矩阵 + pooled 行 + 每配置 overall，作为 F6.1b/F6.1d 的数值附录（`extract … trap_family_matrix`）|
| `F6_2_forest.csv`（新，出图用） · `F6_2_variant_triplet.csv`（保留） | F6.2 | **每模型 Δ(core−variant) + 解析 95% CI + McNemar p + Holm p，两个家族** —— 由 `eval.analysis.robustness --json` 直接导出，图不可能与分析漂移 |
| `F6_3_prompt_sensitivity.csv` | F6.3 | 4 模型两侧准确率 + **两侧 unrecoverable 数** |
| `F6_4_tolerance_sweep.csv` | — | MCQ10 上 5/10/20% 三档 code 准确率 + option 参照（仅数值表） |
| `F6_5_run_stability.csv` | — | 每配置 pass@3 / all@3 / 差距（仅数值表） |
| `F6_6_difficulty_strata.csv` + `F6_6b_difficulty_sizes.csv` | — | 按 low/medium/high 分层的准确率（仅数值表） |
| `F7_mcq_inflation.csv`（新） | F7 | option vs code（全 670 与 clean-480）、Δ、rescue 率；in-house 三模型从 `experiments/mcq_*` 现抽，另三模型 option 侧为 AtmosSci-Bench 论文发表值（`option_source=paper`） |
| `F9_scaffolding.csv`（新） | F9 | 169 配对题上 with/stripped 准确率 ± SD、Δ、majority-of-3 lost/gained（`extract … scaffold`） |
| `F10_cross_domain.csv` · `F10b_domain_gaps.csv`（新） | F10 | 5 模型跨领域总体+分域准确率；四域 strong-4 vs weak 差距（core 侧出图时从 F4 CSV 连接） |
| `F11_discrimination.csv`（新） | F11 | 436 题逐题"被 16 配置中几个解出"（majority-of-3）+ 难度标签 |
| `F12_echo_funnel.csv`（新） | F12 | 污染证据链五级计数——echo_forensics 现跑 + contamination_final 判决 |
| `F13_repair_budget.csv` | —（数值表） | 预算 k=1…5 的累计准确率 + 依赖修复的 pass 占比：k=1 时 Kimi 孪生反转、修复贡献集中在推理配置 |
| `F14_reasoning_lift.csv` | —（数值表） | 7 对孪生推理增益按难度分层：+1.6/+6.4/+13.2 |
| `F15_core_tolerance.csv` | —（数值表） | core 16 配置 1/2/5/10% 容差离线重评：5→10% ≤+1.2 pt、排序 ρ≥0.99 |
| `F16_arity.csv` | —（数值表） | 难度 × 子答案数通过率（评分为 N 重合取） |
| `F17_solve_matrix.csv`（新） | F17 | 436 题 × 16 配置 0/1 矩阵 + 难度 + solved_by（`extract … solve_matrix`） |
| `F18_trap_matrix.csv`（新） | F18 | 67 陷阱 × 27 run 三态判定（pass/fail/captured，全向量口径） |
| `F19_answer_space.csv`（新） | F19 | `4.5`/`ry_7.7` 每 run 实际答案 + 子级判定 |
| `F20_mcq_verdicts.csv`（新） | F20 | MCQ 670 × 3 双模式模型四态判定 + 缺陷模板标记 |
| `F21_unit_rescue.csv` · `F21b_unit_totals.csv`（新） | F21 | 仅靠单位调和通过的子答案（`eval.engine.compare_values` 精确重放）：换算对计数 + 总量/逐模型 |
| `F22_fragility.csv`（新） | F22 | 346 父题 × 16 模型四态（both/fragile/gained/neither）+ 泄漏标记 |

**这些 CSV 是从 `experiments/` 重新算出来的，不是从 `docs/` 抄的**；全部 14 张已逐格对着 `experiments/`（或对着实跑的 `eval.analysis` 模块）复核。token 口径见下方专节；`F4_token_accuracy.csv` 的 16 行与 `CORE_RESULTS.md` 表 1 的 `Tokens/run (M)` 已逐行两位小数核对一致。

### `extract_figure_data.py` —— 需要现算的 CSV（可随时重跑）

```bash
uv run python supplement/extract_figure_data.py                     # 全部（forest/mcq/trap_* + scaffold/crossdomain/discrimination/echo_funnel + repair/lift/tolerance/arity + solve_matrix/trap_matrix/answer_space + mcq_verdicts/unit_rescue/fragility）
uv run python supplement/extract_figure_data.py forest              # 只重抽森林图统计（跑 eval.analysis.robustness）
uv run python supplement/extract_figure_data.py token_bins          # 只重抽 F4c 的逐题 token 分箱
uv run python supplement/extract_figure_data.py spend_dist          # 只重抽 F2c/F4d 的逐题花费分布
```

### `make_figures.py` —— 出图脚本

```bash
uv run --with matplotlib python supplement/make_figures.py          # 全部
uv run --with matplotlib python supplement/make_figures.py F4 F7    # 只出某几张（键：F1 F23 F2B F4 F5 F6 F7 F8 F9 F10 F11 F12 F17 F18 F19 F20 F21 F22）
```

输出到 `figures/`，每张同时给 **PDF（矢量）+ PNG（400 dpi）**。

**图面不带 caption**（保持简洁、便于排版）：每张图的论点、完整 caption 与数据来源在
[`FIGURES.md`](FIGURES.md) —— 该文件由 `make_figures.py` 渲染时**自动生成**（`note()` 调用），
caption 里的统计量与图一样是从 CSV 现算的，改数据重跑即同步更新；不要手改 `FIGURES.md`。

**配色**：Nature Publishing Group（ggsci `npg`）分类色，取其中通过色觉校验的四色 —— `#E64B35` `#4DBBD5` `#3C5488` `#00A087`。校验方法是模拟红色盲/绿色盲/蓝色盲后计算 CIELAB 两两分离度：最坏 ΔE = 12.1、L\* 带 36–71，任何一对在任一色觉类型下都不会并成一色，也没有一色浅到在白底上看不清。连续型与**有序**面板（F1 热图、F0 难度分层）用同一深蓝派生的单色渐变，**不用红绿** —— 故 F0 里的深蓝表示 high difficulty，与"NAVY = reasoning"的分类语义不冲突（那条只管分类色）。**正文红字一律用 `RED_TXT`（#B03A26，白底 6.0:1）**；`RED` 本身只有 3.87:1，低于 Nature 的 4.5:1 门槛，仅可用于图形元素（Pareto 线、强调行），不可用于文字。

**其它约定**：语义固定 —— NAVY = reasoning、CYAN = non-reasoning、SAND = out-of-distribution、**RED 只作强调**（Pareto 线、未校正显著行）；模型排序全局 = 排行榜序；线细、点小；无上/右边框；每条序列直接标注（**不用编号点查表**）；涉及 token 的图，**gpt-5.5 (reasoning) 与 Gemini-3.1-Pro 一律按删失观测处理**（思维链只回传摘要，计数是下界不是测量值）：空心标记 + 向右短箭头 + †，排除出 Pareto 前沿；F4c 里直接不画。详见下方"token 口径"；**图内统计量（均值、区间、最小 Holm p 等）全部渲染时从 CSV 计算**；样本量一律写成 `(N = XX 单位)` 并点明计数单位（题数 / 题-轮 / model-run / 父题 / 配置数），**例外**：当某个轴的主体本身就是样本时（如 F17 的 x 轴即「436 core problems」、F18 的「67 traps」），不再重复标 N。

**版面（2026-08-09 定档）**：Nature 只接受**两档宽度**——单栏 **89 mm**、双栏 **183 mm**，中间宽度排版时会被缩放、**连字号一起缩放**，因此 `save()` 已改为**固定画布**（去掉 `bbox_inches="tight"`，全部 `subplots(..., layout="constrained")`），**`figsize[0]` 即成品宽度**，只能取 `WIDTH_1COL` / `WIDTH_2COL`。当前 22 张双栏、6 张单栏。字号收敛为**四档**：`FS_PANEL 8`（面板字母，粗体）/ `FS_LABEL 7`（轴标题）/ `FS_TICK 6.5`（刻度、模型名）/ `FS_ANNOT 6`（图内注记），网格线宽统一 `GRID_LW 0.4`。**多面板图一律标 a/b**（8 pt 粗体）；共享主轴的边缘注释条（如 F17 顶部的难度带）**不算面板、不标字母**，理由写在 `panel()` 的 docstring 里。固定画布的风险是元素被静默裁掉，`scratchpad/overflow.py` 会渲染全部 28 张并报告任何越界元素，改版式后必跑。

**token 口径（2026-08-09 统一）**

**所有 token 一律读 `result.usage`**。迁移之后它就是仓库自己的 o200k 重数
（`eval/store.py._o200k_usage`：system 每次调用计入 prompt、reasoning 只在是非空字符串时计入、
按 **全部 attempts** 累加），**既不是供应商自报，也不需要在这里重数一遍文本**。
辅助函数是 `extract_figure_data.py` 的 `rec_tokens()`，所有 token 抽数都走它，别再写第二处。

**这是 docs 用的同一套账**。`CORE_RESULTS.md` 的表 1/表 2/附录 B 本来就是用
`eval.analysis.token_count`（同一公式的独立实现）算的，所以图与文档现在逐值可比 ——
反漂移检查见文末"闭环"一节。

> **为什么必须核验，而不是直接信这个字段**：迁移之前 `result.usage` 在不同目录含义不同。
> `store.py` 只在**写入某条记录时**覆写它的 usage，resume 保留的旧记录原样不动，于是
> `core_code`/`trap`/`variants_*`/`scaffolding_ablation` 存着供应商数，
> 而 `core_direct`/`cross_domain`/`mcq_code` 存着 o200k 重数。跨目录读这个字段会**静默混用两套口径**：
> 实测会把 gpt-5.5 (reasoning) 的 direct/code 比值从 **1.20 翻成 0.60**，凭空推翻"direct 从不更省"。
> 2026-08-09 已把 264 个文件、238,120 条记录全部重算统一，`attempts[].usage` 保留供应商原始数据。

**自己数的代价，以及 † 是怎么判定出来的**：只数得到供应商**愿意回传**的文本。两个端点只回传
思维链**摘要** —— gpt-5.5 (reasoning) 走 `/v1/responses`（且只有 65.4% 的 attempt 带摘要）、
Gemini-3.1-Pro 走 native thought summary。用「供应商自报 total ÷ 自算 total」量一下：

| | 比值 |
|---|---|
| **gpt-5.5 (reasoning)** | **2.03×** |
| **Gemini-3.1-Pro (reasoning)** | **1.81×** |
| 其余 6 个推理配置 | 0.68–1.06× |

两组之间有干净的间隔，所以 `tokens_understated_dagger` 用阈值 `DAGGER_RATIO = 1.25`
**实测判定**，不硬编码名单。这两个配置：图上空心标记 + 向右短箭头 + †、**排除出 Pareto 前沿**；
**F4c 里整体不画**（那张图的 x 轴本身就是 token 测量值，用下界摆点会落进错误的箱，脚注修不好）。

**设计要点（2026-08-03 版）**：
- **F0（新）**：数据集本体的构成——(a) 10 类别按题量堆叠 low/medium/high、条尾标类别总数；(b) 同样的行归一到 100%，让规模相差近一个数量级的类别之间难度配比可比，虚线为全集 high 占比（31%），行尾百分比超过该值时标红。类别规模随源材料而非配额，**difficulty 是跑模型之前算的内在评分**（不是观测通过率），这一点写在 caption 里，避免 reviewer 误读成循环论证。
- **F0b（新）· 拼图 treemap**：语料构成的第二视图（参照 HLE Fig. 2 的拼图语法，纯 matplotlib 实现）。**面积 = 类别题数（精确成正比）**、**颜色 = 该类别 high 难度占比**（色条与色块同一段截断色阶，同值同色已核验）。布局为**全高列堆叠**（竖线全贯通、零 T 型接缝），每对相邻块经共享边中点的**单个半圆舌头**互扣，凸凹中心错位 0.000。标签按**实测宽度**折行（两遍布局：先画块 draw 一次再量字），文字颜色按块内实测亮度选墨/白（含副行），多行名称做垂直居中补偿。断言基线：文字四角均在自己块内 0 越界、文字框距 15 个舌头圆盘最小 +0.55 单位、标签组中心偏差 ≤0.22 单位。与 F0 分工：F0 给精确分层计数供读数，F0b 给语料形状。
- **F5_main_results**：主结果排行榜（**全局模型排序的基准**，其余各图一律沿用此序）。18 配置横条 + 3 轮 s.d. 误差棒，配色按语义分三组：NAVY 推理 / CYAN 非推理 / SAND 域特化（两个 ClimateGPT 单列为 out-of-distribution，不参与主排名叙述）。2026-08-03 改版中判定形式已合格，仅随全局规格更新（两档宽度、四档字号、`(N = XX)` 标注），未改结构。
- **F2_F3_protocol**：放弃 slope 端点，改为效应量双面板 —— (a) Δ(code−direct) 围绕 0 参考线（±合成 SD），(b) token 比围绕 1× 参考线。"近乎打平、符号因模型而异"与"direct 从不更省"就是那两条参考线。
- **F4d（新）· 山脊图**：**"花多少 token"是一个分布，不是一个数**。16 个配置逐题输出 token 的密度脊，log 轴、按中位排序、每条按自身峰值归一（比的是形状不是高度），白线 = 中位，右列 = P90/中位（≥5× 标红）。
  三层可读信息：**位置**（中位从 269 到 12,968，两个数量级）、**形状**（Kimi K2.6 (reasoning) 与 Qwen-3.6-27B (reasoning) 明显双峰 = 一批题走短路径、一批陷入长推理）、**离散度**（Gemini 1.3× 近乎确定性 vs Kimi K2.6 **10.8×** 重尾）。
  **为什么必须有这张**：其余所有 token 图报的都是均值，而 Kimi K2.6 的均值是中位的 **3.18 倍**——对重尾模型均值是失真的摘要，账单由少数失控题目决定。红色的四个里三个是**非推理**配置，说明长尾不是"开了推理才有"。
- **F2c（新）· 成对山脊**：F2b 的替代品，同样六个双协议配置。**深色（direct）整条压在浅色（code）右边，不是只有尾巴长出去** —— 额外成本付在**普通题**上。中位比 1.5–2.3×，**6/6 全部 >1**。
  口径提醒：中位比系统性高于 `CORE_RESULTS` Finding 5 的**均值**比（1.20–2.08×），因为**code 侧的尾巴更重**（Qwen-3.6-27B：code 均值/中位 2.01 vs direct 1.44），长尾抬高 code 均值、压低均值比。中位答"普通题贵多少"，均值答"跑一整轮贵多少"，两个都对，caption 已写明。
- **F2b_tokens_absolute**：b 面板的绝对量伴图——六模型 code/direct 每轮 token 总量**竖向**成对条形（无倍数，直读消耗量；共用线性轴保留量级差，故每根都标数值），数据同 `F2_F3_direct_vs_code.csv`。
- **F4c（新）**：**输出长度是不是失败信号——去掉三个混淆之后**。左：一个**完整计数**的配置（DeepSeek-V4-flash (reasoning)）按难度层分的三条曲线（low 平、high 陡）；右：14 个配置 × 3 难度层的**加权最小二乘斜率**（准确率 pt / 输出长度翻一倍），0 参考线，实心 = ≥3 个箱、空心 = 2 个箱，横线下的菱形是各层均值。
  **结论：low +0.2、medium -4.0、high -5.7 pt/翻倍**，high 层 14/14 为负——**简单题上写多长不携带信息，难题上每翻一倍掉约 6 分**。
  三处刻意的设计（都写进 caption，缺一个结论就不成立）：① token 用**仓库自己的 o200k 计数**，与结果表同一套账；② **只用单次成功的记录**——token 是按 self-repair 各次累加的，多试几次的记录既 token 翻倍又更可能失败，不剔除就等于把结论造出来；③ **层内比较**，难度是跑模型之前算的 rubric 标签，否则"话多 → 做错"只是"难题难"的复述。
  箱内 <25 题-轮不用，某层可用箱 <2 则不出斜率。**两个只回传摘要的配置整体不画**（见 token 口径节）。
- **F4b（新）**：等成本图——同样的 (tokens, accuracy)，叠加**每道正确答案 token 成本**的虚线等值线（1k/3k/10k/30k）。同一条线上的配置成本相同，**左上角同时更便宜也更准**，"谁更省"不再需要从两个坐标里心算。成本定义 = tokens/run ÷ (accuracy × 436)，写在 caption 里。早期版本曾给整个平面加成本渐变底色，后移除：与等值线**双重编码同一变量**（无新信息），且深蓝底与全图色彩语义冲突（NAVY = reasoning、深 = 高准确率），还压低了青色方块的对比度。等值线标注贴线放置（`clabel`），组合版为避开图例与标签逐条定位。**原 F4 未改动**，两张并存。
- **F4**：编号点改**直接标注**（配对 backbone 只标一次），backbone 连线改为 non-reasoning → reasoning **箭头**并标 +Δpt —— "开推理买什么"变成向量场；Pareto 阶梯线（† 排除）。
- **F6.1 拆为四张独立图**（原三面板版已删除）：**F6.1a** 能力梯度 + 推理孪生箭头（−Δpp）、**F6.1b** 六族 pooled 解出率条形（最难置顶）、**F6.1c** 捷径捕获收敛（18/27 等，`*` = 含前沿配置）、**F6.1d** 同一批判定按机制族分组的三态光栅（27 model-run × 67 陷阱，沿用 F18 语法，族间留空列）。F6.1b 给聚合结论，F6.1d 给逐 run 影像——最难族的暗带在每一行都在，包括最上面的前沿两行，这是"难度属于触发机制而非模型"的直接证据。
- **F6.2** 改为**森林图**：Δ ± 95% CI、0 参考线、红标未校正 p<0.05 行（Holm 校正后无一存活，最小校正 p 见 caption）—— 把全文最强的统计内容画出来，替代 16 条近乎水平的 slope 线。轴标签写明**分析单位是父题**（`Δ parent-level accuracy … paired over N = 346/436 parent problems`）：core 侧是父题本身按 3 轮多数判定，variant 侧是"5 个变体中 ≥3 个解出"，两侧同分母才使配对 McNemar 成立；N 由 `F6_2_forest.csv` 的 `n_parents` 列现取，不硬编码。
- **F7（新）**：(a) 同 670 题上 option ○ vs code ● 哑铃 + clean-480 残差对（青色），(b) rescue 率条形对 25% 随机参考线。
- **F8（新）**：三轴构念效度总览 —— 格式轴区间条（从 F7 CSV 现算）、协议轴均值点（从 F2_F3 CSV 现算）、**伪造轴只作注记**（存在性 + 后果 0 pt，刻意不画成频率）。
- **F6.2 双面板分母不合并**的理由不变：numeric 只在 346 个可扰动 parent 上有定义。

- **F9（新）**：去脚手架消融——(a) with→stripped 哑铃（−1.8…−18.5、lost 计数），(b) 模型分布带 10.2→27.1 pt（×2.7）。
- **F10（新）**：跨领域泛化——(a) core vs 131 题跨领域的对角散点（5 点贴 y=x，排序完整保持），(b) 四域 strong-4 vs weak 差距（76/50/45/29 pt）。
- **F11（新）**：题目区分度剖面——436 题按"16 配置解出数"分布、难度着色；1 题零解（dn_6.8）、147 题全解、12 题 ≤3 解。
- **F12（新）**：污染证据漏斗——83,040 runs → 10,430 失败 → 173 echo → 92 严格记忆 → 12 题点名（fence 修复后 fails=10,430，非文档旧值 10,572）。

- **F17 可解性图谱（图集主视觉）**：16 × 436 全矩阵光栅——整个 core 评测一张图；近乎完美的嵌套阶梯（Guttman 型结构，caption 现算重现率）+ 难度色带右侧变深；147 全解 / 1 零解直接可见。
- **F18 陷阱判定光栅**：27 model-run × 67 陷阱三态图——"落入预测捷径"的红色**竖条纹**就是收敛失败的直接影像，条纹顶到前沿行（holton_28）。
- **F19 答案空间解剖**：同一道题的全部 48 个答案摆上数轴——(a) `4.5` 的 0.345% 错误共识竖线贯穿所有梯队（正确值印在题面里）；(b) `ry_7.7` 横跨 40 个数量级的无结构散布。结构性捷径 vs 无结构崩塌。

- **F20 MCQ 判定图谱**：670 × 3 四态光栅、缺陷/干净分块——缺陷块内 computed-only **恰好为 0**（坏键下正确推导结构上不可得分），选项字母仍拿 58–76%。
- **F21 单位调和解剖**：1,684/28,884 (5.8%) 的通过子答案仅靠单位调和成立，top-10 换算对条形——"单位盲评分器每 17 个正确答案错判 1 个"。
- **F22 脆弱性地图**：346 × 16 四态光栅 + 12 个泄漏父题 ▼ 标记——fragile 仅 2.9%、无条纹、最深列 5/16，与 F18 的红条纹构成"阴性对照"。

已出 23 张：F1 热图、F2_F3_protocol、F2b 绝对 token、F4 效率前沿、F5 主结果、F6.1a/b/c/d 陷阱四图、F6.2 森林图、F6.3 提示词、F7 MCQ 虚高、F8 三轴、F9 去脚手架、F10 跨领域、F11 区分度、F12 证据漏斗、F17 可解性图谱、F18 陷阱光栅、F19 答案空间、F20 MCQ 判定图谱、F21 单位调和、F22 脆弱性地图。F6.4/F6.5 与 **F13–F16 的四张 CSV（修复预算/推理增益×难度/core 容差/元数）保留为数值表**——统计结论可在正文引用，图形呈现被 F17–F19 取代。

---

## 复算

所有数字可用需求单 §0 的方法复算。核心口径：

- **前沿配置 = 16 个**（不含 ClimateGPT-13B/70B），除非明确写了 18；
- **题级通过 = 3 次 run 中 ≥2 次**（majority-of-3）；
- **变体家族的 parent 保住 = 5 个变体中 ≥3 个**；
- **陷阱落坑判定必须用 `shortcut_values` 完整向量**，不能用 `shortcut_value` 标量（见 `docs/results/TRAP_RESULTS.md` Table 4）。
