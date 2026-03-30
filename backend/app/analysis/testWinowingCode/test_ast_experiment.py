import ast

from render_result import store_compare_result_as_html

from ast_experiment import (
    change_var_order_tree,
    copied_tree,
    original_tree,
    refactor_function_rename_variable_by_defining_order,
    refactor_function_switch_variable_definition_lines,
    refactor_function_switch_variable_definition_lines_given_similarity_list,
    slice_first_defined_function,
)


def demo_RefactorByOrder_vs_DirectCompare():
    functionA = slice_first_defined_function(original_tree)
    functionB = slice_first_defined_function(copied_tree)
    from testWinowingLib import compare_texts_with_template

    result_1 = compare_texts_with_template(
        ast.unparse(functionA), ast.unparse(functionB), auto_store=False
    )
    store_compare_result_as_html(
        base_dir=result_1["base_dir"],
        name_a="DirectCompare:original.py",
        name_b="DirectCompare:onlyChangeName.py",
        text_a=result_1["text_a"],
        text_b=result_1["text_b"],
        similarity=result_1["similarity"],
        overlap=result_1["overlap"],
        groups=result_1["groups"],
    )

    functionA_renamed = refactor_function_rename_variable_by_defining_order(functionA)
    functionB_renamed = refactor_function_rename_variable_by_defining_order(functionB)
    result_2 = compare_texts_with_template(
        ast.unparse(functionA_renamed), ast.unparse(functionB_renamed), auto_store=False
    )
    store_compare_result_as_html(
        base_dir=result_2["base_dir"],
        name_a="RefactorByOrder:original.py",
        name_b="RefactorByOrder:onlyChangeName.py",
        text_a=result_2["text_a"],
        text_b=result_2["text_b"],
        similarity=result_2["similarity"],
        overlap=result_2["overlap"],
        groups=result_2["groups"],
    )
    return result_1, result_2


def demo_ChangeVarOrder_vs_DirectCompare():
    functionA = slice_first_defined_function(original_tree)
    functionB = slice_first_defined_function(change_var_order_tree)
    from testWinowingLib import compare_texts_with_template

    result_1 = compare_texts_with_template(
        ast.unparse(functionA), ast.unparse(functionB), auto_store=False
    )
    store_compare_result_as_html(
        base_dir=result_1["base_dir"],
        name_a="DirectCompare:original.py",
        name_b="DirectCompare:changeVarOrder.py",
        text_a=result_1["text_a"],
        text_b=result_1["text_b"],
        similarity=result_1["similarity"],
        overlap=result_1["overlap"],
        groups=result_1["groups"],
    )

    functionA_renamed = refactor_function_rename_variable_by_defining_order(functionA)
    functionB_renamed = refactor_function_rename_variable_by_defining_order(functionB)
    result_2 = compare_texts_with_template(
        ast.unparse(functionA_renamed), ast.unparse(functionB_renamed), auto_store=False
    )
    store_compare_result_as_html(
        base_dir=result_2["base_dir"],
        name_a="RefactorByOrder:original.py",
        name_b="RefactorByOrder:changeVarOrder.py",
        text_a=result_2["text_a"],
        text_b=result_2["text_b"],
        similarity=result_2["similarity"],
        overlap=result_2["overlap"],
        groups=result_2["groups"],
    )
    return result_1, result_2

def demo_SwitchVariableDefinitionLines_vs_DirectCompare():
    functionA = slice_first_defined_function(original_tree)
    functionB = slice_first_defined_function(change_var_order_tree)
    from testWinowingLib import compare_texts_with_template

    result_1 = compare_texts_with_template(
        ast.unparse(functionA), ast.unparse(functionB), auto_store=False
    )
    store_compare_result_as_html(
        base_dir=result_1["base_dir"],
        name_a="DirectCompare:original.py",
        name_b="DirectCompare:changeVarOrder.py",
        text_a=result_1["text_a"],
        text_b=result_1["text_b"],
        similarity=result_1["similarity"],
        overlap=result_1["overlap"],
        groups=result_1["groups"],
    )

    similarity_list = [("rows", "rows_num"), ("cols", "cols_num"), ("new_grid", "new_grid")]
    func_swapped = refactor_function_switch_variable_definition_lines_given_similarity_list(
        functionA, functionB, similarity_list
    )
    func_A_renamed = refactor_function_rename_variable_by_defining_order(functionA)
    func_swapped_renamed = refactor_function_rename_variable_by_defining_order(func_swapped)
    result_2 = compare_texts_with_template(
        ast.unparse(func_A_renamed), ast.unparse(func_swapped_renamed), auto_store=False
    )
    store_compare_result_as_html(
        base_dir=result_2["base_dir"],
        name_a="SwitchVariableDefinitionLines:original.py",
        name_b="SwitchVariableDefinitionLines:changeVarOrder.py",
        text_a=result_2["text_a"],
        text_b=result_2["text_b"],
        similarity=result_2["similarity"],
        overlap=result_2["overlap"],
        groups=result_2["groups"],
    )
    return result_1, result_2

def test_switch_variable_definition_lines():
    """Swap rows and cols in game_of_life_next_frame, print before/after."""
    func = slice_first_defined_function(original_tree)
    text_before = ast.unparse(func)
    func_swapped = refactor_function_switch_variable_definition_lines(func, [("rows", "cols")])
    text_after = ast.unparse(func_swapped)
    print("=== BEFORE (rows then cols) ===")
    print(text_before)
    print("\n=== AFTER (cols then rows) ===")
    print(text_after)

def test_switch_given_similarity_list():
    """Reorder changeVarOrder's defs to match original, then print."""
    func_a = slice_first_defined_function(original_tree)
    func_b = slice_first_defined_function(change_var_order_tree)
    similarity_list = [("rows", "rows_num"), ("cols", "cols_num"), ("new_grid", "new_grid")]
    print("=== functionB BEFORE (cols_num, rows_num, new_grid) ===")
    print(ast.unparse(func_b))
    func_b_reordered = refactor_function_switch_variable_definition_lines_given_similarity_list(
        func_a, func_b, similarity_list
    )
    print("\n=== functionB AFTER (rows_num, cols_num, new_grid to match A) ===")
    print(ast.unparse(func_b_reordered))


if __name__ == "__main__":
    # test_switch_variable_definition_lines()
    # print("\n" + "=" * 60 + "\n")
    # test_switch_given_similarity_list()
    demo_RefactorByOrder_vs_DirectCompare()
    demo_ChangeVarOrder_vs_DirectCompare()
    demo_SwitchVariableDefinitionLines_vs_DirectCompare()