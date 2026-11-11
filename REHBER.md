# ARGUS'a katkı rehberi

Bu repo tarayıcının tamamı: basılacak her parça ayrı bir dosya, ortak ölçüler tek bir yerde, ve her gönderimde parçaların hâlâ birbirine uyduğunu kontrol eden otomatik testler var. Sen bir parça alırsın, kendi AI'ına yaptırırsın, sistem kontrol eder, yeşilse birleştiririz.

## Sistem 1 dakikada

**Proje sitesi:** https://mmucteba.github.io/argus/ — genel durum, doğrulama haritası, 3D görüntüleyici, parça listesi ve kablolama. Her değişiklikten ve her sabahki denetimden sonra kendini yeniler.

- **Parçalar:** `parts/<modül>/<parça>.py`. Her basılacak parça tek bir dosya.
- **Ortak ölçüler:** `spec/` klasöründe. Buna sadece entegratör (Mücteba) dokunur.
- **Kontrat:** her parçanın kullanabileceği bir kutu (zarf) ve tutması gereken delikler var. Bu kutunun içinde kalıp delikleri koruduğun sürece başkasının parçasını bozamazsın.
- **Kontroller:** her gönderimde kendiliğinden çalışır. Yeşil tamam demek. Kırmızıysa rapor neyin, nerede, neden bozulduğunu söyler.
- **Görevler:** Issues sekmesinde. Her görevin içinde, herhangi bir AI'a yapıştırılabilecek hazır bir prompt var.

## Önce doğrula, sonra tasarla

Tasarımdaki her gerçek ölçü (satın aldığımız parçaların boyutları, yazıcının delikleri nasıl bastığı) `spec/facts.yaml` dosyasında, kaynağıyla birlikte duruyor:
- **Zayıf kaynaklar:** `assumed` (tahmin) ve `listing` (mağaza sayfası). Bunlar doğrulanmış sayılmaz.
- **Doğrulanmış sayılanlar:** `datasheet` (üretici çizimi), `standard` (standart ölçü) ve `measured` (kendi parçamızı kumpasla ölçtük).

Her parça hangi ölçüleri kullandığını sistem kendisi takip eder. Böylece bir ölçü değişince ondan etkilenen her parça otomatik işaretlenir.

Her ölçü hangi satın alınan parçadan geldiğini de söyler (`buy:`, `spec/bom.yaml` anahtarları). Ürün seçilmemişse ya da sadece bir arama linki varsa ölçü `assumed` kalır. Önce tam ürünü seç ve ürün sayfasının linkini `bom.yaml`'a koy; mağaza sayfası `listing` yapar, üretici çizimi `datasheet`, kendi parçamızı ölçmek `measured`.

**Parçaların durumu:**
- **provisional:** doğrulanmamış bir ölçü kullanıyor. Tasarımı taslak, görevi `waiting` etiketli.
- **needs re-check:** bütün ölçüleri doğrulandı, parça baştan kontrol edilip gerekirse yeniden tasarlanacak. Sistem bunun için kendisi görev açar.
- **confirmed:** doğrulanmış ölçülere göre kontrol edildi. Bir ölçü sonradan değişirse kendiliğinden tekrar "needs re-check" olur.

**Verify (doğrulama) görevi nasıl yapılır:**
1. `verify` etiketli bir görev al, kendini ata.
2. Parça elindeyse kumpasla ölç ve cetvelli fotoğraf çek. Elinde değilse üreticinin datasheet'ini bul (mağaza sayfası yetmez); AI'a görevi yapıştırıp aratabilirsin.
3. Kanıtı `evidence/<parça>/` klasörüne koy (fotoğraf veya PDF), ya da linki yaz.
4. `spec/facts.yaml` dosyasında o parçanın `values`, `status`, `evidence` alanlarını güncelle, `by` (adın) ve `date` ekle. Pull request aç.

Bu yüzden bir tasarım görevi `waiting` etiketliyse, önce altındaki yorumda listelenen verify görevlerini yap.

**Her gün sabah 07:23'te otomatik denetim çalışır:**
- verify ve re-check görevlerini açar, biteni kapatır
- **Status board** issue'sunu günceller: hangi ölçü eksik, hangi parça onu bekliyor ve ikisinin bağlantı grafiği

## Görev almak

1. **Issues** sekmesinde `design` etiketli, kimseye atanmamış bir görev seç.
2. Sağdaki **Assignees** kısmından kendini ata. Atanmış görev "alındı" demek, başkası almaz.
3. **Prompt** kutusundaki metnin tamamını kopyala.

## Yol A: Sadece sohbet (Claude.ai, ChatGPT, Gemini)

1. Prompt'u AI'a yapıştır. Görevde "Fable" yazıyorsa ve erişimin varsa Fable'ı kullan.
2. AI sana parçanın tam dosyasını ve kısa bir not verecek. Dosyayı aynı adla kaydet (örneğin `lens_clamp.py`).
3. GitHub'da parçanın klasörüne git (örneğin `parts/optics`). **Add file → Upload files**, dosyayı sürükle.
4. Alttan **Create a new branch for this commit and start a pull request** seç. **Propose changes**, sonra **Create pull request**. Açıklamaya AI'ın notunu ve `Closes #<görev no>` yaz.
5. 2-3 dakika bekle. Kontroller çalışır ve sonucu pull request'e yorum olarak yazar.
6. Kırmızıysa raporu kopyala, AI'a "bu kontroller başarısız oldu, düzelt" de. Yeni dosyayı aynı pull request'in branch'ine tekrar yükle.

## Yol B: Kodlama ajanı (Claude Code, Codex, Cursor)

1. Repo'da **Code → Codespaces → Create codespace** de; Python, kütüphaneler, Claude Code ve Codex kurulu gelir. Ya da repo'yu kendi bilgisayarına klonla ve `pip install -r requirements.txt` çalıştır.
2. Terminalde `claude` ya da `codex` aç, prompt'u ver. Ajan `CONTEXT.md` dosyasını okuyup kuralları öğrenir.
3. `python tools/check.py <parça>` (saniyeler) ve `python tools/check.py` (yaklaşık 1 dakika) çalışsın, hepsi geçsin.
4. Ajana "open a pull request" de, ya da branch açıp kendin gönder.

## Rapor ne diyor

- **FAIL:** birleştirilemez. Rapordaki "What to do" sütunu ne yapacağını söyler.
- **WARN:** birleştirilebilir ama bakılmalı. Örneğin ölçülmemiş bir değer, ya da destek isteyebilecek bir çıkıntı.
- **En sık hatalar:**
  - zarfın dışına taşmak
  - bir deliği kapatmak veya kaydırmak
  - parçanın birbirine değmeyen iki ayrı parçaya bölünmesi

## Ortak bir şey değişmeliyse

Bazen parça, başka parçaların bağlı olduğu bir şey değişmeden olmaz: daha büyük bir kutu, kayan bir delik, yeni bir ölçü, farklı bir satın alınan parça. O zaman:
1. Ortak dosyalara dokunma.
2. **Issues → New issue → Change request** aç. Neyin değişmesi gerektiğini, nedenini ve yeni sayıları yaz.
3. Entegratör karar verir ve spec sürümünü artırır. Kontroller etkilenen parçaları gösterir, onlar için yeni görev açılır.

Ajanların birbirinin işini bozmaması bu kurala bağlı. Herkes kendi dosyasında kalır, ortak değişiklikler tek kapıdan geçer.

## Fable'ı nerede kullanalım

Fable erişimi kısıtlı, o yüzden:
- **Fable:** sadece "Best done by: Fable" yazan zor geometri görevleri.
- **Diğer AI'lar:** küçük düzeltmeler, raporda çıkan hataları düzeltmek, dokümantasyon, yazılım.
- **Kontroller:** AI harcamaz, betik olarak çalışır.
- **İpucu:** Fable'a prompt'un tamamını tek seferde ver. Repo'yu gezdirme; gereken her şey prompt'ta.

## Ölçüm getirmek

Gerçek parça elimize geçince (LED kartı, endstop, lens):
1. Kumpasla ölç.
2. Yanına cetvel koyup fotoğraf çek.
3. İlgili görevin altına yorum olarak yaz.

Bu bilgiler o görevin girdisi olur ve tahmini değerlerin yerini alır.

## Kurallar

1. Sadece görevdeki dosyayı değiştir.
2. Ölçüleri `spec`'ten oku, kopyalama.
3. Zarfın içinde kal, delikleri koru.
4. Parça desteksiz basılabilsin.
5. Tahmin ettiğin her sayıyı notunda söyle.
