#!/usr/bin/env python3
"""
Dragon Warrior Info Project - GitHub Issues Manager
Automated issue creation and project board management
Based on FFMQ project patterns
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from github import Github
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import dotenv

# Load environment variables
dotenv.load_dotenv()

console = Console()

class GitHubManager:
	"""GitHub issues and project management automation"""
	
	def __init__(self):
		self.token = os.getenv('GITHUB_TOKEN')
		if not self.token:
			console.print("[red]ERROR: GITHUB_TOKEN environment variable not set[/red]")
			console.print("Create a personal access token at: https://github.com/settings/tokens")
			sys.exit(1)
		
		self.github = Github(self.token)
		self.repo_name = "TheAnsarya/dragon-warrior-info"
		self.project_id = 5  # GitHub Project #5
		
		try:
			self.repo = self.github.get_repo(self.repo_name)
		except Exception as e:
			console.print(f"[red]ERROR: Cannot access repository {self.repo_name}: {e}[/red]")
			sys.exit(1)
	
	def create_issue(self, title: str, body: str, labels: List[str] = None, 
					assignee: str = None, milestone: str = None) -> Dict[str, Any]:
		"""Create a new GitHub issue"""
		try:
			issue_labels = []
			if labels:
				# Get or create labels
				repo_labels = {label.name: label for label in self.repo.get_labels()}
				for label_name in labels:
					if label_name not in repo_labels:
						# Create label if it doesn't exist
						self.repo.create_label(label_name, color="0052cc")
					issue_labels.append(label_name)
			
			# Create the issue
			issue = self.repo.create_issue(
				title=title,
				body=body,
				labels=issue_labels,
				assignee=assignee if assignee else None
			)
			
			console.print(f"[green]✅ Created issue #{issue.number}: {title}[/green]")
			return {
				"number": issue.number,
				"url": issue.html_url,
				"title": title,
				"labels": labels or [],
				"created_at": issue.created_at.isoformat()
			}
			
		except Exception as e:
			console.print(f"[red]ERROR creating issue: {e}[/red]")
			return None
	
	def list_issues(self, state: str = "open", labels: List[str] = None) -> List[Dict[str, Any]]:
		"""List issues with optional filtering"""
		try:
			issues = self.repo.get_issues(state=state, labels=labels or [])
			
			table = Table(title=f"GitHub Issues ({state.upper()})")
			table.add_column("#", style="cyan", no_wrap=True)
			table.add_column("Title", style="bold")
			table.add_column("Labels", style="green")
			table.add_column("Updated", style="dim")
			
			issue_list = []
			for issue in issues[:20]:  # Limit to 20 most recent
				labels_str = ", ".join([label.name for label in issue.labels])
				table.add_row(
					str(issue.number),
					issue.title[:50] + ("..." if len(issue.title) > 50 else ""),
					labels_str,
					issue.updated_at.strftime("%Y-%m-%d")
				)
				issue_list.append({
					"number": issue.number,
					"title": issue.title,
					"url": issue.html_url,
					"labels": [label.name for label in issue.labels],
					"state": issue.state,
					"updated_at": issue.updated_at.isoformat()
				})
			
			console.print(table)
			return issue_list
			
		except Exception as e:
			console.print(f"[red]ERROR listing issues: {e}[/red]")
			return []
	
	def update_issue(self, issue_number: int, title: str = None, body: str = None, 
					state: str = None, labels: List[str] = None) -> bool:
		"""Update an existing issue"""
		try:
			issue = self.repo.get_issue(issue_number)
			
			if title:
				issue.edit(title=title)
			if body:
				issue.edit(body=body)
			if state:
				issue.edit(state=state)
			if labels is not None:
				issue.edit(labels=labels)
			
			console.print(f"[green]✅ Updated issue #{issue_number}[/green]")
			return True
			
		except Exception as e:
			console.print(f"[red]ERROR updating issue #{issue_number}: {e}[/red]")
			return False
	
	def bulk_create_from_yaml(self, yaml_file: str) -> List[Dict[str, Any]]:
		"""Create multiple issues from YAML configuration"""
		try:
			with open(yaml_file, 'r', encoding='utf-8') as f:
				config = yaml.safe_load(f)
			
			created_issues = []
			for issue_config in config.get('issues', []):
				result = self.create_issue(
					title=issue_config['title'],
					body=issue_config['body'],
					labels=issue_config.get('labels', []),
					assignee=issue_config.get('assignee')
				)
				if result:
					created_issues.append(result)
			
			console.print(f"[green]✅ Created {len(created_issues)} issues from {yaml_file}[/green]")
			return created_issues
			
		except Exception as e:
			console.print(f"[red]ERROR creating issues from YAML: {e}[/red]")
			return []

@click.group()
def cli():
	"""Dragon Warrior Info Project - GitHub Issues Manager"""
	console.print(Panel.fit(
		"[bold blue]Dragon Warrior GitHub Issues Manager[/bold blue]\n"
		"Automated issue creation and project management",
		border_style="blue"
	))

@cli.command()
@click.option('--title', '-t', required=True, help='Issue title')
@click.option('--body', '-b', default='', help='Issue body/description')
@click.option('--labels', '-l', multiple=True, help='Issue labels')
@click.option('--assignee', '-a', help='Issue assignee')
def create(title: str, body: str, labels: tuple, assignee: str):
	"""Create a new GitHub issue"""
	manager = GitHubManager()
	manager.create_issue(title, body, list(labels), assignee)

@cli.command()
@click.option('--state', '-s', default='open', help='Issue state (open/closed/all)')
@click.option('--labels', '-l', multiple=True, help='Filter by labels')
def list(state: str, labels: tuple):
	"""List GitHub issues"""
	manager = GitHubManager()
	manager.list_issues(state, list(labels) if labels else None)

@cli.command()
@click.argument('issue_number', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--body', '-b', help='New body')
@click.option('--state', '-s', help='New state (open/closed)')
@click.option('--labels', '-l', multiple=True, help='New labels')
def update(issue_number: int, title: str, body: str, state: str, labels: tuple):
	"""Update an existing GitHub issue"""
	manager = GitHubManager()
	manager.update_issue(issue_number, title, body, state, list(labels) if labels else None)

@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True))
def bulk_create(yaml_file: str):
	"""Create multiple issues from YAML file"""
	manager = GitHubManager()
	manager.bulk_create_from_yaml(yaml_file)

@cli.command()
def init():
	"""Initialize project with standard Dragon Warrior issues"""
	manager = GitHubManager()
	
	# Create standard project issues based on FFMQ patterns
	standard_issues = [
		{
			"title": "🔧 Set up build pipeline and ROM assembly system",
			"body": """## Objective
Create a comprehensive build system for Dragon Warrior ROM assembly and testing.

## Tasks
- [ ] Set up ca65/asar assembler pipeline
- [ ] Create PowerShell build scripts
- [ ] Implement ROM verification and checksums
- [ ] Set up emulator testing integration
- [ ] Create clean/rebuild functionality

## Reference
Based on FFMQ project build system patterns.

## Acceptance Criteria
- [ ] Single command ROM build
- [ ] Automated testing pipeline
- [ ] Build verification reports
- [ ] Cross-platform compatibility""",
			"labels": ["enhancement", "infrastructure", "high-priority"]
		},
		{
			"title": "📊 Create comprehensive ROM data mapping and documentation",
			"body": """## Objective
Document complete ROM structure and data formats for Dragon Warrior.

## Tasks
- [ ] Map ROM banks and memory layout
- [ ] Document SRAM structure and save game format
- [ ] Create data crystal style wiki documentation
- [ ] Identify and document all data structures
- [ ] Create ROM map visualization

## Reference
Follow DataCrystal wiki standards and FFMQ documentation patterns.

## Acceptance Criteria
- [ ] Complete ROM map documentation
- [ ] SRAM format specification
- [ ] DataCrystal compatible wiki structure
- [ ] Hacking information database""",
			"labels": ["documentation", "research", "high-priority"]
		},
		{
			"title": "🎨 Develop asset extraction and editing toolchain",
			"body": """## Objective
Create tools for extracting, editing, and reinserting game assets.

## Tasks
- [ ] Graphics extraction (tiles, sprites, backgrounds)
- [ ] Text extraction and editing system
- [ ] Music/sound data extraction
- [ ] PNG conversion pipeline
- [ ] Asset recompression and insertion

## Reference
Based on FFMQ graphics and text tools.

## Acceptance Criteria
- [ ] Extract all graphics to PNG
- [ ] Complete text editing system
- [ ] Asset modification workflow
- [ ] Automated asset rebuilding""",
			"labels": ["enhancement", "tools", "high-priority"]
		},
		{
			"title": "🛠️ Create visual editors for game data modification",
			"body": """## Objective
Build GUI tools for editing game data with immediate feedback.

## Tasks
- [ ] Enemy stats editor
- [ ] Item/weapon/armor editor
- [ ] Map/level editor
- [ ] Dialog/text editor
- [ ] Experience/level progression editor

## Reference
Based on FFMQ enemy editor patterns and GUI frameworks.

## Acceptance Criteria
- [ ] Visual GUI editors with search/filter
- [ ] JSON export/import workflow
- [ ] Undo/redo functionality
- [ ] Real-time ROM preview""",
			"labels": ["enhancement", "gui", "tools", "medium-priority"]
		},
		{
			"title": "🧪 Establish comprehensive testing and validation framework",
			"body": """## Objective
Create automated testing for ROM modifications and tool reliability.

## Tasks
- [ ] ROM integrity testing
- [ ] Asset extraction/insertion roundtrip tests
- [ ] Tool functionality unit tests
- [ ] Emulator integration testing
- [ ] Regression testing suite

## Reference
Based on FFMQ testing patterns and pytest framework.

## Acceptance Criteria
- [ ] Complete test coverage
- [ ] Automated CI/CD pipeline
- [ ] ROM validation tools
- [ ] Performance benchmarking""",
			"labels": ["testing", "infrastructure", "medium-priority"]
		},
		{
			"title": "📚 Create comprehensive project documentation and tutorials",
			"body": """## Objective
Provide complete documentation for users, modders, and developers.

## Tasks
- [ ] User quickstart guides
- [ ] Comprehensive modding tutorials
- [ ] Developer onboarding documentation
- [ ] API reference documentation
- [ ] Video tutorial creation

## Reference
Follow FFMQ documentation structure and completeness.

## Acceptance Criteria
- [ ] Complete documentation index
- [ ] Step-by-step tutorials
- [ ] API and tool references
- [ ] Video demonstrations""",
			"labels": ["documentation", "tutorial", "medium-priority"]
		}
	]
	
	created_issues = []
	for issue in standard_issues:
		result = manager.create_issue(
			title=issue["title"],
			body=issue["body"],
			labels=issue["labels"]
		)
		if result:
			created_issues.append(result)
	
	# Save created issues to file for tracking
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	output_file = f"~docs/github_issues_created_{timestamp}.json"
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(created_issues, f, indent=2)
	
	console.print(f"[green]✅ Created {len(created_issues)} standard issues[/green]")
	console.print(f"[blue]📁 Issue details saved to: {output_file}[/blue]")

if __name__ == "__main__":
	cli()