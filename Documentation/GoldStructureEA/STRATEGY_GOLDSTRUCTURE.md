# GoldStructureEA: pre-registered sinov rejasi

Holat: **LOYIHA v3 (DRAFT) — foydalanuvchi ko'rib chiqishi va muzlatishga alohida ruxsati kutilmoqda; MUZLATILMAGAN.** Muzlatishdan keyin ham kod yozishga alohida ruxsat kerak. Hech qanday kod yozilmagan; natijaga qarab parametrlar o'zgartirilmaydi. Qoidalar `STRATEGY_SPEC.md` (v2) bo'yicha; parametrlar sozlanmaydi. O'zgartirish faqat 12-bo'limdagi jurnalga.
v3: foydalanuvchining 6 ta qarori kiritildi (o'zgarishlar ro'yxati 13-bo'limda). v2 dagi 10 ta aniqlashtirish saqlangan.

## 1. Savol
`STRATEGY_SPEC.md` dagi qoida oltinda (2018-04 → 2025-02) xarajatdan keyin **tasodifiy kirishdan ishonchli yaxshi** va yetarli barqaror natija beradimi? **Savdolar soni kutilmaydi**; backtest o'lchaydi (N < 100 bo'lsa "xulosasiz").

## 2. Ma'lumot (savol 5, 8)
- **Asosiy:** XAUUSD M1 BID (ZombitX64, Europe/Athens server vaqtidan UTC ga o'tkazilgan; alshahri BID datasetiga qarshi tekshirilgan: farq o'rtacha $0.09), **2018-01-02 → 2025-02-28**; M5/M15/H1 M1 dan UTC bo'yicha quriladi; H1 EMA200 isitishi uchun qaror davri 2018-04-01 dan boshlanadi.
- **Ma'lumot bo'shlig'i (savol 8) — aniq qayd:**
  - **2025-03-01 → 2026-06-30 (16 oy): ishonchli M1 yo'q.** ZombitX64 datasetida 2025-03 dan keyin oylik barlar soni to'liq emas: 2025-03 — 20,796 (to'liq ~30,000), 2025-04 — 5,507, 2025-05 — 29,928, 2025-06 — 13,897, 2025-07 — 11,086, **2025-08 — yo'q**, 2025-09 — 13,109, 2025-10 — 150; **2025-10-02 → 2026-06 — yo'q**. Shu sababli bu davr qaror va tavsifiy tekshiruvga **kiritilmaydi** (bo'shliq).
  - **2026-07 → 2026-11-03:** MT5 MetaQuotes-Demo XAUUSD M1 (Hugging Face `bnq-ii/MT5_MetaQuotes-Demo_XAUUSD`): 2026-07, 08, 09, 10 oylar to'liq, 2026-11 qisman. **Tavsifiy tekshiruv: 2026-09 va 2026-10** (iyul–avgust faqat indikator isitishi uchun). Bu **boshqa manba** (broker demo narxi), M1 vaqti UTC+1 siljigan (NFP spike orqali aniqlangan, −1 soat tuzatiladi), spredi noma'lum. Natijalar "qaror" emas, "tavsifiy".
  - **Natija:** qaror davri bilan tavsifiy davr orasida 16 oylik uzilish bor; ular **bir uzluksiz vaqt qatori emas**. 2026 oylarida EMA200/zona holati faqat 2026-07 dan boshlab isitiladi.
- **FX qo'shimcha dalil (qarorga kirmaydi):** EURUSD, GBPUSD, AUDUSD M1 (`qleap/dukascopy-ticks-ohlcv`), 2020-04 → 2025-12; spred 1.0 pip (stress 1.5).
- **Kalendar:** `STRATEGY_SPEC.md` 11.1: Forex Factory (HF), sana fayldan, vaqt standart ET; NFP/CPI **to'liq**, FOMC to'liq, **GDP 2019–2022 da to'liq emas**; 2025-04 dan keyin kalendar yo'q (qaror davri 2025-02 gacha — ta'sir yo'q); 2026 tavsifiy tekshiruvda kalendar yo'q, **filtr o'chirilgan**.

## 3. Davrlar (savol 8)
- **Dev:** 2018-04 → 2021-12. **Val:** 2022-01 → 2023-12. **Final:** 2024-01 → 2025-02. Qoidalar sozlanmagani uchun hammasi hisobot qilinadi; **qaror davri = 2018-04 → 2025-02** (G1–G6) va har davr alohida (G3).
- **Tavsifiy:** 2026-09, 2026-10 (alohida, qarorga kirmaydi). **Bo'shliq 2025-03 → 2026-06 hech qaerda ishlatilmaydi.**
- **Yangilik filtri bo'yicha qismlar (alohida ko'rsatiladi):** (F1) filtr to'liq: NFP+CPI+FOMC hamma oylar, GDP ham to'liq: 2023-01 → 2025-02 (+ 2018 to'liq); (F2) filtr to'liq emas: 2019-01 → 2022-12 (GDP bo'shliqlari); (F3) 2026 tavsifiy: filtr yo'q. G-mezonlar butun qaror davrida hisoblanadi; F1/F2 bo'yicha natijalar qo'shimcha jadvalda (yangilik filtri ta'siri tekshiriladi).
- Eslatma: davr oldingi tadqiqotlarda boshqa qoidalar bilan ko'rilgan; natija dastlabki.

## 4. Simulyatsiya va xarajatlar (muzlatilgan) (savol 6, 9, 10)
- Signal M5 yopilishida (spetsifikatsiya), kirish keyingi M5 ochilishida; **SL/TP M1 yo'li bo'yicha**; bir M1 shamda SL va TP ikkalasi tegsa — **stop birinchi**; gap bo'lsa ochilish narxida.
- **Hisobotlar alohida:** (1) **Asosiy** ssenariy (spred $0.30, komissiya 0, slippage 0); (2) **Stress** ssenariy (spred $0.50, slippage kirish $0.10 va SL $0.10, komissiya 0); (3) **Komissiya sezgirligi** ($0.07/oz = $7/lot, asosiy xarajatlarga qo'shimcha). Birliklar $/oz; 1 lot = 100 oz: spred $0.30 = $30/lot, $0.50 = $50/lot; slippage $0.10 = $10/lot har bir tomonga.
- **Spred ($/oz, to'liq aylanma):** asosiy **$0.30**, stress **$0.50**; Long — kirish Ask = Bid+S, chiqish Bid; Short — kirish Bid, chiqish Ask = Bid+S (SL/TP Short uchun Bid+S bo'yicha). 1 lot = 100 oz; $0.30/oz = $30/lot.
- **Komissiya:** asosiy 0; sezgirlik $0.07/oz ($7/lot). **Slippage:** asosiy 0; stress: kirish $0.10/oz + stop-loss chiqishi $0.10/oz. **Swap:** NY 16:30 yopish bilan 0; "yopishsiz" sezgirlikda 3%/yil × qiymat × tunlar.
- **Risk:** hisob equity ning 1%, kompaundlangan, lot qadami cheklovi yo'q. **Kunlik −4% limit:** **faqat EA P&L** (yopilgan sof natija + floating, komissiya va swap bilan; boshqa EA va qo'lda pozitsiyalar kirmaydi), kun boshi NY 17:00, M1 adverse bo'yicha; breachda EA ning hamma pozitsiyasi −4% narxida yopiladi, keyingi NY 17:00 gacha blok. **NY 16:30 yopish** muvaffaqiyatli deb olinadi (favqulodda holat backtestda modellashtirilmaydi); sessiya S1 (zoneinfo, DST mustaqil); bir vaqtda 1 pozitsiya; yangilik filtri `data/news/usd_high_impact.csv` bo'yicha.
- Barcha spetsifikatsiya qoidalari o'zgarishsiz (swing, BOS (A8 tanlangan variant), zona algoritmi, retest, P+M, signal eskirishi, stop filtri).

## 5. O'lchovlar
N (jami, yiliga, davrlar bo'yicha), g'alaba ulushi, o'rtacha net R, profit factor, ushlash vaqti medianasi, hafta-klasterlangan bir tomonlama t-test, equity (1% risk): daromad, maksimal drawdown, foydali oylar ulushi, eng yomon oy, yillar bo'yicha; **filtrlar voronkasi** (bias → BOS → zona yaratilish (no_zone / pre_violated / bad_height sabablari) → retest → P+M → signal eskirishi sabablari → A1 filtri → sessiya/yangilik/spred → savdo); kunlik −4% ishga tushgan kunlar; NY 16:30 yopilgan savdolar ulushi va ularning o'rtacha R i; F1 va F2 bo'yicha ajratilgan natijalar.

## 6. Tasodifiy kirish nazorati (savol 7)
Maqsad: strukturaviy kirish (zona+retest+P+M) **bias bilan mos tasodifiy kirishdan** yaxshimi?
- **Bir xil sharoitlar:** shu davr, shu H1 bias (EMA va struktura ikkalasi mos), **bir xil sessiya (S1, DST)**, yangilik/spred filtri, **bir xil risk (equity 1%)**, **bir xil xarajatlar (spred, komissiya, slippage)**, bir vaqtda 1 pozitsiya, kunlik −4% limit, NY 16:30 yopish, **TP = 2R**.
- **Kirish:** eligible M5 bar ochilishlaridan tasodifiy tanlash; **yo'nalish = bias**. **Stop masofasi:** real savdolarning stop masofasi / ATR(M15) nisbatlari taqsimotidan tasodifiy tanlanadi va tasodifiy kirish paytidagi ATR(M15) ga ko'paytiriladi (A1 diapazoni 0.5–2.0 ATR avtomatik bajariladi); TP = 2 × stop.
- **Soni:** real N ga teng (ketma-ket, bir vaqtda 1 pozitsiya qoidasi bilan; ustma-ust tushganlari o'tkazib yuborilib, kerakli sonda to'ldiriladi); **1000 ta tasodifiy to'plam**.
- **Statistika:** p = (tasodifiy to'plamlar o'rtacha net R ≥ real o'rtacha net R) ulushi. G5: p ≤ 0.10.
- **Cheklov:** nazorat "zona/retest/pattern tanlovi" qo'shgan foydani o'lchaydi (bias va vaqt bir xil), "H1 bias o'zi foyda beradimi" savoliga alohida javob beradi: bias-tasodifiy natijasi ham hisobotda (ustunlik bias dan bo'lsa ko'rinadi).
- **Parametrlarni qayta sozlash taqiqi:** bu reja bo'yicha **bitta tasdiqlovchi ishga tushirish** o'tkaziladi. Natijani ko'rgach parametrlarni (yoki ta'riflarni) o'zgartirib, **xuddi shu davrni (2018-04 → 2025-02) qayta sinash TAQIQLANADI**; sezgirlik (8-bo'lim) faqat tavsifiy va qaror uchun ishlatilmaydi. Har qanday o'zgartirish 12-bo'limga yoziladi va faqat **yangi, ko'rilmagan ma'lumotda** (masalan, 2026-07 dan keyingi davr, forward) tasdiqlanadi; shu davr ma'lumoti "ishlatilgan" deb belgilanadi. Ishga tushirish uchun kod commit xeshi va natija fayli hisobotga yoziladi.

## 7. Qaror mezonlari (hammasi shart; oltin, qaror davri)
- **G1:** N ≥ 100; o'rtacha net R > 0 va bir tomonlama klasterlangan p ≤ 0.10. **N < 100 → "XULOSASIZ" va qoida o'tmagan hisoblanadi; A8 yoki boshqa parametr o'zgartirilmaydi, natija o'zgarishsiz "xulosasiz" deb belgilanadi** (FX qo'shimcha dalil sifatida ko'rsatiladi, qarorni o'zgartirmaydi).
- **G2:** stress (spred $0.50, slippage kirish+SL $0.10) da o'rtacha net R > 0.
- **G3:** Dev, Val, Final har birida o'rtacha net R > 0 (davrda N < 15 bo'lsa "kam ma'lumot", o'tkazib yuboriladi, lekin kamida 2 davr baholanishi kerak).
- **G4:** profit factor ≥ 1.2. **G5:** tasodifiy kirish nazoratida p ≤ 0.10. **G6:** maksimal drawdown ≤ 20% (1% risk).
Hammasi bajarilsa — **PASS (dastlabki)**; aks holda **FAIL** yoki **XULOSASIZ**.

## 8. Sezgirlik (faqat tavsifiy, qarorga ta'sir qilmaydi)
A8 variantlari (a)/(b)/(c); sessiya S2/S3/S4; NY 16:30 yopishsiz (swap bilan); zona tana varianti; k=2/4; P–M oynasi 1 bar; stop filtrisiz; zona muddati 48/192; faqat Long/Short; komissiya $0.07/oz; GDP filtrsiz/GDP bilan; komponent hissasi: (a) bias+BOS+zona retest, M5 tasdiqsiz, zona chegarasida limit kirish; (b) faqat bias-tasodifiy; yillar va soatlar bo'yicha taqsimot; 2026-09/10 tavsifiy (filtr yo'q).

## 9. Natijaga qarab
- **PASS:** MQL5 EA (modullar: Structure, Zones, Confirmation, Risk, Sessions/DST, News, Execution/Emergency, Logging), demo ≥ 3 oy, real pul haqida gap 24 oy / 60 savdodan keyin.
- **FAIL / XULOSASIZ:** MQL5 yozilmaydi; parametrlar "yaxshilanmaydi"; yangi variant faqat yangi reja va yangi ma'lumot bilan.
- Natijadan qat'i nazar hisobot to'liq e'lon qilinadi.

## 10. Cheklovlar
M1 BID (tick emas), doimiy spred, sirpanish yo'q (asosiy — optimistik), sham ichidagi tartib taxminiy (stop birinchi), kalendar 2025-04 gacha va GDP bo'shliqlari, zona ta'rifi bitta variant, oldingi tadqiqotlarda ko'rilgan davr, 16 oylik ma'lumot bo'shlig'i, tavsifiy davr boshqa manba.

## 11. Bosqichlar
1. **(Hozir)** SPEC v2 + reja v2 — foydalanuvchi ko'radi va **alohida tasdiqlaydi.**
2. Tasdiqdan keyin: hujjatlar muzlatiladi (commit), keyin `tools/build_news_calendar.py` va Python backtest kodlanadi va **bir marta** ishga tushiriladi.
3. Natija yuboriladi; MQL5 faqat PASS bo'lsa.

## 12. O'zgartirishlar jurnali
(hozircha bo'sh; muzlatishga foydalanuvchi alohida ruxsat bergandan keyin to'ldiriladi)

## 13. v2 → v3 o'zgarishlar ro'yxati (test rejasi)
1. A8 qat'iy (b) (real tana ≥ 1.0×ATR(B−1)); N<100 bo'lsa parametr o'zgartirilmaydi, natija "xulosasiz" (4, 7-bo'lim).
2. Zona tekshiruvi simmetrik va barcha hisob faqat yopilgan shamlar bo'yicha (SPEC 4).
3. Signal eskirishi: retest epizodi boshidan 12 M5 bar, keyingi ochilishda bajarilmasa eskiradi (SPEC 7).
4. Kunlik −4%: faqat EA P&L (boshqa EA va qo'lda pozitsiyalar kirmaydi) (4-bo'lim).
5. Asosiy, Stress va Komissiya sezgirligi **alohida hisobotlar**; birliklar va 1 lot qiymati (4-bo'lim).
6. Favqulodda tartib va holatni saqlash/tiklash SPEC da; backtestda modellashtirilmaydi (4-bo'lim).
7. BUY/SELL simmetriyasi SPEC da yagona formulada.
