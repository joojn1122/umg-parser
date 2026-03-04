# UMG Parser (Python)

This is the legacy Python implementation of UMG Parser. The main project has been rewritten in TypeScript — see the [root README](../README.MD).

## Prerequisites

- Python 3.10+
- pip

## Installation

```bash
cd python-old
pip install -r requirements.txt
```

## Usage

### CLI Mode

1. Copy widgets from UEFN hierarchy (`Ctrl+C`)
2. Run the converter:

```bash
cd src
python main.py [optional: ScreenName]
```

The tool will:
- Detect your project from the export path
- Load the matching config from `configs/<project_name>.yml`
- Replace content between `# START UI #` and `# END UI #` markers in your Verse file
- If no file is found, copy the generated code to clipboard

### Web API Mode

```bash
cd src
uvicorn web:app --host 0.0.0.0 --port 8000
```

## Configuration

Create project-specific YAML configs in `src/configs/`:

```yaml
root_path: $USERPROFILE/Documents/Fortnite Projects/MyProject/Plugins/MyProject/Content
use_lang: false
lang_path: ''
override_screens:
  - name: MainMenu
    path: ./UI/Screens/MainMenu.verse
```
