//+------------------------------------------------------------------+
//| H4_Breakout_Daily.mq5                                            |
//| Daily-bias + H4 Donchian(20) breakout, daily limits layer.       |
//| Spec: STRATEGY_H4_BREAKOUT.md + STRATEGY_DAILY.md + STRATEGY_DEMO_H4.md |
//| STATUS: NOT COMPILED, NOT TESTED in MetaTrader. DEMO ONLY.       |
//+------------------------------------------------------------------+
#property copyright "research"
#property version   "0.10"
#property strict

#include <Trade/Trade.mqh>

//--- risk
input double RiskPercent      = 0.75;   // risk per trade, % of equity (used if RiskMoney = 0)
input double RiskMoney        = 0.0;    // fixed risk per trade in account currency (e.g. 1.0 for a $100 micro account); 0 = use RiskPercent
//--- strategy (frozen, do not tune)
input int    DonchianBars     = 20;
input int    AtrPeriod        = 14;
input double StopAtrBuffer    = 0.3;    // stop = breakout candle extreme -/+ 0.3*ATR
input double MaxStopAtr       = 2.0;    // skip if stop distance > 2.0*ATR
input double Tp1Mult          = 1.5;    // TP1 = 1.5 * stop distance (close 50%)
input double Tp2Mult          = 3.0;    // TP2 = 3.0 * stop distance (rest)
input int    MaxTradesPerDay  = 2;
input int    MaxConsecLosses  = 3;      // after 3 consecutive losing trades: no entries for 24h
//--- daily layer (account currency)
input int    DailyMaxLosses   = 3;      // losing trades per day -> stop for the day
input double DailyTarget      = 10.0;   // day profit >= target -> stop for the day
input double DailyKeep        = 5.0;    // once day profit >= keep, stop if it falls back below keep
//--- news filter (MT5 economic calendar, may be unavailable in the tester)
input bool   UseNewsFilter    = true;
input int    NewsBeforeMin    = 60;
input int    NewsAfterMin     = 30;
//--- misc
input long   MagicNumber      = 770015;
input int    SlippagePoints   = 50;
input string LogFile          = "H4BO_log.csv";

CTrade   trade;
int      hEma50D, hEma200D, hAtr;
datetime lastBar = 0;

//--- state of the single open position
bool     g_open = false;
int      g_dir = 0;
double   g_entry = 0, g_s = 0, g_U0 = 0, g_risk = 0, g_tp1 = 0, g_profit = 0;
int      g_rel0 = 0;
bool     g_partial = false;
datetime g_entryTime = 0;
//--- day/loss state
datetime g_cooldownUntil = 0;
int      g_consecLosses = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   hEma50D  = iMA(_Symbol, PERIOD_D1, 50, 0, MODE_EMA, PRICE_CLOSE);
   hEma200D = iMA(_Symbol, PERIOD_D1, 200, 0, MODE_EMA, PRICE_CLOSE);
   hAtr     = iATR(_Symbol, PERIOD_H4, AtrPeriod);
   if(hEma50D == INVALID_HANDLE || hEma200D == INVALID_HANDLE || hAtr == INVALID_HANDLE) return INIT_FAILED;
   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetDeviationInPoints(SlippagePoints);
   if(!FileIsExist(LogFile))
   {
      int f = FileOpen(LogFile, FILE_WRITE | FILE_CSV | FILE_ANSI, ';');
      if(f != INVALID_HANDLE) { FileWrite(f, "close_time", "dir", "entry", "stop_dist", "risk_money", "profit", "R"); FileClose(f); }
   }
   SyncPosition();
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
double Buf(int handle, int shift)
{
   double b[];
   ArraySetAsSeries(b, true);
   if(CopyBuffer(handle, 0, shift, 1, b) < 1) return EMPTY_VALUE;
   return b[0];
}

//--- Daily bias from last CLOSED daily bar: +1 bull, -1 bear, 0 none; rel = sign(EMA50-EMA200)
int DailyBias(int &rel)
{
   double e50 = Buf(hEma50D, 1), e200 = Buf(hEma200D, 1);
   double c = iClose(_Symbol, PERIOD_D1, 1);
   if(e50 == EMPTY_VALUE || e200 == EMPTY_VALUE || c <= 0) { rel = 0; return 0; }
   rel = (e50 > e200) ? 1 : (e50 < e200 ? -1 : 0);
   if(c > e50 && c > e200 && e50 > e200) return 1;
   if(c < e50 && c < e200 && e50 < e200) return -1;
   return 0;
}

//+------------------------------------------------------------------+
bool HasPosition()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == MagicNumber) return true;
   }
   return false;
}

void SyncPosition() { g_open = HasPosition(); }

//+------------------------------------------------------------------+
datetime DayStartUTC()
{
   MqlDateTime d; TimeToStruct(TimeGMT(), d);
   d.hour = 0; d.min = 0; d.sec = 0;
   return StructToTime(d);
}

//--- daily realized stats (positions closed today, UTC), grouped by position id
void DailyStats(double &dayProfit, int &losers, int &entriesToday)
{
   dayProfit = 0; losers = 0; entriesToday = 0;
   datetime from = DayStartUTC() + (TimeTradeServer() - TimeGMT());   // server-time start of the UTC day
   if(!HistorySelect(from, TimeCurrent() + 60)) return;
   int n = HistoryDealsTotal();
   ulong pids[]; double sums[]; int k = 0;
   ArrayResize(pids, n + 1); ArrayResize(sums, n + 1);
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(tk, DEAL_MAGIC) != MagicNumber) continue;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol) continue;
      long entry = HistoryDealGetInteger(tk, DEAL_ENTRY);
      ulong pid = (ulong)HistoryDealGetInteger(tk, DEAL_POSITION_ID);
      if(entry == DEAL_ENTRY_IN) { entriesToday++; continue; }
      double p = HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_COMMISSION);
      int idx = -1;
      for(int j = 0; j < k; j++) if(pids[j] == pid) { idx = j; break; }
      if(idx < 0) { idx = k; pids[k] = pid; sums[k] = 0; k++; }
      sums[idx] += p;
   }
   for(int j = 0; j < k; j++)
   {
      dayProfit += sums[j];
      if(sums[j] < 0) losers++;
   }
}

//--- daily layer: may we open a new trade today?
bool DailyAllows(int &entriesToday)
{
   double dp; int losers;
   DailyStats(dp, losers, entriesToday);
   if(entriesToday >= MaxTradesPerDay) return false;
   if(losers >= DailyMaxLosses) return false;
   if(dp >= DailyTarget) return false;
   static double peak = 0;
   static datetime peakDay = 0;
   if(peakDay != DayStartUTC()) { peak = 0; peakDay = DayStartUTC(); }
   if(dp > peak) peak = dp;
   if(peak >= DailyKeep && dp < DailyKeep) return false;
   return true;
}

//--- news filter: block if now is within [-NewsAfterMin, +NewsBeforeMin] of a high-impact NFP/CPI/FOMC event
bool NewsBlocked()
{
   if(!UseNewsFilter) return false;
   MqlCalendarValue vals[];
   datetime now = TimeTradeServer();
   if(CalendarValueHistory(vals, now - NewsAfterMin * 60, now + NewsBeforeMin * 60, "US") <= 0) return false;
   for(int i = 0; i < ArraySize(vals); i++)
   {
      MqlCalendarEvent ev;
      if(!CalendarEventById(vals[i].event_id, ev)) continue;
      if(ev.importance != CALENDAR_IMPORTANCE_HIGH) continue;
      string nm = ev.name;
      if(StringFind(nm, "Nonfarm") >= 0 || StringFind(nm, "Non-Farm") >= 0 || StringFind(nm, "CPI") >= 0 ||
         StringFind(nm, "Interest Rate Decision") >= 0 || StringFind(nm, "FOMC") >= 0) return true;
   }
   return false;
}

//+------------------------------------------------------------------+
double CalcLots(double stopDist)
{
   double money = (RiskMoney > 0) ? RiskMoney : AccountInfoDouble(ACCOUNT_EQUITY) * RiskPercent / 100.0;
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickVal  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(tickSize <= 0 || tickVal <= 0 || step <= 0) return 0;
   double lossPerLot = stopDist / tickSize * tickVal;
   if(lossPerLot <= 0) return 0;
   double lots = MathFloor(money / lossPerLot / step) * step;
   if(lots < vmin) return 0;           // cannot size the trade within the risk -> skip (logged)
   return MathMin(lots, vmax);
}

//+------------------------------------------------------------------+
void WriteLog(datetime t, int dir, double entry, double s, double risk, double profit)
{
   int f = FileOpen(LogFile, FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI, ';');
   if(f == INVALID_HANDLE) return;
   FileSeek(f, 0, SEEK_END);
   double r = (risk > 0) ? profit / risk : 0;
   FileWrite(f, TimeToString(t, TIME_DATE | TIME_MINUTES), dir, DoubleToString(entry, _Digits), DoubleToString(s, _Digits), DoubleToString(risk, 2), DoubleToString(profit, 2), DoubleToString(r, 3));
   FileClose(f);
}

//--- track P&L of our single trade and log when it is fully closed
void OnTradeTransaction(const MqlTradeTransaction &tx, const MqlTradeRequest &rq, const MqlTradeResult &rs)
{
   if(tx.type != TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(tx.deal)) return;
   if(HistoryDealGetInteger(tx.deal, DEAL_MAGIC) != MagicNumber) return;
   if(HistoryDealGetString(tx.deal, DEAL_SYMBOL) != _Symbol) return;
   long entry = HistoryDealGetInteger(tx.deal, DEAL_ENTRY);
   if(entry == DEAL_ENTRY_IN) return;
   g_profit += HistoryDealGetDouble(tx.deal, DEAL_PROFIT) + HistoryDealGetDouble(tx.deal, DEAL_SWAP) + HistoryDealGetDouble(tx.deal, DEAL_COMMISSION);
   if(!HasPosition() && g_open)
   {
      g_open = false;
      WriteLog(TimeCurrent(), g_dir, g_entry, g_s, g_risk, g_profit);
      if(g_profit < 0) { g_consecLosses++; if(g_consecLosses >= MaxConsecLosses) { g_cooldownUntil = TimeCurrent() + 24 * 3600; g_consecLosses = 0; } }
      else g_consecLosses = 0;
      g_profit = 0;
   }
}

//--- partial close at TP1
void ManageTp1()
{
   if(!g_open || g_partial) return;
   if(!PositionSelect(_Symbol)) return;
   if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   bool hit = (g_dir > 0 && bid >= g_tp1) || (g_dir < 0 && ask <= g_tp1);
   if(!hit) return;
   double vol = PositionGetDouble(POSITION_VOLUME);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double half = MathFloor(vol * 0.5 / step) * step;
   g_partial = true;                       // only try once
   if(half >= vmin && vol - half >= vmin) trade.PositionClosePartial(_Symbol, half);
}

//+------------------------------------------------------------------+
void OnTick()
{
   ManageTp1();

   datetime bar = iTime(_Symbol, PERIOD_H4, 0);
   if(bar == lastBar) return;               // everything else runs once per new H4 bar
   lastBar = bar;
   SyncPosition();

   int rel;
   int bias = DailyBias(rel);
   double atr = Buf(hAtr, 1);
   if(atr == EMPTY_VALUE || atr <= 0) return;
   double c1 = iClose(_Symbol, PERIOD_H4, 1), h1 = iHigh(_Symbol, PERIOD_H4, 1), l1 = iLow(_Symbol, PERIOD_H4, 1);

   // channel of the DonchianBars bars BEFORE the signal bar (shifts 2..DonchianBars+1)
   double U = -1e18, L = 1e18;
   for(int i = 2; i <= DonchianBars + 1; i++) { U = MathMax(U, iHigh(_Symbol, PERIOD_H4, i)); L = MathMin(L, iLow(_Symbol, PERIOD_H4, i)); }

   //--- exits evaluated on the new bar (executed at its open)
   if(g_open)
   {
      bool exitNow = false;
      if(rel != 0 && rel != g_rel0) exitNow = true;                         // daily bias flipped
      if(g_dir > 0 && c1 <= g_U0) exitNow = true;                           // closed back inside the channel
      if(g_dir < 0 && c1 >= g_U0) exitNow = true;
      if(exitNow && PositionSelect(_Symbol)) trade.PositionClose(_Symbol);
      return;
   }

   //--- entries
   if(TimeCurrent() < g_cooldownUntil) return;
   if(bias == 0) return;
   int dir = 0;
   if(bias > 0 && c1 > U) dir = 1;
   if(bias < 0 && c1 < L) dir = -1;
   if(dir == 0) return;
   int entriesToday;
   if(!DailyAllows(entriesToday)) return;
   if(NewsBlocked()) return;

   double entry = (dir > 0) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double stop  = (dir > 0) ? l1 - StopAtrBuffer * atr : h1 + StopAtrBuffer * atr;
   double s = (entry - stop) * dir;
   if(s <= 0 || s > MaxStopAtr * atr) return;
   double lots = CalcLots(s);
   if(lots <= 0) { Print("H4BO: skipped (lot below minimum for risk). stop distance=", s); return; }

   double tp2 = entry + dir * Tp2Mult * s;
   double tp1 = entry + dir * Tp1Mult * s;
   bool ok = (dir > 0) ? trade.Buy(lots, _Symbol, 0, stop, tp2, "H4BO") : trade.Sell(lots, _Symbol, 0, stop, tp2, "H4BO");
   if(ok)
   {
      g_open = true; g_dir = dir; g_entry = entry; g_s = s; g_tp1 = tp1; g_partial = false; g_U0 = (dir > 0) ? U : L;
      g_rel0 = rel; g_entryTime = TimeCurrent(); g_profit = 0;
      g_risk = (RiskMoney > 0) ? RiskMoney : AccountInfoDouble(ACCOUNT_EQUITY) * RiskPercent / 100.0;
   }
}
//+------------------------------------------------------------------+
