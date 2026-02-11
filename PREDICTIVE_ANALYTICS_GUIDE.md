# 📊 Predictive Analytics Guide - How to Use Inventory Forecasts

## Overview

The **30-Day Inventory Forecast** predicts how many spare parts you'll need to restock over the next 30 days based on historical usage patterns and machine learning predictions.

---

## 🎯 Understanding the Forecast Display

### What You See

The forecast shows:
- **Part Name**: The spare part that needs restocking
- **Predicted Units**: How many units you'll likely need in the next 30 days
- **Color-Coded Status**: Visual indicator of urgency
- **Progress Bar**: Relative demand compared to other parts

### Example from Your Screen:

```
Voltage Regulator: 26 units (RED)    ████████████████████
Carburetor:        5 units (GREEN)   ███
Engine Gasket:     0 units (GREEN)   ░
```

---

## 🚦 Color-Coded Restock Urgency

### 🔴 **RED (High Priority) - Restock Immediately**
- **When**: Predicted demand is **10+ units** in 30 days
- **Action**: 
  - ✅ Order immediately
  - ✅ Check current stock levels
  - ✅ Consider ordering extra buffer stock
- **Example**: Voltage Regulator (26 units) - **URGENT**

### 🟠 **ORANGE (Medium Priority) - Plan to Restock**
- **When**: Predicted demand is **5-9 units** in 30 days
- **Action**:
  - ✅ Order within the next week
  - ✅ Monitor stock levels closely
  - ✅ Consider ordering if stock is low
- **Example**: If a part shows 7 units

### 🟢 **GREEN (Low Priority) - Monitor Only**
- **When**: Predicted demand is **0-4 units** in 30 days
- **Action**:
  - ✅ Monitor stock levels
  - ✅ No immediate action needed
  - ✅ Order when stock gets low
- **Example**: Carburetor (5 units), Engine Gasket (0 units)

---

## 📋 Step-by-Step: How to Use the Forecast

### Step 1: Review the Forecast
1. Navigate to **Admin Panel → Predictions**
2. Look at the **30-Day Inventory Forecast** section
3. Review all parts listed

### Step 2: Check Current Stock Levels
1. Go to **Admin Panel → Spare Parts**
2. Compare forecasted demand with current stock
3. Calculate: `Current Stock - Forecasted Demand = Remaining Stock`

### Step 3: Make Restocking Decisions

#### For RED Items (High Priority):
```
Example: Voltage Regulator
- Forecast: 26 units needed in 30 days
- Current Stock: 10 units
- Decision: Order 30-40 units immediately
  (26 needed + 4-14 buffer for safety)
```

#### For ORANGE Items (Medium Priority):
```
Example: Carburetor
- Forecast: 5 units needed in 30 days
- Current Stock: 8 units
- Decision: Order 10-15 units within a week
  (5 needed + 5-10 buffer)
```

#### For GREEN Items (Low Priority):
```
Example: Engine Gasket
- Forecast: 0 units needed in 30 days
- Current Stock: 20 units
- Decision: No action needed, monitor monthly
```

---

## 💡 Practical Restocking Strategy

### Weekly Review Process:

1. **Monday Morning**: Check the forecast
   - Identify all RED items
   - Check current stock levels
   - Place urgent orders

2. **Mid-Week**: Review ORANGE items
   - Plan restocking for next week
   - Check supplier lead times

3. **Friday**: Review GREEN items
   - Monitor stock levels
   - Plan for next month if needed

### Monthly Planning:

- **Week 1**: Review full 30-day forecast
- **Week 2**: Place orders for RED items
- **Week 3**: Place orders for ORANGE items
- **Week 4**: Review and adjust for next month

---

## 📊 Understanding the Numbers

### What "26 units in 30 days" Means:

- **Not**: "You need exactly 26 units"
- **But**: "Based on historical patterns, you'll likely use around 26 units in the next 30 days"

### Factors Considered by the AI:
- ✅ Historical usage patterns
- ✅ Day of week trends (weekends vs weekdays)
- ✅ Recent usage trends (last 7 days average)
- ✅ Seasonal patterns (if data available)

---

## ⚠️ Important Notes

### The Forecast is a Prediction, Not a Guarantee

- **Use it as a guide**, not an exact requirement
- **Always check current stock** before ordering
- **Consider buffer stock** for critical parts
- **Account for supplier lead times**

### When to Adjust:

1. **Special Events**: If you know of upcoming events (e.g., motorcycle rally), order extra
2. **Seasonal Changes**: Adjust for known seasonal patterns
3. **New Services**: If you add new services, monitor closely
4. **Supplier Issues**: If suppliers have delays, order earlier

---

## 🎯 Best Practices

### ✅ DO:
- ✅ Review forecast weekly
- ✅ Order RED items immediately
- ✅ Keep buffer stock for critical parts
- ✅ Track actual vs predicted usage
- ✅ Adjust orders based on current stock

### ❌ DON'T:
- ❌ Order exactly the forecasted amount (add buffer)
- ❌ Ignore RED items
- ❌ Wait until stock is zero
- ❌ Order without checking current stock
- ❌ Ignore the forecast completely

---

## 📈 Example Scenario

### Scenario: Voltage Regulator (26 units forecast)

**Current Situation:**
- Forecast: 26 units needed in 30 days
- Current Stock: 5 units
- Supplier Lead Time: 7 days
- Average Daily Usage: ~0.87 units/day (26 ÷ 30)

**Calculation:**
```
Days until stockout: 5 units ÷ 0.87 units/day = ~6 days
Time to order: NOW (before stock runs out)
Order Quantity: 30-35 units
  - 26 units (forecasted need)
  - 4-9 units (safety buffer)
```

**Action Plan:**
1. ✅ Order 30-35 units TODAY
2. ✅ Track delivery (7 days)
3. ✅ Stock will arrive before running out
4. ✅ Maintain healthy inventory levels

---

## 🔄 How the Forecast Updates

### Automatic Updates:
- ✅ Forecast refreshes when you click the refresh button
- ✅ Model retrains automatically when new appointment data is available
- ✅ Predictions improve as more data is collected

### When to Refresh:
- ✅ After completing many appointments
- ✅ At the start of each week
- ✅ Before making restocking decisions
- ✅ After special events or busy periods

---

## 📞 Quick Reference

| Forecast | Color | Action | Timeline |
|----------|-------|--------|----------|
| 10+ units | 🔴 RED | Order immediately | Today |
| 5-9 units | 🟠 ORANGE | Order this week | Within 7 days |
| 0-4 units | 🟢 GREEN | Monitor only | No rush |

---

## 🎓 Summary

**The 30-Day Inventory Forecast helps you:**
1. **Predict** future demand based on historical patterns
2. **Prioritize** which parts need restocking first
3. **Plan** orders before running out of stock
4. **Optimize** inventory levels and reduce stockouts

**Remember**: The forecast is a tool to guide your decisions. Always combine it with:
- Current stock levels
- Supplier lead times
- Business knowledge (events, seasons, etc.)
- Safety buffer for critical parts

**Use it weekly, act on RED items immediately, and you'll maintain optimal inventory levels!** 🚀

