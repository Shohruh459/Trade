# Foydalanuvchi qoidasi: Daily bias + H4 EMA20 pullback-reclaim (oltin, pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida foydalanuvchi tomonidan berilgan; yozilmagan joylarni (7-bo'lim) natijani ko'rmasdan muzlatdim. Parametrlar sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. Qoida (foydalanuvchi matni bo'yicha)
- **Aktiv:** oltin (XAUUSD). Entry/boshqaruv H4, trend filtri Daily. Savdo vaqti cheklanmagan.
- **Daily bias:** Bullish = oxirgi yopilgan Daily yopilishi EMA50 va EMA200 dan yuqori **va** EMA50 > EMA200; Bearish = ikkalasidan past va EMA50 < EMA200; aks holda savdo yo'q.
- **Buy:** Bullish bias; H4 EMA20 > EMA50; H4 yopilishi > EMA20; reclaim: shu H4 sham EMA20 ga tegdi yoki pastga teshdi (low ≤ EMA20) va EMA20 dan yuqorida yopildi. Kirish: reclaim shami yopilgach keyingi H4 bar ochilishida (market). **Sell:** nosimmetrik.
- **Stop:** Buy uchun pullback pastki nuqtasi − 0.5 × ATR(14, H4); Sell uchun pullback yuqori nuqtasi + 0.5 × ATR. Stop masofasi s > 1.8 × ATR bo'lsa savdo olinmaydi.
- **TP1:** kirishdan 1.5 × s (50% yopiladi). **TP2:** 3 × s (qolgan 50%).
- **Chiqish:** TP1/TP2; stop; Daily EMA50/EMA200 munosabati teskari bo'lsa; H4 EMA20/EMA50 qarama-qarshi kesishsa (TP1 ga yetmagan bo'lsa ham, yetgan bo'lsa ham) — keyingi H4 bar ochilishida.
- **Filtrlar:** kuniga ko'pi bilan 2 savdo; ketma-ket 3 ta zararli savdodan keyin 24 soat yangi savdo yo'q; yangilik (NFP, CPI, FOMC): oldin 1 soat va keyin 30 daqiqa yangi savdo ochilmaydi.
- **Risk:** har savdoda 0.75% (asosiy), 1% sezgirlikda.

## 2. Ma'lumot
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28; H4 va Daily M1 dan (UTC bo'yicha tekis) quriladi. Daily EMA200 uchun isitish: qaror davri **2019-01-01 → 2025-02-28** (6.2 yil). Dev/Val ajratish: 2019–2021 va 2022-01 → 2025-02.
Cheklov: bu davr oldingi tadqiqotlarda boshqa qoidalar bilan ko'rilgan; natija dastlabki bo'ladi.

## 3. Xarajat
Spred $0.30 aylanma; moliyalashtirish yiliga 3% × narx × ushlab turilgan kun/365. Stress: $0.50 va 5%. Net R = (foyda − xarajat) / s (butun pozitsiya bo'yicha).

## 4. O'lchovlar
N, yutuq ulushi, o'rtacha net R, profit factor, ushlab turish medianasi; hafta-klasterlangan bir tomonlama t-test; equity (0.75% risk, kompaundlangan): daromad, maksimal drawdown, foydali oylar ulushi, eng yomon oy, yillar bo'yicha.
**Tasodifiy kirish nazorati:** xuddi shu davrda tasodifiy H4 bar (bias nolga teng emas, yangilik bloki yo'q), bias yo'nalishida, stop masofasi real savdolar taqsimotidan, xuddi shu chiqish; savdolar soni real bilan teng; 1000 marta; p = tasodifiy o'rtacha net R ≥ real.

## 5. Qaror mezonlari (hammasi shart; qaror davri 2019-01 → 2025-02)
- **C1:** o'rtacha net R > 0, p ≤ 0.10, N ≥ 60. (N < 60 → xulosasiz = o'tmagan.)
- **C2:** stress xarajat bilan ham o'rtacha net R > 0.
- **C3:** 2019–2021 va 2022–2025 yarmlarida alohida o'rtacha net R > 0.
- **C4:** profit factor ≥ 1.2.
- **C5:** tasodifiy kirish nazoratida p ≤ 0.10.
- **C6:** maksimal drawdown ≤ 20% (0.75% risk).
Hammasi bajarilsa **PASS (dastlabki)**; aks holda FAIL, qoida o'zgartirilib qayta sinalmaydi.

## 6. Sezgirlik (faqat ma'lumot)
Yangilik filtrisiz; risk 1%; faqat Buy / faqat Sell; H4 kesishuv bilan chiqishsiz; stop filtri (1.8 ATR) siz; xarajatsiz; yillar bo'yicha.

## 7. Aniqlashtirishlar (natijani ko'rishdan oldin muzlatilgan)
1. **Pullback nuqtasi:** oxirgi 3 H4 sham (reclaim shami bilan) ichidagi eng past low (Sell: eng baland high).
2. **Reclaim:** bir shamning o'zida (low ≤ EMA20 va close > EMA20); alohida "oldingi shamda teshish" varianti yo'q.
3. **Kuniga 2 savdo:** kirish UTC sanasi bo'yicha. **3 ta ketma-ket zarar:** shu uchinchi zararli chiqishdan 24 soat yangi kirish yo'q.
4. **Yangilik oynasi:** kirish bari ochilishi [yangilik − 60 min, yangilik + 30 min] ichida bo'lsa o'tkaziladi. Yangiliklar: NFP, CPI (m/m, Core m/m, y/y) 08:30 ET; FOMC Statement, Federal Funds Rate 14:00 ET; FOMC Press Conference 14:30 ET (standart jadval, AQSh DST, sana kalendardan).
5. **Gap/hafta oxiri:** pozitsiya hafta oxiridan o'tishi mumkin (tungi moliyalashtirish hisobda); stop gap bo'lsa ochilish narxida.
6. TP1 dan keyin stop siljitilmaydi; bir shamda stop va TP tegsa — stop birinchi.
7. EMA'lar `adjust=False`; ATR = TR ning 14 davrli SMA si.

## 8. Natijaga qarab nima qilamiz
PASS: dastlabki; MT5 kodi, demo/forward ≥ 3 oy. FAIL: rad etiladi; yaxshilash taqiqlanadi.

## 9. O'zgartirishlar jurnali
- 2026-10-17: sinov ishga tushirildi (backtest/h4.py, reports/h4_results.md). Natija: **FAIL** (C1, C3, C4, C5 bajarilmadi; C2, C6 bajarildi). Qoida va mezonlarga o'zgartirish kiritilmadi.
