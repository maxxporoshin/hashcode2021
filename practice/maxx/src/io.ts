import * as fs from 'fs'
import * as path from 'path'

interface ParsedInput {
    pizzas: Pizza[]
    teamsCountBySize: Record<TeamSize, number>
}
interface ReadonlyParsedInput {
    readonly pizzas: ReadonlyArray<Readonly<Pizza>>
    readonly teamsCountBySize: Readonly<Record<TeamSize, number>>
}
interface Pizza {
    ingredients: Set<string>
}
type TeamSize = number

type Solution = Delivery[]
type Delivery = [TeamSize, ...number[]]

const INPUT_DIR = path.join(__dirname, '..', '..', 'data')
const OUTPUT_DIR = path.join(__dirname, '..', 'out')

function parseInput(input: string): ParsedInput {
    const lines = input.split('\n').filter(Boolean)
    const [pizzasCount, teams_2, teams_3, teams_4] = lines.shift()!.split(' ').map(e => parseInt(e))
    const teamsCountBySize = {2: teams_2, 3: teams_3, 4: teams_4}
    const pizzas = lines.map(line => ({ingredients: new Set(line.split(' ').slice(1))}))
    return {pizzas, teamsCountBySize}
}

function readAndParseDataSet(prefix: string): ParsedInput {
    const files = fs.readdirSync(INPUT_DIR)
    const filename = files.find(file => file.match(new RegExp('^' + prefix)))
    if (!filename) {
        throw new Error('No file with such prefix')
    }
    const input = fs.readFileSync(path.join(INPUT_DIR, filename), 'utf8')
    return parseInput(input)
}

function writeSolution(name: string, solution: Solution): void {
    const data = solution.length + '\n' + solution.map(delivery => delivery.join(' ')).join('\n')
    fs.writeFileSync(path.join(OUTPUT_DIR, name + '.out'), data, 'utf8')
}

export {readAndParseDataSet, writeSolution}
export type {ParsedInput, ReadonlyParsedInput, Pizza, TeamSize, Solution, Delivery}
