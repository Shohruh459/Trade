# GoldStructureEA: muzlatish manifesti (v3)

Sana: 2026-11-20. Muzlatishga ruxsat: foydalanuvchi ("Boshlaymiz"). Qoralama: commit `d6f01d9`.
Muzlatilgan fayllar (SHA-256, muzlatilgan holatdagi matn):

- 52ef717f81f4fae3ad13ac5aa31c7ea7fca14cd2533ffa9d82df365bceaab011  STRATEGY_SPEC.md
- 245ab86978bc8ea7a34ad34e16077c5f411efb1fcb9361d6a5682011ef648beb  STRATEGY_GOLDSTRUCTURE.md

Qoidalar:
- Bu fayllar mazmuni natijaga qarab o'zgartirilmaydi. O'zgartirish faqat jurnalga yozilgan sababi va yangi manifest bilan; o'zgarishdan keyin xuddi shu 2018-04 → 2025-02 davrni qayta sinash taqiqlanadi (test rejasi 6-bo'lim).
- **Kod yozishga ruxsat berilmagan.** Foydalanuvchi alohida, aniq ruxsat bergandan keyingina yangilik kalendari qurilishi (`tools/build_news_calendar.py`) va Python backtest yoziladi.
- Keyingi qadamlar (ruxsatdan keyin): (1) yangilik kalendari qurilishi; (2) backtest kodi (SPEC bo'yicha); (3) bir marta ishga tushirish; (4) natija hisoboti (Asosiy/Stress/Komissiya alohida); (5) MQL5 faqat PASS bo'lsa.

## Ishga tushirish jurnali (muzlatilgan hujjatlar o'zgartirilmagan, xeshlar o'zgarmagan)
- 2026-11-20: yangilik kalendari qurildi (`tools/build_news_calendar.py`, `data/news/usd_high_impact.csv`, `reports/news_calendar_coverage.md`).
- 2026-11-20: Python backtest kodlandi (`backtest/goldstructure.py`, `backtest/gs_run.py`, `tests/test_goldstructure.py`; commit `3622fd2`). Ishlab chiqish davrida faqat 2018-04..2018-07 kesimida smoke test; parametrlar o'zgartirilmagan. Bitta amalga oshirish tafsiloti SPEC ning noaniq joyini to'ldirdi: retest epizodini tugatuvchi bar (zonadan to'liq tashqarida) epizod bari hisoblanmaydi (to'g'ridan-to'g'ri o'qish, default); muqobil talqin faqat tavsifiy sezgirlik (`mss_on_exit=True`).
- 2026-11-20: **tasdiqlovchi ishga tushirish bir marta o'tkazildi** (`reports/goldstructure_results.md`, `reports/goldstructure_trades.csv`). Natija: **XULOSASIZ** (N = 14 < 100). Parametrlar o'zgartirilmadi. Kod xatosi tufayli qayta ishga tushirish bo'lmadi.

