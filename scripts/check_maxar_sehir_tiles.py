"""
docs/maxar_sehir_merkezi_adaylari.csv listesindeki sehir merkezi
pre/post ciftlerinden birini indirip gorsel olarak kontrol etmek icin.

v2: Maxar ARD karolari dikdortgen tam dolu degil - gercek goruntu
karo icinde capraz/ucgen seklinde oturuyor (cekim acisina gore).
Bu yuzden artik sabit merkez yerine, dusuk cozunurluklu bir on-tarama
ile gercekten veri olan bolgeyi bulup oradan kirpiyoruz.

Kullanim:
  python scripts/check_maxar_sehir_tiles.py --sehir Antakya --n 1
"""
import argparse
import csv
import os
import urllib.request

import numpy as np
import rasterio
from rasterio.windows import Window
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


def find_data_center(src, probe_size: int = 512):
    """Dusuk cozunurluklu bir onizlemede en yogun veri bolgesini bulur."""
    W, H = src.width, src.height
    small = src.read([1, 2, 3], out_shape=(3, probe_size, probe_size))
    gray = small.sum(axis=0)
    mask = gray > 0  # siyah/nodata degil
    if not mask.any():
        return W // 2, H // 2  # hic veri yok, merkezi dondur (bos kalacak)
    ys, xs = np.where(mask)
    # veri bolgesinin agirlik merkezi
    cy, cx = ys.mean(), xs.mean()
    full_x = int(cx / probe_size * W)
    full_y = int(cy / probe_size * H)
    return full_x, full_y


def crop_preview(tif_path: str, out_png: str, size: int = 2048):
    with rasterio.open(tif_path) as src:
        W, H = src.width, src.height
        cx, cy = find_data_center(src, probe_size=512)
        x0 = min(max(0, cx - size // 2), max(0, W - size))
        y0 = min(max(0, cy - size // 2), max(0, H - size))
        window = Window(x0, y0, min(size, W - x0), min(size, H - y0))
        data = src.read([1, 2, 3], window=window)
    img = np.moveaxis(data, 0, -1)
    nonblack_pct = (img.sum(axis=-1) > 0).mean() * 100
    Image.fromarray(img).save(out_png)
    print(f"  kaydedildi: {out_png}  (dolu alan: %{nonblack_pct:.0f})")


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
        crop_preview(pre_tif, pre_tif.replace(".tif", "_preview.png"))
        crop_preview(post_tif, post_tif.replace(".tif", "_preview.png"))


if __name__ == "__main__":
    main()
