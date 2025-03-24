from convert import convert, replace_file
import sys
import os
import pyperclip
from yaml import load, FullLoader

START_KEYWORD = "# START UI #"
END_KEYWORD = "# END UI #"

if __name__ == "__main__":
    ui = pyperclip.paste()
    name, result = convert(ui, 0)

    if len(sys.argv) > 1:
        name = sys.argv[1]

    with open("config.yml", "r", encoding="utf-8") as yaml:
        config = load(yaml, Loader=FullLoader) 

    root_path = config['root_path']
    override_screens = config['override_screens']

    file_path = f"{root_path}/{name}.verse"

    for screen in override_screens:
        if screen['name'] == name:
            file_path = f"{root_path}/{screen['path']}"
            break
    
    if not os.path.exists(file_path):
        print("UI not found, copying to clipboard!")
        pyperclip.copy(ui)
        exit()

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    indent = -1
    for line in content.splitlines():
        if START_KEYWORD in line:
            indent = line.index(START_KEYWORD) // 4
            break

    if indent == -1:
        print("Start key not found in file")
        exit()
    
    name, result = convert(ui, indent)

    replace_file(file_path, result, START_KEYWORD, END_KEYWORD)
    
    print("[*] File successfully replaced")