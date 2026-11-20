# GoldStructureEA: pre-registered sinov rejasi

Holat: **LOYIHA (DRAFT) — foydalanuvchi tasdig'ini kutmoqda.** Tasdiqdan keyin **natijani ko'rishdan oldin** commit qilinadi va muzlatiladi. Bu rejada ham, `STRATEGY_SPEC.md` da ham **kod yozilmagan**. Qoidalar `STRATEGY_SPEC.md` bo'yicha; parametrlar sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. Savol
`STRATEGY_SPEC.md` dagi qoida oltinda (2018–2025-fevral) xarajatdan keyin **tasodifiy kirishdan ishonchli yaxshi** va yetarli darajada barqaror natija beradimi? **Savdolar soni kutilmaydi**; backtest o'lchaydi (7-bo'lim: N kam bo'lsa "xulosasiz").

## 2. Ma'lumot
- **Asosiy:** XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28; M5/M15/H1 M1 dan quriladi (UTC tekis). H1 EMA200 isitishi: qaror davri 2018-04 dan.
- **Tavsifiy tekshiruv (qaror emas):** 2026-09/10 — MT5 MetaQuotes-Demo XAUUSD M1 (M1 vaqti UTC+1 siljigan, −1 soat).
- **FX qo'shimcha dalil (qarorga kirmaydi):** EURUSD, GBPUSD, AUDUSD M1 (2020-04 → 2025-12); spred 1.0 pip (stress 1.5).
- **Kalendar:** Forex Factory (2007 → 2025-04); 2026 uchun yo'q (tavsifiy tekshiruvda yangilik filtri o'chirilgan deb ko'rsatiladi).

## 3. Davrlar
- **Dev:** 2018-04 → 2021-12. **Val:** 2022-01 → 2023-12. **Final:** 2024-01 → 2025-02. Qoidalar sozlanmagani uchun hammasi hisobot qilinadi; **qaror davri = Dev+Val+Final umumiy (2018-04 → 2025-02)** va har davr alohida (C3).
- Eslatma: bu davr oldingi tadqiqotlarda boshqa qoidalar bilan ko'rilgan; natija dastlabki.

## 4. Simulyatsiya (muzlatilgan)
- Signallar M5 yopilishida (spetsifikatsiya bo'yicha); kirish keyingi M5 ochilishida; **SL/TP M1 yo'li bo'yicha**, bir M1 shamda ikkalasi tegsa — **stop birinchi**; gap bo'lsa ochilish narxida.
- **Xarajat:** spred $0.30 aylanma (stress $0.50); sirpanish yo'q (optimistik); moliyalashtirish: ushlash NY 16:30 gacha (kun ichi) — swap yo'q.
- **Risk:** equity ning 1% i, kompaundlangan; lot qadami cheklovi yo'q (R-bo'yicha); kunlik −4% limit (equity, floating bilan, M1 bo'yicha), kun boshi NY 17:00; NY 16:30 majburiy yopish; sessiya S1 (zoneinfo bilan DST); yangilik −60/+30 (FF, standart ET); bir vaqtda 1 pozitsiya.
- Barcha spetsifikatsiya qoidalari (swing k, BOS, zona, retest, tasdiq, stop filtri) o'zgarishsiz.

## 5. O'lchovlar
N (savdolar soni, yiliga, dastlabki 12 oyda kamida), g'alaba ulushi, o'rtacha net R, profit factor, ushlash vaqti medianasi, hafta-klasterlangan t-test (bir tomonlama), equity (1% risk): daromad, maksimal drawdown, foydali oylar ulushi, eng yomon oy, yillar bo'yicha; filtrlar voronkasi: har bosqichda (bias → BOS → zona → retest → tasdiq → stop filtri → sessiya/yangilik) nechta kandidat qolgani; kunlik −4% limit ishga tushgan kunlar soni; NY 16:30 majburiy yopilgan savdolar ulushi va ularning o'rtacha R i.

## 6. Tasodifiy kirish nazorati
Shu davrda, H1 bias (EMA+struktura) mos kelgan, sessiya/yangilik/spred filtrlari o'tgan tasodifiy M5 vaqtlarida: yo'nalish = bias, **stop masofasi real savdolar stop masofalari taqsimotidan**, TP 2R, xuddi shu chiqish (NY 16:30, kunlik limit); savdolar soni real bilan teng; 1000 marta. p = tasodifiy o'rtacha net R ≥ real o'rtacha.

## 7. Qaror mezonlari (hammasi shart; oltin, qaror davri)
- **G1:** N ≥ 100; o'rtacha net R > 0 va bir tomonlama klasterlangan p ≤ 0.10. **N < 100 bo'lsa natija "XULOSASIZ" va qoida o'tmagan hisoblanadi** (qo'shimcha dalil sifatida FX ko'rsatiladi, lekin qarorni o'zgartirmaydi).
- **G2:** stress xarajatda ($0.50) o'rtacha net R > 0.
- **G3:** Dev, Val, Final davrlarining har birida o'rtacha net R > 0 (yoki davrda N < 15 bo'lsa "kam ma'lumot" va o'tkazib yuboriladi, lekin kamida 2 ta davr baholanishi kerak).
- **G4:** profit factor ≥ 1.2.
- **G5:** tasodifiy kirish nazoratida p ≤ 0.10.
- **G6:** maksimal drawdown ≤ 20% (1% riskda).
Hammasi bajarilsa — **PASS (dastlabki)** va demo/forward ga nomzod; aks holda **FAIL** yoki **XULOSASIZ**.

## 8. Sezgirlik (faqat tavsifiy, qarorga ta'sir qilmaydi)
Sessiya S2/S3/S4; NY 16:30 majburiy yopishsiz (ushlab turish bilan); zona tana varianti; k = 2 va 4; tasdiq oynasi 1 bar; stop filtrisiz; impuls 0.7× va 1.5×; zona muddati 48 va 192 bar; faqat Long / faqat Short; komponent hissasi: (a) bias+BOS+zona retest (M5 tasdiqsiz) bilan, (b) tasdiqsiz zona chegarasidagi limit kirish; yillar va soatlar bo'yicha taqsimot. Tavsifiy tekshiruv 2026-09/10 (yangilik filtri yo'q).

## 9. Natijaga qarab
- **PASS:** MQL5 EA ishlab chiqiladi (modullar: Structure, Zones, Confirmation, Risk, Sessions/DST, News, Logging), demo ≥ 3 oy, real pul haqida gap 24 oy / 60 savdodan keyin.
- **FAIL yoki XULOSASIZ:** MQL5 yozilmaydi; parametrlar "yaxshilanmaydi". Qoida natijaga qarab o'zgartirilmaydi. Yangi variant faqat yangi oldindan yozilgan reja va yangi ma'lumot bilan.
- Natijadan qat'i nazar hisobot to'liq e'lon qilinadi (filtrlar voronkasi, sezgirlik, davrlar).

## 10. Cheklovlar
M1 BID (tick emas), doimiy spred, sirpanish yo'q (optimistik), sham ichidagi tartib taxminiy (stop birinchi — konservativ), kalendar 2025-04 gacha, zona ta'rifi bitta variant, oldingi tadqiqotlarda ko'rilgan davr.

## 11. Bosqichlar (tasdiqlardan keyin)
1. **(Hozir)** SPEC + reja loyihasi — foydalanuvchi ko'radi va **alohida tasdiqlaydi.**
2. Tasdiqdan keyin: spetsifikatsiya va reja muzlatiladi (commit), keyin Python backtest kodlanadi va bir marta ishga tushiriladi.
3. Natija sizga yuboriladi; MQL5 faqat PASS bo'lsa.

## 12. O'zgartirishlar jurnali
(hozircha bo'sh; tasdiqdan keyin to'ldiriladi)
