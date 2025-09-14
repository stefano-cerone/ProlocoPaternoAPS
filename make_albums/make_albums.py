#!/usr/bin/env python3
"""
make_albums.py
Utility per generare automaticamente la struttura album:
assets/img/foto/<evento-XXX>/{thumbs,full} + rinomina sequenziale (img-001.jpg, ...)

Novità:
- --zip-full: crea uno ZIP con tutte le immagini "full" generate,
  salvandolo in assets/img/foto/<evento-XXX>/full/<evento-XXX>-full.zip
- --full-original: salva i "full" alla risoluzione originale (niente resize).
  Se l'originale è JPEG -> copia senza ricompressione; altrimenti converte in JPEG mantenendo le dimensioni.

Requisiti: Python 3.9+ e Pillow (pip install pillow)
"""

import argparse
from pathlib import Path
from PIL import Image
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copyfile

SUPPORTED = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif')

def make_dirs(dest_root: Path, event_name: str):
    thumbs = dest_root / 'thumbs'
    full = dest_root  / 'full' #/event_name
    thumbs.mkdir(parents=True, exist_ok=True)
    full.mkdir(parents=True, exist_ok=True)
    return thumbs, full

def load_images(src: Path):
    files = [p for p in src.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED]
    files.sort(key=lambda p: p.name.lower())
    return files

def resize_long_side(img: Image.Image, long_target: int) -> Image.Image:
    w, h = img.size
    if max(w, h) <= long_target:
        return img.copy()
    if w >= h:
        new_w = long_target
        new_h = int(h * (long_target / w))
    else:
        new_h = long_target
        new_w = int(w * (long_target / h))
    return img.resize((new_w, new_h), Image.LANCZOS)

def save_jpg(img: Image.Image, path: Path, quality: int):
    # Converte in RGB per evitare problemi con alpha/transparenza
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="JPEG", quality=quality, optimize=True, progressive=True)

def make_zip_of_full(full_dir: Path, event_name: str, files_to_zip: list[Path]) -> Path:
    zip_path = full_dir / f"{event_name}-full.zip"
    if zip_path.exists():
        zip_path.unlink()
    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files_to_zip:
            zf.write(p, arcname=p.name)
    return zip_path

def main():
    parser = argparse.ArgumentParser(description="Genera album thumbs/full + rinomina immagini (+ ZIP opzionale delle full)")
    parser.add_argument("--src", required=True, help="Cartella con le immagini originali")
    parser.add_argument("--dest", required=True, help="Cartella root del sito (dove c'è index.html)")
    parser.add_argument("--event-name", required=True, help="Nome cartella evento (es. evento-001)")
    parser.add_argument("--thumb-long", type=int, default=900, help="Lato lungo thumbnail (default 900px)")
    parser.add_argument("--full-long", type=int, default=1800, help="Lato lungo versione full (default 1800px)")
    parser.add_argument("--quality", type=int, default=82, help="Qualità JPEG (default 82)")
    parser.add_argument("--start-index", type=int, default=1, help="Indice iniziale per la numerazione (default 1)")
    parser.add_argument("--zip-full", action="store_true", help="Crea uno ZIP con tutte le immagini full nella cartella full/")
    parser.add_argument("--full-original", action="store_true",
                        help="Salva i 'full' alla risoluzione originale (niente resize). JPEG -> copia; altri formati -> converte in JPEG mantenendo le dimensioni.")
    args = parser.parse_args()

    src = Path(args.src).expanduser().resolve()
    dest_root = Path(args.dest).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"Sorgente non trovata: {src}")

    thumbs_dir, full_dir = make_dirs(dest_root, args.event_name)
    files = load_images(src)
    if not files:
        raise SystemExit("Nessuna immagine trovata nella cartella sorgente.")

    print(f"Trovate {len(files)} immagini. Elaborazione...")

    index = args.start_index
    first_thumb_path = None
    full_written_paths: list[Path] = []

    for p in files:
        with Image.open(p) as im:
            # ===== FULL =====
            full_name = f"img-{index:03d}.jpg"  # manteniamo .jpg per consistenza sul sito
            full_out = full_dir / full_name

            if args.full_original:
                # Se l'originale è JPEG -> copia byte-per-byte senza perdita
                if p.suffix.lower() in ('.jpg', '.jpeg'):
                    # Copiamo con il nuovo nome .jpg (resta JPEG, solo rinominato)
                    copyfile(p, full_out)
                else:
                    # Converte in JPEG mantenendo le dimensioni originali (no resize)
                    save_jpg(im, full_out, args.quality)
            else:
                # Modalità classica: ridimensiona lato lungo
                full_img = resize_long_side(im, args.full_long)
                save_jpg(full_img, full_out, args.quality)

            full_written_paths.append(full_out)

            # ===== THUMB =====
            thumb_img = resize_long_side(im, args.thumb_long)
            thumb_name = f"img-{index:03d}.jpg"
            thumb_out = thumbs_dir / thumb_name
            save_jpg(thumb_img, thumb_out, args.quality)

            if first_thumb_path is None:
                first_thumb_path = thumb_out

            print(f"{p.name} -> {thumb_name} / {full_name}")
            index += 1

    # cover.jpg = copia della prima thumb
    if first_thumb_path and first_thumb_path.exists():
        cover_path = thumbs_dir / "cover.jpg"
        copyfile(first_thumb_path, cover_path)
        print(f"Creato cover.jpg da {first_thumb_path.name}")

    # ZIP delle full, se richiesto
    if args.zip_full:
        print("Creo lo ZIP delle immagini full...")
        zip_path = make_zip_of_full(full_dir, args.event_name, full_written_paths)
        print(f"Creato ZIP: {zip_path.name}")

    print("\nFATTO ✅")
    print(f"Thumbs: {thumbs_dir}")
    print(f"Full:   {full_dir}")
    if args.zip_full:
        print(f"ZIP:    {full_dir / (args.event_name + '-full.zip')}")

if __name__ == "__main__":
    main()
