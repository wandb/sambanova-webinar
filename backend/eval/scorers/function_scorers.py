import weave
from typing import Dict, Any, List, Union
from utils.helpers import load_tools
from weave import Scorer
import json


class ResponseTypeScorer(Scorer): 
    @weave.op()
    def score(self, target: object, output: object) -> bool:
        """
        Scores whether Winston responds with the correct response type (question, answer, statement, or plan) based on the input.
        Returns True if correct, False if incorrect.
        """
        if output is None:
            return {'type': None}  # or some other default value
        target_type = target.get('response_type_scorer')
        model_type = output.get('type', None)

        return model_type == target_type

class ToolUsageScorer(Scorer):
    @weave.op()
    def score(self, target: object, output: object) -> Dict[str, Any]:
        """
        Scores whether Winston uses the appropriate tools in its plan and validates tools exist and have correct inputs.
        Returns a dict with:
        - used_expected_tools: bool - True if all required tools are used
        - missing_tools: list - List of expected tools that weren't used
        - additional_tools: list - List of tools used that weren't in expected tools
        - all_tools_valid: bool - True if all tools mentioned exist in available tools
        - invalid_tools: list - List of tools that don't exist
        - valid_inputs: bool - True if all tool inputs match their expected schemas
        - input_errors: list - List of input validation errors found
        """
        # Get expected tools and their inputs from target
        tool_usage = target.get("tool_usage_scorer", [])
        
        # If tool_usage is a list of strings, convert to dict format
        if tool_usage and isinstance(tool_usage[0], str):
            tool_usage = [{"tool": tool, "input": None} for tool in tool_usage]
        
        expected_tools = [tool if isinstance(tool, str) else tool['tool'] for tool in tool_usage]
        expected_inputs = {tool['tool']: tool['input'] for tool in tool_usage}

        # Load available tools and get their schemas
        available_tools = {
            tool['function']['name']: tool['function'].get('parameters', {})
            for tool in load_tools()
        }

        # Handle invalid output format
        if not isinstance(output, dict) or 'content' not in output or not output.get('content', {}).get('steps'):
            return {
                "used_expected_tools": False if expected_tools else True,
                "missing_tools": expected_tools,
                "additional_tools": [],
                "all_tools_valid": True,
                "invalid_tools": [],
                "valid_inputs": True,
                "input_errors": []
            }

        # Extract tools and their inputs from output steps
        steps = output['content']['steps']
        tools_used = []
        input_errors = []
        invalid_tools = []

        for step in steps:
            if not isinstance(step, dict):
                continue

            tool_name = step.get('tool')
            if not tool_name:
                continue

            tools_used.append(tool_name)

            # Validate tool exists
            if tool_name not in available_tools:
                invalid_tools.append(tool_name)
                continue

            # Validate inputs if tool exists
            tool_inputs = step.get('input')
            if tool_inputs is None:
                tool_inputs = {}
            elif isinstance(tool_inputs, str):
                # Handle both string inputs and dynamic references
                if isinstance(tool_inputs, str) and tool_inputs.startswith('{{') and tool_inputs.endswith('}}'):
                    # Valid dynamic reference, skip type validation
                    continue
                # Convert string input to dict with default parameter
                tool_inputs = {"query": tool_inputs}  # Assuming default parameter is "query"

            tool_schema = available_tools[tool_name]
            
            # Validate required parameters
            required_params = tool_schema.get('properties', {})
            for param_name, param_schema in required_params.items():
                if param_name in tool_schema.get('required', []):
                    if param_name not in tool_inputs:
                        input_errors.append(f"{tool_name}: Missing required parameter '{param_name}'")
                        continue

                if param_name in tool_inputs:
                    param_value = tool_inputs[param_name]
                    
                    # Skip validation if the value is a dynamic reference
                    if isinstance(param_value, str) and param_value.startswith('{{') and param_value.endswith('}}'):
                        continue

                    param_type = param_schema.get('type')

                    # Type validation for non-dynamic values
                    if param_type == 'string' and not isinstance(param_value, str):
                        input_errors.append(f"{tool_name}: Parameter '{param_name}' must be a string")
                    elif param_type == 'integer' and not isinstance(param_value, int):
                        input_errors.append(f"{tool_name}: Parameter '{param_name}' must be an integer")
                    elif param_type == 'array' and not isinstance(param_value, list):
                        input_errors.append(f"{tool_name}: Parameter '{param_name}' must be an array")
                    elif param_type == 'object' and not isinstance(param_value, dict):
                        input_errors.append(f"{tool_name}: Parameter '{param_name}' must be an object")

                    # Enum validation for non-dynamic values
                    if 'enum' in param_schema and param_value not in param_schema['enum']:
                        input_errors.append(f"{tool_name}: Parameter '{param_name}' must be one of {param_schema['enum']}")

        # Calculate missing and additional tools
        missing_tools = [tool for tool in expected_tools if tool not in tools_used]
        additional_tools = [tool for tool in tools_used if tool not in expected_tools]

        return {
            "used_expected_tools": len(missing_tools) == 0,
            "missing_tools": missing_tools,
            "additional_tools": additional_tools,
            "all_tools_valid": len(invalid_tools) == 0,
            "invalid_tools": invalid_tools,
            "valid_inputs": len(input_errors) == 0,
            "input_errors": input_errors
        }

class ResponseStructureScorer(Scorer):
    @weave.op()
    def score(self, output: object) -> Dict[str, Any]:
        """
        Scores whether Winston's response has the correct structure based on its type.
        Returns a dict with:
        - valid_structure: bool - True if the response has all required properties
        - missing_properties: list - List of required properties that are missing
        - invalid_properties: list - List of properties that have incorrect types
        """
        if not isinstance(output, dict) or 'type' not in output or 'content' not in output:
            return {
                "valid_structure": False,
                "missing_properties": ["type", "content"],
                "invalid_properties": []
            }

        response_type = output['type']
        content = output.get('content', {})
        missing_props = []
        invalid_props = []
        
        # Define required properties and their types for each response type
        type_requirements = {
            'answer': {
                'message': str,
                'reason': str
            },
            'question': {
                'message': str,
                'reason': str
            },
            'plan': {
                'steps': list
            }
        }

        if response_type not in type_requirements:
            return {
                "valid_structure": False,
                "missing_properties": [],
                "invalid_properties": ["type"]
            }

        # Check required properties and their types
        for prop, expected_type in type_requirements[response_type].items():
            if prop not in content:
                missing_props.append(prop)
            elif not isinstance(content[prop], expected_type):
                invalid_props.append(prop)

        # Additional validation for plan type
        if response_type == 'plan' and 'steps' in content:
            for i, step in enumerate(content['steps']):
                required_step_props = {
                    'step': int,
                    'tool': str,
                    'input': (str, dict, type(None)),  # input can be string, object, or null
                    'reason': str,
                    'required_for_response': bool
                }
                
                for prop, expected_type in required_step_props.items():
                    if prop not in step:
                        missing_props.append(f"steps[{i}].{prop}")
                    elif prop == 'input':
                        if not (isinstance(step[prop], str) or isinstance(step[prop], dict) or step[prop] is None):
                            invalid_props.append(f"steps[{i}].{prop}")
                    elif not isinstance(step[prop], expected_type):
                        invalid_props.append(f"steps[{i}].{prop}")

        return {
            "valid_structure": len(missing_props) == 0 and len(invalid_props) == 0,
            "missing_properties": missing_props,
            "invalid_properties": invalid_props
        }