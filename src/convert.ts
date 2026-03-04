import { ParsedWidget } from "./types";

export function sortVariables(
    variableContents: Map<string, string>,
    variableDependencies: Map<string, string[]>
): Map<string, string> {
    const adjacencyList = new Map<string, string[]>();
    const inDegree = new Map<string, number>();

    for (const v of variableContents.keys()) {
        inDegree.set(v, 0);
    }

    for (const [v, deps] of variableDependencies) {
        for (const dep of deps) {
            if (!adjacencyList.has(dep)) adjacencyList.set(dep, []);
            adjacencyList.get(dep)!.push(v);
            inDegree.set(v, (inDegree.get(v) ?? 0) + 1);
        }
    }

    const queue: string[] = [];
    for (const [v, degree] of inDegree) {
        if (degree === 0) queue.push(v);
    }

    const sorted: string[] = [];
    while (queue.length > 0) {
        const current = queue.shift()!;
        sorted.push(current);

        for (const neighbor of adjacencyList.get(current) ?? []) {
            const newDeg = inDegree.get(neighbor)! - 1;
            inDegree.set(neighbor, newDeg);
            if (newDeg === 0) queue.push(neighbor);
        }
    }

    if (sorted.length !== variableContents.size) {
        throw new Error("Cycle detected in dependencies, sorting not possible.");
    }

    const result = new Map<string, string>();
    for (const v of sorted) {
        result.set(v, variableContents.get(v)!);
    }
    return result;
}

export function parseProps(content: string, indent: number): Record<string, string> {
    const props: Record<string, string> = {};
    const indentStr = " ".repeat(indent);

    for (const line of content.split("\n")) {
        if (!line.startsWith(indentStr) || line.length <= indent) continue;
        if (line[indent] === " ") continue;

        const part = line.substring(indent);
        if (part.startsWith("Begin Object") || part.startsWith("End Object")) continue;

        const eqPos = part.indexOf("=");
        if (eqPos !== -1) {
            const key = part.substring(0, eqPos).trim();
            const value = part.substring(eqPos + 1).trim();
            props[key] = value;
        }
    }

    return props;
}

export function parseHeaderProps(headerLine: string): Record<string, string> {
    const props: Record<string, string> = {};
    const start = headerLine.indexOf("Begin Object ");
    if (start === -1) return props;

    const rest = headerLine.substring(start + "Begin Object ".length);
    let idx = 0;

    while (idx < rest.length) {
        while (idx < rest.length && rest[idx] === " ") idx++;
        if (idx >= rest.length) break;

        const eqPos = rest.indexOf("=", idx);
        if (eqPos === -1) break;

        const key = rest.substring(idx, eqPos).trim();
        idx = eqPos + 1;

        if (idx < rest.length && rest[idx] === '"') {
            idx++;
            const endQuote = rest.indexOf('"', idx);
            if (endQuote === -1) {
                props[key] = `"${rest.substring(idx)}"`;
                idx = rest.length;
            } else {
                props[key] = `"${rest.substring(idx, endQuote)}"`;
                idx = endQuote + 1;
            }
        } else {
            const spacePos = rest.indexOf(" ", idx);
            if (spacePos === -1) {
                props[key] = rest.substring(idx);
                idx = rest.length;
            } else {
                props[key] = rest.substring(idx, spacePos);
                idx = spacePos;
            }
        }
    }

    return props;
}

function findMatchingEnd(lines: string[], startIdx: number, indent: number): number {
    const indentStr = " ".repeat(indent);
    let depth = 0;

    for (let idx = startIdx; idx < lines.length; idx++) {
        const line = lines[idx];
        if (line.startsWith(indentStr) && line.length > indent && line[indent] !== " ") {
            const stripped = line.substring(indent);
            if (stripped.startsWith("Begin Object")) {
                depth++;
            } else if (stripped.startsWith("End Object")) {
                depth--;
                if (depth === 0) return idx;
            }
        }
    }

    return -1;
}

export function parseWidgets(content: string, indent: number): ParsedWidget[] {
    const objects: ParsedWidget[] = [];
    const lines = content.split("\n");
    const indentStr = " ".repeat(indent);

    let idx = 0;
    while (idx < lines.length) {
        const line = lines[idx];

        if (
            line.startsWith(indentStr) &&
            line.length > indent &&
            line[indent] !== " " &&
            line.substring(indent).startsWith("Begin Object")
        ) {
            const endIdx = findMatchingEnd(lines, idx, indent);
            if (endIdx === -1) {
                idx++;
                continue;
            }

            const blockLines = lines.slice(idx, endIdx + 1);
            const blockContent = blockLines.join("\n");

            const props = parseHeaderProps(line);
            const children = parseWidgets(blockContent, indent + 3);

            Object.assign(props, parseProps(blockContent, indent + 3));

            objects.push({ props, children });
            idx = endIdx + 1;
        } else {
            idx++;
        }
    }

    return objects;
}
