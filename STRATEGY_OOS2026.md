# Oltin: bizning qoidalar 2026-09 va 2026-10 da (ko'rilmagan davr, tavsifiy tekshiruv)

Holat: **natijani ko'rishdan OLDIN yozilgan.** Qoidalar oldin pre-registered va muzlatilgan; bu yerda hech narsa o'zgartirilmaydi. Bu qaror/qabul sinovi emas, **tavsifiy** tekshiruv (ikki oy = juda kam savdo: statistik xulosa chiqarib bo'lmaydi).

## Savol
Foydalanuvchi: "qaysi strategiyada bizning qoida oltinda foydaga chiqdi, 2026-09 va 2026-10 oylik natija?"

## Ma'lumot
`bnq-ii/MT5_MetaQuotes-Demo_XAUUSD` (Hugging Face): MT5 MetaQuotes-Demo serveridan M1 (2026-07 → 2026-11) va D1 (2000–2026). M1 vaqti UTC+1 siljigan (NFP spike 13:30 da; kalendar 12:30 UTC): UTC ga o'tkazish uchun −1 soat. Daily bias (EMA50/200) D1 dan; H4/M15/M5/H1 M1 dan quriladi. **Farqlar:** boshqa manba (broker demo narxi), 2026 yangilik kalendari yo'q (HF kalendar 2025-04 gacha) → **yangilik filtri qo'llanmaydi**; spred oldingidek $0.30 doimiy; Yahoo GC=F fyuchers narxlari faqat oylik N1 qismi uchun.

## Qoidalar (o'zgarishsiz, kodlari repoda)
H4 breakout (`h4b.py`), H4 EMA20 reclaim (`h4.py`), M15 breakout (`m15.py`), M5 London (`ldn.py`), M1 swing + kunlik ±10% (`n3.py`), oylik oltin SMA10 (N1 oltin qismi). Daily/H1 indikator isitishi iyul–avgust M1 dan. Eng yaxshi tavsifiy ko'rsatkich: har qoida uchun sentabr va oktyabrdagi savdolar soni, jami R, hisob o'zgarishi (qoidaning risk foizida), oltin buy&hold (shu oy).
**Qaror mezoni yo'q.** Natija nol N bilan ham chiqishi mumkin; shuning uchun xulosa "bu oylarda qaysi qoida foyda/zarar berdi" bilan cheklanadi.

## O'zgartirishlar jurnali
(hozircha bo'sh)
