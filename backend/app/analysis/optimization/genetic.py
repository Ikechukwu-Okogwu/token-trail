"""
Mutation-only evolutionary loop over ``TokenizePipelineConfig`` (regression fitness).

Config: ``genetic_config.json`` (plain dict). Hall of fame: at most **N** best
fitness values **seen so far in this run** (min-heap of historical top-N; default
``N=5``). A gene is saved only when its ``F`` enters that set (fills a free slot or
strictly beats the weakest in the heap once full).

Outputs are scoped per language under ``optimization/genes/<language>/``:
``genetic_memory.csv`` and timestamped gene bundle directories.
"""

from __future__ import annotations

import csv
import hashlib
import heapq
import json
import random
import shutil
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

from app.analysis.config import (
    TokenizePipelineConfig,
    load_tokenize_pipeline_config_from_meta_json,
    save_tokenize_pipeline_bundle,
)
from app.analysis.optimization.fitness import FitnessBreakdown, evaluate_fitness
from app.analysis.optimization.mutation import load_mutation_config, mutate_pipeline_config

_OPT_ROOT = Path(__file__).resolve().parent
_TREE_SITTER_ROOT = _OPT_ROOT.parent / "tree_sitter_analysis"
DEFAULT_GENETIC_CONFIG_PATH = _OPT_ROOT / "genetic_config.json"
_GENES_ROOT = _OPT_ROOT / "genes"

GENETIC_LANGUAGES: frozenset[str] = frozenset({"java", "c", "cpp"})


def genes_language_root(language: str, *, opt_root: Path | None = None) -> Path:
    """``optimization/genes/<language>/`` (absolute)."""
    lang = (language or "").strip().lower()
    root = Path(opt_root) if opt_root is not None else _OPT_ROOT
    return (root / "genes" / lang).resolve()


def genetic_memory_path(language: str, *, opt_root: Path | None = None) -> Path:
    """``optimization/genes/<language>/genetic_memory.csv`` (absolute)."""
    return genes_language_root(language, opt_root=opt_root) / "genetic_memory.csv"


def init_bundle_dir(language: str, *, opt_root: Path | None = None) -> Path:
    """Human-authored seed bundle: ``optimization/genes/<language>/init/``."""
    return genes_language_root(language, opt_root=opt_root) / "init"


def init_bundle_meta_path(language: str, *, opt_root: Path | None = None) -> Path:
    """Path to ``init/meta.json`` for the given language."""
    return init_bundle_dir(language, opt_root=opt_root) / "meta.json"


def load_genetic_config(path: str | Path | None = None) -> dict:
    p = Path(DEFAULT_GENETIC_CONFIG_PATH if path is None else path)
    return json.loads(p.read_text(encoding="utf-8"))


def _resolve_fixtures(subpaths: Sequence[str]) -> list[Path]:
    return [(_TREE_SITTER_ROOT / Path(s)).resolve() for s in subpaths]


def _language_block(gc: dict, language: str) -> dict:
    langs = gc.get("languages")
    if not isinstance(langs, Mapping):
        return {}
    block = langs.get((language or "").strip().lower())
    return block if isinstance(block, dict) else {}


def _fixture_subpaths_for_run(
    gc: dict,
    *,
    language: str,
    fast: bool,
) -> list[str]:
    """Resolve regression fixture subpaths under ``tree_sitter_analysis/``."""
    lang = (language or "").strip().lower()
    lang_paths = _language_block(gc, lang).get("regression_fixture_subpaths")
    if lang_paths is None or not isinstance(lang_paths, list):
        lang_paths = []
    lang_paths = [str(s).strip().strip("/").replace("\\", "/") for s in lang_paths if str(s).strip()]

    if fast:
        fb = gc.get("fast") or {}
        fast_paths = fb.get("regression_fixture_subpaths")
        if isinstance(fast_paths, list) and fast_paths:
            return [
                str(s).strip().strip("/").replace("\\", "/")
                for s in fast_paths
                if str(s).strip()
            ]
        # Sensible default: first configured fixture for this language.
        if lang_paths:
            return [lang_paths[0]]
        raise ValueError(
            f"genetic fast mode: set genetic_config.languages.{lang}.regression_fixture_subpaths "
            "or fast.regression_fixture_subpaths"
        )

    if lang_paths:
        return lang_paths

    # Backward compatibility: top-level regression_fixture_subpaths (undocumented).
    legacy = gc.get("regression_fixture_subpaths")
    if isinstance(legacy, list) and legacy:
        return [str(s).strip() for s in legacy if str(s).strip()]

    raise ValueError(
        f"genetic_config must define languages.{lang}.regression_fixture_subpaths (non-empty list)"
    )


def _maybe_migrate_legacy_memory(java_memory: Path) -> None:
    """If old ``optimization/genetic_memory.csv`` exists and ``genes/java/`` has none, copy once."""
    legacy = _OPT_ROOT / "genetic_memory.csv"
    if legacy.is_file() and not java_memory.is_file():
        java_memory.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy, java_memory)


class HistoricalTopNFitness:
    """
    Tracks the ``N`` highest fitness scores seen in the current run.

    Internal state is a min-heap of size ``<= N`` where ``heap[0]`` is the
    **weakest** among the kept scores (the admission bar once full).
    """

    def __init__(self, n: int = 5) -> None:
        if n < 1:
            raise ValueError(f"HistoricalTopNFitness: n must be >= 1, got {n}")
        self._n = n
        self._heap: list[float] = []

    def admit(self, f: float) -> bool:
        """If ``f`` enters the historical top-``N``, push/replace and return ``True``."""
        if len(self._heap) < self._n:
            heapq.heappush(self._heap, f)
            return True
        if f > self._heap[0]:
            heapq.heapreplace(self._heap, f)
            return True
        return False


def _append_genetic_memory_row(
    path: Path,
    *,
    run_tag: str,
    generation: int,
    individual_index: int,
    bd: FitnessBreakdown,
    gene_rel: str,
) -> None:
    fieldnames = [
        "run_tag",
        "generation",
        "individual_index",
        "fitness",
        "accuracy",
        "penalty_mean",
        "n_rows",
        "gene_bundle_rel",
    ]
    new_file = not path.is_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if new_file:
            w.writeheader()
        w.writerow(
            {
                "run_tag": run_tag,
                "generation": generation,
                "individual_index": individual_index,
                "fitness": f"{bd.fitness:.8f}",
                "accuracy": f"{bd.accuracy:.8f}",
                "penalty_mean": f"{bd.penalty_mean:.8f}",
                "n_rows": bd.n,
                "gene_bundle_rel": gene_rel,
            }
        )


def _safe_dirname(f: float, gen: int, idx: int, run_tag: str) -> str:
    fs = f"{f:.6f}".replace(".", "p")
    return f"{run_tag}_g{gen:03d}_i{idx:02d}_F{fs}"


def _bundle_file_fingerprint(meta_json: Path) -> str | None:
    """SHA-256 over meta + type_mapping + group_filter files (stable merge of bundle)."""
    if not meta_json.is_file():
        return None
    try:
        data = json.loads(meta_json.read_text(encoding="utf-8"))
        root = meta_json.parent
        tm = root / str(data.get("type_mapping_file", ""))
        gf = root / str(data.get("group_filter_config_file", ""))
        if not tm.is_file() or not gf.is_file():
            return None
        h = hashlib.sha256()
        for path in (meta_json, tm, gf):
            h.update(path.read_bytes())
        return h.hexdigest()
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _load_config_from_gene_rel(rel: str, *, opt_root: Path) -> tuple[TokenizePipelineConfig | None, str | None]:
    """
    Resolve ``gene_bundle_rel`` (relative to ``opt_root``) and load config.

    Returns:
        ``(config, fingerprint)`` or ``(None, None)`` if missing or invalid.
    """
    rel_norm = rel.strip().replace("\\", "/").lstrip("/")
    if not rel_norm:
        return None, None
    bundle_dir = (opt_root / rel_norm).resolve()
    meta = bundle_dir / "meta.json"
    fp = _bundle_file_fingerprint(meta)
    if fp is None:
        return None, None
    try:
        return load_tokenize_pipeline_config_from_meta_json(meta), fp
    except (OSError, ValueError, FileNotFoundError):
        return None, None


def initial_population_from_memory_and_init(
    *,
    pop_size: int,
    memory_csv: Path,
    init_meta: Path,
    mutation_cfg: dict,
    rng: random.Random,
    opt_root: Path | None = None,
) -> tuple[list[TokenizePipelineConfig], int]:
    """
    Rows from ``genetic_memory.csv`` sorted by descending ``fitness``, each row's gene
    bundle loaded if still on disk; **dedupe by SHA-256 of meta + type_mapping +
    group_filter bytes**. Any remaining slots: **one pristine init** bundle, then
    **``mutate_pipeline_config(init, …)``** for the rest (diverse starters near the
    hand-written baseline).

    Returns:
        ``(population, n_from_memory)`` where ``n_from_memory`` counts slots filled
        from memory before padding.
    """
    root = Path(opt_root) if opt_root is not None else _OPT_ROOT
    if not init_meta.is_file():
        raise FileNotFoundError(f"init bundle missing: {init_meta}")
    init_cfg = load_tokenize_pipeline_config_from_meta_json(init_meta)
    if _bundle_file_fingerprint(init_meta) is None:
        raise ValueError(f"could not fingerprint init bundle: {init_meta}")

    scored_rows: list[tuple[float, str]] = []
    if memory_csv.is_file():
        with memory_csv.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    fit = float(row.get("fitness", "nan"))
                except (TypeError, ValueError):
                    continue
                rel = (row.get("gene_bundle_rel") or "").strip()
                if not rel:
                    continue
                scored_rows.append((fit, rel))

    scored_rows.sort(key=lambda x: -x[0])

    population: list[TokenizePipelineConfig] = []
    seen_fp: set[str] = set()

    for _fit, rel in scored_rows:
        if len(population) >= pop_size:
            break
        cfg, fp = _load_config_from_gene_rel(rel, opt_root=root)
        if cfg is None or fp is None:
            continue
        if fp in seen_fp:
            continue
        seen_fp.add(fp)
        population.append(cfg)

    n_from_memory = len(population)

    n_need = pop_size - len(population)
    if n_need > 0:
        population.append(init_cfg)
        n_need -= 1
        while n_need > 0:
            population.append(
                mutate_pipeline_config(init_cfg, mutation_cfg, rng=rng)
            )
            n_need -= 1

    return population[:pop_size], n_from_memory


def run_genetic_search(
    *,
    language: str | None = None,
    fast: bool = False,
    genetic_config_path: str | Path | None = None,
    historical_top_n: int = 5,
) -> None:
    """
    Mutation-only GA: evaluate population each generation (print all fitness),
    elitism + mutate worse half from random parents in the better half.

    Args:
        language: ``java``, ``c``, or ``cpp``. When
            omitted, uses ``default_language`` from ``genetic_config.json``.
        fast: If True, use smaller population/generations from the ``fast`` block and
            a short fixture list (see ``genetic_config.json``).
        historical_top_n: Hall-of-fame size for disk saves / memory rows during this
            run (min-heap of best ``F`` seen); not read from ``genetic_config.json``.
    """
    gc = load_genetic_config(genetic_config_path)
    lang = (language or gc.get("default_language") or "java").strip().lower()
    if lang not in GENETIC_LANGUAGES:
        raise ValueError(
            f"genetic language {language!r} not in {sorted(GENETIC_LANGUAGES)}"
        )
    fast_block = gc.get("fast") or {}
    if fast:
        pop_size = int(fast_block.get("population_size", 2))
        generations = int(fast_block.get("generations", 1))
        elitism = int(fast_block.get("elitism_keep", 1))
        print(f"[genetic] mode=fast language={lang}", flush=True)
    else:
        pop_size = int(gc["population_size"])
        generations = int(gc["generations"])
        elitism = int(gc["elitism_keep"])
        print(f"[genetic] mode=full language={lang}", flush=True)

    fixture_subs = _fixture_subpaths_for_run(gc, language=lang, fast=fast)
    fixtures = _resolve_fixtures(fixture_subs)
    if not fixtures:
        raise ValueError(f"no regression fixtures resolved for language={lang!r}")

    if lang == "java":
        _maybe_migrate_legacy_memory(genetic_memory_path("java"))

    genes_root = genes_language_root(lang)
    memory_csv = genetic_memory_path(lang)
    init_meta = init_bundle_meta_path(lang)
    genes_root.mkdir(parents=True, exist_ok=True)

    seed = gc.get("random_seed")
    rng = random.Random(int(seed) if seed is not None else None)
    penalty_weight = float(gc.get("penalty_weight", 0.25))
    mut_rel = gc.get("mutation_config_file", "mutation_config.json")
    mut_path = Path(mut_rel)
    if not mut_path.is_absolute():
        mut_path = (_OPT_ROOT / mut_path).resolve()
    mc = load_mutation_config(mut_path)

    elitism = max(1, min(elitism, pop_size))

    run_tag = time.strftime("%Y%m%dT%H%M%S", time.localtime())
    hall = HistoricalTopNFitness(historical_top_n)

    pop, n_mem = initial_population_from_memory_and_init(
        pop_size=pop_size,
        memory_csv=memory_csv,
        init_meta=init_meta,
        mutation_cfg=mc,
        rng=rng,
        opt_root=_OPT_ROOT,
    )
    n_fill = pop_size - n_mem
    if n_fill <= 0:
        pad_msg = ""
    elif n_fill == 1:
        pad_msg = ", 1 pristine init"
    else:
        pad_msg = f", 1 pristine init + {n_fill - 1} init mutants"
    print(
        f"[genetic] initial pop: {n_mem} distinct from memory (by bundle hash){pad_msg}",
        flush=True,
    )

    for gen in range(generations):
        print(f"\n--- Generation {gen + 1}/{generations}  pop={pop_size} ---", flush=True)
        scored: list[tuple[FitnessBreakdown, TokenizePipelineConfig]] = []
        for i, ind in enumerate(pop):
            bd = evaluate_fitness(
                ind,
                penalty_weight=penalty_weight,
                fixtures=fixtures,
                silence=True,
            )
            print(
                f"  gen={gen}  ind={i}  F={bd.fitness:.6f}  "
                f"acc={bd.accuracy:.4f}  pen={bd.penalty_mean:.4f}  n={bd.n}",
                flush=True,
            )
            if hall.admit(bd.fitness):
                subdir = _safe_dirname(bd.fitness, gen, i, run_tag)
                out = genes_root / subdir
                save_tokenize_pipeline_bundle(ind, out)
                rel = str(Path("genes") / lang / subdir)
                _append_genetic_memory_row(
                    memory_csv,
                    run_tag=run_tag,
                    generation=gen,
                    individual_index=i,
                    bd=bd,
                    gene_rel=rel,
                )
                print(f"    -> hall save: {rel}", flush=True)
            scored.append((bd, ind))

        scored.sort(key=lambda x: -x[0].fitness)
        elites = [c for _, c in scored[:elitism]]
        new_pop = list(elites)
        better_half_n = max(1, (pop_size + 1) // 2)
        pool = scored[:better_half_n]
        while len(new_pop) < pop_size:
            parent = rng.choice(pool)[1]
            new_pop.append(mutate_pipeline_config(parent, mc, rng=rng))
        pop = new_pop

    print(
        f"\n[genetic] done. language={lang}  genes_dir={genes_root}  memory={memory_csv.resolve()}",
        flush=True,
    )
