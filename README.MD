# UMG Parser
A tool to parse `UMG Widget` files and convert them into `Verse UI` code for use in Unreal Editor for Fortnite (UEFN).

<img src="WBPToVerse.png" width="250px">

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [How to Use](#how-to-use)
    - [Declaring Variables](#1-declaring-variables)
    - [Using Custom Fonts](#2-using-custom-fonts)
    - [Placeholder Widgets](#3-placeholder-widgets)
    - [External Widgets](#4-external-widgets)
    - [Automatic Script Replacer](#5-automatic-script-replacer)
4. [Supported Widgets](#supported-widgets)
5. [To-Do](#to-do)
6. [License](#license)

---

## Introduction
**UMG Parser** simplifies the process of converting UMG Widget structures into `Verse UI` code. Whether you’re handling basic layouts, dynamic variables, or external widgets, this tool helps you streamline the development process in UEFN.

---

## Installation
Follow these steps to install and set up **UMG Parser**:

1. Clone the repository (private):
   ```bash
   git clone https://github.com/joojn1122/UMG_Parser.git
   cd UMG_Parser
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Python 3.8 or higher is installed on your system.

4. (Optional) Set up environment variables for your project paths if needed.

---

## How to Use

### 1. Declaring Variables
Define variables by prefixing widget names with `$`. The parser generates these variables in the Verse code.

**Example:**
```plaintext
$RewardText
```
This creates a `RewardText` variable and assigns it the widget content.

---

### 2. Using Custom Fonts
To use a non-default font, prefix the widget name with `FONT_` followed by the font name.

**Example:**
```plaintext
FONT_RobotoFont
```
This applies the `RobotoFont` style to the widget.

---

### 3. Placeholder Widgets
Create placeholder or dynamically generated widgets by adding `__ignore` to the widget name. These widgets are skipped in the parsing process.

---

### 4. External Widgets
To reference an external widget not part of the current UMG file, use `$external_<VARIABLE_NAME>` in the widget name.

**Example:**
```plaintext
$external_ClickInRange.Widget
```

---

### 5. Automatic Script Replacer
Automate updates to Verse files by configuring a replacer script:

1. Add an entry to `uis/map.json`:
   ```json
   {
       "example_entry": {
           "path": "path/to/file.verse",
           "start_key": "// START_KEY",
           "end_key": "// END_KEY"
       }
   }
   ```
2. Create a `.sh` file matching the entry name and include the root canvas content.
3. Run the script:
   ```bash
   python main.py example_entry
   ```
The script replaces content between the specified keys with generated code.

---

## Supported Widgets
Currently, the following widgets are supported:
- **Canvas & CanvasSlot**
- **StackBox & StackBoxSlot**
- **Overlay & OverlaySlot**
- **TextBlock**
- **Image & ColorBlock**
- **Buttons**

---

## To-Do
Planned features:
- Add support for sliders.
- Expand widget compatibility for more UI components.

---

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the `LICENSE` file for details.