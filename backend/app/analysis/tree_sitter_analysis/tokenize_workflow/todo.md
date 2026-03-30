# 
make sure it rasis warnings when token raw type not shown in the mapping table is encountered - ok

make sure similar region data is written into mongodb
matchingRegion content confirmed - ok

handle group region overlaping situation - ok

在pipeline的前期载入（或构建所需数据结构）阶段建立自定类型映射表，供后续算法使用
drop token步骤改为依赖此映射表，而不依赖raw（drop token也在构建阶段，按映射后类型丢弃）
drop是在自定类型中存在to_drop时即丢弃，只看to_drop列，不论是否具有其他的type。在drop token时，也drop df中的对应行，使得index对应关系不变。
在目前引用的映射csv中补全，原本被硬编码丢弃的类型映射至to_drop
构建阶段先全量df，再删行
Token序列，Fingerprint序列，token_index->自定类型映射表均为可持久化缓存步骤，在一次pipeline调用期间持续存在（多次涉及同一个文件的对比时反复载入的问题以后再优化）
token_index自定类型映射步骤提前至drop token之前，以便手动用配置文件控制drop token的类型

config module - rest at here

1. 在这里列出config整个pipeline所需的全部项目，标注其中哪些是可机器优化项目

2. 实现config module，使相似度检测算法整体依赖此模块

Question:
1. 配置的形态与文件
    单一文件（例如一个 YAML/JSON）里同时包含：数值参数 + 两个路径（type_mapping、group_filtering），还是 继续 用现有 CSV/JSON，只新增一个 Python dataclass 聚合「路径 + 标量 + 策略」？
    环境/部署：是否需要 dev / prod profile，或仅从环境变量读「主配置文件路径」？

    配置在运行时的形态是全部配置的聚合dataclass，并且不包含文件路径，而是包含所有已载入内存，已经可以使用的config对象
    元配置是数值参数+两个路径，程序根据元配置来载入配置对象
    目前我们暂时不考虑环境/部署，直接从硬编码的固定路径读取元配置
    元配置本体是磁盘上的json文件+硬编码该文件路径

2. 所有权边界
    group_filtering_config.json 的庞大 features 数组：是继续独立成文件、由 config module 只存 路径，还是你希望 有朝一日 也嵌进「总配置」里由一处生成（影响 GA 写回方式）？

    这些内容应该全面存在在总配置对象中。
    磁盘上的group_filtering_config.json是单独的文件，元配置指向这个文件。
    type_mapping同理，只是以后用config/config_bundle_2026-3-29 config/config_bundle_2026-3-29/meta.json类似这种形式集中管理

3. 对外 API
    compute_javacode_similarity / analysis_service：新版本是只接受可选的 pipeline_config: TokenizePipelineConfig | None（None = 默认单例），还是仍允许零散 kwargs 长期并存（兼容期多长）？

    compute_javacode_similarity从currently_using_meta中获取配置。
    tokenize_pipeline仅接受传入配置对象，没有默认值。
    函数签名里删掉k，k也从总配置对象读。
    公开API必填pipeline_config

4. 校验与默认值
    是否引入 Pydantic（或其它 schema）做范围校验（如 k>=1、winnow_window>=1），还是保持轻量 dataclass + 手工 ValueError？
    默认值来源：一律和现在 run_tokenize_similarity_pipeline 一致，还是趁这次你希望改一批默认？

    如果你说担心有的东西填错做校验的话我觉得不做了，不然步骤拖太多，我们现在要快速开发。
    默认值就是现在的配置，改成总配置对象之后我会通过检查运行结果是否一致验证改后不影响程序行为。
    

5. 「整体依赖」的严格程度
    是否要求 禁止 业务代码直接 load_type_mapping_csv(Path(...))，而必须经 config module；还是第一步只要 pipeline 入口 统一即可？

    pipeline入口统一即可。pipeline不管从哪弄到的配置对象。

6. GA / 未来机器优化（若已在规划）
    若 config module 要为 GA 服务：参数是 整份可序列化快照 即可，还是需要 显式列出「可优化维度 + 边界」 的元数据（可生成分开在另一模块，不必塞进第一份 config）？

    我们暂时不考虑这个。

默认自定类型的逻辑不改变，实现延续现状。初次实现以维持既有实现为原则。
strategy使用一个字段来指定使用哪个strategy。strategy的k配置从总配置里面读。
strategy必填。没有default，不填或找不到就报错。

3. 「公开 API 必填 pipeline_config」与 HTTP 服务
analysis_service 这类入口：谁负责 pipeline_config？
config模组里有一个currently_using_meta文件作为分析服务实际上会使用的配置。这里说的不是总配置对象里有这个字段。analysis_service调用时，会自动装载此配置。
bundle在首次实现时就使用，只是使用的内容从现有的复制。

template feature

1. 是否能用旧的class-function对应映射部分来做template检测？因为template部分没有学生改动的动机，目前的template全部为提供工具函数而非boilplate形式，似乎可以直接检测类名对应之后将待检测代码的template部分全部删除，这应该是最干净的template exclusion模式。

2. 需求：将template exclusion以数据预处理的模式融入tokenize pipeline。具体实现放置在tree_sitter_analysis/template_exclusion.py。不再使用三方比对的方式来做exclusion，而是只用template vs one side of code的方式来生成对应的待检测代码。这个步骤发生在token序列生成之前，具体方式是获取template文件内的所有类名，从待检测文件中直接删除对应类名的代码，然后作为待对比代码继续剩余的流程。run_tokenize_similarity_pipeline新增template参数，输入template源代码。由此函数负责调用封装的exclusion功能。这可能涉及对相同代码的多次parsing，但目前阶段以快速实现为主，忽略这个问题。

1. run_tokenize_similarity_pipeline 的签名与 config
当前管线 必填 config: TokenizePipelineConfig。template 打算怎么接？
建议：template: str = ""（或 None）；空 → 不做 exclusion，行为与现在一致。
是否需要写进 meta / 总配置（例如作业级 template 路径），还是 第一版只在函数参数里传？

template是额外输入的内容，不包括在配置中，以你建议的形式加入到参数

2. 双边是否都用同一份 template 裁剪
相似度是 code_a vs code_b。按你描述「template vs 一侧」生成待测代码 —— 实际对比时：
是否约定：对 code_a、code_b 各自 用 同一份 template 源 做 同一套类名删除？
（否则只裁一侧会不对称，一般不合理。）

两侧都裁

3. 「类名」范围
是否 仅 template 顶层类名（与现有 get_class_names(template) 一致）？
内部类 / 同名（极少）：是否 只删与 template 完全同路径的声明，还是简单 simple name 命中就删？

暂时不考虑内部类，只在顶层类名匹配的情况下删除待检测文件中的对应类

4. 删除的 AST 范围
是否 整段 class_declaration（含 body） 删除？
删多个类时，是否 从文件末尾往前删（避免 offset 错位），还是 收集区间后一次性合并？（实现细节，你可交由 Agent。）

删除完后parse回明文代码，使后续步骤重新解析，以浪费性能的代价使得后续代码不需要调整。

5. 上游谁传 template
compute_javacode_similarity / analysis_service 短期是否仍不传 template（保持现状）？
若 Mongo/API 日后要带 template：单独字段还是 每次比对由调用方传入？

目前不传。

6. template_exclusion.py 与 tokenize_workflow 的依赖
若复用 refactor_tools.get_class_names / 解析树：template_exclusion 放在 tree_sitter_analysis/ 会直接依赖父包工具，不会形成 tokenize_workflow → 父包（pipeline 在 tokenize_pipeline.py 里先调 exclusion 再进 worker），结构上是 OK 的。
是否接受 template_exclusion 依赖 java_leaf_tokenize 同一套 grammar（再 parse 一次），还是 只用 refactor 的 tree-sitter 路径？

template_exclusion只依赖同级结构，不与自定义token相关代码发生关系。传递给后续步骤的是明文代码而未进行tokenize，双方没有耦合。

7. 快速实现可显式写进 spec 的默认
template 中有、学生里没有的类名：跳过。
删光后某侧无 leaf token：沿用现有 ValueError 即可？

是的，学生提交仅有template的代码时报错。后续如果测试到这种情况，再和团队协商规定对应行为。

template空白时不做exclusion
删类后不作字符串处理
exclusion中可以调用任何refactor功能块

try ga

1. 我如此定义GA的所有模块：
Gene：就是TokenizePipelineConfig，主要训练对象为：
k
winnow_window
min_group_size
delta_tol
max_gap
GroupFilterFeature

Fitness：使用当前的Gene对当前数据库跑分得出的正确率。
（是否要将每个fail的正确率偏差算入Fitness？）
Selection：从Gene中按排名和正确率混合加权获取多次，可以多次获取到相同的Gene
CrossOver：新的Gene从通过Selection的Genes中随机选择两个parents。
GroupFilterFeature在crossover时会优先选择关心字段一致的Feature。剩余不相关的feature随机选择原样继承或丢弃。如果一个Gene的Feature量超过一个定值则丢弃所有互不相关的Feature
其他基础参数随机选择parents中一侧的参数继承
Mutation：随机对Feature的相似度倾向和范围边界进行微调。有较低概率引入新的Feature。有较低概率使其他基础参数发生变动。

实现流程：
1. 实现Fitness的计算（fail时根据偏离程度额外惩罚，如何惩罚？如果最终fitness以百分数表示的话，那么正确率0%的项目再惩罚会出现负项，这是个问题吗？）

analysis/optimization/fitness.py
given a config, get fitness as float
F = accuracy - lambda*penalty

2. 实现将TokenizePipelineConfig在指定Path下保存为bundle的方法
3. 按你自己的理解实现简单的Mutation函数，使其载入默认的mutation_config.json（简单起见以字典而非自定义类实例的方式载入）并且在optimization/description.md中说明mutation会如何随机调整TokenizePipelineConfig。在optimization/demo.py中新增从默认路径载入Config，mutate了之后将前后对比输出到控制台，最后保存到optimization/genes/test_bundle的测试函数。
4. 先只用mutation跑通遗传算法，看看能不能带来fitness变化。
genetic_config.json也以相同的思路保存在optimization。
遗传算法的每一轮迭代要将当前一代所有gene求出的fitness输出到控制台。
新增genetic_memory.csv，在有fitness评分进入前五最高分的时候将对应的gene保存到genes，将fitness和gene path保存到genetic_memory.csv

4. 以同样的思路实现简单的Crossover函数（暂时不做这步）

@dataclass(frozen=True)
class GroupFilterFeature:
    """
    Conjunction over interval constraints: all ``mapped_type`` shares on **both**
    sides A and B must fall in ``[lo, hi]`` (inclusive).
    """

    name: str
    intervals: dict[str, tuple[float, float]]
    contribution: float
    weight: float
    role: str = "unspecified"

这是可以进行crossover或mutate的Feature结构。

4. 试运行





@dataclass(frozen=True)
class GroupTokenTypeStats:
    """Share of each mapped category (mass-normalized) for A/B spans of one group."""

    side_a: dict[str, float]
    side_b: dict[str, float]
    token_count_a: int
    token_count_b: int
    mass_a: int
    mass_b: int
？？？
