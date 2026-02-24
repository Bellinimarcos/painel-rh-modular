import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

def fix_text(s: str) -> str:
    # caso tpico: "çã" etc (latin-1 interpretado como utf-8)
    try:
        return s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        return s

def process_file(path: pathlib.Path) -> bool:
    try:
        raw = path.read_bytes()
    except Exception:
        return False

    text = None
    for enc in ("utf-8", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except Exception:
            pass
    if text is None:
        return False

    fixed = fix_text(text)
    if fixed != text:
        path.write_bytes(fixed.encode("utf-8"))  # UTF-8 sem BOM
        return True
    return False

def main():
    changed = 0
    total = 0
    for p in ROOT.rglob("*.py"):
        total += 1
        if process_file(p):
            changed += 1
    print(f"OK: verificados={total} | alterados={changed}")

if __name__ == "__main__":
    main()