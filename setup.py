"""
Dragon Warrior ROM Hacking Toolkit

A comprehensive suite of tools for Dragon Warrior (NES) ROM hacking.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="dragon-warrior-toolkit",
    version="1.0.0",
    author="Dragon Warrior ROM Hacking Toolkit Contributors",
    author_email="",
    description="Comprehensive toolkit for Dragon Warrior (NES) ROM hacking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dragon-warrior-info",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dragon-warrior-info/issues",
        "Documentation": "https://github.com/yourusername/dragon-warrior-info/tree/master/docs",
        "Source Code": "https://github.com/yourusername/dragon-warrior-info",
    },
    packages=find_packages(include=['tools', 'tools.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "flake8>=6.0",
            "pylint>=2.17",
            "black>=23.0",
            "isort>=5.12",
        ],
        "gui": [
            "PyQt5>=5.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "dw-extract=tools.extract_binary:main",
            "dw-unpack=tools.unpack_binary:main",
            "dw-package=tools.package_binary:main",
            "dw-insert=tools.insert_binary:main",
            "dw-map-editor=tools.map_editor:main",
            "dw-text-editor=tools.text_editor:main",
            "dw-sprite-animator=tools.sprite_animator:main",
            "dw-benchmark=tools.benchmark:main",
            "dw-palette-analyzer=tools.palette_analyzer:main",
        ],
        "gui_scripts": [
            "dw-editor=tools.gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "tools": ["*.py"],
        "docs": ["*.md"],
    },
    zip_safe=False,
    keywords=[
        "dragon warrior",
        "rom hacking",
        "nes",
        "game modding",
        "retro gaming",
        "binary editing",
    ],
)
