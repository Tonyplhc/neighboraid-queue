from __future__ import annotations

import argparse
import json
from pathlib import Path
from .agent import process_batch


def main() -> None:
    parser = argparse.ArgumentParser(description="Process food-bank requests with NeighborAid Queue")
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = process_batch(args.requests, args.inventory, args.output)
    print(json.dumps({k: result[k] for k in ("processed", "auto_ready", "human_review", "blocked")}, sort_keys=True))


if __name__ == "__main__":
    main()
