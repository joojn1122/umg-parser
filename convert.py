from widgets import *
from slots import ( 
    Widget, 
    ParsedWidget,
    Slotable,
    registered_classes,
    variables
)
import re

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

def convert(content: str, indent: int = 0) -> str:
    parsed_widgets: list[ParsedWidget] = parse_widgets(content, 0)
    widgets: list[Widget] = []

    for widget in parsed_widgets:
        props = widget['props']
        className = props.get('Class', "")

        for rclass in registered_classes:
            if rclass.ClassName == className:
                widgets.append(rclass(widget))

    root: Slotable
    for widget in widgets:
        if isinstance(widget, WidgetSlotPair):
            for w in widgets:
                if w.Name == widget.WidgetName and isinstance(w, Slotable):
                    root = w
                    break
            break
    
    result = f"{i(indent)}Canvas := " + root.codify(indent, widgets)
    variables_str = ""

    for variable in variables:
        variables_str += i(indent) + variable.Name[1:] + " := " + variable.codify(indent, widgets) + "\n"

    variables.clear()
    return variables_str + result

def replace_file(file: str, content: str, from_key: str, to_key: str) -> None:
    with open(file, "r") as f:
        lines = f.read().splitlines()

    start_line = -1
    end_line = -1

    for i, line in enumerate(lines):
        if from_key in line:
            start_line = i
        elif to_key in line:
            end_line = i

    if start_line == -1 or end_line == -1:
        print("Key not found")
        return

    pre = "\n".join(lines[:start_line])
    post = "\n".join(lines[end_line:])

    with open(file, "w") as f:
        f.writelines(pre + "\n" + content + post)

if __name__ == "__main__":
    with open("ui.txt", "r") as f:
        ui = f.read()

    result = convert(ui, 1)

    replace_file(
    r"C:\Users\joojn\Documents\Fortnite Projects\HackerTycoon\Plugins\HackerTycoon\Content\Screens\BtcSellScreen.verse", 
    result, 
    "CloseBtn := button_loud", 
    "Screen := btc_exchange_screen"
    )
