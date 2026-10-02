# V2 Yol Haritası — Cascade Hasar Tespiti Mimarisi

Bu doküman, `disaster_routing_V2` reposunun fazlarını, her fazın kabul kriterini ve açık kalan mimari kararları tanımlar. V1 (`disaster-routing`) ile ortak hiçbir kod paylaşılmıyor — bilinçli bir tercih (bkz. KARARLAR.md V2-K01). Bu yüzden V1'de edinilen öğrenmeler burada bir bölüm olarak devralınıyor; kod devralınmıyor, hatalar devralınmasın diye.

## Mimari özet

```
                 ┌─────────────────────┐
  pre+post ───►  │  Model 1 (KATE-CD)  │ ──► "destroyed" ──► yol: kapalı / ağır gecikme
  görsel çifti    │  ikili sınıflandırıcı│
                 └──────────┬───────────┘
                            │ "house"
                            ▼
                 ┌─────────────────────┐
                 │  Model 2 (CVA)       │ ──► sürekli hasar skoru ──► yol: kademeli gecikme
                 │  house alt kümesinde │
                 └─────────────────────┘
                            │
                            ▼
                 A* ağırlıklı güzergah hesabı
```

## V2-Faz 0 — Ortam ve veri kurulumu

**Amaç:** Çalışma ortamını kur, KATE-CD verisini edin.

- `environment.yml` ile conda ortamı (`disaster-v2`).
- KATE-CD'yi CodeOcean capsule üzerinden indir (HuggingFace Parquet değil — CodeOcean asıl kaynak, `preprocessing/` klasörü koordinat/metadata içerebilir, bu doğrulanmadan HuggingFace'e geri dönülmeyecek).
- **Açık madde:** KATE-CD CodeOcean capsule'ünde `grid_maxar.geojson` / `katecd_polygons.geojson` benzeri bir dosya var mı? Varsa koordinat sorunu çözülür, çıktı bir rapor olarak `docs/KARARLAR.md`'ye eklenecek.

**Kabul kriteri:** `conda activate disaster-v2` çalışıyor, KATE-CD train/val/test (404/44/38) diskte, her örnek pre+post çift + binary etiket olarak doğrulanmış.

## V2-Faz 1 — Routing altyapısı

**Amaç:** OSMnx tabanlı yol grafiği + A* arama, V1'den bağımsız yeniden yazım.

- Kahramanmaraş AOI için graph indirme/temizleme.
- A* araması, `edge_cost` **None** dönecek kapalı kenarlar için (bkz. Devralınan Öğrenmeler).
- Conservative merging ilkesi: hasar katmanı, fay/sıvılaşma kaynaklı `closed` etiketini gevşetemez — sadece ek kısıtlama getirebilir.

**Kabul kriteri:** Hasarsız bir graph üzerinde uçtan uca bir rota hesaplanabiliyor (negatif kontrol).

## V2-Faz 2 — Model 1: destroyed / house ikili sınıflandırıcı

**Amaç:** KATE-CD pre+post çiftinden ikili sınıflandırma.

- Girdi: pre (3ch) + post (3ch) — concat ya da iki-kollu (siamese) encoder, karara bağlı.
- Çıktı: `destroyed` / `house` (KATE-CD'nin kendi binary etiketine birebir karşılık gelir — 4 sınıfa zorlama yok).
- KATE-CD'nin kendi train/val/test bölünmesi kullanılacak (401/44/38), harici karışım yok.

**Kabul kriteri:** Test setinde precision/recall raporu (sınıf dengesizliği varsa — KATE-CD'de undamaged çoğunlukta olabilir, tek metrik accuracy ile yetinilmeyecek).

## V2-Faz 3 — Model 2: house alt kümesinde ince hasar skoru

**Amaç:** `house` olarak işaretlenmiş binalarda pre/post embedding farkından sürekli bir hasar skoru üretmek.

**Açık karar — bu faz başlamadan netleşmeli:**
KATE-CD'nin `house` etiketi tanım gereği zaten "hasarsız" demektir; bu sınıfın içinde ayrıca derecelendirilecek bir ground-truth hasar gradyanı KATE-CD'de yok. İki seçenek:
1. Denetimsiz: CVA (change vector analysis) ile embedding farkı → sürekli skor, sabit eşik yok, duyarlılık analiziyle raporlanır (V1'in K-kararına paralel).
2. Küçük bir manuel kalibrasyon seti (V1'in Faz2c'sine benzer, ~100 örnek) ile denetimli ince ayar.

Bu karar verilmeden Faz 3 koduna başlanmayacak — `docs/KARARLAR.md`'ye V2-K03 olarak işlenecek.

**Kabul kriteri:** Karar + gerekçesi dokümante edilmiş, seçilen yönteme göre model eğitilmiş/çalıştırılmış.

## V2-Faz 4 — Birleştirme: yol ağırlıklandırma

**Amaç:** Model 1 + Model 2 çıktısını A* kenar ağırlığına çevirmek.

- `destroyed` → kapalı ya da çok yüksek sabit gecikme.
- `house` + Model 2 skoru → kademeli gecikme (V1'deki `damage_pressure` formülüne benzer mantık, ama girdi kaynağı farklı).
- Conservative merging ilkesi burada da geçerli (Faz 1'deki kapalı kenarlar gevşetilemez).

**Kabul kriteri:** Hasar katmanı uygulanmış bir graph üzerinde rota, hasarlı bölgelerden kaçınıyor (görsel + sayısal doğrulama).

## V2-Faz 5 — V1 ile kontrollü karşılaştırma

**Amaç:** Aynı AOI, aynı test senaryoları üzerinde V1 (tek-aşamalı) ile V2 (cascade) performans/verim karşılaştırması.

- Ortak test kümesi: aynı başlangıç/bitiş noktaları, aynı AOI.
- Metrikler: rota uzunluğu/süresi değişimi, kapanan yol oranı, hesaplama süresi, (varsa) EMSR648 resmi hasar derecelendirmesine yakınlık.
- **Dikkat:** V1 ve V2 ayrı repo/ayrı kod olduğu için graph çıkarım parametreleri (OSMnx versiyonu, AOI sınırları, basitleştirme ayarları) elle eşitlenmeli — aksi halde fark, hasar modelinden değil altyapı farkından kaynaklanabilir. Bu riski azaltmak için her iki repoda da kullanılan graph parametreleri `docs/KARARLAR.md`'de yan yana dokümante edilecek.

**Kabul kriteri:** İki yöntemin karşılaştırmalı rapor halinde, sayısal metriklerle sunulması.

---

## Devralınan Öğrenmeler (V1'den, kod değil bilgi)

- `edge_cost`, kapalı kenarlar için `math.inf` değil **`None`** döndürmeli — A*'ın kenarı doğru elemesi için.
- OSMnx grafiğini Türkçe locale'de kaydetme/okuma GraphML'i bozabilir — `LC_ALL=C` ile çalıştırılmalı.
- Kalibrasyon/eğitim verisinde bölgesel/afet-türü uyumsuzluğu (V1'de kasırga ağırlıklı xBD örnekleriyle deprem kalibrasyonu) sistematik iyimserlik yanlılığına yol açtı — KATE-CD zaten Türkiye depremine özgü olduğu için bu risk V2'de daha düşük, ama Model 2 için harici veri kullanılırsa tekrar gündeme gelir.
- Eşik politikası: sabit bir eşik (ör. 0.50) ground truth yokluğunda keyfi olur — V1 bunu duyarlılık analiziyle çözdü, V2-Faz3'teki açık kararda aynı mantık geçerli.
