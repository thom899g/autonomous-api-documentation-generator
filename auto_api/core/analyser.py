import os
import ast
import importlib
import logging
import time

from typing import List, Optional
from .models import APIDocumentationEntry

logger = logging.getLogger(__name__)

class CodeAnalyser:
    """
    Analyse codebases to generate API documentation.
    
    This class recursively traverses directories and analyses Python files,
    extracting function signatures and docstrings to create API documentation.
    It handles edge cases such as unparseable files and non-Python scripts.
    """

    def __init__(self, max_retries: int = 3):
        """
        Initialize the CodeAnalyser with retry configuration.

        Args:
            max_retries: Maximum number of retries for file analysis.
        """
        self.max_retries = max_retries
        logging.basicConfig(
            filename='code_analyser.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def analyze_codebase(self, directory_path: str) -> List[APIDocumentationEntry]:
        """
        Analyse a codebase and return API documentation entries.

        Args:
            directory_path: Path to the directory containing the codebase.

        Returns:
            A list of APIDocumentationEntry objects.
        """
        documentation_entries = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                if not file.endswith('.py'):
                    continue
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Introduce a small delay to prevent overwhelming the system
                        time.sleep(1 / self.max_retries)
                        
                        tree = ast.parse(content)
                        module = importlib.import_module(
                            os.path.splitext(file)[0]
                        )
                        
                        functions = self._get_functions(tree)
                        
                        for func in functions:
                            name = func.name
                            params = [arg.arg for arg in func.args.args]
                            docstring = ast.get_docstring(func) or ''
                            
                            imports = self._get_imports(tree)
                            
                            entry = APIDocumentationEntry(
                                module_name=file_path.split('/')[-1],
                                function_name=name,
                                parameters=params,
                                docstring=docstring,
                                imported_modules=imports
                            )
                            documentation_entries.append(entry)
                            
                except Exception as e:
                    logger.error(f"Failed to process {file}: {str(e)}")
                    continue

        return documentation_entries

    def _get_functions(self, tree: ast.AST) -> List[ast.FunctionDef]:
        """
        Extract function definitions from an AST.

        Args:
            tree: The abstract syntax tree to analyse.

        Returns:
            A list of FunctionDef nodes.
        """
        functions = []
        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self.generic_visit(node)
                functions.append(node)
        
        FunctionVisitor().visit(tree)
        return functions

    def _get_imports(self, tree: ast.AST) -> List[str]:
        """
        Extract imports from an AST.

        Args:
            tree: The abstract syntax tree to analyse.

        Returns:
            A list of imported modules.
        """
        imports = []
        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node: ast.Import) -> None:
                for alias in node.names:
                    if alias.asname:
                        imports.append(f"{alias.name} as {alias.asname}")
                    else:
                        imports.append(alias.name)
        
        ImportVisitor().visit(tree)
        return imports

    def __repr__(self):
        return f"CodeAnalyser(max_retries={self.max_retries})"