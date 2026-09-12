# 🍽️ Intelligent Restaurant Operations Suite

An intelligent restaurant operations platform that combines **machine learning demand forecasting** with the classical **Newsvendor inventory optimization model** to help restaurants reduce food waste, prevent over-preparation, and maximize profit margins.

---

##  Project Overview

Restaurant operations often face a difficult balancing act:

- **Over-preparation** leads to food spoilage, unnecessary costs, and waste.
- **Under-preparation** leads to stockouts, lost sales, and dissatisfied customers.

This project addresses that challenge by combining **machine learning-based demand forecasting** with **Newsvendor inventory theory**.

The primary objective is to determine **how much food should be prepared** for a given day while balancing the cost of excess inventory against the potential revenue lost from insufficient preparation.

The platform provides restaurant managers and kitchen staff with an intelligent decision-support system for daily preparation and inventory planning.

---

##  Key Features

###  Newsvendor Model Integration

The system integrates the classical **Newsvendor Model** to mathematically optimize preparation quantities.

It balances the trade-off between:

- **Over-preparation cost** — food spoilage and waste caused by preparing too much.
- **Under-preparation cost** — lost sales and missed revenue caused by preparing too little.

This allows the system to recommend preparation quantities that maximize expected profitability while minimizing unnecessary waste.

---

### 🌦️ Real-Time Weather Telemetry

Weather conditions can significantly influence restaurant demand.

The system automatically retrieves real-time:

- 🌡️ Temperature
- 🌧️ Precipitation
- ☁️ Weather conditions

These signals are incorporated into demand predictions so that recommendations can dynamically adapt to changing environmental conditions.

---

### 👨‍🍳 Head Chef Copilot

The platform includes an interactive natural-language **Head Chef Copilot** designed to assist restaurant managers with operational decision-making.

Managers can use the copilot to explore **what-if scenarios**, such as:

- Running a promotional campaign
- Increasing or decreasing menu prices
- Preparing for a special event
- Anticipating unusual demand
- Evaluating different preparation quantities

Example:

> "What happens if we run a 15% promotion today?"

The copilot helps managers understand how these changes may affect demand and preparation requirements.

---

### 📦 Inventory Safeguards

The system includes safeguards designed to prevent excessive preparation before ingredients leave the pantry.

Key protections include:

- **Hard stock capping**
- **Automated shortage alerts**
- Inventory-aware preparation recommendations
- Prevention of excessive batch preparation

These safeguards add an operational layer on top of the forecasting and optimization models.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │      Restaurant User    │
                    │     / Kitchen Manager   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Streamlit Frontend    │
                    │                         │
                    │  • Dashboard            │
                    │  • Forecasts            │
                    │  • Inventory            │
                    │  • Chef Copilot         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Backend    │
                    │                         │
                    │  • Model Inference      │
                    │  • Optimization         │
                    │  • Copilot Routing      │
                    │  • Business Logic       │
                    └───────┬─────────┬───────┘
                            │         │
               ┌────────────┘         └────────────┐
               ▼                                   ▼
    ┌─────────────────────┐             ┌─────────────────────┐
    │   ML Forecasting    │             │ Newsvendor Model    │
    │                     │             │                     │
    │ Historical Demand   │             │ Over-preparation    │
    │ Weather Signals     │             │ Under-preparation   │
    │ Demand Trends       │             │ Optimal Quantity    │
    └──────────┬──────────┘             └──────────┬──────────┘
               │                                   │
               └────────────────┬──────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │   Inventory Safeguards  │
                    │                         │
                    │ • Stock Limits          │
                    │ • Shortage Alerts       │
                    │ • Preparation Controls  │
                    └─────────────────────────┘