"""
docs/maxar_sehir_merkezi_adaylari.csv listesindeki sehir merkezi
pre/post ciftlerinden birini indirip gorsel olarak kontrol etmek icin.

v3 — ONEMLI DUZELTME (V2-K07, docs/KARARLAR.md):
v2'de crop merkezi pre ve post icin BAGIMSIZ hesaplaniyordu. Maxar ARD
karolari sabit piksel-grid oldugu icin (ayni quadkey'de pre/post ayni
koordinat sistemini paylasir), bagimsiz merkezler SECILDIGINDE iki
onizleme FARKLI cografi bolgeleri gosterebiliyordu — degisim tespiti
(CVA, Model 2'nin temeli) icin bu kabul edilemez.

v3'te crop merkezi artik TEK: pre'nin ve post'un dusuk-cozunurluklu
veri maskelerinin KESISIMINDEN (ikisinde de veri olan bolge) hesaplanan
ortak bir agirlik merkezi kullaniliyor. pre_preview ve post_preview
artik AYNI pencereyi gosteriyor — merkezleri ust uste gelir.

Bu scriptin ureteceği onizleme SADECE gorsel kontrol icindir. Kullanim
karari BURADA verilmiyor — o, TUM KARO uzerinden olcum yapan
maxar_filter_temiz.py ile veriliyor (V2-K05/K07: esik tum karoda
sabit kaldi, crop-bazli bir metrige GECILMEDI).

Kullanim:
  python scripts/check_maxar_sehir_tiles.py --sehir Antakya --n 2
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


def nonblack_mask(src, probe_size: int = 512):
    small = src.read([1, 2, 3], out_shape=(3, probe_size, probe_size))
    gray = small.sum(axis=0)
    return gray > 0


def shared_center(pre_src, post_src, probe_size: int = 512):
    """pre VE post'un veri maskelerinin KESISIMINDEN tek bir ortak merkez bulur."""
    W, H = pre_src.width, pre_src.height
    mask_pre = nonblack_mask(pre_src, probe_size)
    mask_post = nonblack_mask(post_src, probe_size)
    inter = mask_pre & mask_post
    if not inter.any():
        return None
    ys, xs = np.where(inter)
    cy, cx = ys.mean(), xs.mean()
    full_x = int(cx / probe_size * W)
    full_y = int(cy / probe_size * H)
    return full_x, full_y


def crop_at(tif_path: str, cx: int, cy: int, out_png: str, size: int = 2048):
    with rasterio.open(tif_path) as src:
        W, H = src.width, src.height
        x0 = min(max(0, cx - size // 2), max(0, W - size))
        y0 = min(max(0, cy - size // 2), max(0, H - size))
        window = Window(x0, y0, min(size, W - x0), min(size, H - y0))
        data = src.read([1, 2, 3], window=window)
    img = np.moveaxis(data, 0, -1)
    nonblack_pct = (img.sum(axis=-1) > 0).mean() * 100
    Image.fromarray(img).save(out_png)
    print(f"  kaydedildi: {out_png}  (dolu alan: %{nonblack_pct:.0f})")


def process_pair(pre_tif: str, post_tif: str, pre_png: str, post_png: str, size: int = 2048):
    with rasterio.open(pre_tif) as pre_src, rasterio.open(post_tif) as post_src:
        if (pre_src.width, pre_src.height) != (post_src.width, post_src.height):
            print("  UYARI: pre ve post boyutlari farkli — ortak merkez guvenilir olmayabilir.")
        center = shared_center(pre_src, post_src)
    if center is None:
        print("  ATLANDI: pre ve post'un dolu bolgeleri hic ortusmuyor, ortak kirpma mumkun degil.")
        return
    cx, cy = center
    crop_at(pre_tif, cx, cy, pre_png, size)
    crop_at(post_tif, cx, cy, post_png, size)


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
        process_pair(
            pre_tif, post_tif,
            pre_tif.replace(".tif", "_preview.png"),
            post_tif.replace(".tif", "_preview.png"),
        )


if __name__ == "__main__":
    main()
