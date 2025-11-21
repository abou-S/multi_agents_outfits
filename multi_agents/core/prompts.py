from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return f.read()
