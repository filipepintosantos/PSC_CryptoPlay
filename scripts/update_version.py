"""
Script to update version in all project files.
Updates sonar-project.properties to match src/__init__.py version.
"""
import re
import sys
from pathlib import Path

def get_version_from_init():
    """Read version from src/__init__.py"""
    init_path = Path(__file__).parent.parent / 'src' / '__init__.py'
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise RuntimeError('Unable to find version in src/__init__.py')

def update_sonar_version(version):
    """Update version in sonar-project.properties"""
    sonar_path = Path(__file__).parent.parent / 'sonar-project.properties'
    with open(sonar_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(
        r'sonar\.projectVersion=.*',
        f'sonar.projectVersion={version}',
        content
    )
    
    with open(sonar_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return sonar_path

if __name__ == '__main__':
    try:
        version = get_version_from_init()
        print(f'Current version: {version}')
        
        sonar_path = update_sonar_version(version)
        print(f'✓ Updated {sonar_path.name}')
        
        print()
        print('Version is now consistent across:')
        print('  1. src/__init__.py (source of truth)')
        print('  2. setup.py (reads from __init__.py)')
        print('  3. sonar-project.properties (updated)')
        print('  4. CHANGELOG.md (manual update required)')
        
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
