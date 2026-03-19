"""Generate regression ZIP fixtures.

Run from repo root:
    python tests/analysis/generate_regression_fixtures.py
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "regression"


def _write_zip(zip_path: Path, files: dict[str, str]) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def _long_java_program(class_name: str, var_prefix: str, *, method_order: list[str] | None = None) -> str:
    helper_lines = []
    for i in range(1, 21):
        helper_lines.extend(
            [
                f"    public static int helper{i}(int {var_prefix}x) {{",
                f"        int {var_prefix}sum = 0;",
                f"        for (int {var_prefix}i = 0; {var_prefix}i < {var_prefix}x; {var_prefix}i++) {{",
                f"            {var_prefix}sum += ({var_prefix}i * {i}) % ({i + 3});",
                "        }",
                f"        return {var_prefix}sum;",
                "    }",
                "",
            ]
        )

    methods = {
        "sumEven": "\n".join(
            [
                "    public static int sumEven(int[] values) {",
                "        int total = 0;",
                "        for (int v : values) {",
                "            if (v % 2 == 0) {",
                "                total += v;",
                "            }",
                "        }",
                "        return total;",
                "    }",
                "",
            ]
        ),
        "weighted": "\n".join(
            [
                "    public static int weighted(int[] values) {",
                "        int total = 0;",
                "        for (int i = 0; i < values.length; i++) {",
                "            total += values[i] * (i + 1);",
                "        }",
                "        return total;",
                "    }",
                "",
            ]
        ),
        "rotate": "\n".join(
            [
                "    public static int[] rotate(int[] values) {",
                "        if (values.length == 0) return values;",
                "        int first = values[0];",
                "        for (int i = 0; i < values.length - 1; i++) {",
                "            values[i] = values[i + 1];",
                "        }",
                "        values[values.length - 1] = first;",
                "        return values;",
                "    }",
                "",
            ]
        ),
    }
    order = method_order or ["sumEven", "weighted", "rotate"]
    ordered_methods = "".join(methods[name] for name in order)

    main_lines = [
        f"public class {class_name} {{",
        "    public static void main(String[] args) {",
        "        int[] values = new int[40];",
        "        for (int i = 0; i < values.length; i++) {",
        "            values[i] = (i * 3 + 7) % 19;",
        "        }",
        "        int total = sumEven(values);",
        "        int w = weighted(values);",
        "        int[] rotated = rotate(values);",
        "        System.out.println(total + w + rotated[0]);",
        "    }",
        "",
        ordered_methods,
        "\n".join(helper_lines),
        "}",
        "",
    ]
    return "\n".join(main_lines)


def _light_rename_variant(text: str) -> str:
    replacements = {
        "values": "dataset",
        "total": "accumulator",
        "weighted": "weightedScore",
        "rotate": "shiftLeft",
        "sumEven": "sumEvenTerms",
    }
    updated = text
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    return updated


def _distinct_java_program(class_name: str, seed: int) -> str:
    lines = [
        f"public class {class_name} {{",
        "    public static int gcd(int a, int b) {",
        "        while (b != 0) {",
        "            int t = b;",
        "            b = a % b;",
        "            a = t;",
        "        }",
        "        return a;",
        "    }",
        "",
        "    public static int lcm(int a, int b) {",
        "        return (a / gcd(a, b)) * b;",
        "    }",
        "",
        "    public static boolean isPrime(int n) {",
        "        if (n < 2) return false;",
        "        for (int i = 2; i * i <= n; i++) {",
        "            if (n % i == 0) return false;",
        "        }",
        "        return true;",
        "    }",
        "",
    ]
    for i in range(1, 45):
        lines.extend(
            [
                f"    public static int sequence{i}(int x) {{",
                "        int value = x;",
                f"        for (int i = 0; i < {i + 5}; i++) {{",
                f"            value = (value * {31 + (seed % 11)} + i + {seed % 13}) % {907 + (seed % 89)};",
                "        }",
                "        return value;",
                "    }",
                "",
            ]
        )
    lines.extend(
        [
            "    public static void main(String[] args) {",
            "        int output = 0;",
            "        for (int i = 1; i < 50; i++) {",
            "            output += sequence1(i) + sequence2(i);",
            "        }",
            f"        System.out.println(output + lcm({84 + (seed % 9)}, {30 + (seed % 7)}));",
            "    }",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def _starter_template_java() -> str:
    lines = [
        "public class StarterTemplate {",
        "    public static int[] sanitize(int[] input) {",
        "        int[] out = new int[input.length];",
        "        for (int i = 0; i < input.length; i++) {",
        "            out[i] = Math.abs(input[i]);",
        "        }",
        "        return out;",
        "    }",
        "",
    ]
    for i in range(1, 35):
        lines.extend(
            [
                f"    public static int helperTemplate{i}(int value) {{",
                f"        return (value * {i + 3} + {i * 2}) % {i + 97};",
                "    }",
                "",
            ]
        )
    lines.extend(["}", ""])
    return "\n".join(lines)


def _template_heavy_program(class_name: str, unique_seed: int, mode: str) -> str:
    template_body = _starter_template_java()
    if mode == "window":
        unique = [
            f"public class {class_name}Extension {{",
            "    public static int solve(int[] nums) {",
            f"        int seed = {unique_seed};",
            "        int best = Integer.MIN_VALUE;",
            "        for (int start = 0; start < nums.length; start++) {",
            "            int sum = 0;",
            "            for (int end = start; end < nums.length; end++) {",
            "                sum += (nums[end] * seed + end) % 101;",
            "                if (sum > best) best = sum;",
            "                seed = (seed * 17 + 11) % 127;",
            "            }",
            "        }",
            "        return best;",
            "    }",
            "}",
            "",
        ]
    else:
        unique = [
            f"public class {class_name}Extension {{",
            "    public static int solve(int[] nums) {",
            "        int[] dp = new int[nums.length + 1];",
            "        for (int i = 1; i <= nums.length; i++) {",
            "            int include = dp[Math.max(0, i - 2)] + Math.abs(nums[i - 1]);",
            "            int exclude = dp[i - 1];",
            "            dp[i] = Math.max(include, exclude);",
            "        }",
            "        int checksum = 0;",
            "        for (int i = 0; i < dp.length; i++) {",
            f"            checksum += (dp[i] * ({unique_seed % 19 + 3})) % 113;",
            "        }",
            "        return dp[nums.length] + checksum;",
            "    }",
            "}",
            "",
        ]
    return template_body + "\n" + "\n".join(unique)


def _build_assignment(
    assignment_name: str,
    submissions: dict[str, str],
    *,
    template_text: str = "",
    language: str = "java",
    require_all_pairs: bool = True,
) -> None:
    assignment_dir = FIXTURES_ROOT / assignment_name
    if assignment_dir.exists():
        shutil.rmtree(assignment_dir)
    submissions_dir = assignment_dir / "submissions"
    submissions_dir.mkdir(parents=True, exist_ok=True)

    for zip_name, source_text in submissions.items():
        _write_zip(submissions_dir / zip_name, {"Main.java": source_text})

    if template_text:
        _write_zip(assignment_dir / "template.zip", {"Template.java": template_text})

    result_path = assignment_dir / "result.txt"
    if not result_path.exists():
        lines = [
            f"fixture={assignment_name}",
            f"language={language}",
            "homogeneous=true",
            f"template_exclusion={'true' if bool(template_text) else 'false'}",
            "engine_mode=direct",
            f"require_all_pairs={'true' if require_all_pairs else 'false'}",
            "",
            "# Add pair expectations manually.",
            "# IMPORTANT: expected values must be human-curated targets, not engine-derived baselines.",
        ]
        result_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    FIXTURES_ROOT.mkdir(parents=True, exist_ok=True)

    # 1) Renamed variables fixture
    _build_assignment(
        "assignment_renamed_vars",
        {
            "Alice.zip": _long_java_program("RenamedBase", "a"),
            "Bob.zip": _light_rename_variant(_long_java_program("RenamedBase", "a")),
            "Carol.zip": _distinct_java_program("DifferentProgram", 13),
        },
    )

    # 2) Reordered functions fixture
    _build_assignment(
        "assignment_reordered_functions",
        {
            "Dev1.zip": _long_java_program("OrderedA", "v", method_order=["sumEven", "weighted", "rotate"]),
            "Dev2.zip": _long_java_program("OrderedB", "v", method_order=["rotate", "sumEven", "weighted"]),
            "Dev3.zip": _distinct_java_program("AltMathTool", 29),
        },
    )

    # 3) Template-heavy fixture
    template_text = _starter_template_java()
    _build_assignment(
        "assignment_template_heavy",
        {
            "TemplateA.zip": _template_heavy_program("TemplateA", 11, "window"),
            "TemplateB.zip": _template_heavy_program("TemplateB", 77, "dp"),
            "TemplateC.zip": _distinct_java_program("TemplateHeavyControl", 53),
        },
        template_text=template_text,
    )

    # 4) Stage3 fixture with 10 submissions and at least one pair + one triple.
    stage3 = {
        "S01.zip": _long_java_program("RankA", "x", method_order=["sumEven", "weighted", "rotate"]),
        "S02.zip": _long_java_program("RankB", "y", method_order=["weighted", "sumEven", "rotate"]),
        "S03.zip": _long_java_program("RankC", "z", method_order=["rotate", "weighted", "sumEven"]),
        "S04.zip": _long_java_program("PairHighA", "h"),
        "S05.zip": _long_java_program("PairHighB", "h"),
        "S06.zip": _template_heavy_program("StageTemplate1", 19, "window"),
        "S07.zip": _template_heavy_program("StageTemplate2", 51, "dp"),
        "S08.zip": _distinct_java_program("UniqueOne", 71),
        "S09.zip": _distinct_java_program("UniqueTwo", 83),
        "S10.zip": _distinct_java_program("UniqueThree", 97),
    }
    _build_assignment(
        "assignment_stage3_rankset",
        stage3,
        template_text=template_text,
    )

    print(f"Generated fixtures under {FIXTURES_ROOT}")
    print("Note: result.txt expectations are intentionally manual/aspirational and are not auto-generated.")


if __name__ == "__main__":
    main()
