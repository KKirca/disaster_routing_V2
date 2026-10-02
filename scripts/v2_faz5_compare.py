"""
V2-Faz 5: V1 (disaster-routing) ile kontrollü karşılaştırma.

TODO — sen yazacaksın:
1. Ortak test senaryoları tanımla: aynı AOI, aynı başlangıç/bitiş
   noktaları, iki repoda da birebir aynı olmalı.
2. Metrikler: rota uzunluğu/süresi değişimi, kapanan yol oranı,
   hesaplama süresi, EMSR648 resmi hasar derecelendirmesine yakınlık
   (varsa).
3. UYARI: V1 ve V2 ayrı kod tabanı. Graph çıkarım parametrelerini
   (OSMnx versiyonu, AOI sınırları, basitleştirme ayarları) iki
   repoda da elle eşitlediğinden emin ol — aksi halde ölçtüğün fark
   hasar modelinden değil altyapı farkından kaynaklanabilir. Bu
   parametreleri docs/KARARLAR.md'de yan yana dokümante et.
"""

def compare_routes(v1_route, v2_route, graph_metadata) -> dict:
    """TODO: iki rotayı karşılaştırıp metrik sözlüğü döndür."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
