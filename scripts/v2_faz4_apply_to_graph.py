"""
V2-Faz 4: Model 1 + Model 2 çıktısını A* kenar ağırlığına uygula.

TODO — sen yazacaksın:
1. destroyed -> kapalı (None) ya da çok yüksek sabit gecikme.
2. house + Model 2 skoru -> kademeli gecikme (V1'deki damage_pressure
   formülüne benzer bir fonksiyon tasarla, ama girdi Model 2'nin
   sürekli skoru olacak).
3. Conservative merging ilkesi: Faz 1'deki fay/sıvılaşma kaynaklı
   kapalı kenarları bu faz GEVŞETEMEZ, sadece ek kısıtlama ekleyebilir.
"""

def apply_damage_to_graph(graph, model1_outputs, model2_scores):
    """TODO: graph kenarlarını model çıktılarına göre güncelle."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
