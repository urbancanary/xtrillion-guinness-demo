# Using Claude's /agents for Documentation Checking

## 🚀 Quick Reference: From Python Scripts to /agents

This guide shows how to leverage Claude's built-in `/agents` command for documentation checking, replacing complex Python scripts with natural language prompts.

## 📋 Common Documentation Checking Tasks

### 1. Basic Syntax Validation

**Instead of Python script:**
```python
# universal_doc_checker.py - 400+ lines of code
checker = UniversalDocChecker()
results = checker.check_file("README.md")
```

**Use /agents:**
```
/agents
Task: Check README.md for syntax errors in all code blocks. Validate JSON, Python, YAML, and bash examples.
```

### 2. API Documentation Validation

**Instead of Python script:**
```python
# ga10_doc_agent.py - 370+ lines of code
agent = GA10DocumentationAgent()
results = agent.run_full_check()
```

**Use /agents:**
```
/agents
Task: Validate all API documentation in this project:
- Check JSON request/response examples are valid
- Verify required fields (description, price) are documented
- Find deprecated field usage (parse_description, calculate_all)
- Ensure endpoints match implementation
```

### 3. Link and Reference Checking

**Instead of custom code:**
```python
def _check_links(self, content, file_path):
    # Complex regex and file checking logic
```

**Use /agents:**
```
/agents
Task: Check all markdown files for broken links:
- Internal anchors (#sections)
- Relative file paths
- External URLs (if accessible)
Report broken links with their locations
```

## 🎯 GA10-Specific Documentation Checks

### Complete Documentation Audit
```
/agents
Task: Perform comprehensive GA10 documentation audit:

1. Check critical files exist:
   - API_SPECIFICATION_PRODUCTION_REALITY.md
   - API_SPECIFICATION_EXTERNAL.md
   - CLAUDE.md
   - README.md

2. Validate all API examples:
   - Bond analysis requests have 'price' field
   - Portfolio requests use correct field names
   - No deprecated fields are used

3. Check code consistency:
   - Import statements match renamed files (google_analysis10.py)
   - API endpoints in docs match implementation
   - Settlement dates are consistent (2025-04-18)

4. Find documentation issues:
   - TODO/FIXME markers
   - Outdated version references
   - Inconsistent metric names
```

### API Example Validation
```
/agents
Task: Extract and validate all API examples from documentation:
- Find all JSON code blocks that look like API requests
- Check they have required fields for their endpoint type
- Validate JSON syntax
- Flag any that use old field names or patterns
```

### Cross-Reference Checking
```
/agents
Task: Cross-reference documentation with code:
- Check that documented functions exist in code
- Verify endpoint URLs match Flask routes
- Ensure database table names are correct
- Validate import statements reference actual files
```

## 🔧 Advanced Patterns

### 1. Fix Documentation Issues
```
/agents
Task: Fix common documentation issues in GA10 project:
- Update deprecated field names to current ones
- Fix JSON syntax errors in examples
- Update broken internal links
- Correct import statements for renamed files
Show me changes before applying them
```

### 2. Generate Documentation Report
```
/agents
Task: Generate documentation health report for GA10:
- Count total documentation files
- List issues found by category
- Identify files with most problems
- Calculate documentation completeness score
- Suggest top 5 improvements
Format as a management summary
```

### 3. Migration Validation
```
/agents
Task: Validate documentation after google_analysis9.py → google_analysis10.py rename:
- Find all references to old filename
- Check import statements are updated
- Verify file paths in examples
- Update any outdated references
```

## 📊 Comparison: When to Use What

| Task | Python Scripts | /agents |
|------|---------------|---------|
| Pre-commit validation | ✅ Better | ❌ Not suitable |
| CI/CD integration | ✅ Better | ❌ Not suitable |
| One-time audit | ❌ Overkill | ✅ Better |
| Semantic clarity | ❌ Can't do | ✅ Better |
| Bulk file processing | ✅ Better | ❌ Slower |
| Context understanding | ❌ Limited | ✅ Better |
| Custom project rules | ✅ Better | ✅ Good |
| Fix suggestions | ❌ Basic | ✅ Better |

## 💡 Best Practices

### 1. Be Specific About Project Context
```
/agents
Task: Check GA10 bond API documentation ensuring:
- Examples use Universal Parser format (description or ISIN)
- Settlement dates follow policy (prior month-end or specific date)
- All 13 enhanced metrics are documented
```

### 2. Combine Multiple Checks
```
/agents
Task: Complete documentation check for deployment:
1. Validate all JSON examples compile
2. Check internal links work
3. Verify API endpoints exist in code
4. Find any TODO items that block release
5. Ensure version numbers are consistent
```

### 3. Request Actionable Output
```
/agents
Task: Find and prioritize documentation issues:
- Group by severity (blocks deployment vs nice-to-have)
- Provide specific file:line references
- Suggest fixes for each issue
- Order by importance
```

## 🚦 Quick Start Examples

### For New Projects
```
/agents
Task: Set up documentation checking for my project similar to GA10's approach
```

### For Existing Documentation
```
/agents
Task: Audit existing API documentation and create improvement plan
```

### For Regular Maintenance
```
/agents
Task: Weekly documentation check - find new TODOs, broken examples, and outdated content
```

## 🎓 Learning from GA10's Approach

The GA10 project demonstrates several documentation best practices:

1. **Separate internal and external docs** (PRODUCTION_REALITY vs EXTERNAL)
2. **Maintain CLAUDE.md** for AI assistant context
3. **Version documentation** with API changes
4. **Include working examples** that can be validated
5. **Document both current and deprecated** patterns

Use these patterns in your /agents prompts for better results.

## 📝 Summary

Claude's `/agents` command provides a powerful, flexible alternative to custom Python scripts for documentation checking. While Python scripts excel at automated, repeatable validation, `/agents` offers superior understanding of context, semantics, and can provide intelligent fixes.

**Key Takeaway:** Use `/agents` for:
- One-time audits and investigations
- Understanding documentation quality holistically  
- Getting fix suggestions
- Validating semantic correctness

Keep Python scripts for:
- Automated CI/CD checks
- Pre-commit hooks
- Bulk validation
- Deterministic rule enforcement

Together, they form a comprehensive documentation quality system.