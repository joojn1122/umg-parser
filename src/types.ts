export interface ParsedWidget {
    props: Record<string, string>;
    children: ParsedWidget[];
}

export interface OverrideScreen {
    name: string;
    path: string;
}

export interface UMGParserConfig {
    useTranslated?: boolean;
    rootPath?: string;
    langPath?: string;
    overrideScreens?: OverrideScreen[];
}
