"""Demo: function_rename_variable_inplace and get_var_def_order on Java methods."""

import sys
from pathlib import Path

_backend = Path(__file__).resolve().parents[3]
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.analysis.tree_sitter_analysis.function_refactor_tools import (
    function_rename_variable_by_defining_order,
    function_rename_variable_inplace,
    get_var_def_order,
)
from app.analysis.tree_sitter_analysis.refactor_tools import (
    get_all_function_names_in_class,
    get_all_functions_in_class,
    node_to_source,
)

_SCRIPT_DIR = Path(__file__).resolve().parent
# original_file_path = _SCRIPT_DIR / "assignment_renamed_vars/submissions/Alice/Main.java"
original_file_path = _SCRIPT_DIR / "regression/assignment_stage3_rankset/submissions/S09/Main.java"
compared_file_path = _SCRIPT_DIR / "regression/assignment_stage3_rankset/submissions/S10/Main.java"



def demo_get_var_def_order():
    """Show variable definition order (top-level only) in sumEven, rotate, and main."""
    with open(original_file_path, encoding="utf-8") as f:
        code = f.read()
    code_bytes = code.encode("utf-8")
    methods = get_all_functions_in_class(code_bytes, "RenamedBase")
    names = get_all_function_names_in_class(code_bytes, "RenamedBase")
    # sumEven: int total = 0; for (v : values) - only total is top-level
    sum_even = methods[names.index("sumEven")]
    order = get_var_def_order(sum_even, code_bytes, ["total"])
    print("sumEven variables [total] def order:", order)
    assert order == ["total"], order
    # rotate: int first = ...; for (int i...) - only first is top-level
    rotate = methods[names.index("rotate")]
    order2 = get_var_def_order(rotate, code_bytes, ["first"])
    print("rotate variables [first] def order:", order2)
    assert order2 == ["first"], order2
    # main: int[] values; for(...); int total; int w; int[] rotated
    main = methods[names.index("main")]
    order3 = get_var_def_order(main, code_bytes, ["values", "total", "w", "rotated"])
    print("main variables [values, total, w, rotated] def order:", order3)
    assert order3 == ["values", "total", "w", "rotated"], order3
    print("Assertions passed.")


def demo_rename_variable():
    with open(original_file_path, encoding="utf-8") as f:
        code = f.read()
    code_bytes = code.encode("utf-8")
    methods = get_all_functions_in_class(code_bytes, "RenamedBase")
    names = get_all_function_names_in_class(code_bytes, "RenamedBase")
    sum_even = methods[names.index("sumEven")]
    print("=== Before (sumEven, variable 'total') ===")
    print(node_to_source(sum_even, code_bytes))
    print()
    new_code = function_rename_variable_inplace(code, sum_even, "total", "sum")
    # Re-parse to get updated method node for display
    code_new_bytes = new_code.encode("utf-8")
    methods_new = get_all_functions_in_class(code_new_bytes, "RenamedBase")
    names_new = get_all_function_names_in_class(code_new_bytes, "RenamedBase")
    sum_even_new = methods_new[names_new.index("sumEven")]
    print("=== After (renamed 'total' -> 'sum') ===")
    print(node_to_source(sum_even_new, code_new_bytes))
    print()
    # Assert the rename worked in sumEven
    assert "int sum = 0" in new_code, "Expected 'int sum = 0'"
    assert "sum += v" in new_code, "Expected 'sum += v'"
    assert "return sum" in new_code, "Expected 'return sum'"
    print("Assertions passed.")


def demo_rename_variable_by_defining_order():
    """Rename all variables in main to VAR_1, VAR_2, ... by def order."""
    with open(original_file_path, encoding="utf-8") as f:
        code = f.read()
    code_bytes = code.encode("utf-8")
    methods = get_all_functions_in_class(code_bytes, "RenamedBase")
    names = get_all_function_names_in_class(code_bytes, "RenamedBase")
    main_method = methods[names.index("main")]
    func_source = node_to_source(main_method, code_bytes)
    print("=== Before (main) ===")
    print(func_source)
    print()
    new_func = function_rename_variable_by_defining_order(func_source)
    print("=== After (vars -> VAR_1, VAR_2, VAR_3, VAR_4) ===")
    print(new_func)
    print()
    for i in range(1, 5):
        assert f"VAR_{i}" in new_func, f"Expected VAR_{i}"
    print("Assertions passed.")


if __name__ == "__main__":
    # demo_get_var_def_order()
    # print()
    demo_rename_variable()
    # print()
    # demo_rename_variable_by_defining_order()
