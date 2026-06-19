from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_agent_cli() -> object:
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    agent_cli_path = root / "agent_cli.py"
    spec = importlib.util.spec_from_file_location("crestline_agent_cli", agent_cli_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load agent_cli.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = _load_agent_cli()
    if hasattr(module, "main"):
        module.main()
    else:
        raise AttributeError("agent_cli.py does not define a main() function")


if __name__ == "__main__":
    main()
