# MTF2: "sifatli H1 trend boshlanishi"ga kirish va uzoq ushlash — oldindan yozilgan sinov rejasi

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida bitta, parametrlar muzlatilgan. Sinov faqat ko'rilmagan ma'lumotda (Final va FX) bir marta o'tkaziladi.
Har qanday o'zgartirish 9-bo'limdagi jurnalga sababi bilan yoziladi va natijaga moslashtirilgan deb belgilanadi.

## 1. Nega bu qoida (nimaga tayanamiz va nimaga tayanmaymiz)
`STRATEGY_MTF.md` ning Discovery (2018–2020) va Validation (2021–2022) bosqichlarida **ikki marta takrorlangan** tavsifiy topilma:
H1 trend yo'nalishi almashganda (EMA20/EMA50 kesishuvi), agar shu paytda M1, M5 va M15 ham xuddi shu tomonda bo'lsa (**Lfull**) va H1 "trendli" bo'lsa (**T**, ER_H1 ≥ 0.30),
trend **uzoqroq davom etadi va uzoqroq masofa bosadi** (mediana davomiyligi ~40–59 H1 bar ga qarshi 21–33; maksimal harakat ~2.5 ATR ga qarshi ~1 ATR; hammasi p < 0.02, ikkala davrda).
H4 yo'nalishi bilan bog'liq topilma takrorlanmadi, shuning uchun qoidada **H4 ishlatilmaydi**.
Lekin: davomiylik ≠ foyda. Eski "TP 2 ATR / SL 1 ATR" qoidasi xarajatdan keyin foyda bermagan edi. Bu reja **yangi chiqish qoidasini** (uzoq trendni ushlab turish) sinaydi.
Chiqish qoidasi Discovery/Validation da foyda bo'yicha sinalmagan va sozlanmagan: u amaliyotda keng tarqalgan oddiy variant sifatida a priori tanlangan (bu o'ziga xos erkinlik darajasi, 7-bo'limda xavf sifatida ko'rsatilgan).

## 2. Ma'lumot
- **Final (qaror shu yerda):** XAUUSD M1 BID (ZombitX64 dataseti, UTC), 2023-01-01 → 2025-02-28. **Hali hech qanday qoida bilan sinalmagan.** M5/M15/H1/H4 M1 dan `backtest/mtf.py` dagi kabi quriladi.
- **FX tasdiqlash (qaror shu yerda):** EURUSD, GBPUSD, AUDUSD M1 (`qleap/dukascopy-ticks-ohlcv`, 1min), 2020-04 → 2025-12. Hali sinalmagan.
- **Dev (faqat izchillik tekshiruvi):** XAUUSD 2018-01-22 → 2022-12-31 (Discovery+Validation). Bu davrlar qoidaning **g'oyasini** shakllantirgan, shuning uchun u yerdagi natija mustaqil dalil emas; faqat 6-bo'limdagi C4 uchun.
- Indikatorlar/bar qurilishi `STRATEGY_MTF.md` 4-bo'limdagidek (EMA20/50, ER n=20, ATR_H1 = 14 barli SMA(TR)). Faqat to'liq yopilgan barlar.

## 3. Qoida (hammasi muzlatilgan)
**Signal:** `STRATEGY_MTF.md` dagi F1 hodisasi, ya'ni H1 bar yopilishida d_H1 almashadi (yangi yo'nalish D), shu qaror vaqti t 07:00 ≤ t < 20:00 UTC bo'lsa, va
- **Lfull:** t paytida oxirgi yopilgan M1, M5, M15 barlarining yo'nalishi (d_M1, d_M5, d_M15) hammasi D ga teng;
- **T:** almashish bari uchun ER_H1 ≥ 0.30.
**Kirish:** t dan keyingi birinchi M15 bar ochilishi (30 daqiqagacha bo'shliq bo'lsa o'tkazib yuboriladi), yo'nalish D. Bir vaqtda faqat bitta pozitsiya; pozitsiya ochiq paytdagi signallar e'tiborsiz.
**Risk birligi:** R = 2.0 × ATR_H1 (kirish paytidagi ATR_H1).
**Dastlabki stop:** kirish − D × 2.0 × ATR_H1.
**Trailing stop:** har bir to'liq yopilgan H1 bardan keyin: long uchun yangi stop = max(eski stop, kirishdan beri eng yuqori H1 high − 2.0 × ATR_H1(kirish)); short uchun nosimmetrik.
**Chiqish** (qaysi biri birinchi bo'lsa):
 1. Stop (dastlabki yoki trailing) M15 yo'l bo'yicha tegsa: stop narxida; bar ochilishi stopdan o'tib ketgan bo'lsa (gap) — ochilish narxida.
 2. Yopilgan H1 barda d_H1 D ga teskari bo'lsa (teskari kesishuv): keyingi M15 bar ochilishida.
 3. Vaqt bo'yicha: 96 H1 bardan keyin: keyingi M15 bar ochilishida.
**Xarajat:** (a) spred $0.30 aylanma; (b) moliyalashtirish yiliga 3% × narx × (ushlab turilgan kunlar/365). Net R = (foyda − xarajat)/(2·ATR_H1).
**Stress:** spred $0.50 va moliyalashtirish 5%.
**FX:** spred 1.0 pip aylanma (stress 1.5 pip), moliyalashtirish yo'q (carry ma'lumoti yo'q; shuning uchun FX faqat signal haqiqiyligini tekshiradi).

## 4. O'lchovlar
- Bitim darajasida: soni N, yutuq ulushi, o'rtacha net R, profit factor, ushlab turish vaqti medianasi.
- **Hafta bo'yicha klasterlangan** t-test (bir tomonlama) o'rtacha net R > 0 uchun.
- Equity: har bitimda 0.5% risk (R = 0.5% kapital) bilan bitimma-bitim; sof natija, maksimal drawdown, Sharpe (bitimlar bo'yicha).
- **Tasodifiy kirish nazorati (timing):** shu davrda, shu soatlar oralig'ida, N ta tasodifiy kirish vaqti (yo'nalishlar ulushi saqlangan) tanlanib, shu chiqish qoidasi qo'llanadi; 2000 marta. p = tasodifiy o'rtacha net R ≥ haqiqiy o'rtacha bo'lgan ulush.

## 5. Qaror mezonlari (hammasi bajarilishi shart)
- **C1 (Final):** o'rtacha net R > 0, bir tomonlama p ≤ 0.10, N ≥ 25. (N < 25 bo'lsa natija "xulosasiz", qoida o'tmagan hisoblanadi.)
- **C2 (xarajat stressi, Final):** stress xarajat bilan ham o'rtacha net R > 0.
- **C3 (FX):** 3 juft birlashtirilgan: o'rtacha net R > 0, p ≤ 0.10, N ≥ 60.
- **C4 (izchillik, Dev):** Dev davrida o'rtacha net R **ishonchli manfiy emas** (agar o'rtacha < 0 va bir tomonlama p(manfiy) ≤ 0.10 bo'lsa qoida o'tmagan hisoblanadi).
- **C5 (iqtisodiy ahamiyat, Final):** o'rtacha net R ≥ +0.10, profit factor ≥ 1.2, maksimal drawdown ≤ 15%.
- **C6 (timing, Final):** tasodifiy kirish nazoratida p ≤ 0.10.
Hammasi bajarilsa — **PASS**.

## 6. Natijaga qarab nima qilamiz
- **PASS:** aniq qoida (kirish/chiqish/risk/lot hisobi) hujjatlanadi, MT5 uchun kod yoziladi (H1 trend, M1/M5/M15 holati, trailing), keyin demo hisobda kamida 3 oy forward-test. Haqiqiy pulga o'tish faqat demo natijasi kutilganga mos bo'lganda va kichik risk bilan.
- **FAIL:** qoida rad etiladi; parametrlarni "yaxshilash" taqiqlanadi. 2018–2025-fevral oltin ma'lumoti shundan keyin to'liq "ishlatilgan" hisoblanadi: yangi gipotezalar uchun yangi ma'lumot (2025-03 dan keyingi davr, boshqa manba) kerak bo'ladi.
- Natijadan qat'i nazar, Final, FX, Dev va sezgirlik natijalari to'liq e'lon qilinadi.

## 7. Xavflar va cheklovlar
- **Erkinlik darajasi:** chiqish qoidasi (2×ATR trailing, teskari kesishuv, 96 bar) a priori tanlangan, lekin boshqa tanlov ham mumkin edi. Sinov faqat bitta variantni baholaydi; boshqa variantlar natijaga qarab sinalmaydi.
- **Kichik namuna:** Final'da ~60–80 bitim kutiladi; kuchsiz effektni aniqlash qiyin. C1 dagi N ≥ 25 va p ≤ 0.10 shundan kelib chiqqan.
- **Moliyalashtirish farazi** (3%) va doimiy spred haqiqiy brokerdan farq qilishi mumkin. BID shamlar; kechikish/sirpanish stress bilan qisman qoplanadi.
- **Hindsight:** 2023–2025 oltin kuchli o'sgan davr; long bitimlar foyda berishi mumkin (beta). Timing nazorati (C6) va FX tasdig'i (C3) shu xavfni kamaytirish uchun.
- **Bir nechta TF ishlatilgan "sifat" filtrlari** (Lfull, T) Dev davrida topilgan; ularning prediktiv kuchi Final/FX da to'g'ridan-to'g'ri sinaladi.

## 8. Sezgirlik (faqat ma'lumot uchun, qarorga ta'sir qilmaydi)
Filtrsiz F1 (Lfull/T yo'q), faqat Lfull, faqat T, H4 mosligi, trailing 3 ATR, TP 3R bilan variantlar; long va short alohida; yillar bo'yicha taqsimot.

## 9. O'zgartirishlar jurnali
(hozircha bo'sh)
