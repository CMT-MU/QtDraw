"""
Create function table for jupyterbook document.

Run this to create "docs/src/function_table.md".
"""

import os
import ast


# ==================================================
def get_function_info(file_path):
    """
    Get function info.

    Args:
        file_path (str): file path.

    Returns:
        - (list) -- function info., [(name,class,summary)].
    """
    with open(file_path, "r", encoding="utf-8") as source:
        tree = ast.parse(source.read(), file_path)

    add_parents(tree)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            parent = node.parent
            class_name = parent.name if isinstance(parent, ast.ClassDef) else None
            functions.append((node.name, class_name, get_summary_from_docstring(ast.get_docstring(node))))
    return functions


# ==================================================
def get_summary_from_docstring(docstring):
    """
    Get summary (first sentence) of docstring.

    Args:
        docstring (str): docstring.

    Returns:
        - (str) -- docstring summary.
    """
    if not docstring:
        return ""
    # get first sentence.
    summary = docstring.strip().split("\n")[0]
    return summary


# ==================================================
def add_parents(tree):
    """
    Add parent to AST tree.

    Args:
        tree (Any): AST tree.
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node


# ==================================================
def generate_myst_document(file_function_map, title="Function Summary"):
    """
    Generate MyST document.

    Args:
        file_function_map (dict): file_function map.

    Returns:
        - (str) -- document.
    """
    document = f"# {title}\n\n"
    for file, functions in file_function_map.items():

        class_function_map = {}
        for func_name, class_name, summary in functions:
            if class_name not in class_function_map:
                class_function_map[class_name] = []
            class_function_map[class_name].append((func_name, summary))

        if len(class_function_map) > 0:
            document += f"## <div class='my-heading' style='color: darkgreen;'>{file}\n\n"

            for class_name, funcs in class_function_map.items():
                if class_name:
                    class_header = f"### <div class='my-heading' style='color: royalblue;'>{class_name}\n\n"
                else:
                    class_header = "### <div class='my-heading' style='color: royalblue;'>Global function\n\n"
                document += class_header
                table = "| Function | Summary |\n"
                table += "|--------|----------|\n"
                for func_name, summary in funcs:
                    if func_name == "__init__":
                        func_name = class_name
                    summary = summary or ""  # empty for None.
                    summary = " ".join(summary.split())  # convert to single line.
                    table += f"| {func_name} | {summary} |\n"
                document += table + "\n\n"
    return document


# ==================================================
def analyze_directory(directory):
    """
    Analyze directory.

    Args:
        directory (str): directory.

    Returns:
        - (dict) -- file_function map.
    """
    file_function_map = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                functions = get_function_info(file_path)
                file_function_map[file] = functions
    return file_function_map


# ==================================================
def create_function_table(directory, file):
    """
    Create function table.

    Args:
        directory (str): directory to analyze.
        file (str): full file name.
    """
    file_function_map = analyze_directory(directory)
    myst_document = generate_myst_document(file_function_map)
    with open(file, "w", encoding="utf-8") as f:
        f.write(myst_document)


# ==================================================
if __name__ == "__main__":
    from qtdraw.core.qtdraw_info import __top_dir__

    directory = __top_dir__ + "qtdraw"
    file = __top_dir__ + "docs/src/function_table.md"

    create_function_table(directory, file)
