import json
import litellm
from weave import Scorer
import weave
from typing import Dict, Any

class ResponseQualityScorer(Scorer):
    """Evaluates the quality of an AI assistant's response using an LLM.
    Different response types (statement, answer, question, plan) are evaluated 
    using type-specific criteria.
    """

    @weave.op
    def _build_prompt(self, user_input: str, output: Dict[str, Any]) -> str:
        """Builds the evaluation prompt based on response type."""
        if output is None:
            return None
        
        response_type = output.get('type', '')
        prompt_template = {
        'statement': """
1. Empathy: Does it show appropriate understanding and acknowledgment?
2. Relevance: Is the statement directly related to the user's input?
3. Tone: Is the tone appropriate for the context?
4. Natural Flow: Does it sound natural and conversational?""",
        
        'answer': """
1. Accuracy: Is the answer factually correct?
2. Completeness: Does it fully address the question?
3. Explanation Quality: Is the explanation clear and well-supported?
4. Conciseness: Is it appropriately detailed without being verbose?""",
        
        'question': """
1. Relevance: Is the clarifying question directly related to the user's request?
2. Necessity: Is the question truly needed to better understand the user's needs?
3. Clarity: Is the question clear and easy to understand?
4. Purpose: Is the reason for asking the question well justified?""",
        
        'plan': """
1. Completeness: Does it include all necessary steps?
2. Tool Usage: Are the selected tools appropriate?
3. Step Sequence: Is the order of steps logical?
4. Efficiency: Is it the most efficient approach?"""
        }

        criteria = prompt_template.get(response_type, "")
        
        return f"""Evaluate this AI assistant's {response_type} response to the user's request.
Consider these specific criteria for a {response_type} response:
```
{criteria}
```

User's request: {user_input}
Assistant's response: {json.dumps(output, indent=2)}

Provide your evaluation in JSON format:
{{
    "score": <float between 0.0 and 1.0>,
    "reasoning": <string explaining the score>,
    "strengths": [<list of strengths>],
    "weaknesses": [<list of weaknesses>]
}}"""

    @weave.op
    def score(self, output: Dict[str, Any], input: str) -> Dict[str, Any]:
        """
        Score the quality of the assistant's response.
        
        Args:
            output: The assistant's response dictionary
            input: The user's input text
        
        Returns:
            Dictionary containing quality metrics including score, reasoning, 
            strengths and weaknesses
        """
        prompt = self._build_prompt(input, output)

        if not output.get('type') in prompt:
            return {
                'quality_score': 0.0,
                'reasoning': f'Invalid response type: {output.get("type")}',
                'strengths': [],
                'weaknesses': ['Invalid response type']
            }

        try:
            response = litellm.completion(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            
            return {
                'quality_score': float(evaluation.get('score', 0.0)),
                'reasoning': evaluation.get('reasoning', ''),
                'strengths': evaluation.get('strengths', []),
                'weaknesses': evaluation.get('weaknesses', [])
            }
            
        except Exception as e:
            return {
                'quality_score': 0.0,
                'reasoning': f'Error during evaluation: {str(e)}',
                'strengths': [],
                'weaknesses': ['Evaluation failed']
            }

    def summarize(self, score_rows: list) -> dict:
        """
        Summarize scores across all evaluated responses.
        
        Args:
            score_rows: List of score dictionaries from each evaluation
            
        Returns:
            Dictionary with aggregated metrics
        """
        if not score_rows:
            return {
                'mean_quality_score': 0.0,
                'total_strengths': 0,
                'total_weaknesses': 0
            }
            
        quality_scores = [row['quality_score'] for row in score_rows]
        total_strengths = sum(len(row['strengths']) for row in score_rows)
        total_weaknesses = sum(len(row['weaknesses']) for row in score_rows)
        
        return {
            'mean_quality_score': sum(quality_scores) / len(quality_scores),
            'total_strengths': total_strengths,
            'total_weaknesses': total_weaknesses
        } 