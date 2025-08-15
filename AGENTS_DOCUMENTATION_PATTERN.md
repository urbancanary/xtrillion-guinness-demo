# Using /agents for Documentation Checking

## Quick Start: Using Claude's /agents Instead of Python Scripts

Instead of maintaining complex Python scripts, you can use Claude's built-in `/agents` command for powerful documentation checking:

### Basic Documentation Check
```
/agents
Task: Check all markdown files for broken code examples, invalid JSON, and broken links
```

### Project-Specific Check
```
/agents
Task: Validate all API documentation in this project. Check that:
- All JSON examples are valid
- API endpoints match current implementation
- Required fields are documented
- No deprecated patterns are used
```

### Find Specific Issues
```
/agents
Task: Find all TODO and FIXME markers in documentation files
```

## Why Use /agents Instead of Custom Scripts?

| Feature | /agents | Python Scripts |
|---------|---------|----------------|
| Setup Required | None | Copy files, install deps |
| Maintenance | None | Update code regularly |
| Intelligence | Understands context | Only programmed checks |
| Flexibility | Natural language | Fixed logic |
| Cross-Project | Works anywhere | Must port code |

## Common Documentation Checking Tasks

### 1. Validate Code Examples
```
/agents
Task: Check all code examples in markdown files for syntax errors. For each language (Python, JSON, JavaScript), verify the code is valid.
```

### 2. Check API Consistency
```
/agents
Task: Compare API examples in documentation with actual API endpoints in the code. Flag any mismatches or deprecated endpoints.
```

### 3. Find Broken Links
```
/agents
Task: Check all internal links in markdown files (like [text](#anchor) or [text](file.md)) and verify they point to valid targets.
```

### 4. Enforce Documentation Standards
```
/agents
Task: Check that all markdown files follow our documentation standards:
- Have a proper H1 heading
- Include a table of contents for files over 500 lines
- Use consistent code block formatting
- Don't have trailing whitespace
```

### 5. Security Audit
```
/agents
Task: Search all documentation for accidentally exposed secrets like API keys, passwords, or internal URLs that shouldn't be public.
```

## Creating a Documentation Checking "Recipe"

You can save common checks as a reusable pattern:

### For API Projects
```
/agents
Task: Run comprehensive API documentation check:
1. Validate all JSON request/response examples
2. Check that documented endpoints exist in code
3. Verify required fields match implementation
4. Find any references to deprecated features
5. Check for missing error response documentation
```

### For Open Source Projects
```
/agents
Task: Validate open source documentation:
1. Check README has installation instructions
2. Verify all code examples work
3. Find broken links to external resources
4. Check CONTRIBUTING.md exists and has clear guidelines
5. Ensure LICENSE file is referenced
```

## Advanced Usage

### Automated Fixes
```
/agents
Task: Fix common documentation issues:
1. Update deprecated API endpoints to current versions
2. Fix JSON syntax errors in examples
3. Update broken internal links
4. Remove trailing whitespace
Then show me the changes before applying them.
```

### Cross-Reference Checking
```
/agents
Task: Cross-reference documentation with code:
1. Find all functions mentioned in docs and verify they exist in code
2. Check that documented parameters match function signatures
3. Verify return types match documentation
```

### Generate Documentation Report
```
/agents
Task: Generate a documentation health report showing:
1. Number of files checked
2. Issues found by category
3. Files with the most problems
4. Overall documentation quality score
5. Specific recommendations for improvement
```

## Best Practices

1. **Be Specific**: The more specific your request, the better the results
   ```
   ❌ "Check docs"
   ✅ "Check all API examples in markdown files for valid JSON syntax"
   ```

2. **Iterate**: Start broad, then narrow down
   ```
   First: "Find all documentation issues"
   Then: "Focus on the JSON validation errors in API_GUIDE.md"
   ```

3. **Combine Tasks**: You can check multiple things at once
   ```
   /agents
   Task: For all markdown files:
   - Validate code examples
   - Check internal links
   - Find TODO markers
   - Identify missing required sections
   ```

4. **Use Context**: Reference specific files or patterns
   ```
   /agents
   Task: Check documentation files matching API_*.md for consistency with the OpenAPI spec in api/openapi.yaml
   ```

## When to Still Use Python Scripts

While `/agents` is powerful, consider Python scripts for:

- **Scheduled Checks**: Running via cron or CI/CD
- **Deterministic Results**: When you need exactly the same check every time
- **Performance**: Checking thousands of files
- **Offline Usage**: When you don't have access to Claude

## Migrating from Python Scripts to /agents

If you have existing Python documentation checkers:

1. **Identify Core Checks**: List what your scripts currently validate
2. **Create Agent Prompts**: Convert each check to a natural language task
3. **Test Coverage**: Ensure /agents finds the same issues
4. **Archive Scripts**: Keep scripts for reference but use /agents going forward

Example migration:
```python
# Old Python code:
def check_json_examples(content):
    for match in re.findall(r'```json\n(.*?)\n```', content):
        try:
            json.loads(match)
        except:
            print("Invalid JSON")

# New /agents approach:
/agents
Task: Find all JSON code blocks in markdown files and validate they are syntactically correct
```

## Summary

Using `/agents` for documentation checking provides:
- **Zero maintenance**: No code to update
- **Natural language**: Describe what you want in plain English
- **Intelligent analysis**: Understands context and relationships
- **Cross-project**: Works on any codebase immediately
- **Evolving capabilities**: Gets better as Claude improves

Start using `/agents` today and retire those maintenance-heavy Python scripts!