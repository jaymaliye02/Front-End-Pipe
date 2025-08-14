\
import os, re, shutil, uuid

_INVALID = r'[\\/:*?"<>|\x00-\x1F]'
_RESERVED = {"CON","PRN","AUX","NUL",*(f"COM{i}" for i in range(1,10)),*(f"LPT{i}" for i in range(1,10))}

def sanitize_subject(s: str, strip_external: bool = True) -> str:
    if not s: return "message"
    s = s.strip()
    if strip_external:
        s = re.sub(r'^\s*\[External\]\s*', '', s, flags=re.IGNORECASE)
    # normalize date separators within numbers -> hyphen
    s = re.sub(r'(?<=\d)[/\\](?=\d)', '-', s)
    s = re.sub(_INVALID, '_', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'_+', '_', s).strip(' ._')
    stem = s.split('.')[0].upper()
    if stem in _RESERVED:
        s = f"_{s}"
    if len(s) > 120:
        s = s[:120].rstrip(' ._')
    return s or "message"

def ensure_drop_folder(drop_root: str, ymd: str) -> str:
    p = os.path.join(drop_root, "Data Files", ymd)
    os.makedirs(p, exist_ok=True)
    return p

def atomic_move(src_path: str, dst_dir: str) -> str:
    os.makedirs(dst_dir, exist_ok=True)
    base = os.path.basename(src_path)
    dst = os.path.join(dst_dir, base)
    if not os.path.exists(dst):
        return shutil.move(src_path, dst)
    root, ext = os.path.splitext(base)
    for _ in range(20):
        cand = os.path.join(dst_dir, f"{root}__{uuid.uuid4().hex[:6]}{ext}")
        if not os.path.exists(cand):
            return shutil.move(src_path, cand)
    return shutil.move(src_path, os.path.join(dst_dir, f"{root}__{uuid.uuid4().hex}{ext}"))
