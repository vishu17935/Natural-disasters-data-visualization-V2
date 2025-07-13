# visualizations/__init__.py

import importlib
import pathlib
import sys

# Ensure parent path is in sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

this_dir = pathlib.Path(__file__).parent

for file in this_dir.glob("*.py"):
    if file.name == "__init__.py":
        continue
    module_name = f"visualizations.{file.stem}"
    module = importlib.import_module(module_name)
    for attr_name in dir(module):
        if attr_name.startswith("get_") or attr_name.startswith("plot_") or attr_name.startswith("create_"):
            globals()[attr_name] = getattr(module, attr_name)
