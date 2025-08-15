#!/usr/bin/env python3
"""
Python Documentation Agent - Comprehensive Documentation Generator
==================================================================

Based on the code-documenter pattern, adapted specifically for Python projects.
Generates and maintains documentation for Python codebases including:
- API documentation
- Docstrings
- README files
- Type hints documentation
- Usage examples
"""

AGENT_CONFIG = """---
name: python-doc-agent
description: Create comprehensive documentation for Python projects including API docs, docstrings, type hints, and usage examples. Specializes in Python-specific documentation patterns and best practices. Use PROACTIVELY for Python documentation tasks.
model: sonnet
---

You are a Python documentation specialist focused on creating clear, comprehensive, and Pythonic documentation for Python projects.

## Python Documentation Expertise
- Python docstrings (Google, NumPy, Sphinx styles)
- Type hints and typing module documentation
- API documentation with Sphinx and MkDocs
- FastAPI/Flask automatic API documentation
- Jupyter notebook documentation and examples
- Package structure and module documentation
- pytest examples and test documentation
- Python-specific README templates

## Python Documentation Standards
1. PEP 257 compliant docstrings with consistent style
2. Type hints with proper typing annotations
3. Working code examples with doctest compatibility
4. Clear parameter and return value documentation
5. Exception documentation with raise conditions
6. Class and method relationship documentation
7. Module-level documentation with usage examples
8. Integration with Python documentation tools

## Python-Specific Content
- `__init__.py` documentation for packages
- Setup.py and pyproject.toml documentation
- Requirements and dependency documentation
- Virtual environment setup instructions
- Python version compatibility notes
- Import structure and namespace documentation
- Decorator and context manager documentation
- Generator and async function documentation

## Documentation Generation Tools
- Sphinx with autodoc for automatic generation
- MkDocs with mkdocstrings plugin
- pydoc for built-in documentation
- pdoc3 for simplified API docs
- Doctest for executable documentation
- Type stub files (.pyi) generation
- API schema generation (OpenAPI/JSON Schema)
- Jupyter notebook to documentation conversion

## Code Analysis Integration
- pylint and flake8 docstring checking
- mypy for type hint validation
- pydocstyle for docstring style enforcement
- Coverage reports with documentation gaps
- Complexity metrics and documentation needs
- Import graph visualization
- Call graph documentation
- Performance profiling documentation

Create Python documentation that follows community best practices while being accessible to both beginners and advanced users. Ensure all code examples are executable and maintain consistency with PEP standards.
"""

import os
import ast
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import inspect
import importlib.util

class PythonDocumentationAgent:
    """
    Agent for generating comprehensive Python documentation.
    
    This agent analyzes Python code and generates various forms of documentation
    including docstrings, API docs, README files, and usage examples.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the Python Documentation Agent.
        
        Args:
            project_path: Root path of the Python project to document
        """
        self.project_path = Path(project_path)
        self.modules = {}
        self.documentation = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyze the entire Python project structure.
        
        Returns:
            Dictionary containing project analysis including:
            - Module structure
            - Class hierarchy
            - Function inventory
            - Import dependencies
            - Documentation coverage
        """
        analysis = {
            "modules": {},
            "classes": {},
            "functions": {},
            "documentation_coverage": {},
            "import_graph": {}
        }
        
        # Walk through Python files
        for py_file in self.project_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            module_info = self._analyze_module(py_file)
            analysis["modules"][str(py_file)] = module_info
            
        return analysis
    
    def _analyze_module(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single Python module.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Module analysis including classes, functions, and docstrings
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"error": "Failed to parse file"}
            
        module_info = {
            "docstring": ast.get_docstring(tree),
            "classes": [],
            "functions": [],
            "imports": [],
            "type_hints": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [],
                    "base_classes": [base.id for base in node.bases if hasattr(base, 'id')]
                }
                module_info["classes"].append(class_info)
                
            elif isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "parameters": [arg.arg for arg in node.args.args],
                    "return_annotation": None
                }
                if node.returns:
                    func_info["return_annotation"] = ast.unparse(node.returns)
                module_info["functions"].append(func_info)
                
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                module_info["imports"].append(ast.unparse(node))
                
        return module_info
    
    def generate_api_documentation(self) -> str:
        """
        Generate comprehensive API documentation for the project.
        
        Returns:
            Markdown-formatted API documentation
        """
        doc = ["# API Documentation\n"]
        doc.append(f"Generated for: {self.project_path.name}\n")
        
        analysis = self.analyze_project()
        
        # Document each module
        for module_path, module_info in analysis["modules"].items():
            doc.append(f"\n## Module: {module_path}\n")
            
            if module_info.get("docstring"):
                doc.append(f"{module_info['docstring']}\n")
            
            # Document classes
            if module_info.get("classes"):
                doc.append("\n### Classes\n")
                for class_info in module_info["classes"]:
                    doc.append(f"\n#### {class_info['name']}\n")
                    if class_info.get("docstring"):
                        doc.append(f"{class_info['docstring']}\n")
                    if class_info.get("base_classes"):
                        doc.append(f"**Inherits from:** {', '.join(class_info['base_classes'])}\n")
            
            # Document functions
            if module_info.get("functions"):
                doc.append("\n### Functions\n")
                for func_info in module_info["functions"]:
                    doc.append(f"\n#### {func_info['name']}\n")
                    if func_info.get("docstring"):
                        doc.append(f"{func_info['docstring']}\n")
                    if func_info.get("parameters"):
                        doc.append(f"**Parameters:** {', '.join(func_info['parameters'])}\n")
                    if func_info.get("return_annotation"):
                        doc.append(f"**Returns:** {func_info['return_annotation']}\n")
        
        return "\n".join(doc)
    
    def generate_docstring_template(self, function_node: ast.FunctionDef, style: str = "google") -> str:
        """
        Generate a docstring template for a function.
        
        Args:
            function_node: AST node representing the function
            style: Docstring style - "google", "numpy", or "sphinx"
            
        Returns:
            Formatted docstring template
        """
        if style == "google":
            return self._google_style_docstring(function_node)
        elif style == "numpy":
            return self._numpy_style_docstring(function_node)
        elif style == "sphinx":
            return self._sphinx_style_docstring(function_node)
        else:
            raise ValueError(f"Unknown docstring style: {style}")
    
    def _google_style_docstring(self, node: ast.FunctionDef) -> str:
        """Generate Google-style docstring."""
        lines = ['"""Brief description of function.']
        lines.append("")
        
        if node.args.args:
            lines.append("Args:")
            for arg in node.args.args:
                if arg.arg != 'self':
                    type_hint = ""
                    if arg.annotation:
                        type_hint = f" ({ast.unparse(arg.annotation)})"
                    lines.append(f"    {arg.arg}{type_hint}: Description of {arg.arg}.")
            lines.append("")
        
        if node.returns:
            lines.append("Returns:")
            lines.append(f"    {ast.unparse(node.returns)}: Description of return value.")
            lines.append("")
            
        lines.append('"""')
        return "\n".join(lines)
    
    def check_documentation_coverage(self) -> Dict[str, float]:
        """
        Check documentation coverage for the project.
        
        Returns:
            Dictionary with coverage percentages for different components
        """
        analysis = self.analyze_project()
        coverage = {
            "modules": 0,
            "classes": 0,
            "functions": 0,
            "overall": 0
        }
        
        # Calculate coverage for each component
        total_modules = len(analysis["modules"])
        documented_modules = sum(1 for m in analysis["modules"].values() if m.get("docstring"))
        
        total_classes = sum(len(m.get("classes", [])) for m in analysis["modules"].values())
        documented_classes = sum(
            sum(1 for c in m.get("classes", []) if c.get("docstring")) 
            for m in analysis["modules"].values()
        )
        
        total_functions = sum(len(m.get("functions", [])) for m in analysis["modules"].values())
        documented_functions = sum(
            sum(1 for f in m.get("functions", []) if f.get("docstring")) 
            for m in analysis["modules"].values()
        )
        
        if total_modules > 0:
            coverage["modules"] = (documented_modules / total_modules) * 100
        if total_classes > 0:
            coverage["classes"] = (documented_classes / total_classes) * 100
        if total_functions > 0:
            coverage["functions"] = (documented_functions / total_functions) * 100
            
        total_items = total_modules + total_classes + total_functions
        documented_items = documented_modules + documented_classes + documented_functions
        if total_items > 0:
            coverage["overall"] = (documented_items / total_items) * 100
            
        return coverage
    
    def generate_readme_template(self) -> str:
        """
        Generate a README.md template for the Python project.
        
        Returns:
            Markdown-formatted README template
        """
        project_name = self.project_path.name
        
        readme = f"""# {project_name}

Brief description of what this project does.

## Installation

```bash
pip install {project_name}
```

## Quick Start

```python
import {project_name}

# Example usage
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- Python 3.8+
- See requirements.txt for package dependencies

## Documentation

Full documentation is available at [docs link].

## Development

```bash
# Clone the repository
git clone https://github.com/username/{project_name}.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linters
flake8 {project_name}
mypy {project_name}
```

## API Reference

See the [API documentation](./docs/api.md) for detailed information.

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
"""
        return readme


# Example usage
if __name__ == "__main__":
    # Initialize agent for current project
    agent = PythonDocumentationAgent(".")
    
    # Analyze project
    print("Analyzing project...")
    analysis = agent.analyze_project()
    
    # Check documentation coverage
    print("\nDocumentation Coverage:")
    coverage = agent.check_documentation_coverage()
    for component, percent in coverage.items():
        print(f"  {component}: {percent:.1f}%")
    
    # Generate API documentation
    print("\nGenerating API documentation...")
    api_docs = agent.generate_api_documentation()
    with open("API_GENERATED.md", "w") as f:
        f.write(api_docs)
    print("API documentation saved to API_GENERATED.md")
    
    # Generate README template
    print("\nGenerating README template...")
    readme = agent.generate_readme_template()
    print(readme[:500] + "...")