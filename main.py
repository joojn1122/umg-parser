from convert import convert, replace_file
from constants import Message, INDENT
import sys
import os
import pyperclip
from yaml import load, FullLoader

START_KEYWORD = "# START UI #"
END_KEYWORD = "# END UI #"

if __name__ == "__main__":
    with open("config.yml", "r", encoding="utf-8") as yaml:
        config = load(yaml, Loader=FullLoader)

    Message.Translate = config.get('use_lang', True)

    ui = pyperclip.paste()
    name, result, _ = convert(ui, 0)

    if len(sys.argv) > 1:
        name = sys.argv[1]

    root_path = config['root_path']
    override_screens = config['override_screens']
    
    file_path = f"{root_path}/{name}.verse"
    
    for screen in override_screens:
        if screen['name'] == name:
            file_path = f"{root_path}/{screen['path']}"
            break
    
    if not os.path.exists(file_path):
        print("UI not found, copying to clipboard!")
        pyperclip.copy(result)
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
    
    name, result, widgets = convert(ui, indent)
    replace_file(file_path, result, START_KEYWORD, END_KEYWORD)
    
    # Create messages
    lang_path = config['lang_path']

    if lang_path and Message.Translate:
        with open(lang_path, "r", encoding="utf-8") as f:
            content = f.read()

        added_content = ""

        for widget in widgets:
            if hasattr(widget, "text"):
                text = getattr(widget, "text")

                if isinstance(text, Message) and text.translation_key and text.include_in_translation_file:
                    check_key = f"{text.translation_key}<public><localizes>"
                    
                    # Check if the message already exists in the file
                    if check_key in content or check_key in added_content:
                        continue
                    
                    # Needs to manually add types for arguments
                    args_str = ", ".join([f"{arg}: " for arg in text.params])
                    if args_str:
                        args_str = f"({args_str})"

                    # Add the message to the file
                    added_content += f"\n{INDENT}{text.translation_key}<public><localizes>{args_str}: message = \"{text.message}\""

        if added_content:
            with open(lang_path, "a", encoding="utf-8") as f:
                f.write(added_content)

            print(f"[*] Added {len(added_content.split("\n")) - 1} messages to lang file")

    print("[*] File successfully replaced")