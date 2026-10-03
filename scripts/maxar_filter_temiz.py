"""
docs/maxar_sehir_merkezi_adaylari.csv'deki 36 adayin TAMAMI icin,
pre VE post gorsellerinin ikisinin de "temiz" (nodata/siyah alani
dusuk) olup olmadigini toplu kontrol eder.

Kritik tasarim karari: dosyalari TAM INDIRMIYORUZ.
check_maxar_sehir_tiles.py once urllib.request.urlretrieve ile
tum GeoTIFF'i (~30-70MB) diske cekip sonra okuyordu. 36 cift * 2
dosya = 72 tam indirme, bu ~3-5GB olurdu — sadece "temiz mi"
sorusuna cevap aramak icin gereksiz.

Bunun yerine GDAL'in /vsicurl/ sanal dosya sistemini kullaniyoruz:
rasterio.open("/vsicurl/https://...") ile dosyayi acinca, GDAL sadece
okudugumuz kadarini HTTP range request ile ceker. Biz out_shape ile
dusuk cozunurluklu (512x512) bir probe istedigimiz icin, GDAL
sunucudan sadece o probe'u olusturacak kadar veri cekiyor — tum
dosyayi degil.

ONEMLI FARK — bu scriptin olctugu % ile check_maxar_sehir_tiles.py'nin
bastigi "dolu alan %" AYNI SEY DEGIL:
  - check_maxar_sehir_tiles.py: SECTIGI 2048x2048 kirpma penceresi
    icindeki dolu alan yuzdesi (veri-yogun bolgeye merkezlenmis).
  - Bu script: TUM goruntunun (orijinal karo) dolu alan yuzdesi.
Bu script daha katidir: "secilen bir pencere iyi mi" sorusuna degil,
"bu karonun genel olarak ne kadari kullanilabilir" sorusuna cevap
verir. Filtreleme icin dogru soru budur, cunku ileride ayni karodan
birden fazla veya farkli boyutta pencere kirpmak isteyebiliriz.

Kullanim:
  python scripts/maxar_filter_temiz.py --esik 95

--esik: hem pre hem post'un gecmesi gereken minimum dolu-alan yuzdesi.
Varsayilan %95 seçildi cunku: 2048x2048 bir karoda %95 doluluk, kirpma
sirasinda veri-yogun bolgeye merkezlenince pratik olarak %100 dolu bir
pencere bulmaya yetecek kadar pay birakiyor (bkz. find_data_center,
check_maxar_sehir_tiles.py). Bu sayiyi degistirirsen NEDEN degistirdigini
docs/VERI_SETI_ANALIZI.md'ye not et — keyfi bir sayi degil, bir
muhendislik kararidir.
"""
import argparse
import csv
import os

import rasterio

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "maxar_sehir_merkezi_adaylari.csv")
OUT_CSV = os.path.join(os.path.dirname(__file__), "..", "docs", "maxar_temiz_ciftler.csv")


def vsicurl(url: str) -> str:
    return "/vsicurl/" + url


def nonblack_pct_whole(url: str, probe_size: int = 512) -> float:
    """Tum goruntunun (orijinal karo) dolu-alan yuzdesi, indirmeden."""
    with rasterio.open(vsicurl(url)) as src:
        small = src.read([1, 2, 3], out_shape=(3, probe_size, probe_size))
    gray = small.sum(axis=0)
    return float((gray > 0).mean() * 100)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--esik", type=float, default=90.0,
                     help="Hem pre hem post'un gecmesi gereken min. dolu-alan yuzdesi")
    args = ap.parse_args()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    for row in rows:
        try:
            pre_pct = nonblack_pct_whole(row["pre_url"])
            post_pct = nonblack_pct_whole(row["post_url"])
        except Exception as e:
            print(f"HATA  {row['sehir']:15s} {row['quadkey']:14s} -> {e}")
            continue
        gecti = pre_pct >= args.esik and post_pct >= args.esik
        durum = "GECTI" if gecti else "elendi"
        print(f"{row['sehir']:15s} {row['quadkey']:14s} pre=%{pre_pct:5.1f} post=%{post_pct:5.1f}  {durum}")
        results.append({
            **row,
            "pre_dolu_pct": f"{pre_pct:.1f}",
            "post_dolu_pct": f"{post_pct:.1f}",
            "esik_gecti": gecti,
        })

    gecenler = [r for r in results if r["esik_gecti"]]
    print(f"\n{len(gecenler)}/{len(results)} cift esigi (>=%{args.esik} hem pre hem post) gecti.")

    if results:
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"Tum sonuclar (gecen+elenen) kaydedildi: {OUT_CSV}")


if __name__ == "__main__":
    main()
