# H4 breakout + kunlik qatlam: demo (qog'oz) kuzatuv protokoli va MT5 EA (pre-registered)

Holat: **demo boshlanishidan OLDIN yozilgan.** Qoidalar muzlatilgan; o'zgartirish faqat 8-bo'limdagi jurnalga. **Bu real pulga tayyorlash emas, demo kuzatuv.**

## 1. Nima tayyorlandi
- `mt5/H4_Breakout_Daily.mq5` — MT5 EA (MQL5). **Kompilyatsiya qilinmagan va MetaTrader'da sinalmagan** (bu muhitda MT5 yo'q). Birinchi qadam: MetaEditor'da F7 (kompilyatsiya xatolari bo'lsa tuzatish kerak), keyin demo.
- `forward_test/h4_reference_trades.csv` — Python modeli (`backtest/h4b.py`) bo'yicha 2019-01 → 2025-02 dagi 197 ta savdo (kirish vaqti, narx, stop, TP1/TP2, chiqish, model R): MT5 Strategy Tester (yoki demo) bilan solishtirish uchun.
- `tools/h4_demo_eval.py` — EA yozgan `H4BO_log.csv` ni baholaydi (`python tools/h4_demo_eval.py H4BO_log.csv --balance 100`), 5-bo'lim qoidalari bo'yicha.

## 2. Qoida (STRATEGY_H4_BREAKOUT.md bilan bir xil)
Daily EMA50/EMA200 bias (narx ikkalasidan yuqori/past va EMA50 > / < EMA200); H4 sham yopilishi oldingi 20 H4 shamning eng yuqori High (Buy) / eng past Low (Sell) dan tashqarida; kirish yangi H4 bar ochilishida (market); stop = breakout shami Low/High ∓ 0.3×ATR(14); stop masofasi > 2.0×ATR bo'lsa o'tkaziladi; TP1 = 1.5×stop (50%), TP2 = 3×stop; chiqish: Daily EMA50/200 munosabati teskari, yoki H4 yopilishi kanal chegarasiga qaytsa; kuniga ≤ 2 savdo; 3 ketma-ket zarar → 24 soat; yangilik (NFP/CPI/FOMC) oynasi (−60/+30 daqiqa). Risk: `RiskPercent=0.75` yoki `RiskMoney` (micro $100 hisob uchun 1.0).

## 3. Kunlik qatlam (STRATEGY_DAILY.md): hisob valyutasida
`DailyMaxLosses=3` (kuniga 3 zararli savdo → kun yopiladi), `DailyTarget=10` (kunlik foyda ≥ $10 → yopiladi), `DailyKeep=5` (kunlik foyda bir marta ≥ $5 ga yetsa va keyin < $5 ga tushsa → yopiladi). UTC kun. **Eslatma:** H4 breakout kuniga ~0.1 savdo qiladi (≈ 32 savdo/yil), shuning uchun qatlam deyarli hech qachon ishga tushmaydi; u himoya.

## 4. Backtest bilan farqlar (ogohlantirish)
- **Server vaqti:** backtest H4/Daily barlari UTC bo'yicha (00,04,08,…). Broker serveri odatda UTC+2/+3: H4 barlari 01:00/05:00… (UTC) ga siljiydi, Daily yopilish ham. Signal vaqtlari va ba'zi savdolar farq qiladi; ta'siri o'lchanmagan.
- Spred/sirpanish real; backtestda doimiy $0.30. Yangilik filtri MT5 kalendaridan (nomi bo'yicha), backtestda standart jadval.
- TP1 qisman yopish lot qadamiga bog'liq: micro lotlarda 50% bo'lib bo'lmasa, TP1 o'tkaziladi (butun pozitsiya TP2 yoki stopgacha).
- `RiskMoney=1` va stop masofasi katta bo'lsa (oltinda bir necha dollar), kerakli lot minimal lotdan kichik bo'lib, **savdo o'tkaziladi** ("skipped" logga yoziladi): $100 hisobda ko'p signal o'tkazib yuborilishi mumkin.

## 5. Demo baholash (oldindan belgilangan; statistik xulosa emas)
Kutilgan savdolar: ~32/yil (3 oyda ~8, 12 oyda ~32). Backtest o'rtacha ≈ +0.09 R (SD ~1.3 R): shuncha savdoda kichik ustunlikni **aniqlab bo'lmaydi**; demo faqat ijro (EA qoidaga mosmi, xarajat/sirpanish modeldagidanmi) va katta xatolarni tekshiradi.
- **1–3 oy:** har savdo qoida bilan mos (reference CSV va xususiyatlar bilan qo'lda solishtirish); xatolar bo'lsa EA to'g'rilanadi (yangi demo boshlanadi).
- **Hard stop (istalgan vaqtda):** demo drawdown > 20% → to'xtatish.
- **12 oy (≈ 30 savdo):** o'rtacha R > −0.25 va drawdown ≤ 20% va qoida buzilishlari yo'q → demo davom etadi; aks holda to'xtatiladi.
- **Real pul haqida qaror:** **eng kamida 24 oy / 60 savdo** va o'rtacha R > 0, profit factor > 1.1 bo'lgandan keyin; ya'ni hozir real pulga o'tish yo'q. Real pulga o'tilsa — faqat kichik risk (≤ 0.5% yoki $1), hisobning yo'qotilishiga tayyor bo'lgan summa bilan.

## 6. Ishga tushirish (qisqacha)
1) `mt5/H4_Breakout_Daily.mq5` ni MetaEditor ga qo'ying (MQL5/Experts), F7. 2) XAUUSD, H4 grafigi, **demo hisob**, Algo Trading yoqilgan. 3) Parametrlar default (micro $100 uchun `RiskMoney=1`). 4) Log: `MQL5/Files/H4BO_log.csv`. 5) Oyiga bir marta `python tools/h4_demo_eval.py H4BO_log.csv --balance 100`.

## 7. Cheklovlar
Kod sinalmagan; backtest ma'lumoti 2018–2025-fevral (ilgari ko'rilgan davr), natija chegarada (p = 0.15, profit factor 1.198); kuniga savdo kam; kalendar API tester'da ishlamasligi mumkin.

## 8. O'zgartirishlar jurnali
(hozircha bo'sh)
