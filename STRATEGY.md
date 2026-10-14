# EUR/USD MT5 EA — Strategiya, risk va test qoidalari

Holat: **LOYIHA (draft)**. Qoidalar test boshlanishidan OLDIN qotiriladi. Natijani ko'rib turib o'zgartirish (overfitting) taqiqlanadi.

## 1. Maqsad va doiralar
- Instrument: EUR/USD, platforma: MetaTrader 5.
- Ish tartibi: (1) Python'da backtest, (2) MQL5 EA, (3) MT5 Strategy Tester, (4) demo hisob.
- Hech qanday foyda kafolati yo'q. Maqsad: ishlamaydigan g'oyani erta rad etish.

## 2. Nomzod strategiyalar (ikkalasi bir xil testdan o'tadi)

### A. Trend-following (EMA + ATR)
- Taymfreym: H1. Trend filtri: EMA 200 (H1) yoki H4 yo'nalishi.
- Kirish (long): EMA20 > EMA50, narx > EMA200, ADX(14) > 20, RSI(14) 40–70 oralig'ida. Short — teskarisi.
- Stop-loss: 1.5 × ATR(14). Take-profit: 2 × risk (R:R = 1:2).
- Signal yopilgan sham bo'yicha, keyingi sham ochilishida bitim.

### B. Volatility-breakout
- Taymfreym: H1. Oldingi N (boshlang'ich 20) sham diapazoni chegarasini yopilgan sham bilan buzish.
- Filtr: ATR/spred nisbati, EMA200 yo'nalishi.
- SL/TP: ATR asosida (A bilan bir xil mantiq).
- Manba g'oyasi: mql5.com/en/articles/16569 (Gamuchirai Zororo Ndawana, 2024-12). Kanal = oldingi sham high/low; narx kanaldan tashqarida ochilib yopilsa "bias" belgilanadi; bias keyingi shamlar bilan tasdiqlansa kirish; yo'nalish EMA(5) va EMA(60) bilan tasdiqlanadi (tez > sekin = long); SL/TP ATR(14) asosida. Muallif H1, 2020-01…2024-11 da sinagan.
- Muhim: muallifning o'zi yozishicha, birinchi variantda savdolarning ~70% i zarar bilan yopilgan, filtrlardan keyin ~55%; "breakout strategiyalar EUR/USD uchun mos bo'lmasligi mumkin" deb xulosa qilgan. Ya'ni foydali ekani isbotlanmagan, bu faqat tekshiriladigan g'oya.
- Tuzatish (2026-10-14): tasdiq sharti "ochilish va yopilish ikkalasi ham tashqarida" H1'da deyarli bajarilmasdi (461 breakoutdan 3 tasi), shuning uchun faqat "yopilish tashqarida" qoldirildi. Bu B ning natijasini ko'rishdan oldin qilingan mantiqiy tuzatish.
- Mualliflik: maqola kodiga MetaQuotes huquqlari saqlangan. Kodni ko'chirmaymiz, qoidalarni o'zimiz mustaqil yozamiz.

## 3. Umumiy filtrlar
- Sessiya: London + Nyu-York (broker serveri vaqti bo'yicha sozlanadi).
- Spred > chegara (boshlang'ich 2.0 pip) bo'lsa savdo yo'q.
- Yuqori ta'sirli yangilik atrofida (±30 daqiqa) savdo yo'q.
- Juma kechqurun yangi pozitsiya ochilmaydi, hafta oxiriga pozitsiya qoldirilmaydi.

## 4. Risk qoidalari (o'zgarmas)
- Har bitimda balansning 1% gacha risk (lot SL masofasidan hisoblanadi).
- Bir vaqtda 1 ta pozitsiya. Martingale, grid, averaging YO'Q.
- Kunlik zarar 3% ga yetsa — shu kuni to'xtaydi.
- Umumiy drawdown 15% ga yetsa — EA o'chadi, qo'lda ko'rib chiqiladi.
- Har bitimda SL majburiy.

## 5. Test rejasi
| Bosqich | Muddat | Maqsad |
|---|---|---|
| In-sample | 2018-01 … 2022-12 | Parametrlarni cheklangan oraliqda tanlash |
| Out-of-sample | 2023-01 … 2025-12 | Parametrlarni O'ZGARTIRMASDAN tekshirish (1 marta) |
| Xarajatli test | butun davr | Spred, komissiya, slippage bilan |
| Rejim tekshiruvi | trend / yon bozor / yuqori va past volatillik | Qaysi sharoitda yo'qotishini aniqlash |
| Demo (forward) | kamida 1–2 oy | MT5 va broker muhitida tasdiqlash |

Parametr oraliqlari (oldindan): EMA tez 10–30, sekin 40–80, ATR ko'paytma 1.0–2.5, R:R 1.5–3. Oraliqdan tashqariga chiqmaymiz.

## 6. "Ishlaydi" mezonlari (out-of-sample bo'yicha)
- Profit factor > 1.3
- Maksimal drawdown < 15%
- Kamida 200 ta bitim
- In-sample va out-of-sample natijalari sezilarli farq qilmasligi
- Xarajatlar kiritilgandan keyin ham foyda saqlanishi

Mezonlarga erishilmasa: g'oya rad etiladi yoki ochiq e'lon qilinib yangi g'oya sinaladi. Mezonlarni natijaga qarab yumshatmaymiz.

## 7. Ma'lumot
- Manba: Dukascopy yoki HistData (M1 yoki tick), yoki MT5'dan eksport (CSV).
- Holat: tarmoq cheklovi tufayli avtomatik yuklash hozircha ishlamadi (qarang: README/izoh).

## 8. Ochiq savollar
- Broker serveri vaqt zonasi va spred darajasi.
- Hisob valyutasi va boshlang'ich balans (backtest uchun, masalan 10 000 USD).
- Qaysi strategiya (A yoki B) birinchi sinaladi — ikkalasi ham sinaladi.
