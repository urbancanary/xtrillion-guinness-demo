#!/usr/bin/env python3
"""
Demonstration of Documentation Agent Capabilities
=================================================

This script demonstrates the capabilities of our documentation agents
and compares them with using Claude's /agents command.
"""

import json
import os
from datetime import datetime
from universal_doc_checker import UniversalDocChecker
from ga10_doc_agent import GA10DocumentationAgent
from agent_framework_example import PluggableDocAgent, AgentOrchestrator, create_project_agent


def demonstrate_universal_checker():
    """Demonstrate the universal documentation checker"""
    print("\n" + "="*60)
    print("1. UNIVERSAL DOCUMENTATION CHECKER")
    print("="*60)
    
    checker = UniversalDocChecker({
        'check_links': True,
        'code_languages': ['python', 'json', 'yaml', 'bash']
    })
    
    # Check the test file
    result = checker.check_file('test_doc_with_issues.md')
    
    print("\nCapabilities demonstrated:")
    print("✓ JSON syntax validation")
    print("✓ Python syntax checking")
    print("✓ Bash script analysis")
    print("✓ Internal link validation")
    print("✓ File link checking")
    print("✓ TODO/FIXME detection")
    
    print("\nIssues detected:")
    for issue in result['issues']:
        print(f"  - {issue['type']}: {issue['message']}")
    
    print("\nWarnings detected:")
    for warning in result['warnings']:
        print(f"  - {warning['type']}: {warning['message']}")


def demonstrate_ga10_agent():
    """Demonstrate GA10-specific documentation agent"""
    print("\n" + "="*60)
    print("2. GA10-SPECIFIC DOCUMENTATION AGENT")
    print("="*60)
    
    agent = GA10DocumentationAgent()
    
    # Check the test file with GA10-specific validations
    result = agent.checker.check_file('test_doc_with_issues.md')
    
    print("\nGA10-specific capabilities:")
    print("✓ Bond API request validation")
    print("✓ Missing price field detection")
    print("✓ Deprecated field warnings")
    print("✓ Portfolio format validation")
    print("✓ API endpoint reference checking")
    print("✓ Live API example testing (when API available)")
    
    # Extract GA10-specific warnings
    ga10_warnings = [w for w in result['warnings'] 
                     if w['type'] in ['missing_price', 'deprecated_field']]
    
    print("\nGA10-specific issues found:")
    for warning in ga10_warnings:
        print(f"  - {warning['type']}: {warning['message']}")


def demonstrate_agent_framework():
    """Demonstrate the pluggable agent framework"""
    print("\n" + "="*60)
    print("3. PLUGGABLE AGENT FRAMEWORK")
    print("="*60)
    
    # Create a custom agent with project-specific validators
    agent = create_project_agent("GA10")
    
    # Add custom preprocessor
    def add_line_numbers(content: str, file_path: str) -> str:
        """Preprocessor that adds line numbers for better error reporting"""
        lines = content.splitlines()
        return "\n".join(f"{i+1:4d}: {line}" for i, line in enumerate(lines))
    
    # Add custom postprocessor
    def severity_classifier(results: dict, content: str, file_path: str) -> dict:
        """Postprocessor that classifies issue severity"""
        for issue in results.get('issues', []):
            if 'syntax' in issue.get('type', ''):
                issue['severity'] = 'high'
            elif 'deprecated' in issue.get('type', ''):
                issue['severity'] = 'medium'
            else:
                issue['severity'] = 'low'
        return results
    
    # agent.register_preprocessor(add_line_numbers)
    agent.register_postprocessor(severity_classifier)
    
    print("\nFramework capabilities:")
    print("✓ Plugin architecture for custom validators")
    print("✓ Preprocessor pipeline for content transformation")
    print("✓ Postprocessor pipeline for result enhancement")
    print("✓ Multi-agent orchestration")
    print("✓ Standardized reporting across agents")


def demonstrate_multi_agent_orchestration():
    """Demonstrate running multiple agents together"""
    print("\n" + "="*60)
    print("4. MULTI-AGENT ORCHESTRATION")
    print("="*60)
    
    orchestrator = AgentOrchestrator()
    
    # Add different types of agents
    orchestrator.add_agent(PluggableDocAgent("BasicDocAgent"))
    orchestrator.add_agent(create_project_agent("GA10"))
    
    # Run all agents
    results = orchestrator.run_all('test_doc_with_issues.md')
    
    print("\nOrchestration capabilities:")
    print("✓ Parallel agent execution")
    print("✓ Result aggregation")
    print("✓ Error handling per agent")
    print("✓ Combined reporting")
    
    print(f"\nAgents run: {results['agents_run']}")
    for agent_result in results['agent_results']:
        print(f"  - {agent_result['agent']}: {agent_result['status']}")


def compare_with_claude_agents():
    """Show how to achieve similar results with Claude's /agents"""
    print("\n" + "="*60)
    print("5. COMPARISON WITH CLAUDE'S /AGENTS COMMAND")
    print("="*60)
    
    print("\nOur Python agents vs Claude's /agents:")
    print("\n✅ Advantages of our Python agents:")
    print("  - Programmatic and scriptable")
    print("  - Can be integrated into CI/CD pipelines")
    print("  - Customizable validators for project-specific rules")
    print("  - Can run offline without API calls")
    print("  - Batch processing of multiple files")
    print("  - Structured JSON output for further processing")
    
    print("\n✅ Advantages of Claude's /agents:")
    print("  - Natural language interface")
    print("  - No code required")
    print("  - Can understand context and intent")
    print("  - Can provide explanations and suggestions")
    print("  - Can learn from examples in conversation")
    
    print("\n📝 Example /agents prompts to achieve similar results:")
    
    prompts = [
        """
/agents documentation-checker

Check the GA10 project documentation for:
- Invalid JSON examples in code blocks
- Python syntax errors
- Missing required fields in API examples (like 'price')
- Broken internal links
- TODO/FIXME items that need attention
""",
        """
/agents api-validator

Validate all API examples in the documentation:
- Ensure all bond requests have required fields
- Check for deprecated field usage
- Verify JSON syntax is correct
- Test examples against the API specification
""",
        """
/agents project-auditor

Audit the GA10 project for documentation quality:
- Check if all critical docs (README, API specs) exist
- Validate code examples compile/parse correctly
- Ensure internal consistency between docs
- Find outdated or contradictory information
"""
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nExample {i}:")
        print("```")
        print(prompt.strip())
        print("```")


def create_summary_report():
    """Create a comprehensive summary report"""
    print("\n" + "="*60)
    print("SUMMARY: DOCUMENTATION AGENT CAPABILITIES")
    print("="*60)
    
    capabilities = {
        "Syntax Validation": {
            "JSON": "✓ Detects missing commas, trailing commas, invalid syntax",
            "Python": "✓ Finds syntax errors, Python 2 vs 3 issues",
            "YAML": "✓ Validates YAML structure",
            "Bash": "✓ Checks for unquoted variables, common issues"
        },
        "Link Checking": {
            "Internal": "✓ Validates anchor links within documents",
            "External": "✓ Checks relative file paths exist",
            "References": "✓ Finds broken cross-references"
        },
        "Project-Specific": {
            "API Examples": "✓ Validates against project's API schema",
            "Required Fields": "✓ Ensures mandatory fields are present",
            "Deprecated Usage": "✓ Warns about outdated patterns",
            "Live Testing": "✓ Can test examples against running API"
        },
        "Reporting": {
            "Text Reports": "✓ Human-readable summaries",
            "JSON Output": "✓ Structured data for processing",
            "Severity Levels": "✓ Categorizes issues by importance",
            "Statistics": "✓ Provides metrics and health scores"
        }
    }
    
    print("\nDetailed Capabilities Matrix:")
    for category, items in capabilities.items():
        print(f"\n{category}:")
        for feature, description in items.items():
            print(f"  {description}")
    
    print("\n📊 Use Cases:")
    print("  1. Pre-commit hooks to validate documentation")
    print("  2. CI/CD pipeline integration for quality gates")
    print("  3. Regular documentation health monitoring")
    print("  4. Migration validation (ensuring examples still work)")
    print("  5. API documentation accuracy verification")


if __name__ == "__main__":
    print("DOCUMENTATION AGENT DEMONSTRATION")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all demonstrations
    demonstrate_universal_checker()
    demonstrate_ga10_agent()
    demonstrate_agent_framework()
    demonstrate_multi_agent_orchestration()
    compare_with_claude_agents()
    create_summary_report()
    
    print("\n" + "="*60)
    print("Demonstration complete!")
    print("="*60)