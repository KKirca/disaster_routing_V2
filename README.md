# disaster_routing_V2

OtonomAraç graduation project — **V2 mimarisi**: deprem sonrası mobil trafo nakliyesi için güzergah planlama.

Bu repo, [disaster-routing](../disaster-routing) (V1) projesinin bağımsız bir dalı değil, **kademeli (cascade) hasar tespiti mimarisiyle sıfırdan kurulan ikinci bir uygulamasıdır**. Amaç: aynı problem için iki farklı hasar-tespit yaklaşımını (V1: tek-aşamalı Siamese CNN + CVA, V2: iki-aşamalı cascade) birbirinden bağımsız inşa edip, sonunda kontrollü bir performans/verim karşılaştırması yapmak.

## V1'den fark

| | V1 (disaster-routing) | V2 (bu repo) |
|---|---|---|
| Hasar tespiti | Tek aşama: Siamese CNN + CVA, 4 sınıf | İki aşama (cascade) |
| Aşama 1 | — | KATE-CD (pre+post çift) → ikili sınıflandırıcı: `destroyed` / `house` |
| Aşama 2 | — | Sadece `house` alt kümesinde CVA tabanlı ince hasar skoru |
| Yol ağırlıklandırma | `damage_pressure` formülü (tek skor) | `destroyed` → kapalı/ağır gecikme; `house`+CVA skoru → kademeli gecikme |

Routing motoru (OSMnx + A*), conservative merging ilkesi (hasar katmanı fay/sıvılaşma kapalı etiketini gevşetemez) ve genel yaklaşım V1 ile aynı mantığı izler — bkz. [docs/ROADMAP.md](docs/ROADMAP.md).

## Durum

Kurulum aşamasında. Bkz. [docs/ROADMAP.md](docs/ROADMAP.md) ve [docs/KARARLAR.md](docs/KARARLAR.md).
