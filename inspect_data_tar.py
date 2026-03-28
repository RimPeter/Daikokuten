import tarfile
from pathlib import Path

path = Path('data.tar')
print('MISSING' if not path.exists() else 'FOUND')
if path.exists():
    with tarfile.open(path, 'r') as tar:
        members = tar.getmembers()
        print('TOTAL', len(members))
        for member in members[:100]:
            print(member.name)
