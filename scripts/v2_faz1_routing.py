"""
V2-Faz 1: Routing altyapısı (OSMnx + A*), V1'den bağımsız.

TODO — sen yazacaksın:
1. Kahramanmaraş AOI için OSMnx ile yol grafiği indir.
2. A* arama fonksiyonu yaz. KRİTİK: kapalı kenarlar için edge_cost
   fonksiyonu math.inf DEĞİL, None döndürmeli (V1'de bulunan hata,
   bkz. docs/ROADMAP.md "Devralınan Öğrenmeler").
3. Hasarsız bir graph üzerinde uçtan uca bir rota hesapla (negatif
   kontrol — Faz 2/3/4'e geçmeden önce bu çalışıyor olmalı).

Not: Grafiği kaydedip okurken LC_ALL=C ile çalıştır (Türkçe locale
GraphML'i bozabiliyor, V1'de yaşanmış bir sorun).
"""

def build_graph(aoi_bounds) -> "networkx.MultiDiGraph":
    """OSMnx ile AOI için yol grafiğini indirir.

    TODO: aoi_bounds formatını belirle (bbox mi, polygon mu),
    osmnx.graph_from_bbox / graph_from_polygon kullan.
    """
    raise NotImplementedError


def edge_cost(u, v, data: dict):
    """A* için kenar maliyeti.

    TODO: kapalı kenar -> None döndür (math.inf DEĞİL).
    """
    raise NotImplementedError


if __name__ == "__main__":
    pass
