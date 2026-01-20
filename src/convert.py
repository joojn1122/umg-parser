from collections import defaultdict, deque
import re
from slots import ParsedWidget

def sort_variables(variable_contents, variable_dependencies):
    # Build the adjacency list and in-degree count for the dependency graph
    adjacency_list = defaultdict(list)
    in_degree = defaultdict(int)

    # Initialize graph with all variables
    for var in variable_contents:
        in_degree[var] = 0  # Ensure all variables have an entry

    for var, dependencies in variable_dependencies.items():
        for dep in dependencies:
            adjacency_list[dep].append(var)
            in_degree[var] += 1

    # Collect all nodes with zero in-degree
    queue = deque([var for var, degree in in_degree.items() if degree == 0])
    sorted_vars = []

    # Perform topological sort
    while queue:
        current = queue.popleft()
        sorted_vars.append(current)

        # Reduce the in-degree of each neighbor
        for neighbor in adjacency_list[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles (unsorted items)
    if len(sorted_vars) != len(variable_contents):
        raise ValueError("Cycle detected in dependencies, sorting not possible.")

    # Return the sorted variable contents
    return {var: variable_contents[var] for var in sorted_vars}

def parse_props(content: str, indent: int) -> dict:
    props = {}

    for line in content.splitlines():
        if not re.match(fr"{indent * ' '}\w", line):
            continue

        part = line[indent:]
        if part.startswith("Begin Object"):
            continue

        if "=" in part:
            key, value = part.split("=", 1)
            props[key.strip()] = value.strip()

    return props

def parse_widgets(content: str, indent: int) -> list[ParsedWidget]:
    regex = fr"{indent * ' '}Begin Object.*?\n{indent * ' '}End Object"

    objects = []

    for match in re.finditer(regex, content, re.DOTALL | re.MULTILINE):
        content = match.group(0)
        first_line = content.splitlines()[0]

        props_raw = first_line.split("Begin Object ")[1].split(" ")
        
        props = { prop.strip().split("=")[0]: prop.strip().split("=")[1] for prop in props_raw }

        children: list[ParsedWidget] = parse_widgets(content, indent + 3)
        props.update(parse_props(content, indent + 3))

        obj: ParsedWidget = {
            "props": props,
            "children": children
        }

        objects.append(obj)

    return objects

def replace_file(file: str, content: str, from_key: str, to_key: str) -> None:
    with open(file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    start_line = -1
    end_line = -1

    for i, line in enumerate(lines):
        if from_key in line:
            start_line = i + 1
        elif to_key in line:
            end_line = i

    # Start line shouldn't ever be -1, because we check for it in the main function
    if start_line == -1 or end_line == -1:
        print("End key not found")
        return
    
    pre = "\n".join(lines[:start_line])
    post = "\n".join(lines[end_line:])

    with open(file, "w", encoding="utf-8") as f:
        f.write(pre + "\n" + content + post)
