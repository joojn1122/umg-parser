import { ParsedWidget } from "./types";
import {
    Padding,
    parseOffsets,
    parseAnchors,
    parseVector2,
    formatVector2,
    i,
    fn,
} from "./constants";
import type { UMGParser } from "./parser";

export const registeredClasses: Array<{
    ClassName: string;
    new (parser: UMGParser, object: ParsedWidget, ...args: unknown[]): Widget;
}> = [];

export class Widget {
    Name: string;
    DisplayName: string;
    ClassName?: string;
    SimpleName = "Widget";
    props: Record<string, string>;
    parser: UMGParser;

    get varName(): string {
        return this.DisplayName.substring(1); // .split("_FONT")[0]
    }

    isVar(): boolean {
        return this.DisplayName.startsWith("$");
    }

    constructor(parser: UMGParser, object: ParsedWidget) {
        this.parser = parser;
        this.Name = (object.props.Name ?? "").replace(/"/g, "");
        this.DisplayName = (object.props.DisplayLabel ?? "").replace(/"/g, "");
        if (this.DisplayName === "") this.DisplayName = this.Name;
        this.props = object.props;
    }

    codify(_indent: number, _parsedObjects: Widget[]): string {
        // Fallback to export path
        let widgetClass = this.props.Class ?? `Script error: Class for ${this.Name} not found`;

        // Remove project name from path
        const secondSlash = widgetClass.indexOf("/", 1);
        if (secondSlash !== -1) {
            widgetClass = widgetClass.substring(secondSlash + 1);

            // Remove part after last dot
            const lastDot = widgetClass.lastIndexOf(".");
            if (lastDot !== -1) {
                widgetClass = widgetClass.substring(0, lastDot);
            }
        }

        const widgetPath = widgetClass.replace(/\//g, ".") + "{}";
        return `${widgetPath}\n`;
    }
}

// Slots
export class Slot extends Widget {
    Content: string;
    variable: Widget | null = null;
    widget: Widget | null = null;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);
        this.Content = (object.props.Content ?? "").split("'")[1]?.split("'")[0] ?? "";
    }

    formatWidget(indent: number, parsedObjects: Widget[]): string {
        this.widget = parsedObjects.find((obj) => obj.Name === this.Content) ?? null;

        if (this.widget === null) {
            return `Script error: Widget ${this.Content} not found\n`;
        }

        if (this.widget.DisplayName.startsWith("$external_")) {
            const name = this.widget.DisplayName.substring(10);
            return name + "\n\n";
        }

        if (this.widget.isVar()) {
            this.variable = this.widget;
            this.widget.codify(indent, parsedObjects);
            return this.widget.varName + "\n\n";
        }

        return this.widget.codify(indent, parsedObjects) + "\n";
    }
}

export class CanvasSlot extends Slot {
    static ClassName = "/Script/UMG.CanvasPanelSlot";
    override SimpleName = "CanvasSlot";

    Anchors: [number, number, number, number] | null;
    Offsets: Record<string, number> | null;
    Alignment: [number, number] | null;
    SizeToContent: boolean;
    ZOrder: number;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);

        const props = object.props;
        this.SizeToContent = props.bAutoSize === "True";
        this.Offsets = null;
        this.Anchors = null;
        this.Alignment = null;

        let layoutData = props.LayoutData ?? "";
        if (layoutData) {
            layoutData = layoutData.substring(1, layoutData.length - 1);

            const offsets = layoutData.match(/Offsets=\((.*?)\)/);
            const anchors = layoutData.match(/Anchors=\((.*?)\)\)/);
            const alignment = layoutData.match(/Alignment=\((.*?)\)/);

            if (offsets) {
                this.Offsets = parseOffsets(offsets[1]);
                if (Object.values(this.Offsets).every((o) => o === 0.0)) {
                    this.Offsets = null;
                }
            }

            if (anchors) {
                this.Anchors = parseAnchors(anchors[1]);
            }

            if (alignment) {
                this.Alignment = parseVector2(alignment[1]);
                if (this.Alignment[0] === 0.0 && this.Alignment[1] === 0.0) {
                    this.Alignment = null;
                }
            }
        }

        this.ZOrder = parseInt(props.ZOrder ?? "0", 10);
    }

    override codify(indent: number, parsedObjects: Widget[]): string {
        let result = `${i(indent)}canvas_slot:\n`;

        if (this.ZOrder !== 0) {
            result += `${i(indent + 1)}ZOrder := ${this.ZOrder}\n`;
        }

        if (this.Anchors) {
            result += `${i(indent + 1)}Anchors := Anchors(${fn(this.Anchors[0])}, ${fn(this.Anchors[1])}, ${fn(this.Anchors[2])}, ${fn(this.Anchors[3])})\n`;
        }

        result += `${i(indent + 1)}SizeToContent := ${this.SizeToContent ? "true" : "false"}\n`;

        if (this.Offsets) {
            const left = this.Offsets.Left ?? 0.0;
            const top = this.Offsets.Top ?? 0.0;
            const sizeStr = this.SizeToContent
                ? ""
                : `, ${this.Offsets.Right ?? 100.0}, ${this.Offsets.Bottom ?? 30.0}`;
            result += `${i(indent + 1)}Offsets := Offsets(${left}, ${top}${sizeStr})\n`;
        }

        if (this.Alignment) {
            result += `${i(indent + 1)}Alignment := ${formatVector2(this.Alignment)}\n`;
        }

        return result + `${i(indent + 1)}Widget := ` + this.formatWidget(indent + 1, parsedObjects);
    }
}
registeredClasses.push(CanvasSlot as any);

export class StackBoxSlot extends Slot {
    static ClassName = "/Script/UMG.StackBoxSlot";
    override SimpleName = "StackBoxSlot";
    static DefaultVAlign = "VAlign_Fill";
    static DefaultHAlign = "HAlign_Fill";

    distribution: number;
    padding: Padding;
    horizontalAlignment: string;
    verticalAlignment: string;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);

        const props = object.props;
        const ctor = this.constructor as typeof StackBoxSlot;

        this.verticalAlignment = (props.VerticalAlignment ?? ctor.DefaultVAlign).replace("VAlign_", "");
        this.horizontalAlignment = (props.HorizontalAlignment ?? ctor.DefaultHAlign).replace("HAlign_", "");
        this.padding = Padding.parse(props.Padding ?? "Padding(Left=0.0)");
        this.distribution = -1;

        const size = props.Size;
        if (size) {
            const sizeRule = size.match(/SizeRule=([a-zA-Z]+)/);
            if (sizeRule && sizeRule[1] === "Fill") {
                this.distribution = 1.0;
                const value = size.match(/Value=([0-9.\-]+)/);
                if (value) this.distribution = parseFloat(value[1]);
            }
        }
    }

    override codify(indent: number, parsedObjects: Widget[]): string {
        let result = `${i(indent)}stack_box_slot:\n`;

        if (!this.padding.isEmpty()) {
            result += this.padding.codify(indent + 1);
        }

        result += `${i(indent + 1)}HorizontalAlignment := horizontal_alignment.${this.horizontalAlignment}\n`;
        result += `${i(indent + 1)}VerticalAlignment := vertical_alignment.${this.verticalAlignment}\n`;

        if (this.distribution !== -1) {
            result += `${i(indent + 1)}Distribution := ${fn(this.distribution)}.Maybe()\n`;
        }

        return result + `${i(indent + 1)}Widget := ` + this.formatWidget(indent + 1, parsedObjects);
    }
}
registeredClasses.push(StackBoxSlot as any);

export class OverlaySlot extends StackBoxSlot {
    static override ClassName = "/Script/UMG.OverlaySlot";
    override SimpleName = "OverlaySlot";
    static override DefaultVAlign = "VAlign_Top";
    static override DefaultHAlign = "HAlign_Left";

    override codify(indent: number, parsedObjects: Widget[]): string {
        return super.codify(indent, parsedObjects).replace("stack_box_slot", "overlay_slot");
    }
}
registeredClasses.push(OverlaySlot as any);

// Slotables
export class Slotable extends Widget {
    slots: Slot[];

    constructor(
        parser: UMGParser,
        object: ParsedWidget,
        SlotClass: typeof CanvasSlot | typeof StackBoxSlot | typeof OverlaySlot,
    ) {
        super(parser, object);
        this.slots = [];

        for (const child of object.children) {
            try {
                if (
                    (child.props.ExportPath ?? "").includes(SlotClass.ClassName) &&
                    child.props.Content
                ) {
                    const slot = new SlotClass(parser, child);
                    if (slot.Content.includes("__ignore")) continue;
                    this.slots.push(slot);
                }
            } catch {
                // skip invalid slots
            }
        }

        // Sort slots by their index in the Slots(...) props
        const slotIndexes: Array<[number, string]> = [];
        for (const prop of Object.keys(object.props)) {
            if (prop.startsWith("Slots")) {
                const slotIndex = parseInt(prop.split("(")[1].split(")")[0], 10);
                const slotName = object.props[prop].replace(/"/g, "").split("'")[1]?.split("'")[0] ?? "";
                slotIndexes.push([slotIndex, slotName]);
            }
        }

        slotIndexes.sort((a, b) => a[0] - b[0]);

        const sortedSlots: Slot[] = [];
        for (const [, slotName] of slotIndexes) {
            const s = this.slots.find((slot) => slot.Name === slotName);
            if (s) sortedSlots.push(s);
        }

        this.slots = sortedSlots;
    }

    formatSlots(indent: number, parsedObjects: Widget[]): string {
        if (this.slots.length === 0) return "";

        let result = `${i(indent - 1)}Slots := array:\n`;
        for (const slot of this.slots) {
            result += slot.codify(indent, parsedObjects);
        }
        return result;
    }
}

export class Canvas extends Slotable {
    static ClassName = "/Script/UMG.CanvasPanel";
    override SimpleName = "Canvas";

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object, CanvasSlot);
    }

    override codify(indent: number, parsedObjects: Widget[]): string {
        return "canvas:\n" + this.formatSlots(indent + 2, parsedObjects);
    }
}
registeredClasses.push(Canvas as any);

export class StackBox extends Slotable {
    static ClassName = "/Script/UMG.StackBox";
    override SimpleName = "StackBox";
    vertical: boolean;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object, StackBoxSlot);
        this.vertical = (object.props.Orientation ?? "Horizontal").replace("Orient_", "") === "Vertical";
    }

    override codify(indent: number, parsedObjects: Widget[]): string {
        let result = `stack_box:\n`;
        result += `${i(indent + 1)}Orientation := orientation.${this.vertical ? "Vertical" : "Horizontal"}\n`;
        return result + this.formatSlots(indent + 2, parsedObjects);
    }
}
registeredClasses.push(StackBox as any);

export class Overlay extends Slotable {
    static ClassName = "/Script/UMG.Overlay";
    override SimpleName = "Overlay";

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object, OverlaySlot);
    }

    override codify(indent: number, parsedObjects: Widget[]): string {
        return "overlay:\n" + this.formatSlots(indent + 2, parsedObjects);
    }
}
registeredClasses.push(Overlay as any);
