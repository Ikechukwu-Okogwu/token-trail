# Optimization 模块说明

## Mutation（`mutation.py` + `mutation_config.json`）

配置以 **JSON 字典** 读入（无专用类），默认文件为包内的 `mutation_config.json`。

### 会变什么


| 对象                                                                                      | 行为                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **整数超参** `k`, `winnow_window`, `max_pos_each`, `min_group_size`, `delta_tol`, `max_gap` | 以概率 `prob_int_param` 分别尝试变异；在 `[-int_step_max, int_step_max]` 内随机加减一步，再 **钳制到** `bounds` **中对应区间**。`min_group_size` 额外保证 **至少 2**。                                                                                                                                                                                           |
| **Group filter 全局** `keep_threshold`, `default_similarity_no_match`                     | 以概率 `prob_float_global` 分别尝试；加上 `[-float_delta, float_delta]` 均匀扰动，再 **钳制到 `bounds`**。                                                                                                                                                                                                                                       |
| **每个 `GroupFilterFeature`**                                                             | 以概率 `prob_feature_interval` 对该 feature 的**全部** `intervals` 条目做扰动：对 `[lo,hi]` 各加 `[-interval_jitter, interval_jitter]`，再 **限制在 [0,1]**，若 `lo>hi` 则压到同一点。`contribution` / `weight` 分别以 `prob_feature_contribution`、`prob_feature_weight` 用类似全局的浮点步长扰动，并钳制到 `bounds.contribution` / `bounds.weight`；`weight` 步长略大，且若非正会被抬到允许下界。 |
| **复制 feature**                                                                          | 以概率 `prob_duplicate_feature`，在已有 feature 中随机选一个 **深拷贝式** 复制（新 `name` 带 `_dup_` 后缀随机数），并 **仅在当前 feature 个数 < 24 时** 追加一条。                                                                                                                                                                                                     |


### 当前不会变什么

- `type_mapping`（整张 CSV 等价的映射表不变）
- `strategy`（仍为 `json_leaf`）
- `default_categories`
- feature 的 `name`（除复制产生新名）、`role` 字符串

### 随机种子

`mutation_config.json` 中 `random_seed` 为 **数字** 时，未传入 `rng` 的 `mutate_pipeline_config` 会使用该种子；为 `**null`** 时使用系统非确定性 RNG。

### 与 GA 的关系

本实现是 **单代单个体 mutation 算子**：输入一个 `TokenizePipelineConfig`，输出一个新实例（frozen dataclass，`replace` 构造），便于与 selection / crossover 组合。

## Crossover（`crossover.py` + `crossover_config.json`）

- **配对**：以 **parent A 的每个 feature 为锚**，在 parent B 中 **贪心** 找一个未使用的 donor：要求 interval key 交集大小 ≥ `min_overlap_keys`，可选 **同 `role`**（`require_same_role_for_pairing`）；在候选中取 **先比 |∩|、再比 Jaccard** 最大者。每个 donor **最多配对一次**。
- **杂交**：对匹配上的两边，子代 interval 的 key 集合为 **并集**；**交集上的每个 key** 随机选自父之一；**仅 A 有 / 仅 B 有** 的 key 分别继承对应父本。`name` 拼接，`contribution`/`weight` 二选一，`weight` 保证 >0。
- **未匹配**：锚侧或剩余 donor 以概率 `prob_keep_unmatched_feature` **整条保留**，否则丢弃。
- **Pipeline**：`crossover_pipeline_config` 对整型/布尔式字段做 **均匀交叉**；`type_mapping` / `strategy` / `default_categories` 整包来自某一父本。
- **测试**：在 `backend` 下执行  
`python -m unittest discover -s app/analysis/optimization/tests -p "test_*.py" -v`

## Genetic（`genetic.py` + `genetic_config.json`）

- **入口**：`python -m app.analysis.optimization.demo genetic`，加 `**--fast`** 使用 `genetic_config.json` 内 `fast` 块：更小种群/代数 + **单套**回归 fixture（默认 `assignment_reordered_functions`），便于冒烟。
- **流程**：第 0 代用 active bundle 作种子，补满种群为「对随机父代 mutation」；每代对 **每个个体** 算 regression fitness 并 **打印**；保留 `elitism_keep` 个最优，其余父代从当代较好的一半里随机选后再 mutation。
- **Hall of fame（历史前 5 名 Fitness）**：单次运行内用 **小根堆** 维护已见到的 **五个最高** `F`；堆顶为当前「第五名」门槛。仅当本次评估的 `F` **进入**该集合时保存 gene（未满 5 次先填满；已满则 `**F` 必须严格大于**堆顶才会替换并保存）。并 **追写** `genetic_memory.csv`。`genetic_memory.csv` 与 `genes/` 已在 `.gitignore` 中忽略。

