# Oltin: Daily/H4 bias + M15 breakout, soatlar ichida ushlash, xarajat-nisbati filtri (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Bu "skalping"dan voz kechib, xarajat ulushini kamaytiradigan qisqa muddatli (soatlar) qoida. Bitta qoida, parametrlar muzlatilgan, sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. Maqsad va asos
Oldingi sinovlarda M1–M5 qoidalari xarajat (~0.15 R) tufayli yutqazdi; H4 breakout chegarada ijobiy chiqdi. Taxmin: foyda maqsadi spreddan ≥ 8× katta bo'lsa, xarajat ulushi pasayadi va yo'nalish bo'yicha ustunlik (agar bo'lsa) ko'rinadi. Bu reja shu taxminni sinaydi.

## 2. Qoida (hammasi muzlatilgan)
- **Bias (Daily + H4, ikkalasi mos):** Long: oxirgi yopilgan Daily yopilishi EMA50 va EMA200 dan yuqori **va** Daily EMA50 > EMA200 **va** H4 EMA20 > EMA50. Short: nosimmetrik. Aks holda savdo yo'q.
- **Signal (M15):** M15 sham yopilishi oldingi 16 ta M15 shamning (4 soat) eng yuqori High idan yuqori (Long) / eng past Low idan past (Short).
- **Kirish:** signal shamidan keyingi M15 bar ochilishida (market).
- **Sessiya:** kirish 07:00 ≤ t < 16:00 UTC, dushanba–juma.
- **Volatillik/xarajat filtri:** ATR_H1(14) ≥ 8 × spred (oltin: ≥ $2.40; FX: ≥ 8 pip). Aks holda o'tkaziladi.
- **Stop:** kirishdan 1.0 × ATR_H1 uzoqlikda. **Take-profit:** 2.0 × ATR_H1. ATR_H1 — kirish paytidagi oxirgi yopilgan H1 bar bo'yicha SMA(TR, 14).
- **Boshqa chiqish:** Daily bias qarama-qarshiga o'zgarsa (Daily EMA50/EMA200 munosabati teskari) → keyingi M15 ochilishida; 12 soatdan keyin (48 M15 bar) → yopilish; hafta oxiri/gap bo'lsa ochilish narxida.
- **Filtrlar:** kuniga ko'pi bilan 2 savdo; bir vaqtda bitta pozitsiya; ketma-ket 3 zarardan keyin 24 soat kirish yo'q; yangilik (NFP, CPI, FOMC; AQSh): kirish yangilikdan 60 daqiqa oldin va 30 daqiqa keyin bo'lmasin (standart ET jadvali, `STRATEGY_H4.md` 7.4 dagidek).
- **Risk:** savdoga kapitalning 0.5% (R = stop masofasi). Net R = (foyda − xarajat)/stop masofasi.

## 3. Ma'lumot va xarajat
- **Oltin (qaror):** XAUUSD M1 BID (ZombitX64, UTC), 2018-01 → 2025-02; M15/H1/H4/Daily M1 dan quriladi. Qaror davri 2019-01-01 → 2025-02-28; yarmlar 2019–2021 va 2022–2025. Spred $0.30 aylanma (stress $0.50). Moliyalashtirish yo'q (≤ 12 soat).
- **FX tasdiqlash:** EURUSD, GBPUSD, AUDUSD M1 (`qleap/dukascopy-ticks-ohlcv`), 2020-04 → 2025-12, xuddi shu qoida; spred 1.0 pip (AUDUSD ham 1.0), stress 1.5 pip.
- Cheklov: oltin davri oldingi tadqiqotlarda boshqa qoidalar bilan ko'rilgan; natija dastlabki. Spred doimiy (real tick spredi yo'q; Dukascopy tick hozircha cheklangan).

## 4. O'lchovlar
N, yutuq ulushi, o'rtacha net R, profit factor, o'rtacha xarajat/R (xarajat ulushi), ushlab turish medianasi; hafta-klasterlangan bir tomonlama p; equity (0.5% risk, kompaundlangan) daromad, maksimal drawdown, foydali oylar ulushi, eng yomon oy; yillar bo'yicha.
**Tasodifiy kirish nazorati (oltin):** sessiya/bias/yangilik/vol-filtri o'tgan vaqtlarda tasodifiy M15 bar, bias yo'nalishida, xuddi shu chiqish, savdolar soni teng; 1000 marta; p = tasodifiy o'rtacha net R ≥ real.

## 5. Qaror mezonlari (hammasi shart)
- **C1 (oltin):** o'rtacha net R > 0, p ≤ 0.10, N ≥ 150. **C2:** stress xarajatda o'rtacha net R > 0. **C3:** 2019–2021 va 2022–2025 alohida o'rtacha net R > 0. **C4:** profit factor ≥ 1.15.
- **C5:** tasodifiy kirish nazoratida p ≤ 0.10. **C6:** maksimal drawdown ≤ 20% (0.5% risk).
- **C7 (FX tasdiq):** EURUSD+GBPUSD+AUDUSD birlashtirilgan: o'rtacha net R > 0, p ≤ 0.10, N ≥ 300; stress xarajatda ham > 0.
Hammasi bajarilsa — **PASS (dastlabki)** va forward (demo) kuzatuvga nomzod; aks holda FAIL, parametrlarni "yaxshilash" taqiqlanadi.

## 6. Sezgirlik (faqat ma'lumot)
Filtrsiz (xarajat-nisbati filtrisiz); ATR_H1 ≥ 5× va ≥ 12× spred; risk 0.25% / 1%; faqat Long / Short; London (07–11) va overlap (12–16) alohida; TP 1.5× va 3×; xarajatsiz; yillar bo'yicha.

## 7. Aniqlashtirishlar (natijani ko'rishdan oldin muzlatilgan)
1. Kanal — signal shamidan oldingi 16 ta M15 sham (signal shami kirmaydi). 2. Bir shamda stop va TP tegsa — stop birinchi; gapda ochilish narxida. 3. "Kuniga 2 savdo" kirish UTC sanasi bo'yicha. 4. Daily/H4 bias oxirgi to'liq yopilgan bar bo'yicha. 5. FX da yangilik filtri AQSh yangiliklari bilan bir xil. 6. Vaqt chiqishi — 12 soat (48 M15 bar), yopilish narxida.

## 8. Natijaga qarab nima qilamiz
PASS: dastlabki, demo/forward ≥ 3 oy (yangi ma'lumotda), real pul faqat kichik risk bilan. FAIL: rad etiladi; hisobot to'liq e'lon qilinadi.

## 9. O'zgartirishlar jurnali
- 2026-10-17: sinov ishga tushirildi (backtest/m15.py, reports/m15_results.md). Natija: **FAIL** (C1–C7 hammasi bajarilmadi). Qoida va mezonlarga o'zgartirish kiritilmadi.
