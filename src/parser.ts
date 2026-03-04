import { UMGParserConfig, OverrideScreen } from "./types";
import { INDENT, Message, i } from "./constants";
import { parseWidgets } from "./convert";
import { Widget, Slotable, registeredClasses } from "./slots";
import { WidgetSlotPair } from "./widgets";

// Ensure widgets module is loaded (registers classes)
import "./widgets";

export class InvalidConfigError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "InvalidConfigError";
    }
}

function validateOverrideScreens(screens: unknown): OverrideScreen[] {
    if (!Array.isArray(screens)) {
        throw new InvalidConfigError(
            `override_screens must be an array, got ${typeof screens}`,
        );
    }

    for (let idx = 0; idx < screens.length; idx++) {
        const screen = screens[idx];
        if (typeof screen !== "object" || screen === null) {
            throw new InvalidConfigError(
                `override_screens[${idx}] must be an object`,
            );
        }
        if (!("name" in screen)) {
            throw new InvalidConfigError(
                `override_screens[${idx}] is missing required key 'name'`,
            );
        }
        if (!("path" in screen)) {
            throw new InvalidConfigError(
                `override_screens[${idx}] is missing required key 'path'`,
            );
        }
        if (typeof screen.name !== "string") {
            throw new InvalidConfigError(
                `override_screens[${idx}]['name'] must be a string`,
            );
        }
        if (typeof screen.path !== "string") {
            throw new InvalidConfigError(
                `override_screens[${idx}]['path'] must be a string`,
            );
        }
    }

    return screens as OverrideScreen[];
}

export class UMGParser {
    config: Required<UMGParserConfig>;
    private _collectedMessages: Message[] = [];

    constructor(config?: UMGParserConfig) {
        const cfg = config ?? {};
        this.config = {
            useTranslated: cfg.useTranslated ?? false,
            rootPath: cfg.rootPath ?? "",
            langPath: cfg.langPath ?? "",
            overrideScreens: validateOverrideScreens(cfg.overrideScreens ?? []),
        };
    }

    get useTranslated(): boolean {
        return this.config.useTranslated;
    }

    set useTranslated(value: boolean) {
        this.config.useTranslated = value;
    }

    convert(content: string, indent = 0): { exportPath: string; code: string; widgets: Widget[] } {
        this._collectedMessages = [];

        const parsedWidgets = parseWidgets(content, 0);
        const widgets: Widget[] = [];

        for (const widget of parsedWidgets) {
            const className = widget.props.Class ?? "";
            let found = false;

            for (const rclass of registeredClasses) {
                if (rclass.ClassName === className) {
                    widgets.push(new rclass(this, widget));
                    found = true;
                    break;
                }
            }

            if (!found) {
                widgets.push(new Widget(this, widget));
            }
        }

        let root: Widget | null = null;
        let slotRoot: WidgetSlotPair | null = null;

        for (const widget of widgets) {
            if (widget instanceof WidgetSlotPair) {
                slotRoot = widget;
                for (const w of widgets) {
                    if (w.Name === widget.WidgetName && w instanceof Slotable) {
                        root = w;
                        break;
                    }
                }
                break;
            }
        }

        if (root === null) {
            if (widgets.length === 0) {
                throw new Error("Invalid widget blueprint");
            }
            root = widgets[0];
        }

        const exportPath = root.props.ExportPath ?? "";
        let result = `${i(indent)}${root.SimpleName} := ` + root.codify(indent, widgets);

        let variables: Widget[] = [];
        if (root instanceof Slotable) {
            variables = this._getVariables(root);
        }

        let variablesStr = "";
        for (const variable of variables) {
            const varName = variable.varName;
            variablesStr += i(indent) + varName + " := " + variable.codify(indent, widgets) + "\n";
        }

        return { exportPath, code: variablesStr + result, widgets };
    }

    private _getVariables(widget: Slotable): Widget[] {
        const variables: Widget[] = [];

        for (const slot of widget.slots) {
            if (slot.widget instanceof Slotable) {
                variables.push(...this._getVariables(slot.widget));
            }
            if (slot.variable) {
                variables.push(slot.variable);
            }
        }

        return variables;
    }

    generateMessagesModule(widgets: Widget[]): string {
        if (!this.useTranslated) return "";

        let messagesContent = "";
        const seenKeys = new Set<string>();

        for (const widget of widgets) {
            const text = (widget as any).text;
            if (text instanceof Message && text.translationKey && text.includeInTranslationFile) {
                const checkKey = `${text.translationKey}<public><localizes>`;
                if (seenKeys.has(checkKey)) continue;
                seenKeys.add(checkKey);

                let argsStr = text.params.map((arg: string) => `${arg}: `).join(", ");
                if (argsStr) argsStr = `(${argsStr})`;

                messagesContent += `\n${INDENT}${text.translationKey}<public><localizes>${argsStr}: message = "${text.message}"`;
            }
        }

        if (messagesContent) {
            return "Messages<public> := module:" + messagesContent + "\n\n\n";
        }

        return "";
    }

    getNewMessagesForFile(widgets: Widget[], existingContent: string): string {
        if (!this.useTranslated) return "";

        let addedContent = "";

        for (const widget of widgets) {
            const text = (widget as any).text;
            if (text instanceof Message && text.translationKey && text.includeInTranslationFile) {
                const checkKey = `${text.translationKey}<public><localizes>`;
                if (existingContent.includes(checkKey) || addedContent.includes(checkKey)) continue;

                let argsStr = text.params.map((arg: string) => `${arg}: `).join(", ");
                if (argsStr) argsStr = `(${argsStr})`;

                addedContent += `\n${INDENT}${text.translationKey}<public><localizes>${argsStr}: message = "${text.message}"`;
            }
        }

        return addedContent;
    }
}
