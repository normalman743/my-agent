import ast
import os

def extract_functions_from_file(filepath):
    """Extract function names and parameters from a Python file."""
    with open(filepath, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read(), filename=filepath)
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            functions.append((func_name, args))
    return functions


def extract_functions_from_directory(directory):
    """Extract functions from all Python files in a directory."""
    result = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                functions = extract_functions_from_file(filepath)
                if functions:
                    result.append((filepath, functions))
    return result

def main(directory):
    """Main function."""
    functions_info = extract_functions_from_directory(directory)
    
    with open('functions_summary.txt', 'w', encoding='utf-8') as out_file:
        for filepath, functions in functions_info:
            out_file.write(f'File: {filepath}\n')
            for func_name, args, defaults in functions:
                out_file.write(f'  Function: {func_name}\n')
                out_file.write(f'    Arguments: {", ".join(args)}\n')
                out_file.write(f'    Defaults: {", ".join(defaults)}\n')
            out_file.write('\n')

if __name__ == '__main__':
    directory = input("Enter the directory path: ")
    main(directory)
