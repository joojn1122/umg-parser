# UMG Parser
Parses `UMG Widget` and converts it into `Verse UI`

## How to use
- Open UMG Widget in UEFN, copy main Canvas
- Paste clipboard into `ui.txt`
- Edit `convert.py` to match your file 
- Run `py convert.py`
- Verse code will be generated

## Declaring variables
You can declare variable by naming the widget `_<NAME>`,
putting `_` before the name<br>

**Example**: `_RewardText`

This will then create a `RewardText` variable before the canvas with the widget content.

## Using different font
To change default fortnite font, name the widget like this: `FONT_<FONT_NAME>`

**Example**: `FONT_RobotoFont`

This will create a widget using our `CustomFont`, which has to be created beforehand.

## Placeholder widgets
Sometimes we want to create placeholder widgets which will fill the place and are dynamically created. We can create placeholder widget / ignore widget by putting `__ignore` in the name.

## Other
To use font custom font and variable combine the two text like this:

`_<VARIABLE_NAME>_FONT_<FONT_NAME>`

**Example**: `_RewardText_FONT_RobotoFont`

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