import {readAndParseDataSet, writeSolution} from './io'
import { calculateScore } from './scoring'
import { Solver } from './solvers'
import { fromPairs } from 'lodash'

function runDataSets(datasets: string[], solver: Solver): void {
    for (const dataset of datasets) {
        console.log(`Starting ${dataset} ...`)
        const data = readAndParseDataSet(dataset)
        solver(data, solution => {
            console.log('Evaluating score ...')
            const score = calculateScore(data, solution)
            console.log(`Score for ${dataset} is ${score}`)
            console.log()
            writeSolution(dataset, solution)
        })
    }    
}

export {runDataSets}
