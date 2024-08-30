import re

INDENT = " " * 4
def i(indent: int) -> str:
    return INDENT * indent

# Format number
def fn(num: float):
    s = str(num)

    if "." not in s:
        return s + ".0"
    
    return s


def parse_offsets(offsets: str) -> dict[str, float]:
    offsets_data = offsets.split(",")

    result = {}

    for data in offsets_data:
        key, value = data.split("=")
        result[key] = float(value)

    return result

def parse_vector2(alignment: str) -> tuple[float, float]:
    alignment_data = alignment.split(",")

    return (float(alignment_data[0].split("=")[1]), 
            float(alignment_data[1].split("=")[1]))

def format_vector2(vector: tuple[float, float]) -> str:
    return f"vector2{'{'} X := {vector[0]}, Y := {vector[1]} {'}'}"

def parse_anchors(anchors: str) -> tuple[float, float, float, float]:
    xs = list(map(float, re.findall(r"(?<=X=)[\d\.]*", anchors)))
    ys = list(map(float, re.findall(r"(?<=Y=)[\d\.]*", anchors)))

    if len(xs) == 1:
        if "Minimum" in anchors:
            return (xs[0], ys[0], 0, 0)
        else:
            return (0, 0, xs[0], ys[0])
        
    return (xs[0], ys[0], xs[1], ys[1])

class Padding:
    Left: float
    Top: float
    Right: float
    Bottom: float

    def __init__(self, left: float, top: float, right: float, bottom: float):
        self.Left = left
        self.Top = top
        self.Right = right
        self.Bottom = bottom

    @staticmethod
    def parse(string: str) -> "Padding":
        # String example
        # (Right=25.000000,Left=25.000000)

        values: list[float] = [0, 0, 0, 0]
        matches = [r"Left=([0-9\.-]+)", r"Top=([0-9\.-]+)", r"Right=([0-9\.-]+)", r"Bottom=([0-9\.-]+)"]
        
        for i, match in enumerate(matches):
            result = re.search(match, string)
            if result:
                try:
                    values[i] = float(result.group(1))
                except ValueError:
                    pass

        return Padding(*values)

    def __str__(self) -> str:
        return f"Padding(Left={self.Left}, Top={self.Top}, Right={self.Right}, Bottom={self.Bottom})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_empty(self) -> bool:
        return self.Left == self.Top == self.Right == self.Bottom == 0

    def codify(self, indent: int) -> str:
        string = f"{i(indent)}Padding := margin:\n"

        if self.Left != 0:
            string += f"{i(indent + 1)}Left := {self.Left}\n"

        if self.Top != 0:
            string += f"{i(indent + 1)}Top := {self.Top}\n"

        if self.Right != 0:
            string += f"{i(indent + 1)}Right := {self.Right}\n"

        if self.Bottom != 0:
            string += f"{i(indent + 1)}Bottom := {self.Bottom}\n"

        return string

def rgb_to_srgb(color):
    if color <= 0.0031308:
        return 12.92 * color
    else:
        return 1.055 * (color ** (1.0 / 2.4)) - 0.055

def rgb2hex(r: float, g: float, b: float) -> str:
    r = rgb_to_srgb(r)
    g = rgb_to_srgb(g)
    b = rgb_to_srgb(b)

    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    
def color2hex(r: float, g: float, b: float, a: float) -> str:
    return rgb2hex(r, g, b) + f"{int(a * 255):02x}"
    
def parse_color(color: str) -> tuple[float, float, float, float] | None:
    match = re.search(r"\(R=(.*?),G=(.*?),B=(.*?),A=(.*?)\)", color)

    if match:
        return (float(match.group(1)), float(match.group(2)), float(match.group(3)), float(match.group(4)))
    

def format_float(f: float) -> str:
    s = str(f)

    if "." not in s:
        return s + ".0"
    
    return s