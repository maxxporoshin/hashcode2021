/**
 * How `b` is different from `a`
 */
function setDiff<T>(a: Set<T>, b: Set<T>): T[] {
    const diff = []
    for (const e of b) {
        if (!a.has(e)) {
            diff.push(e)
        }
    }
    return diff
}

export {setDiff}
