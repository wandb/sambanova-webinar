import weave
from weave import Evaluation
from weave import Dataset

import asyncio
import json

#from objects.scorers.winston.response_quality_judge import ResponseQualityScorer


@weave.op()
async def main():
    # Load examples from winston_dataset.jsonl
    with open('winston_dataset.jsonl', 'r') as file:
        examples = [json.loads(line) for line in file][:3]  # Only take the first 3 examples

    # Publish the dataset
    dataset = Dataset(name="Process", rows=examples)
    weave.publish(dataset)

    # Create and run the evaluation
    evaluation = Evaluation(
        name="Process",
        dataset=dataset,
        scorers=[tools_called]
    )

    results = await evaluation.evaluate(function_to_evaluate)
    
    # Publish the evaluation results
    weave.publish(results, name="Winston Evaluation Results")

if __name__ == "__main__":
    asyncio.run(main())