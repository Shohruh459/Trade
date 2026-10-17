# XAU/USD skalping: oldindan yozilgan (pre-registered) tadqiqot rejasi

Holat: **natijalarni ko'rishdan OLDIN yozilgan va commit qilingan.** Quyidagi qoidalar test paytida o'zgartirilmaydi. O'zgartirish kerak bo'lsa, alohida
"o'zgartirish" bandi sifatida sababi bilan yoziladi va natijaga qarab moslashtirilgan deb belgilanadi.

## 1. Nega bu reja (sinalgan EA'lardan olingan darslar)
Sinalgan 6 EA (FvgGold, TickRobust, klassik MR, Trend Breakout, Trillex 10S) xarajatdan keyin foyda bermadi (reports/summary_gold_EAs.md). Oltin narxida oddiy
qisqa muddatli bashorat yo'q: 1–5 daqiqalik qaytishlar korrelyatsiyasi −0.01…−0.05 va 2023 dan ~0; ertalabki harakat tushdan keyingisini bashorat qilmaydi (+0.024,
chegara 0.046). Eng o'zgaruvchan soatlar 12–16 UTC. Demak edge faqat shartli holatlardan kelishi mumkin. **Avval strategiya emas, hodisa tadqiqoti (event study):
parametr sozlamasdan, xarajatgacha va xarajatdan keyin narx qanday harakat qilishini o'lchaymiz.**

## 2. Bizning qoidalar (kelajakdagi EA uchun, hozircha faqat tamoyil)
1. Hamma narsa ATR birligida (punkt emas). 2. Bitim faqat kutilgan harakat ≥ 4× aylanma xarajat (jonli spreddan) bo'lsa. 3. Faqat o'zgaruvchan soatlar (12–16 UTC asosiy).
4. Bitimga risk 0.25–0.5%, kunlik limit 2%, umumiy DD 15% da o'chirish, lot "zinapoyasi" yo'q. 5. Har buyurtmada muddat; bitta pozitsiya yoki buyurtma.
6. Optimallashtirish mezoni xarajatdan keyingi kutilma (R), yutuq ulushi emas. 7. Tick darajasida sinov, real bid/ask, alohida tasdiqlash to'plami.

## 3. Gipoteza H1: o'ta katta bir daqiqalik "portlash"dan keyingi harakat (event study)
**Savol:** 12:00–16:00 UTC oralig'ida bir daqiqalik sham diapazoni keskin katta bo'lsa, keyingi 3/5/10 daqiqada narx shu yo'nalishda davom etadimi (continuation) yoki
qaytadimi (fade), xarajatdan keyin?

**Hodisa ta'rifi (o'zgarmas):**
- 1 daqiqalik O/H/L/C sham o'rta narxdan (mid = (bid+ask)/2) tick'lardan quriladi. Sham boshlanishi 12:00 ≤ t < 16:00 UTC.
- Hodisa: sham diapazoni (H−L) ≥ **4.0 ×** ATR14 (oldingi 14 ta 1 daqiqalik shamning TR o'rtachasi; hodisa shami kirmaydi). ATR > 0.
- Yo'nalish: sign(C − O); teng bo'lsa tashlanadi.
- Takroriy hodisalar: qabul qilingan hodisadan keyin 10 daqiqa ichidagilar tashlanadi.
- Kirish: hodisa shami yopilgandan **1 soniya keyingi** birinchi tick (kechikish farazi). Continuation = hodisa yo'nalishida, Fade = teskarisi.
  Sotib olish ask'da, sotish bid'da. Chiqish: kirishdan keyin h daqiqa o'tgandan keyingi birinchi tick, h ∈ {3, 5, 10}. SL/TP yo'q (sof vaqt bo'yicha chiqish, signalni toza o'lchash uchun).
- O'lchovlar: gross = mid-to-mid foyda ($/uns), net = real bid/ask bilan; o'rtacha, std, yutuq ulushi, kirish spredi; t-statistika **kun bo'yicha klasterlangan** standart xato bilan.
- Stress: net'ga har bitimda qo'shimcha $0.10 salbiy sirpanish.

**Asosiy hujayralar (6 ta):** {continuation, fade} × {3, 5, 10 daqiqa}. Ko'p test tuzatmasi (Bonferroni, 6 test): topilma uchun |t| ≥ 2.6 talab qilinadi.

**Namunalar:**
- *Discovery:* allaqachon yuklangan 15 tick fayl (har yil mart va sentyabr, 2019–2026, qoidasi `tick_sample.txt` da).
- *Confirmation:* alohida to'plam: har yil (2019–2026) iyun va dekabr oyining 1–20 kunlari orasida boshlanadigan birinchi fayl (Discovery bilan kesishmaydi).

**O'tish mezoni (hammasi bajarilishi shart):**
1. Discovery'da bir hujayra uchun **net o'rtacha > 0**, |t| ≥ 2.6, N ≥ 300.
2. Shu hujayra Confirmation'da **bir xil ishora**, net o'rtacha > 0, t ≥ 1.65.
3. Stress ($0.10 qo'shimcha sirpanish) bilan net o'rtacha hali ham > 0.
4. Foyda bitta yil/bitta oydan emas: kamida 70% yillarda net o'rtacha ishorasi musbat.

**Sezgirlik (faqat ma'lumot uchun, o'tish mezoniga ta'sir qilmaydi):** ATR ko'paytmasi 3, 5, 6; soat oynalari 07–10 UTC; hodisa yo'nalishi bo'yicha buy/sell alohida.

## 4. Natijaga qarab nima qilamiz
- **H1 o'tmasa** (gross ≈ 0 yoki net ≤ 0): skalping uchun bu gipotezani rad etamiz. H2/H3 ni (quyida) faqat yangi, oldindan yozilgan mezonlar bilan sinaymiz. Vaqtni tejash uchun H1–D1 trend strategiyalariga o'tish tavsiya etiladi.
- **H1 o'tsa:** ushbu hodisa uchun qoidalar yoziladi (kirish/chiqish/SL, ATR birligida, risk 0.25–0.5%), alohida tick sinovi va keyin demo.
- **Gross > 0, net ≤ 0** bo'lsa: ustunlik bor, lekin xarajat yeydi. Faqat yaxshi spredli (≤ $0.15) brokerda mumkinligi aniqlanadi; real spredni tasdiqlamay davom etilmaydi.

## 5. Keyingi gipotezalar (hozircha sinalmaydi)
- **H2:** 12:00–13:30 UTC oralig'idan 13:30 dan keyin chiqish (AQSh ochilishi). **H3:** tendensiya ichidagi xarajat-darvozali orqaga qaytish. Ularning aniq mezonlari H1 natijasidan KEYIN yoziladi.

## 6. Cheklovlar
Tick ma'lumoti Dukascopy (spred brokeringiznikidan farq qilishi mumkin; real ijro kechikishi/sirpanishi ko'rinmaydi). Yangiliklar kalendari yo'q (portlashlar kalendarsiz, faqat shamdan aniqlanadi).
