# UMG Parser
Parses `UMG Widget` and converts it into `Verse UI`

## How to use
- Open UMG Widget in UEFN, copy main Canvas
- Paste clipboard into `ui.txt`
- Edit `convert.py` to match your file 
- Run `py convert.py`
- Verse code will be generated

## Declaring variables
You can declare variable by naming the widget `$<NAME>`,
putting `$` before the name<br>

**Example**: `$RewardText`

This will then create a `RewardText` variable before the canvas with the widget content.

## Using different font
To change default fortnite font, name the widget like this: `FONT_<FONT_NAME>`

**Example:** `FONT_RobotoFont`

This will create a widget using our `CustomFont`, which has to be created beforehand.

## Placeholder widgets
Sometimes we want to create placeholder widgets which will fill the place and are dynamically created. We can create placeholder widget / ignore widget by putting `__ignore` in the name.

## External widgets
You can also use widgets that are not created by the current UMG Widget eg. external widget. To use external widget name it `$external_<VARIABLE_NAME>`.

**Example:** `$external_ClickInRange.Widget`

## Automatic script replacer
You can automatically replace a part of verse file when you change the UMG Widget. Create new entry in `uis/map.json` file and name it, then create new file in the same directory with the name you named it and `.sh` extension. Specity the path of the file, `start key` and `end key`. Put the content of root canvas into the `.sh` file and run `python main.py <name_of_the_entry>`.
Indents will be generated automatically based on the `start key`.

This script will then replace content in range of `start-end key`.

## Other
To use font custom font and variable combine the two text like this:

`$<VARIABLE_NAME>_FONT_<FONT_NAME>`

**Example:** `$RewardText_FONT_RobotoFont`

## Supported widgets
Currently these are all supported widgets:
- Canvas & CanvasSlot
- StackBox & StackBoxSlot
- Overlay & OverlaySlot
- TextBlock
- Image & ColorBlock
- All buttons

## TO-DO
- Add support to slider