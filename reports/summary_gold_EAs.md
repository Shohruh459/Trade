# Oltin (XAUUSD) uchun ochiq manbali EA'lar: mustaqil sinov xulosasi

Barcha sinovlar bizning ma'lumotimizda (Dukascopy asosida), EA standart sozlamalari o'zgartirilmasdan, Python portlari orqali. Port taxminiy (MT5 tick sinovi emas).
Mezon (oldindan): PF > 1.3, DD < 15%, 200+ bitim, xarajatdan keyin foyda. Hech biri o'tmadi.

| EA | Ma'lumot | Natija | Asosiy sabab |
|---|---|---|---|
| foeed/FvgGold-EA | M15, 2018–2025-02 | PF 0.34 (e'lon qilingandek), eng yaxshi stsenariyda 0.86 | Kutilayotgan buyurtma GTC va MaxTrades=1 hisoblaydi: 2019-yildan EA to'xtab qoladi. README'dagi +$4 874 arifmetik jihatdan mumkin emas. |
| gold-pro-scalper TickRobust | M1, 2018–2025-02 | PF 0.80, 176 bitim, o'rtacha −0.02 R (CI nolni kesadi) | Xarajat darvozasi tufayli juda kam bitim; natija nolga yaqin. |
| gold-pro-scalper klassik MR | M1, 2018–2025-02 | Spred $0.25: 81 bitim, PF 1.43 (CI nolni kesadi, foyda 2020-yildan); $0.15: PF 0.88, DD 23% | ATR-nisbiy spred cheklovi (spred ≤ ATR×12%) vaqtning ~1% ida o'tadi; natija bir necha o'ta o'zgaruvchan kunga bog'liq. |
| gold-pro-scalper Trend Breakout | M1, 2018–2025-02 | 6615 bitim, PF 0.63, o'rtacha −0.029 R (CI −0.034…−0.024) | Aniq zarar, 8 yilda 7 yil salbiy. |
| NadirAliOfficial/trillex-10s-ea | 15 tick namunasi, 2019–2026 | 12 840 bitim, PF 0.52, o'rtacha −0.118 R; xarajatdan oldin ≈ 0 | Signalda edge yo'q; EA'ning o'z lot qoidasi bitta SL'da balansning 20–40% ini xavf ostiga qo'yadi. |

Umumiy xulosa: sinalgan oddiy indikator/skalping EA'lari spred va komissiyadan keyin foyda bermaydi. Ularning README'lardagi da'volari (foydali bo'lsa) qisqa, moslashtirilgan davrga tayanadi.
Hisobotlar: fvggold.md, n30_tickrobust.md, n30_variants.md, trillex.md.
