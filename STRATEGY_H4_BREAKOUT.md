# Foydalanuvchi qoidasi: Daily bias + H4 Donchian(20) breakout (oltin, pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida foydalanuvchi tomonidan berilgan; yozilmagan joylarni (7-bo'lim) natijani ko'rmasdan muzlatdim. Parametrlar sozlanmaydi. O'zgartirish faqat 9-bo'limdagi jurnalga.

## 1. Qoida (foydalanuvchi matni bo'yicha)
- **Aktiv:** XAUUSD. H4 entry/boshqaruv, Daily trend filtri. Risk har savdoda 0.75%.
- **Daily bias:** Bullish = oxirgi yopilgan Daily yopilishi EMA50 va EMA200 dan yuqori **va** EMA50 > EMA200; Bearish = ikkalasidan past va EMA50 < EMA200; aks holda savdo yo'q.
- **Buy:** Bullish bias; H4 sham yopilishi oxirgi 20 ta H4 shamning eng yuqori High idan yuqori (breakout). **Sell:** Bearish bias; yopilish oxirgi 20 ta shamning eng past Low idan past. Kirish: breakout shami yopilgach keyingi H4 ochilishida (market).
- **Stop:** Buy: breakout shamining Low − 0.3 × ATR(14, H4); Sell: breakout shamining High + 0.3 × ATR. Stop masofasi s > 2.0 × ATR bo'lsa savdo olinmaydi.
- **TP1:** 1.5 × s (50% yopiladi). **TP2:** 3 × s (qolgan 50%).
- **Chiqish:** TP1/TP2; stop; Daily bias teskari bo'lsa (Daily EMA50/EMA200 munosabati o'zgarsa); narx 20-period kanal ichiga qaytib yopilsa (TP1 dan oldin ham, keyin ham).
- **Filtrlar:** kuniga ko'pi bilan 2 savdo; ketma-ket 3 zarar → 24 soat yangi savdo yo'q; NFP/CPI/FOMC dan 1 soat oldin va 30 daqiqa keyin yangi savdo yo'q.

## 2. Ma'lumot
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28; H4 va Daily M1 dan quriladi. Qaror davri **2019-01-01 → 2025-02-28** (Daily EMA200 isitishi); yarmlar: 2019–2021 va 2022-01 → 2025-02. Bu davr oldingi tadqiqotlarda boshqa qoidalar bilan ko'rilgan: natija dastlabki.

## 3. Xarajat
Spred $0.30 aylanma + moliyalashtirish yiliga 3% (kunlar bo'yicha). Stress: $0.50 va 5%. Net R = (foyda − xarajat)/s.

## 4. O'lchovlar va 5. Mezonlar
`STRATEGY_H4.md` 4 va 5-bo'limlari bilan bir xil: C1 meanR>0, hafta-klasterlangan p ≤ 0.10, N ≥ 60; C2 stress meanR>0; C3 ikki yarimda meanR>0; C4 profit factor ≥ 1.2; C5 tasodifiy kirish nazorati p ≤ 0.10 (bias yo'nalishida tasodifiy H4 bar, stop masofasi real taqsimotdan, savdolar soni teng, 1000 marta, xuddi shu chiqish); C6 maksimal drawdown ≤ 20% (0.75% risk). Hammasi bajarilsa PASS (dastlabki), aks holda FAIL.

## 6. Sezgirlik (faqat ma'lumot)
Yangilik filtrisiz; risk 1%; faqat Buy / faqat Sell; kanal-chiqishsiz; stop filtri (2.0 ATR) siz; xarajatsiz; yillar bo'yicha.

## 7. Aniqlashtirishlar (natijani ko'rishdan oldin muzlatilgan)
1. **Kanal:** breakout shamidan oldingi 20 ta H4 shamning eng yuqori High/eng past Low (breakout shamining o'zi kirmaydi).
2. **"Kanal ichiga qaytib yopish":** breakout paytidagi kanal chegarasi (Buy: yuqori chegara U0; Sell: pastki chegara L0) ga nisbatan: keyingi H4 sham Buy da ≤ U0, Sell da ≥ L0 yopilsa → keyingi H4 ochilishida chiqish. (Harakatlanuvchi kanal emas.)
3. **Daily bias o'zgarishi:** Daily EMA50/EMA200 munosabati kirishdagidan teskari bo'lsa. Chiqish keyingi H4 ochilishida.
4. **Kuniga 2 savdo:** kirish UTC sanasi bo'yicha. 3 zarar: uchinchi zarardan 24 soat. Yangilik oynasi `STRATEGY_H4.md` 7.4 dagidek (kirish bari ochilishi oyna ichida bo'lsa o'tkaziladi).
5. Pozitsiya hafta oxiridan o'tishi mumkin; gap bo'lsa stop ochilish narxida. TP1 dan keyin stop siljitilmaydi; bir shamda stop va TP tegsa — stop birinchi. ATR = TR ning 14 davrli SMA si.

## 8. Natijaga qarab nima qilamiz
PASS: dastlabki, MT5 kodi, demo ≥ 3 oy. FAIL: rad etiladi; yaxshilash taqiqlanadi.

## 9. O'zgartirishlar jurnali
(hozircha bo'sh)
