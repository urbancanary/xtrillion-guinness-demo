# Agent Development Guide

## Overview

This guide explains how to create reusable autonomous agents for code and documentation maintenance across projects.

## Agent Architecture

### 1. Universal Sub-Agents
These are generic, reusable components that can work across any project:

```python
# Example: universal_doc_checker.py
- Validates markdown syntax
- Checks code blocks in multiple languages
- Finds broken links
- No project-specific logic
```

### 2. Project-Specific Agents
These wrap universal agents and add project-specific logic:

```python
# Example: ga10_doc_agent.py
- Uses universal_doc_checker as a sub-agent
- Adds GA10-specific API validation
- Knows about GA10 endpoints and formats
```

### 3. Agent Framework
The framework provides:
- Base classes for consistency
- Plugin system for extensibility
- Orchestration for running multiple agents
- Standardized reporting

## Creating a New Agent

### Step 1: Define the Purpose
Agents should have a single, clear purpose:
- ✅ "Check documentation for broken examples"
- ✅ "Find duplicate code patterns"
- ❌ "Fix everything" (too broad)

### Step 2: Choose the Right Base

#### For Documentation Checking:
```python
from universal_doc_checker import UniversalDocChecker

class MyDocAgent:
    def __init__(self):
        self.checker = UniversalDocChecker()
```

#### For Custom Logic:
```python
from agent_framework_example import BaseAgent

class MyCustomAgent(BaseAgent):
    def run(self, target):
        # Custom implementation
        pass
```

### Step 3: Implement Core Methods

```python
class MyAgent(BaseAgent):
    def run(self, target: str) -> Dict:
        """Main execution method"""
        self.start()  # Start timing
        
        # Do work
        results = self.process(target)
        
        self.finish()  # End timing
        return results
    
    def validate(self, content: Any) -> Dict:
        """Validation logic"""
        return {
            'issues': [],
            'warnings': []
        }
```

### Step 4: Add CLI Interface

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--fix', action='store_true')
    args = parser.parse_args()
    
    agent = MyAgent()
    if args.check:
        results = agent.run('.')
        print(agent.generate_report(results))

if __name__ == '__main__':
    main()
```

## Agent Patterns

### 1. Check-Only vs Fix Mode
```python
class SafeAgent:
    def __init__(self, fix_mode=False):
        self.fix_mode = fix_mode
    
    def run(self):
        issues = self.find_issues()
        
        if self.fix_mode:
            self.fix_issues(issues)
        else:
            self.report_issues(issues)
```

### 2. Plugin System
```python
class ExtensibleAgent:
    def __init__(self):
        self.validators = {}
    
    def register_validator(self, name, func):
        self.validators[name] = func
    
    def validate(self, content, type):
        if type in self.validators:
            return self.validators[type](content)
```

### 3. Batch Processing
```python
class BatchAgent:
    def process_directory(self, path):
        results = []
        for file in Path(path).rglob('*.py'):
            result = self.process_file(file)
            results.append(result)
        return results
```

## Integration with Agent Scheduler

Add your agent to `agent_scheduler.py`:

```python
self.agents = {
    'my_agent': {
        'name': 'My Custom Agent',
        'script': 'my_agent.py',
        'args': ['--check'],
        'description': 'Does something useful',
        'requires_api': False,
        'frequency': 'weekly'
    }
}
```

## Best Practices

### 1. Error Handling
```python
def safe_process(self, file):
    try:
        return self.process(file)
    except Exception as e:
        self.log(f"Error processing {file}: {e}", "ERROR")
        return {'error': str(e)}
```

### 2. Logging
```python
def log(self, message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{self.name}] [{level}] {message}")
```

### 3. Progress Reporting
```python
def process_many(self, items):
    total = len(items)
    for i, item in enumerate(items):
        self.log(f"Processing {i+1}/{total}: {item}")
        self.process(item)
```

### 4. Configuration
```python
class ConfigurableAgent:
    def __init__(self, config_file=None):
        self.config = self.load_config(config_file)
        
    def load_config(self, file):
        if file and os.path.exists(file):
            with open(file) as f:
                return json.load(f)
        return self.default_config()
```

## Example: Creating a Link Checker Agent

```python
#!/usr/bin/env python3
"""Link Checker Agent - Finds broken links in documentation"""

from universal_doc_checker import UniversalDocChecker
import requests

class LinkCheckerAgent:
    def __init__(self):
        self.checker = UniversalDocChecker({
            'check_links': True
        })
        self.external_links = []
    
    def run(self, directory):
        # Use universal checker for basic validation
        results = self.checker.check_directory(directory)
        
        # Add custom link checking
        for file_result in results['files']:
            self.check_external_links(file_result)
        
        return results
    
    def check_external_links(self, file_result):
        # Custom logic for checking HTTP links
        for link in file_result.get('links', []):
            if link.startswith('http'):
                if not self.is_link_valid(link):
                    file_result['issues'].append({
                        'type': 'broken_external_link',
                        'url': link
                    })
    
    def is_link_valid(self, url):
        try:
            response = requests.head(url, timeout=5)
            return response.status_code < 400
        except:
            return False
```

## Testing Agents

### Unit Tests
```python
import unittest

class TestMyAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MyAgent()
    
    def test_validation(self):
        result = self.agent.validate("test content")
        self.assertEqual(len(result['issues']), 0)
```

### Integration Tests
```python
def test_with_real_files():
    agent = MyAgent()
    results = agent.run('test_data/')
    assert results['files_processed'] > 0
```

## Deployment

### Local Development
```bash
# Run directly
python3 my_agent.py --check

# Run via scheduler
python3 agent_scheduler.py --run my_agent
```

### Production
```bash
# Add to cron for regular runs
0 2 * * * /usr/bin/python3 /path/to/agent_scheduler.py --run-all

# Or use GitHub Actions
# See .github/workflows/agent-checks.yml
```

## Monitoring

### Success Metrics
- Files processed
- Issues found/fixed
- Execution time
- Memory usage

### Failure Handling
- Log errors with context
- Send notifications for critical issues
- Implement retry logic
- Graceful degradation

## Security Considerations

1. **Input Validation**: Always validate file paths and content
2. **Resource Limits**: Set timeouts and memory limits
3. **Sandboxing**: Run untrusted code in isolated environments
4. **Permissions**: Use minimal required permissions

## Contributing

When creating new agents:
1. Follow the naming convention: `{purpose}_agent.py`
2. Include comprehensive docstrings
3. Add to agent_scheduler.py
4. Update this guide with examples
5. Add tests

## Existing Agents Reference

### Documentation Maintenance (`doc_maintenance_agent.py`)
- Validates API examples
- Checks documentation completeness
- Measures API performance

### Code Duplication (`code_duplication_agent.py`)
- Finds duplicate code patterns
- Suggests refactoring opportunities
- Updates task lists

### Orphaned Code (`orphaned_code_agent.py`)
- Identifies unused files
- Finds obsolete code
- Helps maintain clean codebase

### Universal Doc Checker (`universal_doc_checker.py`)
- Language-agnostic documentation validation
- Reusable across projects
- Extensible via plugins

### GA10 Doc Agent (`ga10_doc_agent.py`)
- GA10-specific documentation checks
- API example validation
- Uses universal checker as sub-agent