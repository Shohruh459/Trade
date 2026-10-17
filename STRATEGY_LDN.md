# Foydalanuvchi qoidasi: H1 bias + M5 9EMA pullback-reclaim, London/overlap sessiyasi (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida foydalanuvchi tomonidan berilgan; men faqat yozilmagan joylarni (7-bo'lim) natijani ko'rmasdan muzlatdim. Parametrlar sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. Qoida (foydalanuvchi matni bo'yicha)
- **Aktiv:** oltin (XAUUSD) — spred chegarasi $0.35 oltinga xos. **Vaqt oralig'i:** entry M5, bias H1, filtr M15 (matnda M15 uchun aniq shart yo'q: ishlatilmaydi, 7-bo'lim).
- **Sessiya:** faqat 07:00–11:00 va 12:00–16:00 UTC (11:00–12:00 oralig'ida yangi savdo yo'q), dushanba–juma. Asian (00–07) da savdo yo'q.
- **H1 bias:** Bullish = oxirgi yopilgan H1 yopilishi EMA50 va EMA200 dan yuqori **va** EMA50 > EMA200. Bearish = ikkalasidan past va EMA50 < EMA200. Aks holda bias yo'q → savdo yo'q.
- **Buy:** bullish bias; M5 EMA9 > EMA21; yopilish > EMA9; 40 < RSI(14) < 70; oxirgi 3 ta yopilgan M5 shamdan kamida bittasi EMA9 ni pastga teshib (low < EMA9) va yuqoriga yopilgan (close > EMA9) — reclaim. **Sell:** nosimmetrik (60 > RSI > 30, high > EMA9, close < EMA9).
- **Kirish:** signal shamining yopilishidan keyingi M5 bar ochilishida, market.
- **Stop:** 1.5 × ATR(14, M5). **TP1:** 1.0 × ATR — pozitsiyaning 50% yopiladi. **TP2:** 2.0 × ATR — qolgan 50%. (ATR kirish paytidagi qiymat.)
- **Erta chiqish:** (a) TP1 ga yetmagan bo'lsa va M5 EMA9/EMA21 qarama-qarshi kesishsa → darhol (keyingi bar ochilishida); (b) H1 EMA50/EMA200 munosabati teskari bo'lsa → yopish; (c) Buy da RSI > 75 / Sell da RSI < 25 → qolganini yopish.
- **Filtrlar:** kuniga ko'pi bilan 5 savdo; ketma-ket 3 ta zararli savdodan keyin shu kunga savdo yo'q; yangilik: NFP, CPI, FOMC, Fed nutqlaridan 30 daqiqa oldin va 15 daqiqa keyin yangi savdo yo'q; spred > $0.35 bo'lsa savdo yo'q.
- **Risk:** har savdoda kapitalning bir qismi, stop masofasiga qarab lot.

## 2. Ma'lumot
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28; M5/M15/H1 M1 dan quriladi. Davrlar: Dev 2018-01 → 2021-12; Val 2022-01 → 2023-12; Final 2024-01 → 2025-02. **Qaror davri 2022-01 → 2025-02.**
Cheklov: bu davr oldingi tadqiqotlarda boshqa qoidalar bilan ko'rilgan (dastlabki natija sifatida baholanadi).

## 3. Xarajat
Spred $0.30 aylanma (butun pozitsiya bo'yicha bir marta), stress $0.50. Kun ichi, moliyalashtirish yo'q. Sirpanish ($ stress ga kiritilgan).

## 4. O'lchovlar
Savdo (to'liq pozitsiya, ikki bo'lak yig'indisi) darajasida: N, yutuq ulushi, o'rtacha net R (R = 1.5×ATR), profit factor, maks ushlab turish. Kun-klasterlangan t-test (bir tomonlama). Equity: risk 0.75% kapital (R = 0.75%), kompaundlangan, maksimal drawdown, foydali oylar ulushi, eng yomon oy, yillar bo'yicha.
**Tasodifiy kirish nazorati:** shu sessiya/bias/yangilik/kunlik cheklov filtrlaridan o'tgan vaqtlarda tasodifiy kirish (bias yo'nalishida; kunlik savdolar soni real bilan teng), xuddi shu chiqish qoidasi; 1000 marta; p = tasodifiy o'rtacha net R ≥ real.

## 5. Qaror mezonlari (hammasi bajarilishi shart; qaror davri 2022-01 → 2025-02)
- **C1:** o'rtacha net R > 0, p ≤ 0.10, N ≥ 200. **C2:** stress ($0.50) bilan ham o'rtacha net R > 0.
- **C3:** Val va Final alohida o'rtacha net R > 0. **C4:** Dev da o'rtacha net R ishonchli manfiy emas (agar < 0 va p(manfiy) ≤ 0.10 bo'lsa o'tmagan).
- **C5:** tasodifiy kirish nazoratida p ≤ 0.10. **C6:** maksimal drawdown ≤ 20% (0.75% risk; foydalanuvchi chegarasi skalping uchun 30% gacha, shuning uchun ≤ 30% ham hisobotda). Qaror: ≤ 30%.
Hammasi bajarilsa **PASS (dastlabki)**; aks holda FAIL va qoida o'zgartirilib qayta sinalmaydi.

## 6. Sezgirlik (faqat ma'lumot, qarorga ta'sir qilmaydi)
Yangilik filtrisiz; risk 0.5% va 1%; faqat Buy / faqat Sell; London / overlap alohida; reclaim faqat oxirgi bar (3 ta emas); yillar bo'yicha.

## 7. Aniqlashtirishlar (natijani ko'rishdan oldin muzlatilgan)
1. **Spred filtri:** ma'lumotda spred yo'q → test qilinmaydi (xarajat o'rniga ruxsat etilgan spred fiksirlangan). Real brokerda bu filtr savdolar sonini kamaytiradi.
2. **M15 "filtr":** matnda aniq shart yo'q → ishlatilmaydi.
3. **Reclaim:** oxirgi 3 yopilgan M5 shamdan biri reclaim bo'lsa va boshqa shartlar signal paytida bajarilsa signal; bir reclaim shami bir marta ishlatiladi.
4. **Risk foizi:** 0.5–1% oralig'idan 0.75% asosiy.
5. **TP1 dan keyin** stop siljitilmaydi (matnda yo'q). Bitta shamda stop va TP tegsa — stop birinchi.
6. **Yangilik:** kalendar (Forex Factory): NFP, CPI m/m, Core CPI m/m, CPI y/y, FOMC Statement, Federal Funds Rate, FOMC Press Conference, Fed Chair/FOMC Member nutqlari (USD, High Impact). Vaqt: NFP/CPI 08:30 ET, FOMC/Fed Funds 14:00 ET (standart jadval, AQSh DST); nutqlar uchun fayl vaqti −60 min…+75 min (DST xatosi uchun kengaytirilgan), vaqti yarim-tun placeholder bo'lgan nutqlar o'tkazib yuboriladi.
7. **Qo'shimcha xavfsizlik:** pozitsiya 20:00 UTC da yopiladi (matnda sessiya oxiri chiqish yo'q; tungi/haftalik gap xavfi uchun).
8. **ATR:** M5 TR ning 14 davrli SMA si; RSI Wilder; EMA'lar `adjust=False`.
9. **Zararli savdo:** butun pozitsiyaning sof R < 0.

## 8. Natijaga qarab nima qilamiz
PASS: dastlabki; MT5 kodi, demo/forward ≥ 3 oy. FAIL: rad etiladi, parametrlarni "yaxshilash" taqiqlanadi; yangi variant yangi reja va yangi ma'lumot bilan.

## 9. O'zgartirishlar jurnali
- 2026-10-17: sinov ishga tushirildi (backtest/ldn.py, reports/ldn_results.md). Natija: **FAIL** (C1–C6 hammasi bajarilmadi). Qoida va mezonlarga o'zgartirish kiritilmadi.
