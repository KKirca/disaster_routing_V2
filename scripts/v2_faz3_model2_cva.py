"""
V2-Faz 3: Model 2 — house alt kümesinde ince hasar skoru (CVA).

BAŞLAMADAN ÖNCE: docs/KARARLAR.md V2-K03 kararı verilmiş olmalı
(denetimsiz CVA mı, küçük kalibrasyon seti mi). Karar verilmeden bu
dosyaya kod yazmanın anlamı yok — hangi veriyle eğitileceği/
çalıştırılacağı o karara bağlı.

TODO — sen yazacaksın (V2-K03 kararına göre):
- Denetimsiz seçildiyse: pre/post embedding'leri çıkar (Model 1'in
  encoder'ı yeniden kullanılabilir mi, yoksa ayrı bir encoder mı?),
  CVA (change vector analysis) ile fark büyüklüğü hesapla, sabit eşik
  KULLANMA — duyarlılık analiziyle raporla (V1'in eşik politikasına
  paralel, docs/ROADMAP.md'ye bak).
- Kalibrasyon seti seçildiyse: küçük bir manuel etiketleme turu kur
  (V1 Faz2c'ye benzer, ~100 örnek), inter-annotator agreement
  (Cohen's kappa) hesapla.
"""

def compute_cva_score(pre_embedding, post_embedding):
    """TODO: embedding farkının büyüklüğünü sürekli bir skora çevir."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
