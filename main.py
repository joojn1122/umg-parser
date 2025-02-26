from convert import convert, replace_file
import sys
import json
import pyperclip

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # with open("ui.sh", "r", encoding="utf-8") as f:
        #     ui = f.read()
        ui = pyperclip.paste()

        result = convert(ui, 0)

        with open("result.verse", "w", encoding="utf-8") as f:
            f.write(result)

        pyperclip.copy(result)

        exit()

    name = sys.argv[1]

    with open("uis/map.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)

    if name not in mapping:
        print("UI not found")
        exit()

    obj = mapping[name]

    with open(obj["path"], "r", encoding="utf-8") as f:
        content = f.read()

    indent = -1
    for line in content.splitlines():
        if obj["start"] in line:
            indent = line.index(obj["start"]) // 4
            break

    if indent == -1:
        print("Key not found")
        exit()

    # Using extension .sh because of the syntax highlighting
    with open(f"uis/{name}.sh", "r", encoding="utf-8") as f:
        ui = f.read()

    result = convert(ui, indent)

    replace_file(obj["path"], result, obj["start"], obj["end"])
    print("[*] File successfully replaced")