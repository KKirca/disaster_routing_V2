# Veri Seti Analizi — Not Defteri

Her aday veri seti için: görsel kalitesi, etiket kalitesi, bina/hasar içeriği, genel karar. Bu analiz bitmeden V2-Faz 0 koduna geçilmeyecek.

---

## 1. Maxar Open Data (lokal indirilen, `disaster-routing/data/maxar/` + `maxar_tiles/`)

**Durum: İncelendi — mevcut haliyle işimize yaramıyor.**

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
