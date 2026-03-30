import ast
from typing import cast

original_path = "similarCodesVariableManipulation/original.py"
copied_path = "similarCodesVariableManipulation/onlyChangeName.py"
change_var_order_path = "similarCodesVariableManipulation/changeVarOrder.py"

with open(original_path, encoding="utf-8") as f:
    original_text = f.read()
    original_tree = ast.parse(original_text)

with open(copied_path, encoding="utf-8") as f:
    copied_text = f.read()
    copied_tree = ast.parse(copied_text)

with open(change_var_order_path, encoding="utf-8") as f:
    change_var_order_text = f.read()
    change_var_order_tree = ast.parse(change_var_order_text)

"""
get the similarity of the first defined function in the two files
without pre processing
"""

def slice_first_defined_function(tree: ast.Module) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node
    raise ValueError("No function defined in the tree")

original_function = slice_first_defined_function(original_tree)
copied_function = slice_first_defined_function(copied_tree)

def refactor_function_rename_variable(
    tree: ast.FunctionDef, original_name: str, new_name: str
) -> ast.FunctionDef:
    # Deep copy via parse/unparse; extract FunctionDef from Module
    parsed = ast.parse(ast.unparse(tree))
    new_tree = cast(ast.FunctionDef, parsed.body[0])
    for node in ast.walk(new_tree):
        if isinstance(node, ast.Name):
            if node.id == original_name:
                node.id = new_name
    return new_tree

def refactor_function_rename_variable_by_defining_order(tree: ast.FunctionDef) -> ast.FunctionDef:
    """
    Walk through the tree, whenever meet a variable definition, add it to the list.
    For all the variables in the list, rename by defining order.
    Rename pattern: VAR_1, VAR_2, ...
    """
    parsed = ast.parse(ast.unparse(tree))
    new_tree = cast(ast.FunctionDef, parsed.body[0])
    variable_list = []
    for node in ast.walk(new_tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_list.append(target.id)
    for i, variable in enumerate(variable_list):
        new_tree = refactor_function_rename_variable(new_tree, variable, f"VAR_{i+1}")
    return new_tree

def _find_assign_index_for_var(body: list[ast.stmt], var_name: str) -> int | None:
    """Return index in body of the Assign that defines var_name, or None."""
    for i, stmt in enumerate(body):
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    return i
    return None

def refactor_function_switch_variable_definition_lines(
    tree: ast.FunctionDef, switches: list[tuple[str, str]]
) -> ast.FunctionDef:
    """Swap definition lines of variable pairs. Each (var_a, var_b) swaps their Assign stmts."""
    parsed = ast.parse(ast.unparse(tree))
    new_tree = cast(ast.FunctionDef, parsed.body[0])
    body = new_tree.body
    for var_a, var_b in switches:
        idx_a = _find_assign_index_for_var(body, var_a)
        idx_b = _find_assign_index_for_var(body, var_b)
        if idx_a is not None and idx_b is not None:
            body[idx_a], body[idx_b] = body[idx_b], body[idx_a]
    return new_tree

def get_var_def_order(tree: ast.FunctionDef, var_names: list[str]) -> list[str]:
    """
    Return the order of first definition for vars in var_names, as they appear in body.
    Raises ValueError if any var in var_names is not found as an Assign target.
    """
    var_set = set(var_names)
    seen: set[str] = set()
    result: list[str] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id in var_set:
                    if target.id not in seen:
                        seen.add(target.id)
                        result.append(target.id)
    missing = set(var_names) - seen
    if missing:
        raise ValueError(f"Variables not found as Assign targets: {missing}")
    return result


def refactor_function_switch_variable_definition_lines_given_similarity_list(
    functionA: ast.FunctionDef, functionB: ast.FunctionDef,
    var_name_similarity_list: list[tuple[str, str]]
) -> ast.FunctionDef:
    """
    Reorder functionB's variable definitions to match functionA's order.
    var_name_similarity_list: (var_in_A, var_in_B) pairs, order = A's canonical order.
    Raises if A's current order doesn't match the list (A is the reference).
    """
    expected_order_A = [a for a, _ in var_name_similarity_list]
    expected_order_B = [b for _, b in var_name_similarity_list]
    current_order_A = get_var_def_order(functionA, expected_order_A)
    current_order_B = get_var_def_order(functionB, expected_order_B)
    if current_order_A != expected_order_A:
        raise ValueError(
            f"functionA order mismatch: expected {expected_order_A}, got {current_order_A}"
        )
    switches = compute_switches(expected_order_B, current_order_B)
    return refactor_function_switch_variable_definition_lines(functionB, switches)

def compute_switches(
    required_list: list[str], current_list: list[str]
) -> list[tuple[str, str]]:
    """
    Return variable name pairs to swap so current_list matches required_list.
    Uses greedy approach: for each position, swap in the required element if missing.
    """
    swaps: list[tuple[str, str]] = []
    current = list(current_list)
    for i in range(len(current)):
        if current[i] != required_list[i]:
            j = current.index(required_list[i])
            swaps.append((current[i], current[j]))
            current[i], current[j] = current[j], current[i]
    return swaps

"""
todo:

given a var name, find the all necessary lines of codes that is required to define the variable
given two var names, find the intersection of their required previous lines
do this later. for now:

assuming a variable is always independently defined.
given the var name similarity list,
[
    ("var1A", "var1B"),
    ("var2A", "var2B"),
    ("var3A", "var3B"),
]
locate vars def line in two functions.
find their current def order. 
[
    ("var1A", "var2B"),
    ("var2A", "var1B"),
    ("var3A", "var3B"),
]
we assume the vars in function A is the "right" order.
compare these two lists, 
find out the necessary switches of variables to make two lists identical.

like:
switches = [
    ("var2B", "var1B")
    ("var3B", "var4B")
]

perform the line switches on the function B. 
like refactor_function_var_def_line_switch(functionB, switches[i][0], switches[i][1])
only switch two vars at a time, repeat until

"""
