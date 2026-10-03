# V2 Kararlar Günlüğü

Format V1'deki (`disaster-routing/docs/Kararlar.md`) ile aynı: her karar numaralandırılır, gerekçesiyle birlikte kayıt altına alınır. Kararlar geriye dönük değiştirilmez — yeni bilgi gelirse yeni bir karar olarak eklenir ve eskisine referans verilir.

## V2-K01 — Repo, V1'den bağımsız sıfırdan kuruluyor

**Tarih:** 2026-10-02
**Karar:** `disaster_routing_V2`, `disaster-routing`'in fork/clone'u değil, bağımsız bir repo.
**Gerekçe:** Kullanıcı tercihi. Trade-off açıkça belirtildi: Faz 0/1/2/4'teki routing altyapısı (OSMnx, A*, hazard katmanları, EMSR648 validasyonu) iki kez yazılacak.
**Risk:** V2-Faz5'teki V1 vs V2 karşılaştırmasının geçerliliği, iki repodaki ortak altyapı parametrelerinin (graph çıkarımı, AOI sınırları) elle eşitlenmesine bağlı. Bu konu her faz sonunda tekrar gözden geçirilmeli.

## V2-K02 — Model 1 girdisi: pre+post çift (KATE-CD'nin kendi formatı)

**Tarih:** 2026-10-02
**Karar:** Model 1, tek görsel değil, pre+post çift görsel alıyor (KATE-CD'nin asıl change-detection formatına birebir uyumlu).
**Gerekçe:** Kullanıcı tercihi. KATE-PD'nin (post-only) formatına kıyasla, KATE-CD'nin etiketleme mantığıyla tam örtüşüyor.

## V2-K03 — Model 2'nin eğitim verisi kaynağı: AÇIK

**Tarih:** 2026-10-02
**Durum:** Karar verilmedi.
**Sorun:** KATE-CD'nin `house` sınıfı tanım gereği "hasarsız" demek — bu alt kümede ayrıca derecelendirilecek bir ground-truth hasar gradyanı yok. Model 2 (house alt kümesinde ince hasar skoru) bu nedenle KATE-CD üzerinde doğrudan eğitilemez.
**Seçenekler:**
1. Denetimsiz CVA (embedding farkı, sabit eşik yok, duyarlılık analiziyle raporlama).
2. Küçük manuel kalibrasyon seti (V1 Faz2c tarzı, ~100 örnek).
**Sonraki adım:** V2-Faz3 başlamadan bu karar verilecek, buraya V2-K03 güncellemesi olarak eklenecek.

## V2-K04 — Maxar çift seçim kriteri: hem pre HEM post eşiği geçmeli

**Tarih:** 2026-10-03
**Karar:** Bir Maxar pre/post çifti yalnızca HER İKİ taraf da (pre ve post ayrı ayrı) dolu-alan eşiğini (varsayılan %95, bkz. `scripts/maxar_filter_temiz.py`) geçerse kullanılabilir listesine giriyor. Tek tarafı temiz diğeri değilse çift tamamen elenir — kısmi/tek-taraflı kullanım yok.
**Gerekçe:** Kullanıcı tercihi, görsel doğrulamadan sonra netleşti. Antakya `031133023301` çifti örneği: pre=%100 ama post=%79 — pre tek başına kusursuz olsa da post'un eksik alanı değişim-tespiti (change detection) sinyalini bozar, bu yüzden çift bütün olarak elenir.
**Ölçüm notu:** Bu eşik, `check_maxar_sehir_tiles.py`'nin bastığı "dolu alan %" ile AYNI metrik değil — o script SEÇİLEN 2048x2048 kırpma penceresini ölçer, `maxar_filter_temiz.py` TÜM karoyu ölçer (ayrıntı: script docstring'i). Filtreleme kararı tüm karo üzerinden veriliyor.
**Sonraki adım:** `maxar_filter_temiz.py` 36 adayın tamamında çalıştırılacak, geçen alt küme `docs/maxar_temiz_ciftler.csv`'ye yazılacak, bu dosya Maxar'ın nihai kullanılabilir veri kümesi olacak.
