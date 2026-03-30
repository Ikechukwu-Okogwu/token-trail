# Optimization 模块说明

## Mutation（`mutation.py` + `mutation_config.json`）

配置以 **JSON 字典** 读入（无专用类），默认文件为包内的 `mutation_config.json`。

### 会变什么

| 对象 | 行为 |
|------|------|
| **整数超参** `k`, `winnow_window`, `max_pos_each`, `min_group_size`, `delta_tol`, `max_gap` | 以概率 `prob_int_param` 分别尝试变异；在 `[-int_step_max, int_step_max]` 内随机加减一步，再 **钳制到 `bounds` 中对应区间**。`min_group_size` 额外保证 **至少 2**。 |
| **Group filter 全局** `keep_threshold`, `default_similarity_no_match` | 以概率 `prob_float_global` 分别尝试；加上 `[-float_delta, float_delta]` 均匀扰动，再 **钳制到 `bounds`**。 |
| **每个 `GroupFilterFeature`** | 以概率 `prob_feature_interval` 对该 feature 的**全部** `intervals` 条目做扰动：对 `[lo,hi]` 各加 `[-interval_jitter, interval_jitter]`，再 **限制在 [0,1]**，若 `lo>hi` 则压到同一点。`contribution` / `weight` 分别以 `prob_feature_contribution`、`prob_feature_weight` 用类似全局的浮点步长扰动，并钳制到 `bounds.contribution` / `bounds.weight`；`weight` 步长略大，且若非正会被抬到允许下界。 |
| **复制 feature** | 以概率 `prob_duplicate_feature`，在已有 feature 中随机选一个 **深拷贝式** 复制（新 `name` 带 `_dup_` 后缀随机数），并 **仅在当前 feature 个数 < 24 时** 追加一条。 |

### 当前不会变什么

- `type_mapping`（整张 CSV 等价的映射表不变）
- `strategy`（仍为 `json_leaf`）
- `default_categories`
- feature 的 `name`（除复制产生新名）、`role` 字符串

### 随机种子

`mutation_config.json` 中 `random_seed` 为 **数字** 时，未传入 `rng` 的 `mutate_pipeline_config` 会使用该种子；为 **`null`** 时使用系统非确定性 RNG。

### 与 GA 的关系

本实现是 **单代单个体 mutation 算子**：输入一个 `TokenizePipelineConfig`，输出一个新实例（frozen dataclass，`replace` 构造），便于与 selection / crossover 组合。
