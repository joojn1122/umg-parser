import { ParsedWidget } from "./types";
import { Widget, registeredClasses } from "./slots";
import {
    formatColor,
    parseText,
    Message,
    parseVector2,
    color2hex,
    parseColor,
    rgb2hex,
    i,
    formatVector2,
    fn,
} from "./constants";
import type { UMGParser } from "./parser";

export class Button extends Widget {
    text: Message;
    verseName: string;

    constructor(parser: UMGParser, object: ParsedWidget, verseName: string) {
        super(parser, object);
        this.verseName = verseName;
        this.text = parseText(object.props.Text ?? "");
    }

    override codify(indent: number, _parsedObjects: Widget[]): string {
        this.text._useTranslated = this.parser.useTranslated;

        if (this.text.notEmpty()) {
            return `${this.verseName}:\n${i(indent + 1)}DefaultText := ${this.text}\n`;
        }

        return this.verseName + "{}\n";
    }
}

export class QuietButton extends Button {
    static ClassName = "/Game/Valkyrie/UMG/UEFN_Button_Quiet.UEFN_Button_Quiet_C";
    override SimpleName = "QuietButton";

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object, "button_quiet");
    }
}
registeredClasses.push(QuietButton as any);

export class RegularButton extends Button {
    static ClassName = "/Game/Valkyrie/UMG/UEFN_Button_Regular.UEFN_Button_Regular_C";
    override SimpleName = "RegularButton";

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object, "button_regular");
    }
}
registeredClasses.push(RegularButton as any);

export class LoudButton extends Button {
    static ClassName = "/Game/Valkyrie/UMG/UEFN_Button_Loud.UEFN_Button_Loud_C";
    override SimpleName = "LoudButton";

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object, "button_loud");
    }
}
registeredClasses.push(LoudButton as any);

export class Image extends Widget {
    static ClassName = "/Script/UMG.Image";
    override SimpleName = "ImageBlock";

    size: [number, number];
    path: string | null;
    tintColor: string | null;
    opacity: number;
    isMaterial: boolean;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);

        const brush = object.props.Brush ?? "";

        const imageSize = brush.match(/ImageSize=\((.*?)\)/);
        const resourceObject = brush.match(/ResourceObject="(.*?)"/);
        const tint = brush.match(/TintColor=\(([^()]*|(\([^()]*\)))*\)/);
        const tintColor = tint ? parseColor(tint[2] ?? "") : null;

        this.size = [32.0, 32.0];
        this.path = null;
        this.tintColor = null;
        this.opacity = 1.0;
        this.isMaterial = false;

        if (imageSize) {
            this.size = parseVector2(imageSize[1]);
        }

        if (resourceObject) {
            const parts = resourceObject[1].split("'");
            const assetType = parts[0];
            const path = parts[1];
            this.isMaterial = assetType !== "/Script/Engine.Texture2D";
            this.path = path.split("/").slice(2).join("/").split(".")[0].replace(/\//g, ".");
            if (this.isMaterial && this.path) {
                this.path += "{}";
            }
        }

        if (tintColor) {
            if (this.path === null) {
                this.opacity = tintColor[3];
                this.tintColor = rgb2hex(tintColor[0], tintColor[1], tintColor[2]);
            } else {
                this.tintColor = color2hex(tintColor[0], tintColor[1], tintColor[2], tintColor[3]);
            }

            // Try to use NamedColors if possible
            if (this.path === null || tintColor[3] === 1) {
                const [r, g, b] = tintColor;
                if (r === 0 && g === 0 && b === 0) {
                    this.tintColor = "NamedColors.Black";
                } else if (r === 255 && g === 255 && b === 255) {
                    this.tintColor = "NamedColors.White";
                } else if (r === 255 && g === 0 && b === 0) {
                    this.tintColor = "NamedColors.Red";
                } else if (r === 0 && g === 0 && b === 255) {
                    this.tintColor = "NamedColors.Blue";
                }
            }

            if (this.tintColor && !this.tintColor.startsWith("NamedColors.")) {
                this.tintColor = `MakeColorFromHex("${this.tintColor}")`;
            }
        }
    }

    override codify(indent: number, _parsedObjects: Widget[]): string {
        if (this.path === null) {
            let result = "color_block:\n";
            if (this.tintColor) {
                result += `${i(indent + 1)}DefaultColor := ${this.tintColor}\n`;
            }
            if (this.opacity !== 1.0) {
                result += `${i(indent + 1)}DefaultOpacity := ${this.opacity}\n`;
            }
            result += `${i(indent + 1)}DefaultDesiredSize := ${formatVector2(this.size)}\n`;
            return result;
        }

        let result = `${this.isMaterial ? "material" : "texture"}_block:\n`;
        result += `${i(indent + 1)}DefaultImage := ${this.path}\n`;
        result += `${i(indent + 1)}DefaultDesiredSize := ${formatVector2(this.size)}\n`;

        if (this.tintColor) {
            result += `${i(indent + 1)}DefaultTint := ${this.tintColor}\n`;
        }

        return result;
    }
}
registeredClasses.push(Image as any);

export class TextBlock extends Widget {
    static ClassName = "/Game/Valkyrie/UMG/UEFN_TextBlock.UEFN_TextBlock_C";
    override SimpleName = "TextBlock";

    text: Message;
    color: string | null;
    opacity: number;
    fontSize: number;
    justification: string | null;
    shadowOffset: [number, number] | null;
    shadowColor: [number, number, number, number] | null;
    hasOutline: boolean;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);

        const props = object.props;

        this.justification = props.Justification ?? null;
        this.text = parseText(props.Text ?? "");

        const color = parseColor(props.ColorAndOpacity ?? "");
        const font = props.Font ?? "";

        if (!font) {
            this.fontSize = 32;
            this.hasOutline = false;
        } else {
            const fontSizeMatch = font.match(/[,(]Size=([\d.]+)/);
            this.fontSize = fontSizeMatch ? parseFloat(fontSizeMatch[1]) * 1.3333333333333333 : 32;
            this.hasOutline = /OutlineSize=[\d.]+/.test(font);
        }

        this.color = "NamedColors.White";
        this.opacity = 1;

        if (color) {
            this.color = formatColor(color);
            this.opacity = color[3];
        }

        this.shadowColor = parseColor(props.ShadowColorAndOpacity ?? "");
        const shadowOffset = props.ShadowOffset ?? null;
        this.shadowOffset = shadowOffset ? parseVector2(shadowOffset) : null;
    }

    override codify(indent: number, _parsedObjects: Widget[]): string {
        this.text._useTranslated = this.parser.useTranslated;

        // is_local is always false in browser mode, so skip FONT_ and outline special handling

        let result = "text_block:\n";

        if (this.text) {
            result += `${i(indent + 1)}DefaultText := ${this.text}\n`;
        }

        if (this.color) {
            result += `${i(indent + 1)}DefaultTextColor := ${this.color}\n`;
        }

        if (this.fontSize !== 32.0) {
            result += `${i(indent + 1)}DefaultTextSize := ${fn(this.fontSize)}\n`;
        }

        if (this.opacity !== 1.0) {
            result += `${i(indent + 1)}DefaultOpacity := ${this.opacity}\n`;
        }

        if (this.shadowOffset) {
            result += `${i(indent + 1)}DefaultShadowOffset := option. ${formatVector2(this.shadowOffset)}\n`;
        }

        if (this.shadowColor) {
            result += `${i(indent + 1)}DefaultShadowColor := ${formatColor(this.shadowColor)}\n`;
            result += `${i(indent + 1)}DefaultShadowOpacity := ${fn(this.shadowColor[3])}\n`;
        }

        if (this.justification) {
            result += `${i(indent + 1)}DefaultJustification := text_justification.${this.justification}\n`;
        }

        return result;
    }
}
registeredClasses.push(TextBlock as any);

export class Slider extends Widget {
    static ClassName = "/Game/Valkyrie/UMG/UEFN_Slider.UEFN_Slider_C";
    override SimpleName = "Slider";

    min: number;
    max: number;
    value: number;
    step: number;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);

        const pivot = object.props.RenderTransformPivot ?? "(X=0.500000,Y=0.500000)";
        [this.min, this.max] = parseVector2(pivot);
        this.value = this.min;
        this.step = 1.0;

        const renderTransform = object.props.RenderTransform;
        if (renderTransform) {
            const shear = renderTransform.match(/Shear=\((.*?)\)/);
            if (shear) {
                [this.value, this.step] = parseVector2(shear[1]);
            }
        }
    }

    override codify(indent: number, _parsedObjects: Widget[]): string {
        let result = "slider_regular:\n";
        result += `${i(indent + 1)}DefaultValue := ${fn(this.value)}\n`;
        result += `${i(indent + 1)}DefaultMinValue := ${fn(this.min)}\n`;
        result += `${i(indent + 1)}DefaultMaxValue := ${fn(this.max)}\n`;
        result += `${i(indent + 1)}DefaultStepSize := ${fn(this.step)}\n`;
        return result;
    }
}
registeredClasses.push(Slider as any);

export class WidgetSlotPair extends Widget {
    static ClassName = "/Script/UMGEditor.WidgetSlotPair";
    override SimpleName = "WidgetSlotPair";
    WidgetName: string;

    constructor(parser: UMGParser, object: ParsedWidget) {
        super(parser, object);
        this.WidgetName = (object.props.WidgetName ?? "").replace(/"/g, "");
    }
}
registeredClasses.push(WidgetSlotPair as any);
