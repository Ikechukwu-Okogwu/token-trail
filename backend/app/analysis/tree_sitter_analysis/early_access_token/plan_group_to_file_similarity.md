# 从 `FingerprintPairGroup` 到「文件对整体相似度」— 步骤草案

目标：把每个 **group** 视为在 **token 轴**（或字节、k-gram 窗；以下以 **token 下标** 为主，与当前 `pos_a`/`pos_b` 一致）上的一段 **证据**，对涉及的 token **写入或更新「相似/可疑信度」**，再聚合为 **单一标量**（或可再归一化到 \([0,1]\)）。

**关键约束**（与 `plan.md` 一致）：多个 group 的区间 **大量重叠** 时证据 **不独立**；若不 **去相关 / 归一**，同一批 token 会被 **重复计分**，整体分数 **偏乐观**。实现前需选定一种 **组合规则**（示例见下）。

---

## 步骤 1：准备 token 空间与 group 的包络

输入：文件 A、B 各自的 **过滤后** `tokens[]`（与指纹/k-gram 同一序列）；  
已算好的 `groups: List[FingerprintPairGroup]`；k-gram 长度 `k`。

对 each `g` in `groups`：

- 侧 A：`lo_a = g.pos_a_start`，`hi_a = min(g.pos_a_end + k - 1, len(tokens_a)-1)`  
- 侧 B：同理 `lo_b`, `hi_b`  
- （可选）由 `slice_text(tokens_a[lo_a], tokens_a[hi_a], code_a)` 得到人读片段；**计分** 仍以下标为主。

```text
for g in groups:
    envelop_a[g] = [lo_a, hi_a]   # token 闭区间或半开按约定统一
    envelop_b[g] = [lo_b, hi_b]
    weight[g] = f(g)              # 例：len(g.pairs)、链长、hash 稀有度等；见步骤 3
```

---

## 步骤 2：定义「单条证据」对 token 的贡献

对固定一侧（以 A 为例），任选一种 **更新算子** `UPD`，把 group `g` 在 `lo_a..hi_a` 上的贡献 **`weight[g]`** 合并进数组 `cred_a[i]`（初值为 0 或中性值）。

| 策略 | 伪代码（对 `i in [lo_a, hi_a]`） | 备注 |
|------|----------------------------------|------|
| **取 max** | `cred_a[i] = max(cred_a[i], weight[g])` | 防重叠简单堆高；保守 |
| **加权和** | `cred_a[i] += alpha[g,i] * weight[g]` | 易重复计分；可配合步骤 4 |
| **对数赔率** | `logit_a[i] += w_g * evidence_strength(g)`，最后再 `sigmoid` | 需定义中性点 |
| **贝叶斯式** | 用 Beta 或离散后验逐次更新 | 需显式似然 |

```text
# 例：max 池化（单侧）
init cred_a[i] = 0 for all i
for g in groups:
    (lo, hi) = envelop_a[g]
    w = weight[g]
    for i in lo .. hi:
        cred_a[i] = max(cred_a[i], w)
```

---

## 步骤 3：为每个 group 定权 `weight[g]`（可选但建议）

示例（可混用，需调参）：

- `weight[g] = len(g.pairs)` 或 `sqrt(len(g.pairs))`  
- 按 `first_hash` 频率降权（常见模板哈希权重低）  
- 若 group 被 **另一 group 的 pair 集合在区间上严格包含** 且信息重复，可做 **降权或丢弃**（非极大值抑制的一种）

```text
function weight(g) -> float:
    base = len(g.pairs)
    # optional: base *= template_penalty(g.first_hash)
    return base
```

---

## 步骤 4：重叠去相关（与步骤 2 二选一或组合）

任选其一并写进规范：

**A. Pair 先去重再投影到 token**  

```text
seen = empty set of (pos_a, pos_b, hash) from all g.pairs
for g in groups:
    for p in g.pairs:
        if p in seen: continue
        seen.add(p)
        apply UPD to token ranges implied by p (with k)
```

**B. 只对「非支配」group 计分**  

例如按链长或面积排序，若 `envelop(g)` 几乎被已选集合的并 **覆盖** (>90%)，则 `continue`。

**C. 显式折扣**  

对重叠像素式计数：`cred_a[i] += weight[g] * discount(i, g)`，其中 `discount` 随「已贡献到 i 的 group 个数」递减。

---

## 步骤 5：单侧 → 标量

在 **cred_a**（及对称的 **cred_b**，若两侧独立各算一轨）上聚合：

```text
# 分母：全文件 token 数 N_a
N_a = len(tokens_a)
sum_a = sum(cred_a[i] for i in 0 .. N_a-1)
# 例：平均信度
score_a_raw = sum_a / N_a

# 或：仅「曾被触及」的 token（避免大片 0 稀释）
T = { i | cred_a[i] > epsilon }
score_a_region = sum(cred_a[i] for i in T) / max(1, len(T))
```

若希望 **文件对一个数**，可：

- **对称平均**：`(score_a_raw + score_b_raw) / 2`（先对两侧做同一公式）；或  
- **仅用对齐质量**：只对 A 侧 `cred_a` 计分（证据已蕴含 cross-doc）；或  
- **min**：`min(score_a, score_b)` 以悲观合并。

---

## 步骤 6：映射到 \([0,1]\) 与报告

```text
similarity = clip( monotone_normalize(score), 0, 1 )
# monotone_normalize 可为 min-max、sigmoid、或按标定集分位数
```

输出可同时保留：**未加权 token 平均**、**触及区间平均**、**触及覆盖率** `|T|/N`，便于与 **Winnow+Jaccard** 等并列对比。

---

## 小结 checklist

1. 统一 **过滤后 token 下标** 与 **k**，划定每 group 在 A/B 上的 **闭区间/半开区间**。  
2. 选定 **`UPD`**（推荐先 **per-token max** 做基线，再试加权和 + 步骤 4）。  
3. 选定 **`weight[g]`** 与 **重叠策略**（pair 去重 / NMS / 折扣）。  
4. 选定 **分母**（全文件 vs 触及区域）与 **双侧合并** 方式。  
5. **标定** `normalize`，使分数与教务阈值可比。

本文档为设计草图，不接具体类名实现；数据类型见 `ask.md` 与 `token_fingerprint.py` / `grouping_fingerprint_pairs.py`。
