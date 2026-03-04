export const INDENT = "    ";

export function i(indent: number): string {
    return INDENT.repeat(indent);
}

/** Format number: ensures a decimal point is present */
export function fn(num: number): string {
    const s = String(num);
    if (!s.includes(".")) {
        return s + ".0";
    }
    return s;
}

export function formatColor(color: [number, number, number, number]): string {
    const rgb = color.slice(0, 3) as [number, number, number];
    const sum = rgb[0] + rgb[1] + rgb[2];

    if (sum === 0) return "NamedColors.Black";
    if (sum === 3) return "NamedColors.White";

    return `MakeColorFromHex("${rgb2hex(rgb[0], rgb[1], rgb[2])}")`;
}

export function parseOffsets(offsets: string): Record<string, number> {
    const result: Record<string, number> = {};
    for (const data of offsets.split(",")) {
        const [key, value] = data.split("=");
        result[key] = parseFloat(value);
    }
    return result;
}

export function parseVector2(alignment: string): [number, number] {
    const data = alignment.replace(/[()]/g, "").split(",");
    return [
        parseFloat(data[0].split("=")[1]),
        parseFloat(data[1].split("=")[1]),
    ];
}

export function formatVector2(vector: [number, number]): string {
    return `vector2{ X := ${vector[0]}, Y := ${vector[1]} }`;
}

export function parseAnchors(anchors: string): [number, number, number, number] {
    const xs = Array.from(anchors.matchAll(/(?<=X=)[\d.]*/g), (m) => parseFloat(m[0]));
    const ys = Array.from(anchors.matchAll(/(?<=Y=)[\d.]*/g), (m) => parseFloat(m[0]));

    if (xs.length === 1) {
        if (anchors.includes("Minimum")) {
            return [xs[0], ys[0], 0, 0];
        } else {
            return [0, 0, xs[0], ys[0]];
        }
    }

    return [xs[0], ys[0], xs[1], ys[1]];
}

export class Padding {
    Left: number;
    Top: number;
    Right: number;
    Bottom: number;

    constructor(left: number, top: number, right: number, bottom: number) {
        this.Left = left;
        this.Top = top;
        this.Right = right;
        this.Bottom = bottom;
    }

    static parse(str: string): Padding {
        const values: number[] = [0, 0, 0, 0];
        const matches = [
            /Left=([0-9.\-]+)/,
            /Top=([0-9.\-]+)/,
            /Right=([0-9.\-]+)/,
            /Bottom=([0-9.\-]+)/,
        ];

        for (let idx = 0; idx < matches.length; idx++) {
            const result = str.match(matches[idx]);
            if (result) {
                const v = parseFloat(result[1]);
                if (!isNaN(v)) values[idx] = v;
            }
        }

        return new Padding(values[0], values[1], values[2], values[3]);
    }

    isEmpty(): boolean {
        return this.Left === 0 && this.Top === 0 && this.Right === 0 && this.Bottom === 0;
    }

    codify(indent: number): string {
        let str = `${i(indent)}Padding := margin:\n`;
        if (this.Left !== 0) str += `${i(indent + 1)}Left := ${this.Left}\n`;
        if (this.Top !== 0) str += `${i(indent + 1)}Top := ${this.Top}\n`;
        if (this.Right !== 0) str += `${i(indent + 1)}Right := ${this.Right}\n`;
        if (this.Bottom !== 0) str += `${i(indent + 1)}Bottom := ${this.Bottom}\n`;
        return str;
    }
}

export function rgbToSrgb(color: number): number {
    if (color <= 0.0031308) {
        return 12.92 * color;
    } else {
        return 1.055 * Math.pow(color, 1.0 / 2.4) - 0.055;
    }
}

export function rgb2hex(r: number, g: number, b: number): string {
    r = rgbToSrgb(r);
    g = rgbToSrgb(g);
    b = rgbToSrgb(b);

    const toHex = (v: number) => Math.round(v * 255).toString(16).padStart(2, "0");
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

export function color2hex(r: number, g: number, b: number, a: number): string {
    const toHex = (v: number) => Math.round(v * 255).toString(16).padStart(2, "0");
    return rgb2hex(r, g, b) + toHex(a);
}

export function parseColor(color: string): [number, number, number, number] | null {
    const match = color.match(/\(R=(.*?),G=(.*?),B=(.*?),A=(.*?)\)/);
    if (match) {
        return [
            parseFloat(match[1]),
            parseFloat(match[2]),
            parseFloat(match[3]),
            parseFloat(match[4]),
        ];
    }
    return null;
}

export class Message {
    static ARG_REGEX = /\{(.*?)\}/g;

    message: string;
    translationKey: string | null;
    includeInTranslationFile = false;
    params: string[] = [];
    _useTranslated = false;

    constructor(message: string, translationKey: string | null = null) {
        this.message = message;
        this.translationKey = translationKey;
        this.params = [];

        for (const match of message.matchAll(Message.ARG_REGEX)) {
            this.params.push(match[1]);
        }
    }

    notEmpty(): boolean {
        return this.message !== "";
    }

    format(useTranslated = false): string {
        if (this.message === "") return "EmptyMessage";

        if (useTranslated && this.translationKey) {
            this.includeInTranslationFile = true;
            const suffix = this.params.length ? `(${this.params.join(", ")})` : "";
            return `Messages.${this.translationKey}${suffix}`;
        }

        return `"${this.message}".Msg()`;
    }

    toString(): string {
        return this.format(this._useTranslated);
    }
}

export function parseText(text: string): Message {
    const matched = Array.from(text.matchAll(/"(.*?)"/g), (m) => m[1]);

    if (matched.length === 0) return new Message("");
    if (matched.length === 1) {
        const content = matched[0].replace(/\\r\\n/g, "\\n");
        return new Message(content);
    }

    const key = matched[1];
    const content = matched[2].replace(/\\r\\n/g, "\\n");
    return new Message(content, key);
}
