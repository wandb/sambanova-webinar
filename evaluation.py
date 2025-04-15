import weave
from weave import Evaluation
from weave import Dataset
from objects.models.winston import Winston
import asyncio
import json
import argparse
from config import WEAVE_PROJECT
from objects.scorers.winston.function_scorers import (
    ResponseTypeScorer,
    ToolUsageScorer,
    ResponseStructureScorer
)
#from objects.scorers.winston.response_quality_judge import ResponseQualityScorer
#from utils.helpers import load_tools, load_env_vars
from typing import Any, List, Dict

def parse_args():
    parser = argparse.ArgumentParser(description='Run Winston evaluation')
    parser.add_argument('--trials', type=int, default=1,
                       help='Number of trials to run (default: 1)')
    parser.add_argument('--first-n', type=int,
                       help='Only evaluate on first N examples')
    parser.add_argument('--ids', type=str, nargs='+',
                       help='Only evaluate on examples with these IDs')
    return parser.parse_args()

def filter_dataset(examples: List[Dict], first_n: int = None, ids: List[str] = None) -> List[Dict]:
    """Filter dataset based on provided criteria."""
    if first_n is not None:
        return examples[:first_n]
    elif ids is not None:
        # Convert ids to integers since they're stored as ints in the dataset
        id_list = [int(id) for id in ids]
        return [ex for ex in examples if ex['id'] in id_list]
    return examples


# Preprocess input for evaluation
@weave.op(name="winston-preprocess_model_input")
def preprocess_model_input(example: Dict[str, str]) -> Dict[str, Any]:
    return {
        'messages': example['input']
    }

async def main():
    # Load environment variables first
    load_env_vars()

    weave.init(f'{WEAVE_PROJECT}')
    
    args = parse_args()
    
    # Get the dataset
    with open('evaluation/eval_dataset.json', 'r') as file:
        examples = json.load(file)
    
    #filtered_examples = filter_dataset(examples, args.first_n, args.ids)
    
    dataset_name = "AgentResponseDataset"
    if args.first_n:
        dataset_name += f"-first{args.first_n}"
    elif args.ids:
        dataset_name += f"-ids{'_'.join(args.ids)}"
    
    dataset = Dataset(name=dataset_name, rows=filtered_examples)

    # instantiate winston with all tools and specified model_id
    # winston = Winston(
    #     model_id=args.model_id
    # )
    #TODO model loading like winston
    # winston.auto_execute = False
    # winston.use_memory = False
    # if args.model_id == "o1-preview" or args.model_id == "o1-mini":
    #     winston.use_system_message = False

    # Initialize the scorers
    quality_scorer = ResponseQualityScorer()
    response_type_scorer = ResponseTypeScorer()
    tool_usage_scorer = ToolUsageScorer()
    response_structure_scorer = ResponseStructureScorer()

    # Create and run the evaluation
    evaluation = Evaluation(
        name="AgentEvaluation",
        dataset=dataset,
        preprocess_model_input=preprocess_model_input,
        scorers=[
            response_type_scorer,
            tool_usage_scorer,
            response_structure_scorer,
            quality_scorer
        ],
        trials=args.trials
    )

    display_name = f"Agent.{args.trials}.{args.model_id}"
    if args.first_n:
        display_name += f".first{args.first_n}"
    elif args.ids:
        display_name += f".ids{'_'.join(args.ids)}"

    await evaluation.evaluate(winston, __weave={"display_name": display_name})

if __name__ == "__main__":
    asyncio.run(main())