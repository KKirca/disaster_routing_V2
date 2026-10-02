"""
V2-Faz 2: Model 1 — destroyed / house ikili sınıflandırıcı (KATE-CD).

TODO — sen yazacaksın:
1. Girdi mimarisine karar ver: concat (pre+post 6 kanal tek encoder)
   mi, iki-kollu (siamese, paylaşımlı ağırlık) mı? docs/KARARLAR.md'ye
   V2-K04 olarak ekle, gerekçesiyle.
2. KATE-CD'nin kendi train/val/test bölünmesini kullan (404/44/38) —
   harici karışım yok.
3. Sınıf dengesizliği varsa (undamaged çoğunlukta olabilir) sadece
   accuracy ile yetinme — precision/recall/F1 raporla.

Çıktı: destroyed / house etiketi + olasılık skoru (Faz 4'te eşikleme
için olasılık skoru gerekebilir, sadece hard-label yeterli olmayabilir).
"""

def build_model():
    """İkili sınıflandırıcı mimarisi.

    TODO: encoder seçimi (ör. ResNet backbone), girdi kanal sayısı
    (concat ise 6, siamese ise 3+3) netleştirilecek.
    """
    raise NotImplementedError


def train(model, train_loader, val_loader):
    """TODO: eğitim döngüsü, early stopping, checkpoint kaydı."""
    raise NotImplementedError


def evaluate(model, test_loader):
    """TODO: precision/recall/F1, confusion matrix."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
