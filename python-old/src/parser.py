"""
UMG Parser - Main parser class that holds all configuration and converts UMG to Verse code.
"""
from dataclasses import dataclass, field
from typing import Optional, TypedDict
from constants import INDENT, Message, i
from convert import parse_widgets
from slots import Widget, ParsedWidget, Slotable, registered_classes
from widgets import WidgetSlotPair

class OverrideScreen(TypedDict):
    """Type definition for override screen entries."""
    name: str
    path: str


class InvalidConfigError(Exception):
    """Raised when the parser configuration is invalid."""
    pass


def _validate_override_screens(override_screens: list) -> list[OverrideScreen]:
    """
    Validate that override_screens has the correct structure.
    
    Args:
        override_screens: List to validate.
        
    Returns:
        The validated list of OverrideScreen entries.
        
    Raises:
        InvalidConfigError: If the structure is invalid.
    """
    if not isinstance(override_screens, list):
        raise InvalidConfigError(
            f"override_screens must be a list, got {type(override_screens).__name__}"
        )
    
    for idx, screen in enumerate(override_screens):
        if not isinstance(screen, dict):
            raise InvalidConfigError(
                f"override_screens[{idx}] must be a dict, got {type(screen).__name__}"
            )
        
        if 'name' not in screen:
            raise InvalidConfigError(
                f"override_screens[{idx}] is missing required key 'name'"
            )
        
        if 'path' not in screen:
            raise InvalidConfigError(
                f"override_screens[{idx}] is missing required key 'path'"
            )
        
        if not isinstance(screen['name'], str):
            raise InvalidConfigError(
                f"override_screens[{idx}]['name'] must be a string, got {type(screen['name']).__name__}"
            )
        
        if not isinstance(screen['path'], str):
            raise InvalidConfigError(
                f"override_screens[{idx}]['path'] must be a string, got {type(screen['path']).__name__}"
            )
    
    return override_screens

@dataclass
class UMGParserConfig:
    """Configuration for the UMG Parser."""
    use_translated: bool = False
    root_path: str = ""
    lang_path: str = ""
    override_screens: list[OverrideScreen] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.override_screens = _validate_override_screens(self.override_screens)

class UMGParser:
    """
    Main UMG Parser class that handles conversion of UMG Widget blueprints to Verse code.
    
    All configuration is stored in this class instance, avoiding global state.
    """
    
    def __init__(self, config: Optional[UMGParserConfig] = None, is_local: bool = True):
        """
        Initialize the UMG Parser with optional configuration.
        
        Args:
            config: Optional UMGParserConfig instance. If None, uses defaults.
            is_local: Whether the parser is running in a local environment.
        """
        self.config = config or UMGParserConfig()
        self._collected_messages: list = []
        self.is_local = is_local
    
    @property
    def use_translated(self) -> bool:
        return self.config.use_translated
    
    @use_translated.setter
    def use_translated(self, value: bool):
        self.config.use_translated = value
    
    def convert(self, content: str, indent: int = 0) -> tuple[str, str, list]:
        """
        Converts UMG Widget blueprint text into Verse code.

        Args:
            content: The UMG Widget blueprint text.
            indent: The indentation level for the generated Verse code.

        Returns:
            tuple: A tuple containing the export path (str), generated Verse code (str), 
                   and a list of Widget objects.
        """
        
        # Reset collected messages for this conversion
        self._collected_messages = []
        
        parsed_widgets: list[ParsedWidget] = parse_widgets(content, 0)
        widgets: list[Widget] = []

        for widget in parsed_widgets:
            props = widget['props']
            className = props.get('Class', "")

            found = False

            for rclass in registered_classes:
                if rclass.ClassName == className:
                    w = rclass(self, widget)
                    widgets.append(w)
                    found = True
                    break
            
            # Add other widgets as generic widgets
            if not found:
                w = Widget(self, widget)
                widgets.append(w)

        root: Widget | None = None
        slot_root: WidgetSlotPair | None = None

        # Find root & slot_root
        for widget in widgets:
            if isinstance(widget, WidgetSlotPair):
                slot_root = widget
                
                for w in widgets:
                    if w.Name == widget.WidgetName and isinstance(w, Slotable):
                        root = w
                        break
                break
        
        # Set root to first widget if none found
        if root is None:
            if len(widgets) == 0:
                raise ValueError("Invalid widget blueprint")

            root = widgets[0]
        
        export_path = root.props.get("ExportPath", "")
        
        result = f"{i(indent)}{root.SimpleName} := " + root.codify(indent, widgets)

        variables: list[Widget]
        if isinstance(root, Slotable):
            variables = self._get_variables(root)
        else:
            variables = []

        variables_str = ""
        for variable in variables:
            var_name = variable.var_name
            var_content = i(indent) + var_name + " := " + variable.codify(indent, widgets) + "\n"
            variables_str += var_content
        
        return export_path, variables_str + result, widgets
    
    def _get_variables(self, widget) -> list:
        """Get all variable widgets from a slotable widget."""
        variables = []
        
        for slot in widget.slots:
            if isinstance(slot.widget, Slotable):
                variables.extend(self._get_variables(slot.widget))

            if slot.variable:
                variables.append(slot.variable)

        return variables
    
    def generate_messages_module(self, widgets: list) -> str:
        """
        Generate a Verse messages module from widgets that have translatable text.
        
        Args:
            widgets: List of Widget objects from conversion.
            
        Returns:
            str: The generated messages module code, or empty string if no messages.
        """
        if not self.use_translated:
            return ""
        
        messages_content = ""
        seen_keys = set()

        for widget in widgets:
            if hasattr(widget, "text"):
                text = getattr(widget, "text")

                if isinstance(text, Message) and text.translation_key and text.include_in_translation_file:
                    check_key = f"{text.translation_key}<public><localizes>"
                    
                    # Check if the message already exists
                    if check_key in seen_keys:
                        continue
                    
                    seen_keys.add(check_key)
                    
                    # Needs to manually add types for arguments
                    args_str = ", ".join([f"{arg}: " for arg in text.params])
                    if args_str:
                        args_str = f"({args_str})"

                    # Add the message to the content
                    messages_content += f"\n{INDENT}{text.translation_key}<public><localizes>{args_str}: message = \"{text.message}\""

        if messages_content:
            return "Messages<public> := module:" + messages_content + "\n\n\n"
        
        return ""
    
    def get_new_messages_for_file(self, widgets: list, existing_content: str) -> str:
        """
        Get new messages that don't already exist in the file content.
        
        Args:
            widgets: List of Widget objects from conversion.
            existing_content: The existing file content to check against.
            
        Returns:
            str: The new messages to add, or empty string if none.
        """
        if not self.use_translated:
            return ""
        
        added_content = ""

        for widget in widgets:
            if hasattr(widget, "text"):
                text = getattr(widget, "text")

                if isinstance(text, Message) and text.translation_key and text.include_in_translation_file:
                    check_key = f"{text.translation_key}<public><localizes>"
                    
                    # Check if the message already exists in the file or added content
                    if check_key in existing_content or check_key in added_content:
                        continue
                    
                    # Needs to manually add types for arguments
                    args_str = ", ".join([f"{arg}: " for arg in text.params])
                    if args_str:
                        args_str = f"({args_str})"

                    # Add the message
                    added_content += f"\n{INDENT}{text.translation_key}<public><localizes>{args_str}: message = \"{text.message}\""

        return added_content
