import { Delivery, ParsedInput, ReadonlyParsedInput, Solution } from "./io";

function calculateScore(input: ReadonlyParsedInput, solution: Solution): number {
    return solution.reduce((score, delivery) => {
        return score + calculateDeliveryScore(input, delivery)
    }, 0)    
}

function calculateDeliveryScore(input: ReadonlyParsedInput, delivery: Delivery): number {
    const ingredients = delivery.slice(1).reduce((ingredients, pizzaIndex) => {
        input.pizzas[pizzaIndex].ingredients.forEach(e => ingredients.add(e))
        return ingredients
    }, new Set())
    return ingredients.size ** 2
}

export {calculateScore, calculateDeliveryScore}
