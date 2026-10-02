"""
V2-Faz 0: Ortam ve veri kurulumu.

Bu script'in yapması gerekenler (TODO — sen yazacaksın):
1. KATE-CD'yi CodeOcean capsule'den indir (HuggingFace Parquet DEĞİL —
   docs/ROADMAP.md'de belirtilen koordinat/preprocessing açık maddesi
   çözülmeden HuggingFace'e geri dönülmeyecek).
2. İndirilen train/val/test (404/44/38) örnek sayısını doğrula.
3. Her örneğin pre+post çift + binary etiket içerdiğini kontrol et.
4. CodeOcean capsule'ünde data/katecd/preprocessing/ altında bir
   grid/polygon GeoJSON dosyası olup olmadığını tespit et, sonucu
   docs/KARARLAR.md'ye not olarak ekle (V2-K01'e referansla).

Neden önce bunu yapıyoruz: Faz 2 (Model 1) bu veriye bağımlı, veri
doğrulanmadan model koduna geçmenin anlamı yok.
"""

def verify_katecd_download(data_dir: str) -> None:
    """KATE-CD indirmesinin beklenen yapıda olduğunu doğrular.

    TODO: train/val/test klasör sayıları, pre/post/label üçlüsünün
    her örnekte var olduğu, görüntü boyutlarının 512x512 olduğu
    kontrol edilecek.
    """
    raise NotImplementedError


if __name__ == "__main__":
    pass
