from langchain_core.tools import tool
from io import StringIO
import sys
import math
import json
import re
import datetime as dt


@tool
def run_python_code(code: str) -> str:
    """Executes Python code and returns real output. Use for any coding task, algorithm, data processing."""
    capture = StringIO()
    sys.stdout = capture
    try:
        safe_globals = {
            "__builtins__": {
                "print": print, "range": range, "len": len,
                "int": int, "float": float, "str": str, "list": list,
                "dict": dict, "set": set, "tuple": tuple, "bool": bool,
                "sum": sum, "min": min, "max": max, "abs": abs,
                "round": round, "enumerate": enumerate, "zip": zip,
                "sorted": sorted, "reversed": reversed, "map": map,
                "filter": filter, "isinstance": isinstance, "type": type,
                "input": lambda _: "",
                "ValueError": ValueError, "TypeError": TypeError,
                "KeyError": KeyError, "IndexError": IndexError,
                "AttributeError": AttributeError, "Exception": Exception,
                "BaseException": BaseException, "RuntimeError": RuntimeError,
                "StopIteration": StopIteration, "NameError": NameError,
                "ZeroDivisionError": ZeroDivisionError,
                "NotImplementedError": NotImplementedError,
            },
            "math": math, "json": json, "re": re, "datetime": dt,
        }
        exec(code, safe_globals)
        output = capture.getvalue()
        return f"Output:\n{output}" if output.strip() else "Code executed successfully with no output."
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        sys.stdout = sys.__stdout__