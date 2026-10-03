"""
docs/maxar_sehir_merkezi_adaylari.csv listesindeki sehir merkezi
pre/post ciftlerinden birini indirip gorsel olarak kontrol etmek icin.

Kullanim:
  python scripts/check_maxar_sehir_tiles.py --sehir Antakya --n 1

Ne yapar:
1. CSV'den secilen sehrin ilk N eslesen ciftini alir.
2. pre/post visual.tif dosyalarini indirir (buyuk olabilir, ~30-70MB).
3. Ortadan 2048x2048'lik bir kirpma alip PNG olarak kaydeder, boylece
   tum dosyayi acmadan hizlica goz atabilirsin.

TODO: pre/post arasinda gercek bina yikimi gorunuyor mu, gozle
kontrol et ve docs/VERI_SETI_ANALIZI.md'ye notunu ekle.
"""
import argparse
import csv
import os
import urllib.request

import numpy as np
import rasterio
from PIL import Image

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "maxar_sehir_merkezi_adaylari.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "maxar_sehir_merkezi_kontrol")


def load_rows(sehir: str):
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["sehir"] == sehir]
    return rows


def download(url: str, out_path: str):
    if os.path.exists(out_path):
        return
    print(f"  indiriliyor: {url}")
    urllib.request.urlretrieve(url, out_path)


def center_crop_preview(tif_path: str, out_png: str, size: int = 2048):
    with rasterio.open(tif_path) as src:
        W, H = src.width, src.height
        x0 = max(0, W // 2 - size // 2)
        y0 = max(0, H // 2 - size // 2)
        window = rasterio.windows.Window(x0, y0, min(size, W - x0), min(size, H - y0))
        data = src.read([1, 2, 3], window=window)
    img = np.moveaxis(data, 0, -1)
    Image.fromarray(img).save(out_png)
    print(f"  kaydedildi: {out_png}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sehir", required=True)
    ap.add_argument("--n", type=int, default=1)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    rows = load_rows(args.sehir)[: args.n]
    if not rows:
        print(f"'{args.sehir}' icin CSV'de kayit yok.")
        return

    for i, row in enumerate(rows):
        qk = row["quadkey"]
        print(f"[{i}] quadkey={qk} pre={row['pre_tarih']} post={row['post_tarih']}")
        pre_tif = os.path.join(OUT_DIR, f"{args.sehir}_{qk}_pre.tif")
        post_tif = os.path.join(OUT_DIR, f"{args.sehir}_{qk}_post.tif")
        download(row["pre_url"], pre_tif)
        download(row["post_url"], post_tif)
        center_crop_preview(pre_tif, pre_tif.replace(".tif", "_preview.png"))
        center_crop_preview(post_tif, post_tif.replace(".tif", "_preview.png"))


if __name__ == "__main__":
    main()
