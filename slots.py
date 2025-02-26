import re
from typing import TypedDict
from constants import Padding, parse_offsets, parse_anchors, parse_vector2, INDENT, i, format_float, format_vector2, fn
from rich import print
import traceback

registered_classes: list[type['Widget']] = []

class ParsedWidget(TypedDict): 
    props: dict
    children: list['ParsedWidget']

class Widget:
    Name: str
    DisplayName: str
    ClassName: str
    props: dict

    @property
    def var_name(self) -> str:
        return self.DisplayName[1:].split("_FONT")[0]

    def is_var(self) -> bool:
        return self.DisplayName.startswith("$")

    def __init_subclass__(cls) -> None:
        if(getattr(cls, "ClassName", None) is None):
            return
        
        registered_classes.append(cls)
    
    def __init__(self, object: ParsedWidget) -> None:
        self.Name = object['props'].get("Name", "").replace("\"", "")
        self.DisplayName = object['props'].get("DisplayLabel", "").replace("\"", "")

        if(self.DisplayName == ""):
            self.DisplayName = self.Name

        self.props = object['props']

    def codify(self, indent: int, parsed_objects: list['Widget']) -> str:
        return ""
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(Name={self.Name})"

    def __repr__(self) -> str:
        return self.__str__()
    
# Slots
class Slot(Widget):
    Content: str
    
    variable: Widget | None = None
    widget: Widget | None = None

    def __init__(self, object: ParsedWidget) -> None:
        super().__init__(object)

        self.Content = object['props'].get("Content", "").split("'")[1].split("'")[0]

    def format_widget(self, indent: int, parsed_objects: list[Widget]) -> str:
        self.widget = next((obj for obj in parsed_objects if obj.Name == self.Content), None)

        if self.widget is None:
            return f"Script error: Widget {self.Content} not found\n"

        if self.widget.DisplayName.startswith("$external_"):
            name = self.widget.DisplayName[10:]
            return name + "\n\n"

        if self.widget.is_var():
            self.variable = self.widget
            
            # Trigger other variables
            self.widget.codify(indent, parsed_objects)

            return self.widget.var_name + "\n\n" # Put a newline at the end for better formatting

        return self.widget.codify(indent, parsed_objects) + "\n" # Also here
        
class CanvasSlot(Slot):
    ClassName: str = "/Script/UMG.CanvasPanelSlot"

    Anchors: tuple[float, float, float, float] | None
    Offsets: dict[str, float] | None
    Alignment: tuple[float, float] | None
    SizeToContent: bool = False
    ZOrder: int = 0
    
    def __init__(self, object: ParsedWidget) -> None:
        super().__init__(object)

        props = object['props']

        self.SizeToContent = props.get("bAutoSize", "False") == "True"
        
        self.Offsets = None
        self.Anchors = None
        self.Alignment = None

        layout_data = props.get("LayoutData", "")
        if(layout_data):
            layout_data = layout_data[1:-1]
            
            offsets = re.search(r"Offsets=\((.*?)\)", layout_data)
            anchors = re.search(r"Anchors=\((.*?)\)\)", layout_data)
            alignment = re.search(r"Alignment=\((.*?)\)", layout_data)

            if offsets:
                self.Offsets = parse_offsets(offsets.group(1))

                if(all(o == 0.0 for o in self.Offsets.values())):
                    self.Offsets = None

            if anchors:
                self.Anchors = parse_anchors(anchors.group(1))

            if alignment:
                self.Alignment = parse_vector2(alignment.group(1))

                if(self.Alignment == (0.0, 0.0)):
                    self.Alignment = None

        self.ZOrder = int(props.get("ZOrder", 0))

    def __str__(self) -> str:
        return f"CanvasSlot(Name={self.Name}, Anchors={self.Anchors}, Offsets={self.Offsets}, Alignment={self.Alignment}, SizeToContent={self.SizeToContent}, ZOrder={self.ZOrder}, Content={self.Content})\n"
    
    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        result = f"{i(indent)}canvas_slot:\n"

        if self.ZOrder != 0:
            result += f"{i(indent + 1)}ZOrder := {self.ZOrder}\n"

        if self.Anchors:
            result += f"{i(indent + 1)}Anchors := Anchors({fn(self.Anchors[0])}, {fn(self.Anchors[1])}, {fn(self.Anchors[2])}, {fn(self.Anchors[3])})\n"

        result += f"{i(indent + 1)}SizeToContent := {'true' if self.SizeToContent else 'false'}\n"

        if self.Offsets:
            result += f"{i(indent + 1)}Offsets := Offsets({self.Offsets.get('Left', '0.0')}, {self.Offsets.get('Top', '0.0')}{f', {self.Offsets.get('Right', '100.0')}, {self.Offsets.get('Bottom', '30.0')}' if not self.SizeToContent else ''})\n"

        if self.Alignment:
            result += f"{i(indent + 1)}Alignment := {format_vector2(self.Alignment)}\n"

        return result + f"{i(indent + 1)}Widget := " + self.format_widget(indent + 1, parsed_objects)

class StackBoxSlot(Slot):
    ClassName: str = "/Script/UMG.StackBoxSlot"

    distribution: float
    padding: Padding
    horizontal_alignment: str
    vertical_alignment: str
    Content: str

    def __init__(self, object: ParsedWidget) -> None:
        super().__init__(object)

        props = object['props']

        self.vertical_alignment = props.get("VerticalAlignment", "VAlign_Fill").replace("VAlign_", "")
        self.horizontal_alignment = props.get("HorizontalAlignment", "HAlign_Fill").replace("HAlign_", "")

        self.padding = Padding.parse(props.get("Padding", "Padding(Left=0.0)"))
        self.distribution = -1

        size = props.get("Size", None)
        if(size):
            size_rule = re.search(r"SizeRule=([a-zA-Z]+)", size)

            if(size_rule and size_rule.group(1) == "Fill"):
                self.distribution = 1.0

                value = re.search(r"Value=([0-9\.-]+)", size)
                if(value):
                    self.distribution = float(value.group(1))

    def __str__(self) -> str:
        return f"StackBoxSlot(Name={self.Name}, Padding={self.padding}, HorizontalAlignment={self.horizontal_alignment}, VerticalAlignment={self.vertical_alignment}, Content={self.Content})\n"

    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        result = f"{i(indent)}stack_box_slot:\n"

        if(not self.padding.is_empty()):
            result += self.padding.codify(indent + 1)
        
        result += f"{i(indent + 1)}HorizontalAlignment := horizontal_alignment.{self.horizontal_alignment}\n"
        result += f"{i(indent + 1)}VerticalAlignment := vertical_alignment.{self.vertical_alignment}\n"

        if self.distribution != -1:
            result += f"{i(indent + 1)}Distribution := {format_float(self.distribution)}.Maybe()\n"

        return result + f"{i(indent + 1)}Widget := " + self.format_widget(indent + 1, parsed_objects)
    
# OverlaySlot is exactly the same as StackBoxSlot, but with a different class name
class OverlaySlot(StackBoxSlot):
    ClassName: str = "/Script/UMG.OverlaySlot"
    
    def __str__(self) -> str:
        return f"OverlaySlot(Name={self.Name}, Padding={self.padding}, HorizontalAlignment={self.horizontal_alignment}, VerticalAlignment={self.vertical_alignment}, Content={self.Content})\n"

    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        return super().codify(indent, parsed_objects).replace("stack_box_slot", "overlay_slot", 1)

# Slotables
class Slotable(Widget):
    slots: list[Slot]

    def __init__(self, object: ParsedWidget, slot_class: type[Slot]):
        super().__init__(object)

        self.slots = []

        for child in object['children']:
            try:
                if(slot_class.ClassName in child['props'].get('ExportPath', "") and child["props"].get("Content")):
                    slot = slot_class(child)

                    # Ignore slots with __ignore in the content
                    if("__ignore" in slot.Content):
                        continue

                    self.slots.append(slot)

            except Exception as e:
                print(f"Error parsing slot {child['props'].get("ExportPath")}")
                traceback.print_exc()
                pass

        # Sort slots
        slot_indexes: list[tuple[int, str]] = []
        for prop in object['props']:
            if(prop.startswith("Slots")):
                slot_index = int(prop.split("(")[1].split(")")[0])
                slot_indexes.append((
                    slot_index, 
                    object['props'][prop].replace("\"", "").split("'")[1].split("'")[0]
                ))

        slot_indexes.sort(key=lambda x: x[0])
        
        sorted_slots = []
        for index, slot_name in slot_indexes:
            s = next((slot for slot in self.slots if slot.Name == slot_name), None)
            if s:
                sorted_slots.append(s)

        self.slots = sorted_slots

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(Name={self.Name}, Slots={self.slots})"
    
    def __repr__(self) -> str:
        return self.__str__()

    def format_slots(self, indent: int, parsed_objects: list[Widget]) -> str:
        if len(self.slots) == 0:
            return ""
        
        result = f"{i(indent - 1)}Slots := array:\n"
        
        for slot in self.slots:
            result += slot.codify(indent, parsed_objects)
        
        return result

class Canvas(Slotable):
    ClassName: str = "/Script/UMG.CanvasPanel"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, CanvasSlot)

    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        return f"canvas:\n" + self.format_slots(indent + 2, parsed_objects)

class StackBox(Slotable):
    ClassName: str = "/Script/UMG.StackBox"

    vertical: bool

    def __init__(self, object: ParsedWidget):
        super().__init__(object, StackBoxSlot)

        self.vertical = object['props'].get("Orientation", "Horizontal").replace("Orient_", "") == "Vertical"

    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        result = \
f'''stack_box:
{i(indent + 1)}Orientation := orientation.{"Vertical" if self.vertical else "Horizontal"}
'''

        return result + self.format_slots(indent + 2, parsed_objects)
    
class Overlay(Slotable):
    ClassName: str = "/Script/UMG.Overlay"

    def __init__(self, object: ParsedWidget):
        super().__init__(object, OverlaySlot)

    def codify(self, indent: int, parsed_objects: list[Widget]) -> str:
        return f"overlay:\n" + self.format_slots(indent + 2, parsed_objects)