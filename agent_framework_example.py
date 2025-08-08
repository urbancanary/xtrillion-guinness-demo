#!/usr/bin/env python3
"""
Agent Framework Example
=======================

Example of how to create reusable agents that can be used across projects.
This demonstrates:
1. Base agent class that can be inherited
2. Plugin system for custom validators
3. Integration with other agents
4. Standardized reporting
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
import json
import os
from datetime import datetime
from pathlib import Path

class BaseAgent(ABC):
    """
    Base class for all documentation/code checking agents
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self.results = []
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    def run(self, target: str) -> Dict[str, Any]:
        """Run the agent on a target (file, directory, etc)"""
        pass
    
    @abstractmethod
    def validate(self, content: Any) -> Dict[str, List]:
        """Validate content and return issues/warnings"""
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """Standardized logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.name}] [{level}] {message}")
    
    def start(self):
        """Mark agent start"""
        self.start_time = datetime.now()
        self.log(f"Starting {self.name} agent...")
    
    def finish(self):
        """Mark agent completion"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        self.log(f"Completed in {duration:.2f} seconds")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            'agent': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None,
            'results_count': len(self.results)
        }


class PluggableDocAgent(BaseAgent):
    """
    Documentation agent with plugin support for custom validators
    """
    
    def __init__(self, name: str = "PluggableDocAgent", config: Optional[Dict] = None):
        super().__init__(name, config)
        self.validators = {}
        self.preprocessors = []
        self.postprocessors = []
        
        # Register default validators
        self._register_default_validators()
    
    def register_validator(self, language: str, validator: Callable):
        """Register a custom validator for a language"""
        self.validators[language] = validator
        self.log(f"Registered validator for {language}")
    
    def register_preprocessor(self, preprocessor: Callable):
        """Register a preprocessor that runs before validation"""
        self.preprocessors.append(preprocessor)
    
    def register_postprocessor(self, postprocessor: Callable):
        """Register a postprocessor that runs after validation"""
        self.postprocessors.append(postprocessor)
    
    def run(self, target: str) -> Dict[str, Any]:
        """Run the agent on target file/directory"""
        self.start()
        
        results = {
            'target': target,
            'files_processed': 0,
            'total_issues': 0,
            'total_warnings': 0,
            'details': []
        }
        
        # Process target
        if os.path.isfile(target):
            file_results = self._process_file(target)
            results['files_processed'] = 1
            results['details'].append(file_results)
            results['total_issues'] += len(file_results.get('issues', []))
            results['total_warnings'] += len(file_results.get('warnings', []))
        elif os.path.isdir(target):
            for file_path in Path(target).rglob('*.md'):
                file_results = self._process_file(str(file_path))
                results['files_processed'] += 1
                results['details'].append(file_results)
                results['total_issues'] += len(file_results.get('issues', []))
                results['total_warnings'] += len(file_results.get('warnings', []))
        
        self.finish()
        results['summary'] = self.get_summary()
        
        return results
    
    def validate(self, content: str, language: str = 'text') -> Dict[str, List]:
        """Validate content using appropriate validator"""
        if language in self.validators:
            return self.validators[language](content)
        else:
            return {'issues': [], 'warnings': []}
    
    def _process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file"""
        results = {
            'file': file_path,
            'issues': [],
            'warnings': []
        }
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Run preprocessors
        for preprocessor in self.preprocessors:
            content = preprocessor(content, file_path)
        
        # Extract and validate code blocks
        import re
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
        
        for language, code in code_blocks:
            validation = self.validate(code, language or 'text')
            results['issues'].extend(validation.get('issues', []))
            results['warnings'].extend(validation.get('warnings', []))
        
        # Run postprocessors
        for postprocessor in self.postprocessors:
            results = postprocessor(results, content, file_path)
        
        return results
    
    def _register_default_validators(self):
        """Register default validators"""
        
        def validate_json(content: str) -> Dict[str, List]:
            result = {'issues': [], 'warnings': []}
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                result['issues'].append({
                    'type': 'json_syntax',
                    'message': str(e)
                })
            return result
        
        def validate_python(content: str) -> Dict[str, List]:
            result = {'issues': [], 'warnings': []}
            try:
                compile(content, '<string>', 'exec')
            except SyntaxError as e:
                result['issues'].append({
                    'type': 'python_syntax',
                    'message': str(e)
                })
            return result
        
        self.register_validator('json', validate_json)
        self.register_validator('python', validate_python)


class AgentOrchestrator:
    """
    Orchestrates multiple agents and combines their results
    """
    
    def __init__(self):
        self.agents = []
        self.results = []
    
    def add_agent(self, agent: BaseAgent):
        """Add an agent to the orchestrator"""
        self.agents.append(agent)
    
    def run_all(self, target: str) -> Dict[str, Any]:
        """Run all agents on the target"""
        combined_results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'agents_run': len(self.agents),
            'agent_results': []
        }
        
        for agent in self.agents:
            try:
                result = agent.run(target)
                combined_results['agent_results'].append({
                    'agent': agent.name,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                combined_results['agent_results'].append({
                    'agent': agent.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return combined_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate combined report from all agents"""
        report = []
        report.append("=" * 60)
        report.append("Multi-Agent Analysis Report")
        report.append("=" * 60)
        report.append(f"Target: {results['target']}")
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Agents Run: {results['agents_run']}")
        report.append("")
        
        for agent_result in results['agent_results']:
            report.append(f"\n{'='*40}")
            report.append(f"Agent: {agent_result['agent']}")
            report.append(f"Status: {agent_result['status']}")
            
            if agent_result['status'] == 'success':
                result = agent_result['result']
                report.append(f"Files Processed: {result.get('files_processed', 0)}")
                report.append(f"Total Issues: {result.get('total_issues', 0)}")
                report.append(f"Total Warnings: {result.get('total_warnings', 0)}")
            else:
                report.append(f"Error: {agent_result.get('error', 'Unknown error')}")
        
        return "\n".join(report)


# Example usage showing how to create project-specific agents
def create_project_agent(project_name: str) -> PluggableDocAgent:
    """
    Factory function to create project-specific agents
    """
    agent = PluggableDocAgent(f"{project_name}DocAgent")
    
    # Add project-specific validators
    if project_name == "GA10":
        def validate_ga10_api_json(content: str) -> Dict[str, List]:
            result = {'issues': [], 'warnings': []}
            try:
                data = json.loads(content)
                # GA10 specific validation
                if 'description' in data and 'price' not in data:
                    result['warnings'].append({
                        'type': 'ga10_missing_price',
                        'message': 'Bond request missing price field'
                    })
            except:
                pass
            return result
        
        agent.register_validator('json', validate_ga10_api_json)
    
    return agent


def main():
    """Example of using the agent framework"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Framework Example")
    parser.add_argument('target', help='Target file or directory')
    parser.add_argument('--project', default='generic', help='Project type')
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Add agents
    doc_agent = create_project_agent(args.project)
    orchestrator.add_agent(doc_agent)
    
    # You can add more agents here
    # orchestrator.add_agent(CodeQualityAgent())
    # orchestrator.add_agent(SecurityAgent())
    
    # Run all agents
    results = orchestrator.run_all(args.target)
    
    # Generate report
    report = orchestrator.generate_report(results)
    print(report)


if __name__ == '__main__':
    main()