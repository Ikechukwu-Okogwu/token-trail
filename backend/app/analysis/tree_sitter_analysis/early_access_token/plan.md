# early_access_token：token 指纹相似度骨架（计划）

## 目标

两段 Java 源码 → 标量相似度；**tokenize + k-gram 哈希绑定为 `JavaKgramStrategy`**；**Winnow 为模块公共 `winnow_select`**。对齐、证据后续再做。

## 拟增文件

- `compare_javacode.py`：对外入口、`JavaKgramStrategy`、`winnow_select`、`compare_java_code`。
- `json_kgram_strategy.py`：`JsonLeafKgramStrategy`（叶子 token + JSON k-gram + SHA1 截断）；`python json_kgram_strategy.py` 跑通全流程示例。
- `description.md`：流程与各层职责（与 `plan.md` 互补，`plan.md` 偏「要动什么」）。

## 骨架函数与类型（拟定）

| 名称 | 作用 |
|------|------|
| `JavaKgramStrategy` | `Protocol`：`compute_kgram_hashes(code) -> Sequence[int]`（有序 k-gram 哈希）；内部仅 tokenize + k-gram（及策略内 k、序列化等）。 |
| `winnow_select` | 公共：对 k-gram 哈希序列做滑窗 Winnow（默认可与 `winnowingCopy` 窗口语义对齐），返回 `frozenset[int]` 指纹哈希。 |
| `compare_java_code` | `strategy -> kgram 序列 -> winnow_select -> pairwise_set_similarity`；可选 `winnow_window`（默认 4）。 |
| `pairwise_set_similarity` | Jaccard（或日后替换为其它集合度量）。 |

**实现顺序**：`JavaKgramStrategy` + `winnow_select` + `compare_java_code`；策略具体类（如接 `tokenize_java` + TLV）后续再填。

## 语言与 Strategy

- **tokenization 放在 Strategy 内**（与 k-gram 绑定，见 `JavaKgramStrategy`）：`compute_kgram_hashes(code)` 里可用任意语言的 Tree-sitter / 词法器；**编排层**（`compare_java_code`：k-gram 序列 → `winnow_select` → Jaccard）**不依赖 Java**，**换 Strategy 即可适配其它语言**。
- **命名**：当前入口名为 `compare_java_code`、`JavaKgramStrategy`，体现 **本项目先落地 Java**；若日后正式当跨语言骨架用，可另增 `compare_code` 等别名或迁移命名，逻辑不变。
- **谁负责选语言**：作业 / 分析服务按 `assignment.language`（或等价字段）**选用对应 Strategy 实例**；多文件合并、模板排除等仍属 **更外层**，不放在本模块策略里。

## 暂不做的

- 高亮 / `matchingRegions`；模板排除（可 second pass）；与 `pipeline.compute_similarity_javacode` 自动切换。

# 接下来做什么？

待讨论
1. 参数对象。在一次分析过程中，从顶层往下派发全局一致的参数对象，各个部分自行根据dict字段选取自身所需对象。参数对象的定义在顶层写出来，通过文档约定执行。所有参与分析的函数均获取argument_overwrite_dict。在获取原本的参数后，会从dict中获取参数覆盖原本的参数。具体获取哪个字段直接在代码中写死。
2. fingerprint包含信息不足以支撑一部分后续feature。我们需要高亮相似的片段。在tokenize思路下fingerprint应该包含原文起止点信息。并且我们需要testWinowingCode中重新组织匹配fingerprint，找出连续相似组的方法。
3. Tokenize方法在最后三组测试中仍表现不佳（可预期）
  FAIL S08 vs S09: sim=94.64% (expected ~10.00%, range [0.00%,22.00%])
  FAIL S08 vs S10: sim=95.68% (expected ~10.00%, range [0.00%,22.00%])
  FAIL S09 vs S10: sim=95.34% (expected ~10.00%, range [0.00%,22.00%])
这种情况下整体tokenize然后比较的流程可以直接针对它进行优化吗？
可以根据起始点的类型（lebel, operator等）给fingerprint添加权重？
如果有类型权重的话也许可以用数据集跑爬山算法来优化权重……

肯定要做的部分
1. 在tokenize思路中重新实现计算连续相似组
2. 将结果写入matchingRegions。这个改动上main了吗？

Zhang — quick confirmation so you can implement confidently:

Your analysis output should be written to Mongo similarity_results as one document per run:
{ runId, assignmentId, createdAt, pairs: [{submissionA, submissionB, score}] }
(this is already how analysis_service.py is set up).

Inputs are available via submissions.mergedStoragePath.

Template/boilerplate is stored on the assignment as exclusionCode.

So your baseline engine can: load submissions → read merged files → compute pairs[] → write/update the run’s similarity_results doc.


Now what
1. parameter set
2. optimize for S09 S10 cases
3. matchingRegions is been readed but seem not implemented by the frontend. But since we already have the defined format I should add it.
There is a problem
The way to compute the regions will be different. If I still do class/function matching, slice of code tokenization comparing and average similarity, I need to maintain line shift when it goes down to class/function phase. If I do global tokenization/direct compare I just need to read the line info from result.
Anyway, the final product of current analysis.py is no enough information.
We can start by defining the expected product.
The product of analysing a slice of code should be pairs of similar fingerprints.
Fingerprints includes information: 
1. hash value
2. reference of the leaf node that shares the beginning position of the fingerprint(acts as the source of info)
  (Maybe all the leaf nodes that participates the computation process of the fingerprint)

  --- Regression: regression/assignment_reordered_functions ---

  template: (none)
  PASS Dev1 vs Dev2: sim=100.00% (expected ~90.00%, range [82.00%,100.00%])
D:\work\4P02\Project\token-trail\backend\app\analysis\tree_sitter_analysis\refactor_tools.py:129: UserWarning: match_labels: unequal label counts: 24 vs 48
48？？？？？？

总结：
refactor思路的预设过强而且非常难以泛化
可能还是直接tokenize整体对比比较合理。

ast分析一方面可以用来用叶节点生成token，另一方面可以为token添加特征信息（比如包括什么类型的token）
再用类型给token加权，通过参数和权重调整来优化算法

token内容: 类型 字符内容 起止点 行号
fingerprint内容：哈希值 起止点 对应token的reference 行号起止点

对类似S09 S10这种情况进行edgecase检测？如果两段检测到相似的代码符合“结构几乎完全一致，但是参与计算的关键literal不同的数学计算过程”这一特征就放行？

# 继续开发
已完成Token和Fingerprint的定义，接下来
1. 该使用新定义的地方使用新定义
2. 增加中间函数pairing_fingerprints，生成所有哈希一致的fingerprints对集。一对Fingerprint对象使用新的数据结构FingerprintPair，其中包含index_delta值，表示这两个Fingerprint的index位置差。返回值是hash->List[FingerprintPair]的字典

3. 配对列表（`pairing_fingerprints` / 等价于 `build_match_points` 的平面列表）包含所有疑似点匹配。接下来 **`grouping_fingerprint_pairs` 与 `testWinowingCode/fingerprint.py` 中 `group_match_points` 保持一致**，不要用「按左 index 排序 + 在剩余 pair 里选最近」的变体。

   **坐标约定**：`pos_a` / `pos_b` 分别为 A、B 两侧 **`Fingerprint.token_start_index`**（过滤后 token 流上 k-gram 起点）；`delta = pos_b - pos_a`（与 `MatchPoint` 一致）。

   **参数**：与参考相同，记为 `min_group_size`、`delta_tol`、`max_gap`（参考里无单独的「仅左轴 gap」，**两侧**都要约束）。

   **流程**（与 `group_match_points` 同序）：

   ```
   输入：points = List[FingerprintPair]（每项含 pos_a, pos_b, hash_value 或 delta 可由其导出）

   pts = sort(points, key = (delta, pos_a, pos_b))
   groups = []
   cur = []

   for p in pts:
       if cur is empty:
           cur = [p]
           continue
       prev = cur 的最后一项
       same_diag    = |p.delta - prev.delta| <= delta_tol
       increasing   = p.pos_a >= prev.pos_a and p.pos_b >= prev.pos_b
       close_enough = (p.pos_a - prev.pos_a) <= max_gap and (p.pos_b - prev.pos_b) <= max_gap

       if same_diag and increasing and close_enough:
           将 p 追加到 cur
       else:
           if len(cur) >= min_group_size: groups.append(cur)
           cur = [p]

   if len(cur) >= min_group_size: groups.append(cur)

   对 groups 按 (-len(g), min(x.pos_a for x in g)) 排序后返回
   ```

   **说明**：这是**单次线性扫描**已全局排序后的 `pts`，不在「剩余集合」里做最近邻搜索；与参考实现一一对应，便于对照调试。

4. 获取到group后应该做什么？

group可能可以通过某种过程来增加或减少此group的相似信度
这个过程也许可以帮我们处理S09 S10的情况。一个group可以访问fingerprint，fingerprint可以找到自身所相关的token，token里有类型，也许可以用这个类型成分来判定是否是literal区分

当我们获取确定相似的group之后，在group内对所有token设置suspectable=true（可以用boolean index）然后统计suspectable token number / total token number = similarity

前面的加权怎么办？所有标记刻意的token乘类型权重再加和？权重可以>1吗？
如果权重必须<1那就不可能有100%相似度了，即使全同。

最基础的做法：当前的所有group全部标定为可疑，将所有涉及的token也全部定为可疑后，计算可疑token比例。

进阶一点：
group[0] size=410  pos_a:[0..1190]  pos_b:[0..1190]  first_hash=971716140
group[1] size=242  pos_a:[279..1144]  pos_b:[325..1190]  first_hash=402906470
group[2] size=242  pos_a:[325..1190]  pos_b:[279..1144]  first_hash=402906470
看当前的输出group范围是反复出现重合的。像这个例子中group[0]几乎覆盖了后面所有group。
group可以重合和不可以重合时的分析思路应该不一样。如果要对group进行拆分，可能也会影响分析结果。例如，如果一个group连续包含了两个functions，那么也许有理由将其作为两个group分别计算相似度。
从直觉看来group似乎可以重合。一个很简单的例子：code_a.function_a 与code_b.func_a，code_b.func_b都相似，那么在code_a这一边就重合了。但上述例子中group[0]的情况是它和大量的其他group范围重叠，实际计算之中应该怎么处理这种情况呢？是否与其他group完全重合的group应该无视掉？