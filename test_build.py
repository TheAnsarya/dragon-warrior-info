#!/usr/bin/env python3
"""
Quick Build Test - Create a test ROM to demonstrate the build system
"""

import os
import sys
from pathlib import Path
import subprocess
from rich.console import Console

console = Console()

def run_test_build():
	"""Run a quick test build to validate the system"""
	
	console.print("[bold blue]🧪 Dragon Warrior Build System Test[/bold blue]\n")
	
	# Check if we're in the right directory
	if not Path("build.ps1").exists():
		console.print("[red]❌ Must run from project root directory[/red]")
		sys.exit(1)
	
	# Check for reference ROM
	reference_rom = Path("~roms/Dragon Warrior (U) (PRG1) [!].nes").expanduser()
	if not reference_rom.exists():
		console.print(f"[yellow]⚠️  Reference ROM not found at {reference_rom}[/yellow]")
		console.print("   Place the ROM there for comparison testing")
	
	console.print("🔧 Running test build...")
	
	try:
		# Run the build script
		result = subprocess.run([
			"powershell", "-ExecutionPolicy", "Bypass",
			"-File", "build.ps1",
			"-Test"
		], capture_output=True, text=True)
		
		console.print("📋 Build Output:")
		if result.stdout:
			console.print(result.stdout)
		
		if result.stderr:
			console.print("[red]Errors:[/red]")
			console.print(result.stderr)
		
		if result.returncode == 0:
			console.print("\n[green]✅ Build test completed successfully![/green]")
			
			# Check for build artifacts
			build_dir = Path("build")
			if build_dir.exists():
				console.print(f"\n📁 Build artifacts in {build_dir}:")
				for file_path in build_dir.rglob("*"):
					if file_path.is_file():
						size = file_path.stat().st_size
						console.print(f"   📄 {file_path.name} ({size:,} bytes)")
		else:
			console.print(f"\n[red]❌ Build test failed (exit code: {result.returncode})[/red]")
			sys.exit(1)
	
	except Exception as e:
		console.print(f"[red]❌ Error running build: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	run_test_build()