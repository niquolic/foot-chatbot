"""
Utility functions for creating LangChain-compatible tools
"""

import inspect
import typing
from typing import get_type_hints, Annotated
from langchain_core.tools import tool


def create_string_input_tool(func, tool_name: str = None):
    """
    Creates a string-input wrapper for any multi-parameter function.
    """
    # --- Correction pour les bugs Annotated, ArgsSchema, SkipValidation, Optional, Callable ---
    print("Creating string input tool for function:", func)
    globalns = getattr(func, '__globals__', {})
    import typing
    if 'Annotated' not in globalns:
        globalns['Annotated'] = typing.Annotated
    if 'ArgsSchema' not in globalns:
        class ArgsSchema: pass
        globalns['ArgsSchema'] = ArgsSchema
    if 'SkipValidation' not in globalns:
        class SkipValidation: pass
        globalns['SkipValidation'] = SkipValidation
    if 'Optional' not in globalns:
        globalns['Optional'] = typing.Optional
    if 'Callable' not in globalns:
        globalns['Callable'] = typing.Callable
    if 'Any' not in globalns:
        globalns['Any'] = typing.Any
    if 'Awaitable' not in globalns:
        globalns['Awaitable'] = typing.Awaitable
    # ---------------------------------------------------------------------

    sig = inspect.signature(func)
    type_hints = get_type_hints(func, globalns)
    param_names = list(sig.parameters.keys())
    
    def string_wrapper(input_string: str):
        """Parse string input and call the original function."""
        try:
            # Parse the input string
            values = [v.strip() for v in input_string.split(',')]
            
            if len(values) != len(param_names):
                return {"output": f"Error: Expected {len(param_names)} comma-separated values, got {len(values)}"}
            
            # Convert values to correct types
            parsed_args = []
            for i, value_str in enumerate(values):
                param_name = param_names[i]
                target_type = type_hints.get(param_name, str)
                
                if target_type is float:
                    parsed_args.append(float(value_str))
                elif target_type is int:
                    parsed_args.append(int(float(value_str)))
                else:
                    parsed_args.append(value_str)
            
            # Call original function
            result = func(*parsed_args)
            return {"output": result}
            
        except Exception as e:
            return {"output": f"Error: {str(e)}"}
    
    # Set wrapper properties with improved documentation
    wrapper_name = tool_name or f"{func.__name__}_string"
    string_wrapper.__name__ = wrapper_name
    
    # Create example format
    example_values = []
    for param_name in param_names:
        target_type = type_hints.get(param_name, str)
        if target_type is float:
            example_values.append("0.0")
        elif target_type is int:
            example_values.append("1")
        else:
            example_values.append(f"value_{param_name}")
    
    example_format = ", ".join(example_values)
    
    string_wrapper.__doc__ = f"""Function expects values {', '.join(param_names)} as a string, separated by commas, like this:

{example_format}"""
    
    return tool(string_wrapper)
