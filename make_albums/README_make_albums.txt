------------------------------
    ISTRUZIONE DEFINITIVA
-   -   -   -    -   -   -   - 
cd C:\Users\Stefa\Documents\Progetti_Ste\proloco_paterno

python make_albums/make_albums.py --src "originali" --dest "assets/img/foto/NOME-Evento" --event-name gatto1 --full-original --zip-full

---------------------------------




GUIDA RAPIDA — make_albums.py
=============================

Questo script crea automaticamente la struttura degli album foto per il sito,
con miniature (thumbs) e versioni grandi (full) + rinomina sequenziale.

1) Requisiti
------------
- Python 3.9 o superiore
- Pillow: installa da terminale
  pip install pillow

2) Posiziona i file
-------------------
- Cartella del sito: es. C:\sito\proloco-paterno  (deve contenere index.html, css/, assets/, ecc.)
- Cartella delle immagini originali: es. C:\foto_originali

3) Esegui lo script
-------------------
Esempi:
Windows:
  python make_albums.py --src "C:\foto_originali" --dest "C:\sito\proloco-paterno" --event-name evento-001

macOS / Linux:
  python3 make_albums.py --src "/Users/me/Pictures/originali" --dest "/Users/me/dev/proloco-paterno" --event-name evento-001 --thumb-long 900 --full-long 1800 --quality 85

4) Cosa fa
----------
- Crea: assets/img/foto/<evento-XXX>/thumbs e full
- Ordina le immagini per nome e le rinomina: img-001.jpg, img-002.jpg, ...
- Ridimensiona:
  - thumbs: lato lungo = 900px (modificabile con --thumb-long)
  - full:   lato lungo = 1800px (modificabile con --full-long)
- Qualità JPEG default 82 (modificabile con --quality)
- Crea anche thumbs/cover.jpg uguale alla prima thumb.

5) Note
------
- Supporta: .jpg .jpeg .png .webp .heic (se Pillow supporta HEIC sulla tua installazione)
- Usa sempre le thumbs nelle pagine HTML e linka alla versione full per l'apertura a schermo intero.
- Puoi cambiare l'indice iniziale con --start-index se vuoi continuare numerazione.
