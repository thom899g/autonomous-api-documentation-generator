from dataclasses import dataclass
from typing import List, Optional

@dataclass
class APIDocumentationEntry:
    """
    Represents an entry in API documentation.
    
    Contains metadata about a function including its parameters,
    docstring, and imported modules for context.
    """

    module_name: str
    function_name: str
    parameters: List[str]
    docstring: Optional[str] = None
    imported_modules: List[str] = None

    def __repr__(self):
        return f"API documentation entry for {self.module_name}.{self.function_name}"