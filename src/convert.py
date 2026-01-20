from collections import defaultdict, deque
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
    """Parse properties at a specific indentation level, handling quoted values correctly."""
    props = {}
    indent_str = ' ' * indent

    for line in content.splitlines():
        # Skip lines that don't start at the correct indentation
        if not line.startswith(indent_str) or len(line) <= indent:
            continue

        # Skip if the character after indent is whitespace (deeper nesting)
        if line[indent] == ' ':
            continue

        part = line[indent:]

        # Skip Begin/End Object markers
        if part.startswith("Begin Object") or part.startswith("End Object"):
            continue

        # Parse key=value, handling the first = as delimiter
        eq_pos = part.find('=')
        if eq_pos != -1:
            key = part[:eq_pos].strip()
            value = part[eq_pos + 1:].strip()
            props[key] = value

    return props

def _parse_header_props(header_line: str) -> dict:
    """Parse props from 'Begin Object Name="Foo" Class="Bar"' line, handling quoted values."""
    props = {}
    # Extract the part after "Begin Object "
    start = header_line.find("Begin Object ")
    if start == -1:
        return props

    rest = header_line[start + len("Begin Object "):]

    # Parse key=value pairs, handling quoted values with spaces
    i = 0
    while i < len(rest):
        # Skip whitespace
        while i < len(rest) and rest[i] == ' ':
            i += 1
        if i >= len(rest):
            break

        # Find key
        eq_pos = rest.find('=', i)
        if eq_pos == -1:
            break

        key = rest[i:eq_pos].strip()
        i = eq_pos + 1

        # Parse value (may be quoted)
        if i < len(rest) and rest[i] == '"':
            # Find closing quote
            i += 1
            end_quote = rest.find('"', i)
            if end_quote == -1:
                value = rest[i:]
                i = len(rest)
            else:
                value = rest[i:end_quote]
                i = end_quote + 1
            props[key] = f'"{value}"'
        else:
            # Unquoted value - find next space
            space_pos = rest.find(' ', i)
            if space_pos == -1:
                value = rest[i:]
                i = len(rest)
            else:
                value = rest[i:space_pos]
                i = space_pos
            props[key] = value

    return props

def _find_matching_end(lines: list[str], start_idx: int, indent: int) -> int:
    """Find the index of the matching End Object for a Begin Object at start_idx."""
    indent_str = ' ' * indent
    depth = 0

    for i in range(start_idx, len(lines)):
        line = lines[i]
        if line.startswith(indent_str) and len(line) > indent and line[indent] != ' ':
            stripped = line[indent:]
            if stripped.startswith("Begin Object"):
                depth += 1
            elif stripped.startswith("End Object"):
                depth -= 1
                if depth == 0:
                    return i

    return -1

def parse_widgets(content: str, indent: int) -> list[ParsedWidget]:
    """Parse widgets at a specific indentation level, correctly handling nested objects."""
    objects: list[ParsedWidget] = []
    lines = content.splitlines()
    indent_str = ' ' * indent

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line starts a Begin Object at our indent level
        if (line.startswith(indent_str) and
            len(line) > indent and
            line[indent] != ' ' and
            line[indent:].startswith("Begin Object")):

            # Find matching End Object
            end_idx = _find_matching_end(lines, i, indent)
            if end_idx == -1:
                i += 1
                continue

            # Extract the block content
            block_lines = lines[i:end_idx + 1]
            block_content = '\n'.join(block_lines)

            # Parse header props from first line
            props = _parse_header_props(line)

            # Parse children (nested objects at indent + 3)
            children = parse_widgets(block_content, indent + 3)

            # Parse properties at indent + 3
            props.update(parse_props(block_content, indent + 3))

            obj: ParsedWidget = {
                "props": props,
                "children": children
            }
            objects.append(obj)

            # Skip past this entire block
            i = end_idx + 1
        else:
            i += 1

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
