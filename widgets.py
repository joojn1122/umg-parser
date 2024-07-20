from slots import Widget, ParsedWidget
import re
from constants import parse_vector2, INDENT, color2hex, parse_color, rgb2hex, i, format_vector2

class Button(Widget):
    text: str
    verse_name: str

    def __init__(self, object: ParsedWidget, verse_name: str):
        super().__init__(object)

        self.verse_name = verse_name

        self.text = object['props'].get("Text", "")
        matched = re.search(r"\"(.*?)\"", self.text)

        if matched:
            self.text = matched.group(1)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(Text={self.text})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        if not self.text:
            return self.verse_name + "{}\n"
        
        return f"{self.verse_name}:\n{i(indent + 1)}DefaultText := \"{self.text}\".Msg()\n"

class QuietButton(Button):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Button_Quiet.UEFN_Button_Quiet_C"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, "button_quiet")

class RegularButton(Button):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Button_Regular.UEFN_Button_Regular_C"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, "button_regular")

class LoudButton(Button):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_Button_Loud.UEFN_Button_Loud_C"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, "button_loud")

class Image(Widget):
    ClassName: str = "/Script/UMG.Image"

    size: tuple[float, float]
    path: str | None
    tintColor: str | None

    def __init__(self, object: ParsedWidget):
        super().__init__(object)

        brush = object['props'].get("Brush", "")

        imageSize = re.search(r"ImageSize=\((.*?)\)", brush)
        resourceObject = re.search(r"ResourceObject=\"(.*?)\"", brush)
        tintColor = parse_color(brush)

        self.size = (32.0, 32.0)
        self.path = None
        self.tintColor = None

        if imageSize:
            self.size = parse_vector2(imageSize.group(1))

        if resourceObject:
            path = resourceObject.group(1).split("'")[1] # get the path only
            # remove project name and file extension and replace / with .
            self.path = path.split("/", 2)[2].split(".")[0].replace("/", ".")
        
        if tintColor:
            # Convert to hex
            self.tintColor = color2hex(*tintColor)
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

            result += f"{i(indent + 1)}DefaultDesiredSize := {format_vector2(self.size)}\n"

            return result
        
        result = "texture_block:\n"
        result += f"{i(indent + 1)}DefaultImage := {self.path}\n"
        result += f"{i(indent + 1)}DefaultDesiredSize := {format_vector2(self.size)}\n"

        if(self.tintColor):
            result += f"{i(indent + 1)}DefaultTintColor := {self.tintColor}\n"

        return result
        
class TextBlock(Widget):
    ClassName: str = "/Game/Valkyrie/UMG/UEFN_TextBlock.UEFN_TextBlock_C"

    text: str
    color: str | None
    opacity: float
    font_size: int

    def __init__(self, object: ParsedWidget):
        super().__init__(object)

        self.text = object['props'].get("Text", "")
        matched = re.findall(r"\"(.*?)\"", self.text)

        color = object['props'].get("ColorAndOpacity", "")
        color = parse_color(color)

        font = object['props'].get("Font", "")
        if not font:
            self.font_size = 32
        else:
            font_size = re.search(r"Size=(\d+)", font)

            if font_size:
                self.font_size = int(font_size.group(1))
            else:
                self.font_size = 32

        self.color = None
        self.opacity = 1

        if len(matched) > 0:
            self.text = matched[-1].replace("\\r\\n", "\\n") # Fix Windows line endings

        if color:
            self.color = rgb2hex(*color[:3]) # Set alpha to 1
            self.opacity = color[3]

            self.color = f"MakeColorFromHex(\"{self.color}\")"

    def __str__(self) -> str:
        return f"TextBlock(Text={self.text})"
    
    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        if("FONT_" in self.Name):
            font_name = re.sub("[0-9_]", "", self.Name.split("FONT_", 1)[1])
            return f"{font_name}.Draw(\"{self.text}\", {self.color or 'NamedColors.White'}, {self.font_size})\n"
        
        # Use CreateText function for ordinary text blocks
        if self.text and self.opacity == 1.0:
            return f"CreateText(\"{self.text}\".Msg(), {self.color or 'NamedColors.White'})\n"

        result = "text_block:\n"

        if self.text:
            result += f"{i(indent)}DefaultText := \"{self.text}\".Msg()\n"

        if self.color:
            result += f"{i(indent)}DefaultTextColor := {self.color}\n"

        if self.opacity != 1.0:
            result += f"{i(indent)}DefaultOpacity := {self.opacity}\n"

        return result

class WidgetSlotPair(Widget):
    ClassName: str = "/Script/UMGEditor.WidgetSlotPair"
    WidgetName: str

    def __init__(self, object: ParsedWidget) -> None:
        super().__init__(object)

        self.WidgetName = object['props'].get("WidgetName", "").replace("\"", "")
