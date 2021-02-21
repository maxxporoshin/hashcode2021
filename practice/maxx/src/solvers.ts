import * as _ from 'lodash'
import { pick } from 'lodash';
import { ParsedInput, Pizza, ReadonlyParsedInput, Solution, TeamSize } from "./io";
import { calculateScore } from './scoring';
import { setDiff } from './util';

type Solver = (data: ReadonlyParsedInput, onSolution: (solution: Solution) => void) => void

interface Team {
    size: TeamSize
    pizzas: number[]
    ingredients: Set<string>
}

const simple: Solver = (data, onSolution) => {
    const teamsCountBySize = {...data.teamsCountBySize}
    const pizzas = data.pizzas
    let pizzasRequiredToFillTeams = 0
    const teams: Team[] = []

    const pickTeam = (pizzaIndex: number) => {
        let best: {team: Team, diff: string[]} | undefined
        const pizza = pizzas[pizzaIndex]
        for (const team of teams) {
            if (team.pizzas.length >= team.size) {
                continue
            }
            const diff = setDiff(team.ingredients, pizza.ingredients)
            const isBetter = !best || diff.length > best.diff.length
            if (diff.length > 0 && isBetter) {
                best = {team, diff}
           }
        }
        return best
    }
    const addToTeam = (pizzaIndex: number, team: Team, diff: string[] = setDiff(team.ingredients, pizzas[pizzaIndex].ingredients)) => {
        for (const ingredient of diff) {
            team.ingredients.add(ingredient)
        }
        team.pizzas.push(pizzaIndex)
        pizzasRequiredToFillTeams--
    }
    const createTeam = (teamSize: TeamSize, pizzaIndex: number) => {
        const pizza = pizzas[pizzaIndex]
        const team: Team = {
            ingredients: new Set(pizza.ingredients),
            pizzas: [pizzaIndex],
            size: teamSize
        }
        teamsCountBySize[teamSize]--
        pizzasRequiredToFillTeams += teamSize - 1
        return team
    }
    const pickTeamSize = (pizzaIndex: number, sizes = [4, 3, 2]) => {
        const pizzasLeft = pizzas.length - pizzaIndex
        const maxTeamSize = Math.min(pizzasLeft - pizzasRequiredToFillTeams, 4)
        for (let size = sizes.shift(); size !== undefined; size = sizes.shift()) {
            if (teamsCountBySize[size] > 0) {
                return size
            }
        }
        return -1
    }
    const tryToCreateTeam = (pizzaIndex: number) => {
        let teamSize = pickTeamSize(pizzaIndex)
        return teamSize > -1 ? createTeam(teamSize, pizzaIndex) : undefined
    }

    for (let i = 0; i < pizzas.length; i++) {
        const teamWithDiff = pickTeam(i)
        if (teamWithDiff) {
            addToTeam(i, teamWithDiff.team, teamWithDiff.diff)
        } else {
            const team = tryToCreateTeam(i)
            if (team) {
                teams.push(team)
            } else {
                const teamToFill = teams.find(team => team.pizzas.length < team.size)
                if (!teamToFill) {
                    break
                }
                addToTeam(i, teamToFill)
            }
        }
    }

    onSolution(teams.map(team => [team.size, ...team.pizzas]))
} 

const random: Solver = (data, onSolution) => {
    const teamsCountBySize = {...data.teamsCountBySize}
    const teamSizesKeys = [2, 3, 4]
    const fullTeams = []
    const usedPizzas = new Array(data.pizzas.length).fill(false)

    const pickTeamSize = () => {
        let i = _.random(0, teamSizesKeys.length)
        while (teamSizesKeys.length > 0) {
            if (teamsCountBySize[teamSizesKeys[i]] > 0) {
                teamsCountBySize[teamSizesKeys[i]]--
                return teamSizesKeys[i]
            }
            teamSizesKeys.splice(i, 1)
            i = _.random(0, teamSizesKeys.length - 1)
        }
        return -1
    }

    let team: Team | null = null
    while (true) {
        if (!team) {
            // Create team
            const teamSize = pickTeamSize()
            if (teamSize === -1) {
                break
            }
            team = {
                ingredients: new Set(),
                pizzas: [],
                size: teamSize
            }
        }

        // Pick pizza index
        let i = _.random(0, data.pizzas.length - 1)
        let iterations = 1
        while (usedPizzas[i] && iterations < usedPizzas.length) {
            i = _.random(0, data.pizzas.length - 1)
            iterations++
        }
        if (usedPizzas[i]) {
            const notUsedPizzas = data.pizzas.map((pizza, index) => ({pizza, index})).filter(({index}) => !usedPizzas[index])
            if (notUsedPizzas.length === 0) {
                break
            }
            const index = _.random(0, notUsedPizzas.length - 1)
            i = notUsedPizzas[index].index
        }

        // Add pizza to the team
        const pizza = data.pizzas[i]
        team.pizzas.push(i)
        for (const e of pizza.ingredients) {
            team.ingredients.add(e)
        }
        if (team.pizzas.length === team.size) {
            fullTeams.push(team)
            team = null
        }
        usedPizzas[i] = true
    }

    onSolution(fullTeams.map(team => [team.size, ...team.pizzas]))
}

const makeIterativeSolver = (solver: Solver): Solver => (data, onSolution) => {
    let best: {solution: Solution, score: number} | null = null

    const handleSolution = (solution: Solution) => {
        const score = calculateScore(data, solution)
        if (!best || score > best.score) {
            best = {solution, score}
            onSolution(solution)
        }
        process.nextTick(() => solver(data, handleSolution))
    }

    solver(data, handleSolution)
}

export {simple, random, makeIterativeSolver}
export type {Solver}
