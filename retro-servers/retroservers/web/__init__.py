import pkgutil
import importlib
from pathlib import Path
package_dir = Path(__file__).parent/'handlers'
for file_path in package_dir.glob("*.py"):
    if file_path.name == "__init__.py":
        continue
    importlib.import_module(f".{file_path.stem}", package=f'{__name__}.handlers')
from .webserver import WebServer

