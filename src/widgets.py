import re
from slots import Widget, ParsedWidget
from constants import (
    format_color, 
    parse_text, 
    Message, 
    parse_vector2, 
    color2hex, 
    parse_color, 
    rgb2hex, 
    i, 
    format_vector2, 
    fn
)

class Button(Widget):
    text: Message
    verse_name: str

    def __init__(self, object: ParsedWidget, verse_name: str):
        super().__init__(object)

        self.verse_name = verse_name
        self.text = parse_text(object['props'].get("Text", ""))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(Text={self.text})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        # Set translation flag on text message based on parser config
        self.text._use_translated = self.use_translated
        
        if self.text.not_empty():
            return f"{self.verse_name}:\n{i(indent + 1)}DefaultText := {self.text}\n"
        
        return self.verse_name + "{}\n"

class QuietButton(Button):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Button_Quiet.UEFN_Button_Quiet_C"
    SimpleName: str = "QuietButton"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, "button_quiet")

class RegularButton(Button):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Button_Regular.UEFN_Button_Regular_C"
    SimpleName: str = "RegularButton"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, "button_regular")

class LoudButton(Button):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Button_Loud.UEFN_Button_Loud_C"
    SimpleName: str = "LoudButton"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, "button_loud")

class Image(Widget):
    ClassName: str = "/Script/UMG.Image"
    SimpleName: str = "ImageBlock"

    size: tuple[float, float]
    path: str | None
    tintColor: str | None
    is_material: bool = False
    
    def __init__(self, object: ParsedWidget):
        super().__init__(object)

        brush = object['props'].get("Brush", "")

        imageSize = re.search(r"ImageSize=\((.*?)\)", brush)
        resourceObject = re.search(r"ResourceObject=\"(.*?)\"", brush)
        

        tint = re.search(r"TintColor=\(([^()]*|(\([^()]*\)))*\)", brush)
        tintColor = parse_color(tint.group(2)) if tint else None

        self.size = (32.0, 32.0)
        self.path = None
        self.tintColor = None
        self.opacity = 1.0
        self.is_material = False

        if imageSize:
            self.size = parse_vector2(imageSize.group(1))

        if resourceObject:
            # /Script/Engine.Texture2D'/path/name.name'
            asset_type, path, *_ = resourceObject.group(1).split("'")
            self.is_material = asset_type != "/Script/Engine.Texture2D"
            
            # remove project name and file extension and replace / with .
            self.path = path.split("/", 2)[2].split(".")[0].replace("/", ".")
            if self.is_material and self.path:
                self.path += "{}"

        if tintColor:
            # Convert to hex
            if self.path == None:
                self.opacity = tintColor[3]
                self.tintColor = rgb2hex(*(tintColor[:3]))
            
            else:
                self.tintColor = color2hex(*tintColor)
            
            # Try to use NamedColors if possible
            if self.path == None or tintColor[3] == 1:
                match(tintColor[:3]):
                    case [0, 0, 0]:
                        self.tintColor = "NamedColors.Black"
                    case (255, 255, 255):
                        self.tintColor = "NamedColors.White"
                    case (255, 0, 0):
                        self.tintColor = "NamedColors.Red"
                    case (0, 0, 255):
                        self.tintColor = "NamedColors.Blue"
                    case _:
                        pass
            
            if not self.tintColor.startswith("NamedColors."):
                self.tintColor = f"MakeColorFromHex(\"{self.tintColor}\")"
        
    def __str__(self) -> str:
        return f"Image(Size={self.size}, Path={self.path})"

    def __repr__(self) -> str:
        return self.__str__()
    
    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        if(self.path == None): # Color blocks doesn't exist in the UMG, so use a texture block instead with empty path and tint color
            result = "color_block:\n"
            
            if(self.tintColor):
                result += f"{i(indent + 1)}DefaultColor := {self.tintColor}\n"

            if(self.opacity != 1.0):
               result += f"{i(indent + 1)}DefaultOpacity := {self.opacity}\n"

            result += f"{i(indent + 1)}DefaultDesiredSize := {format_vector2(self.size)}\n"

            return result
        
        result = f"{'material' if(self.is_material) else 'texture'}_block:\n"
        result += f"{i(indent + 1)}DefaultImage := {self.path}\n"
        result += f"{i(indent + 1)}DefaultDesiredSize := {format_vector2(self.size)}\n"

        if(self.tintColor):
            result += f"{i(indent + 1)}DefaultTint := {self.tintColor}\n"

        return result
        
class TextBlock(Widget):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_TextBlock.UEFN_TextBlock_C"
    SimpleName: str = "TextBlock"

    text: Message
    color: str | None
    opacity: float
    font_size: float
    justification: str | None # Right or center

    # shadow
    shadowOffset: tuple[float, float] | None
    shadowColor: tuple[float, float, float, float] | None

    # outline, currently just supports checking if it exists
    has_outline: bool = False

    def __init__(self, object: ParsedWidget):
        super().__init__(object)
        
        props = object['props']

        self.justification = props.get("Justification", None)
        self.text = parse_text(props.get("Text", ""))
        
        color = parse_color(props.get("ColorAndOpacity", ""))

        font = props.get("Font", "")
        
        if not font:
            self.font_size = 32
            self.has_outline = False
        else:
            font_size = re.search(r"[,(]Size=([\d\.]+)", font)
            
            if font_size:
                self.font_size = float(font_size.group(1)) * 1.3333333333333333
            else:
                self.font_size = 32

            outline = re.search(r"OutlineSize=([\d\.]+)", font)
            self.has_outline = bool(outline)

        self.color = "NamedColors.White"
        self.opacity = 1
        
        if color:
            self.color = format_color(color)
            self.opacity = color[3]

        # shadow
        self.shadowColor = parse_color(props.get('ShadowColorAndOpacity', ''))
        
        shadowOffset = props.get('ShadowOffset', None)
        self.shadowOffset = None if shadowOffset is None else parse_vector2(shadowOffset)

    def __str__(self) -> str:
        return f"TextBlock(Text={self.text})"
    
    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        # Set translation flag on text message based on parser config
        self.text._use_translated = self.use_translated
        
        if("FONT_" in self.Name):
            font_name = re.sub("[0-9_]", "", self.Name.split("FONT_", 1)[1])
            return f"{font_name}.Draw(\"{self.text.message}\", {self.color or 'NamedColors.White'}, {self.font_size})\n"
        
        # If outline, use custom widget
        if self.has_outline:
            alpha_color = f", ?Alpha := {fn(self.opacity)}" if self.opacity != 1.0 else ""
            return f"CreateOutlineText(0, {self.text}, {self.color or 'NamedColors.White'}{alpha_color})\n"

        result = "text_block:\n"

        if self.text:
            result += f"{i(indent+1)}DefaultText := {self.text}\n"

        if self.color:
            result += f"{i(indent+1)}DefaultTextColor := {self.color}\n"

        if self.font_size != 32.0:
            result += f"{i(indent+1)}DefaultTextSize := {fn(self.font_size)}\n"

        if self.opacity != 1.0:
            result += f"{i(indent+1)}DefaultOpacity := {self.opacity}\n"

        if self.shadowOffset:
            result += f"{i(indent+1)}DefaultShadowOffset := option. {format_vector2(self.shadowOffset)}\n"

        if self.shadowColor:
            result += f"{i(indent+1)}DefaultShadowColor := {format_color(self.shadowColor)}\n"
            result += f"{i(indent+1)}DefaultShadowOpacity := {fn(self.shadowColor[3])}\n"

        if self.justification:
            result += f"{i(indent+1)}DefaultJustification := text_justification.{self.justification}\n"

        return result

class Slider(Widget):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Slider.UEFN_Slider_C"
    SimpleName: str = "Slider"

    min: float    # Pivot[0]
    max: float    # Pivot[1]
    value: float  # Shear[0]
    step: float   # Shear[1]

    def __init__(self, object: ParsedWidget):
        super().__init__(object)

        # Have to use pivot, because you can't change shit in UMG for some reason
        pivot = object['props'].get("RenderTransformPivot", "(X=0.500000,Y=0.500000)")
        self.min, self.max = parse_vector2(pivot)
        self.value = self.min
        self.step = 1.0

        render_transform = object['props'].get('RenderTransform')
        if render_transform:
            shear = re.search(r"Shear=\((.*?)\)", render_transform)
            if shear:
                shear = parse_vector2(shear.group(1))
                self.value, self.step = shear

    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        result = "slider_regular:\n"

        result += f"{i(indent+1)}DefaultValue := {fn(self.value)}\n"
        result += f"{i(indent+1)}DefaultMinValue := {fn(self.min)}\n"
        result += f"{i(indent+1)}DefaultMaxValue := {fn(self.max)}\n"
        result += f"{i(indent+1)}DefaultStepSize := {fn(self.step)}\n"
        
        return result

class WidgetSlotPair(Widget):
    ClassName: str = "/Script/UMGEditor.WidgetSlotPair"
    SimpleName: str = "WidgetSlotPair"
    WidgetName: str

    def __init__(self, object: ParsedWidget) -> None:
        super().__init__(object)

        self.WidgetName = object['props'].get("WidgetName", "").replace("\"", "")
