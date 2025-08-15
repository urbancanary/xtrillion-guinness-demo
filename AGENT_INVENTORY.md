# Sub-Agent Inventory for Google Analysis 10 Project

## Overview
This document lists all the sub-agents currently available in the GA10 project, their purposes, and usage examples.

## 1. Python Documentation Agent (`python_doc_agent.py`)
**Purpose**: Create comprehensive documentation for Python projects including API docs, docstrings, type hints, and usage examples.

**Key Features**:
- AST-based code analysis
- Docstring coverage checking (Google, NumPy, Sphinx styles)
- Type hint documentation
- API documentation generation
- README template generation
- Import graph analysis

**Usage**:
```python
agent = PythonDocumentationAgent("/path/to/project")
coverage = agent.check_documentation_coverage()
api_docs = agent.generate_api_documentation()
```

## 2. Documentation Maintenance Agent (`doc_maintenance_agent.py`)
**Purpose**: Automated monitoring and updating of API documentation, ensuring examples work and docs stay current.

**Key Features**:
- API health checking
- Extract and validate API examples from docs
- Performance benchmarking
- Auto-fix capability
- Scheduled monitoring
- Cross-file consistency checking

**Usage**:
```bash
python3 doc_maintenance_agent.py --check     # Check only
python3 doc_maintenance_agent.py --update    # Check and auto-fix
python3 doc_maintenance_agent.py --schedule  # Set up automated runs
```

## 3. GA10 Documentation Agent (`ga10_doc_agent.py`)
**Purpose**: Project-specific documentation validation for the GA10 bond analysis API.

**Key Features**:
- Bond API request validation
- Missing price field detection
- Deprecated field warnings
- Portfolio format validation
- API endpoint reference checking
- Live API example testing

**Usage**:
```python
agent = GA10DocumentationAgent()
result = agent.checker.check_file('API_SPECIFICATION.md')
```

## 4. Code Duplication Agent (`code_duplication_agent.py`)
**Purpose**: Identify and report duplicate code patterns across the codebase.

**Key Features**:
- AST-based duplicate detection
- Cross-file analysis
- Refactoring suggestions
- Duplicate metrics reporting
- Function similarity scoring

**Usage**:
```bash
./code_duplication_agent.py --threshold 0.8
```

## 5. Orphaned Code Agent (`orphaned_code_agent.py`)
**Purpose**: Find unused functions, classes, and imports that can be safely removed.

**Key Features**:
- Dead code detection
- Unused import analysis
- Unreferenced function finding
- Cross-file usage tracking
- Safe removal suggestions

**Usage**:
```bash
./orphaned_code_agent.py --scan-all
```

## 6. Claude Deployment Agent (`claude_deployment_agent.py`)
**Purpose**: Automate deployment workflows and environment management.

**Key Features**:
- Multi-environment deployment
- Pre-deployment validation
- Rollback capabilities
- Health check integration
- Deployment status tracking

**Usage**:
```python
agent = ClaudeDeploymentAgent()
agent.deploy_to_environment('production')
```

## 7. Universal Documentation Checker (`universal_doc_checker.py`)
**Purpose**: Language-agnostic documentation validation supporting multiple formats.

**Key Features**:
- Multi-language syntax validation (JSON, Python, YAML, Bash)
- Link checking (internal and external)
- TODO/FIXME detection
- Code block validation
- Cross-reference checking

**Usage**:
```python
checker = UniversalDocChecker({'check_links': True})
result = checker.check_file('documentation.md')
```

## 8. Agent Framework (`agent_framework_example.py`)
**Purpose**: Base framework for creating custom agents with plugin support.

**Key Features**:
- Base agent class for inheritance
- Plugin system for validators
- Pre/post processor pipelines
- Multi-agent orchestration
- Standardized reporting

**Usage**:
```python
class MyCustomAgent(BaseAgent):
    def run(self, target):
        # Custom implementation
        pass

orchestrator = AgentOrchestrator()
orchestrator.add_agent(MyCustomAgent())
results = orchestrator.run_all('target_file.py')
```

## Agent Pattern Comparison

### Python Sub-Agents (Code-based)
**Advantages**:
- Programmatic and scriptable
- CI/CD integration ready
- Offline operation
- Batch processing
- Structured output
- Customizable validators

**Best for**:
- Automated workflows
- Regular monitoring
- Build pipelines
- Bulk operations

### Claude /agents Command
**Advantages**:
- Natural language interface
- No code required
- Context understanding
- Interactive explanations
- Learning from examples

**Best for**:
- Ad-hoc analysis
- Complex reasoning
- One-off tasks
- Exploratory work

## Example Claude Agent Prompts

```
/agents code-reviewer
Review the bond calculation functions for:
- Performance bottlenecks
- Error handling gaps
- Best practice violations
- Security concerns
```

```
/agents test-generator
Generate comprehensive test cases for the portfolio analysis endpoint including:
- Edge cases
- Invalid inputs
- Performance tests
- Integration tests
```

```
/agents api-migrator
Help migrate API examples from v9 to v10:
- Identify breaking changes
- Update field names
- Modernize patterns
- Validate conversions
```

## Running Multiple Agents

```python
# Using the orchestrator
orchestrator = AgentOrchestrator()
orchestrator.add_agent(PythonDocumentationAgent("."))
orchestrator.add_agent(GA10DocumentationAgent())
orchestrator.add_agent(CodeDuplicationAgent())

# Run all agents on the project
results = orchestrator.run_all()

# Generate combined report
report = orchestrator.generate_report(results)
```

## Future Agent Ideas

1. **Performance Agent** - Track API response times and identify bottlenecks
2. **Security Agent** - Scan for vulnerabilities and insecure patterns
3. **Migration Agent** - Automate code updates between versions
4. **Test Coverage Agent** - Ensure all code paths are tested
5. **Dependency Agent** - Track and update package dependencies