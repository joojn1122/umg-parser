from parser import UMGParser, UMGParserConfig
from convert import replace_file
from rich import print
from yaml import load, FullLoader
import pyperclip
import sys
import os

START_KEYWORD = "# START UI #"
END_KEYWORD = "# END UI #"
CONFIGS_FOLDER = "configs"

def main():
    ui = pyperclip.paste()
    
    # Create parser with default config first to get export path
    parser = UMGParser()
    export_path, result, _ = parser.convert(ui, 0)

    name = export_path.split("/")[-1].split(".")[0].replace("WBP_", "")
    project_name = export_path.split("'/")[1].split("/")[0]

    normalized_project_name = "".join(
        c for c in project_name if c.isalnum() or c == '_'
    ).rstrip().lower()

    # Override name if provided as argument 
    if len(sys.argv) > 1:
        name = sys.argv[1]

    print("[+] Using project:", normalized_project_name)

    config_path = os.path.join(CONFIGS_FOLDER, f"{normalized_project_name}.yml")
    if not os.path.exists(config_path):
        print("[*] Project config not found, using default config")
        config_path = os.path.join(CONFIGS_FOLDER, "default.yml")

    print("[+] Using config file:", config_path)

    with open(config_path, "r", encoding="utf-8") as yaml:
        yaml_config = load(yaml, Loader=FullLoader)

    # Create parser config from yaml
    parser_config = UMGParserConfig(
        use_translated=yaml_config.get('use_lang', False),
        # Expand environment variables in paths
        lang_path=os.path.expandvars(yaml_config.get('lang_path', '')),
        root_path=os.path.expandvars(yaml_config.get('root_path', '')),
        override_screens=yaml_config.get('override_screens', [])
    )
    
    # Create new parser with full config
    parser = UMGParser(parser_config)

    root_path = parser_config.root_path
    override_screens = parser_config.override_screens
    
    file_path = f"{root_path}/{name}.verse"
    
    for screen in override_screens:
        if screen['name'] == name:
            file_path = f"{root_path}/{screen['path']}"
            break
    
    if not os.path.exists(file_path):
        print("[*] File does not exist, copying to clipboard instead")
        pyperclip.copy(result)
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    indent = -1
    for line in content.splitlines():
        if START_KEYWORD in line:
            indent = line.index(START_KEYWORD) // 4
            break

    if indent == -1:
        raise ValueError("Start keyword not found in target file")
    
    _, result, widgets = parser.convert(ui, indent)
    replace_file(file_path, result, START_KEYWORD, END_KEYWORD)
    
    # Create messages
    lang_path = parser_config.lang_path

    if lang_path and parser.use_translated:
        with open(lang_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

        added_content = parser.get_new_messages_for_file(widgets, existing_content)

        if added_content:
            with open(lang_path, "a", encoding="utf-8") as f:
                f.write(added_content)

            print(f"[*] Added {len(added_content.splitlines()) - 1} messages to lang file")

    print("[*] File successfully replaced")

if __name__ == "__main__":
    main()