How to use:

1. Open any UMG Widget Blueprint in UEFN
2. Select which widgets you want to convert from the hierarchy
3. Copy to clipboard (Ctrl + C)
4. Paste (Ctrl + V) into the input box below

Special features:

Declaring Varibles
- Prefix any widget with `$` to make it a variable, then the generated Verse code will declare it at the top.
- Example: `$MyButton`

Placeholder Widgets
- You can skip converting certain widgets by putting `__ignore` anywhere in the name. The converter will ignore these widgets and not include them in the output.

External Widgets
- You can reference widgets that are not part of the copied hierarchy by prefixing them with `external_`. The converter will treat these as external references.
- Example: `external_Player.Widget` will just use `Widget := Player.Widget` in the output.

Auto Generated Messages
- You can enable this feature and the converter then generates messages for all texts if the text has enabled localization.
- You also need to name the localization keys in UEFN properly for this to work.
- If disabled, the converter will just use the raw text with `.Msg()` suffix.

Supported Widgets:
- Canvas / CanvasSlot
- StackBox / StackBoxSlot
- Overlay / OverlaySlot
- Text Block
- Image Block / Material Block / Color Block
- Buttons
- Slider