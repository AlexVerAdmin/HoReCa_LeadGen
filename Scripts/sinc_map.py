import os
import ast
import argparse

def get_docstring(node):
    return ast.get_docstring(node).split('\n')[0] if ast.get_docstring(node) else "Нет описания"

def parse_python_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return None
    file_info = {"doc": get_docstring(tree), "elements": []}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not node.name.startswith('_'):
                type_name = "Класс" if isinstance(node, ast.ClassDef) else "Функция"
                file_info["elements"].append(f" - **{node.name}** ({type_name}): {get_docstring(node)}")
    return file_info

def generate_map_content(src_dir):
    lines = ["\n"]
    ignore_dirs = {'.venv', 'venv', '__pycache__', 'Persona_Memory', '.env', '.git'}
    
    for root, dirs, files in os.walk(src_dir):
        # Исключаем нежелательные папки из обхода
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in sorted(files):
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src_dir)
                info = parse_python_file(full_path)
                if info:
                    lines.append(f"### `{rel_path}`")
                    lines.append(f"> {info['doc']}")
                    lines.extend(info['elements'])
                    lines.append("")
    return "\n".join(lines)

def update_obsidian_note(output_file, new_map_content):
    start_marker = "<!-- CODE_MAP_START -->"
    end_marker = "<!-- CODE_MAP_END -->"
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if start_marker not in content or end_marker not in content:
        print("Ошибка: Маркеры CODE_MAP не найдены в файле!")
        return

    before = content.split(start_marker)[0]
    after = content.split(end_marker)[1]
    new_content = f"{before}{start_marker}{new_map_content}{end_marker}{after}"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="src", help="Путь к папке с кодом")
    parser.add_argument("--out", required=True, help="Путь к LeadGen_Project_Map.md")
    args = parser.parse_args()
    
    map_text = generate_map_content(args.src)
    update_obsidian_note(args.out, map_text)
    print(f"Карта кода обновлена внутри маркеров в {args.out}")

