"""Build a source-only ZIP; never include local secrets or databases."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
destination = root / 'dist' / 'note-demo.zip'
destination.parent.mkdir(exist_ok=True)
directories = ('app', 'docs', 'migrations', 'tools', 'tests')
files = ['readme.md', 'plan.md', 'prompt.md', 'agent-prompt.md', 'wsgi.py',
         'requirements.txt', 'requirements-dev.txt', 'pytest.ini', '.gitignore']
paths = [root / name for name in files]
for name in directories:
    paths.extend(path for path in (root / name).rglob('*') if path.is_file())
with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        if '__pycache__' in path.parts or path.suffix in ('.pyc', '.sqlite3'):
            continue
        archive.write(path, Path('note-demo') / path.relative_to(root))
print('생성 완료:', destination)
