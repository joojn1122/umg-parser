<!-- <div align="center"> -->

# UMG Parser
<img src="WBPToVerse.png" width="300px" alt="UMG to Verse conversion preview">

**Convert UMG Widget Blueprints to Verse UI code for Unreal Editor for Fortnite (UEFN)**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)


<img src="demo.png" width="600px" alt="UMG to Verse conversion example">

<div align="center">

[**🚀 Try the Live Demo**](https://joojn.xyz/#/umg-parser)
</div>

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
  - [CLI Mode](#cli-mode)
  - [Web API Mode](#web-api-mode)
- [Widget Naming Conventions](#-widget-naming-conventions)
- [Configuration](#-configuration)
- [Supported Widgets](#-supported-widgets)
- [API Reference](#-api-reference)
- [License](#-license)

---

## 🎯 Overview

**UMG Parser** streamlines the process of converting Unreal Motion Graphics (UMG) Widget structures into Verse UI code. Whether you're handling basic layouts, dynamic variables, or external widgets, this tool helps you accelerate development in UEFN.

### Key Benefits

- ⚡ **Instant Conversion** — Copy from UEFN, paste, and get Verse code
- 🔄 **Auto File Replacement** — Automatically updates your Verse files
- 🌐 **Web API** — Deploy as a service with FastAPI
- 🌍 **Localization Support** — Generate translation message modules
- 📁 **Project Configs** — Per-project YAML configuration

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Variable Widgets** | Prefix widget names with `$` to generate variables |
| **External References** | Reference widgets from other files using `$external_` prefix |
| **Font Override** | Apply custom fonts with `_FONT_` suffix in names |
| **Slider Workaround** | Use `PivotPoint` and `Shear` for slider properties |
| **Translation Keys** | Auto-generate localized messages module |
| **Auto Replace** | Replace code between markers in existing Verse files |

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/joojn1122/umg-parser.git
   cd umg-parser
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Set up environment variables:**

   Create a `.env` file for web API configuration:

   ```env
   ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000
   ```

---

## 📖 Usage

### CLI Mode

The CLI tool reads UMG data from your clipboard and processes it automatically.

#### Quick Start

1. Open a UMG Widget Blueprint in UEFN
2. Select the widgets to convert in the hierarchy
3. Copy to clipboard (`Ctrl+C`)
4. Run the converter:

   ```bash
   cd src
   python main.py [optional: ScreenName]
   ```

The tool will:

- Detect your project from the export path
- Load the matching config from `configs/<project_name>.yml`
- Replace content between `# START UI #` and `# END UI #` markers in your Verse file
- If no file is found, copy the generated code to clipboard

---

### 🔄 Automated Workflow Setup

Set up a fully automated pipeline where copying a widget blueprint instantly updates your Verse files.

#### Step 1: Create Your Project Config

Create a YAML config file in `src/configs/` matching your project name (lowercase, alphanumeric only):

```yaml
# src/configs/myproject.yml

# Path to your Verse content folder (supports environment variables)
root_path: $USERPROFILE/Documents/Fortnite Projects/MyProject/Plugins/MyProject/Content

# Optional: Enable translation message generation
use_lang: false
lang_path: ''

# Optional: Map specific screens to custom file paths
override_screens:
  - name: MainMenu
    path: ./UI/Screens/MainMenu.verse
  - name: Settings  
    path: ./UI/Screens/Settings.verse
```

#### Step 2: Add Markers to Your Verse Files

In each Verse file where you want auto-replacement, add these marker comments:

```lua
(Data: player_data).ShowUI<public>():void=
   # START UI #
   -- Your generated UI code will be inserted here --
   # END UI #

   -- Example 
   Screen := screen:
      Canvas := Canvas
      Data := Data
   ...
```

> ⚠️ **Important:** The markers must be on their own lines. The indentation of `# START UI #` determines the indentation of the generated code.

#### Step 3: Name Your Widget Blueprint

The tool matches your Widget Blueprint to the Verse file by name:

| Widget Blueprint | Expected Verse File |
|------------------|---------------------|
| `WBP_MainMenu` | `MainMenu.verse` |
| `WBP_Inventory` | `Inventory.verse` |
| `WBP_Settings` | `Settings.verse` |

The `WBP_` prefix is automatically stripped when searching for the file.

#### Step 4: Run the Workflow

1. **Copy your widget** — Select widgets in UEFN hierarchy → `Ctrl+C`
2. **Run the script** — Execute `python main.py` from the `src/` folder
3. **Done!** — Your Verse file is automatically updated

```bash
# Example output
[+] Using project: myproject
[+] Using config file: configs/myproject.yml
[*] File successfully replaced
```

#### Using Override Screens

If your Verse file path doesn't match the widget name, use `override_screens`:

```yaml
override_screens:
  - name: Rewards        # Widget is WBP_Rewards
    path: ./TycoonFeatures/PlaytimeRewards.verse  # But file is here
```

You can also override the name via command line:

```bash
python main.py CustomScreenName
```

#### Workflow Tips

- **Hotkey Setup** — Bind `python main.py` to a keyboard shortcut for one-key conversion
- **Watch Mode** — Create a script that monitors clipboard changes and auto-runs
- **Multiple Projects** — Each project gets its own config file, auto-detected from the blueprint's export path

---

### Web API Mode

Deploy UMG Parser as a REST API service:

```bash
cd src
uvicorn web:app --host 0.0.0.0 --port 8000
```

Or with Gunicorn for production:

```bash
gunicorn web:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 🏷️ Widget Naming Conventions

Use special prefixes/suffixes in your widget's **Display Label** to control code generation:

### Variables (`$` prefix)

```plaintext
$RewardText
```

Creates a Verse variable:

```verse
RewardText := ...
```

### External References (`$external_` prefix)

```plaintext
$external_PlayerCard.Widget
```

References a widget defined elsewhere—useful for dynamic content.

### Ignored Widgets (`__ignore`)

```plaintext
Placeholder__ignore
```

Skips this widget during parsing (useful for placeholder/template widgets).

---

## ⚙️ Configuration

Create project-specific configs in `src/configs/`:

**Example: `myproject.yml`**

```yaml
# Root path to your Verse files (supports environment variables)
root_path: $USERPROFILE/Documents/Fortnite Projects/MyProject/Plugins/MyProject/Content

# Translation settings
use_lang: true
lang_path: $USERPROFILE/Documents/Fortnite Projects/MyProject/Plugins/MyProject/Content/Messages.verse

# Override file paths for specific screens
override_screens:
  - name: MainMenu
    path: ./UI/MainMenu.verse
  - name: Inventory
    path: ./UI/Inventory.verse
```

### Configuration Options

| Key | Type | Description |
|-----|------|-------------|
| `root_path` | `string` | Base path to search for Verse files |
| `use_lang` | `bool` | Enable translation message generation |
| `lang_path` | `string` | Path to the messages file for translations |
| `override_screens` | `list` | Custom file paths for specific screen names |

---

## 🎨 Supported Widgets

| Widget Type | Verse Equivalent | Notes |
|-------------|-----------------|-------|
| **Canvas Panel** | `canvas` | Root layout container |
| **Canvas Slot** | `canvas_slot` | Positioning within canvas |
| **Stack Box** | `stack_box` | Horizontal/vertical layouts |
| **Overlay** | `overlay` | Layered widgets |
| **Text Block** | `text_block` | Text display with styling |
| **Image** | `texture_block` | Image display |
| **Material Image** | `material_block` | Material-based images |
| **Color Block** | `color_block` | Solid color rectangles |
| **Button (Quiet)** | `button_quiet` | Minimal style button |
| **Button (Regular)** | `button_regular` | Standard button |
| **Button (Loud)** | `button_loud` | Emphasized button |
| **Slider** | `slider` | Value slider control |

### Slider Properties Workaround

Since UMG sliders can't directly specify Verse properties, use these UMG properties:

```
PivotPoint.X → MinValue
PivotPoint.Y → MaxValue
Shear.X     → DefaultValue (optional, defaults to MinValue)
Shear.Y     → Step (optional, defaults to 1)
```

---

## 📡 API Reference

### Endpoints

#### `POST /convert`

Convert UMG blueprint text to Verse code.

**Request Body:**

```json
{
  "umg_text": "Begin Object Class=... End Object",
  "use_translated": false,
  "indent": 0
}
```

**Response:**

```json
{
  "code": "MyWidget := canvas:\n    ...",
  "messages": "Messages<public> := module:\n    ..."
}
```
---

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

<div align="center">

**Made with ❤️ for the UEFN community**

</div>
