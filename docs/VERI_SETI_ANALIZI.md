# Veri Seti Analizi — Not Defteri

Her aday veri seti için: görsel kalitesi, etiket kalitesi, bina/hasar içeriği, genel karar. Bu analiz bitmeden V2-Faz 0 koduna geçilmeyecek.

---

## 1. Maxar Open Data (lokal indirilen, `disaster-routing/data/maxar/` + `maxar_tiles/`)

**Durum: Devam ediyor — şehir merkezi adayları bulundu, görsel doğrulama sürüyor (önizleme script'indeki kırpma hatası düzeltildi, nihai karar kullanıcı doğrulamasına bağlı).**

- **Kapsam:** Kahramanmaraş-turkey-earthquake-23 event'inden 7 eşleşen pre/post çifti (quadkey: 121,123,130,131,132,133,301), her biri 2048px karolara bölünmüş (567+567 PNG).
- **Koordinat:** Var, doğrulandı (EPSG:32637, orijinal GeoTIFF'lerde intact).
- **Etiket:** Yok (ham görüntü) — kriterlere uygun.
- **Görsel kontrol (5 quadkey'den merkez karo örneklendi — 121, 123, 130, 132):**
  - **İçerik:** Zeytin/bağ bahçeleri, seyrek müstakil çiftlik evleri. Yoğun kentsel doku YOK.
  - **Hasar:** Pre/post arasında görünür hiçbir yapısal fark yok — sadece ışık/gölge açısı değişiyor. Bina sayısı, çatı şekilleri birebir aynı.
  - **Ek sorunlar:** `121` quadkey'inin bazı karoları tamamen siyah/nodata (gerçek görüntü yok). `130`'un post görüntüsü yoğun bulut/duman örtüsü altında, kullanılamaz.
- **Karar:** Bu 7 çift, teknik kriterlere uysa da (etiketsiz+koordinatlı+pre/post) bina/hasar içeriği pratikte sıfıra yakın — **self-labeling için işe yaramaz**.
- **Kök neden bulundu:** İndirilen karonun gerçek koordinatı doğrulandı (rasterio + WGS84 dönüşümü): merkez **36.74°N, 37.07°E** — Kahramanmaraş şehir merkezinin (37.575°N, 36.923°E) ~95 km güneyinde, **Kilis'in Suriye sınırına yakın kırsal kesimi**. "Kahramanmaras-turkey-earthquake-23" event'i depremin etkilediği TÜM illeri (Kahramanmaraş, Hatay, Gaziantep, Kilis, Adıyaman, Malatya, Osmaniye) kapsayan geniş bir koleksiyon — indirilen 7 çift bu geniş AOI'nin rastgele bir kırsal kenarına denk gelmiş, herhangi bir şehir merkezi değil.
- **Açık soru / sıradaki adım:** Maxar'ın bu event için tam kataloğu 2.115 kayıt. Kahramanmaraş, Antakya, Adıyaman gibi şehir merkezlerinin koordinatlarını hedefleyerek (rastgele quadkey değil) kataloğu yeniden sorgulamak gerekiyor.

### Güncelleme — tam katalog şehir merkezi taraması (2026-10-03)

2.115 kayıtlık tam katalog indirilip 7 büyük etkilenen il merkezine (Kahramanmaraş, Antakya, Adıyaman, Gaziantep, Malatya, Osmaniye, Kilis — merkez koordinatlarına 8km yarıçap) göre filtrelendi. Sonuç, lokalde indirilen 7 çiftten çok daha iyi:

| Şehir | 8km içinde toplam karo | Temiz (bulut<%10) eşleşen pre/post çift |
|---|---|---|
| Gaziantep | 48 | 9 |
| Antakya | 47 | 8 |
| Kahramanmaraş | 40 | 4 |
| Adıyaman | 21 | 4 |
| Osmaniye | 25 | 4 |
| Malatya | 13 | 4 |
| Kilis | 13 | 3 |

**Toplam 36 temiz, eşleşen, şehir-merkezi pre/post çifti** — tam liste + indirme linkleri `docs/maxar_sehir_merkezi_adaylari.csv`'de. Post tarihleri depremden 2-27 gün sonrasına denk geliyor (Antakya için 2023-02-08/02-11 gibi çok erken tarihler de var — akut hasar için ideal).

**Kök neden netleşti:** Daha önce indirilen 7 çift, bu 2.115 kayıtlık kataloğun rastgele/kenar bir alt kümesiydi (Kilis kırsalı). Kataloğun kendisi şehir merkezlerinde iyi kapsama sağlıyor — sorun veri kaynağında değil, hangi alt kümenin indirildiğindeydi.

**Kalan adım (senin tarafında — bu sandbox S3'e erişemiyor):** `scripts/check_maxar_sehir_tiles.py` ile bu 36 çiftten birkaçını kendi makinende indirip gözle kontrol et — gerçekten görünür bina yıkımı var mı doğrula. Örnek: `python scripts/check_maxar_sehir_tiles.py --sehir Antakya --n 2`

**Ön değerlendirme:** Eğer görsel kontrol de doğrularsa, Maxar artık "işe yaramaz" değil — **en güçlü aday** haline geliyor (koordinatlı, etiketsiz, gerçek şehir merkezi, düşük bulut, deprem sonrası erken tarihli).

### Güncelleme — önizleme script'inde merkez-kırpma hatası bulundu (2026-10-03)

İlk görsel kontrol turunda (`check_maxar_sehir_tiles.py` v1, sabit geometrik merkez kırpma) Antakya'nın 2 çiftinden 4 önizlemeden 2'si tamamen/büyük ölçüde siyah çıktı:

| Dosya | Sonuç |
|---|---|
| `Antakya_031133023301_pre_preview.png` | **Dolu** — yoğun kentsel/endüstriyel doku, gerçek bina yapıları görünüyor |
| `Antakya_031133023301_post_preview.png` | Boş/nodata (siyah) |
| `Antakya_031133023231_pre_preview.png` | Boş/nodata (siyah) |
| `Antakya_031133023231_post_preview.png` | ~%70 siyah, altta dar bir şerit halinde gerçek görüntü |

**Kök neden:** Maxar ARD karoları sabit bir grid hücresi, ama hücre içindeki gerçek uydu görüntüsü (swath) dikdörtgen değil — çekim açısına (`view:azimuth`) bağlı olarak çapraz/üçgen bir şerit halinde oturuyor. Karonun geometrik merkezi bu şeridin İÇİNDE olmak zorunda değil; pre ve post çekimleri birbirinden bağımsız açılarla çekildiği için biri dolu biri boş çıkabiliyor. Bu, veri setinin veya seçilen şehir merkezi adaylarının kalitesizliğinden değil, önizleme script'inin saf (geometrik merkez) varsayımından kaynaklanan bir ölçüm hatasıydı — veri kaynağının kendisiyle ilgisi yok.

**Pozitif bulgu:** `301_pre` önizlemesi gerçek, yoğun kentsel içerik gösteriyor — bu da 36 çiftlik şehir-merkezi listesinin (CSV) doğru AOI'leri bulduğunu doğruluyor. Sorun kırpma yöntemindeydi, kataloğun kendisinde değil.

**Düzeltme:** `scripts/check_maxar_sehir_tiles.py` v2'ye yükseltildi — `find_data_center()` fonksiyonu önce düşük çözünürlüklü (512x512) bir probe okuyor, siyah olmayan piksellerin ağırlık merkezini buluyor, kırpmayı oradan yapıyor. Her kayıt artık `nonblack_pct` (dolu alan yüzdesi) diagnostiğini basıyor, böylece görsel kontrol yapmadan önce hangi çiftlerin boşa çıkacağı script çıktısından anlaşılabiliyor.

**Durum:** v2 script kullanıcıya teslim edildi, çalıştırılması ve sonuçların (özellikle gerçek bina yıkımı görünüp görünmediği) bildirilmesi bekleniyor. Nihai Maxar kararı bu sonuçlara bağlı — henüz hiçbir çiftte hem dolu hem de görünür hasarlı bir POST görüntü doğrulanmadı.

---

## 2. KATE-CD

**Durum: Kullanıcı kontrolü bekleniyor.**

- CodeOcean capsule'üne (`doi.org/10.24433/CO.3747729.v1`) buradan programatik erişim 403 ile engellendi (bot koruması). Kuzey'in kendi tarayıcısından kontrol etmesi gerekiyor: `data/katecd/preprocessing/` klasöründe `grid_maxar.geojson` / `katecd_polygons.geojson` benzeri bir koordinat dosyası var mı?
- HuggingFace dağıtımında (daha önce kontrol edildi) bu dosyalar yok — sadece `pre_image, post_image, label` alanları var, geometry yok.
- Görsel/etiket kalitesi kontrolü bu adımdan sonra yapılacak.

---

## 3. Planet Disaster Data

**Durum: İncelenecek.** (Not: 2023 Türkiye'yi kapsamadığı zaten doğrulandı — görsel kontrolü bölge-genişletme senaryosu için yapılacak.)

---

## 4. GlobalBuildingAtlas

**Durum: Elendi.** Pre/post bileşeni yok, tek-zamanlı statik bina envanteri. Tekrar değerlendirilmeyecek.
