import argparse
from pathlib import Path
from app.catalog import DEFAULT_DATA

def parser():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument("--mock", action="store_true")
    return p
