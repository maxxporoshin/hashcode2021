import * as solvers from './solvers'
import { runDataSets } from "./runner"

const DATASETS = process.argv.slice(2)
if (DATASETS.length === 0) {
    throw new Error('No data sets specified')
}

runDataSets(DATASETS, solvers.simple)
