import numpy as np
import pandas as pd
from scipy.stats import norm

class NewsvendorOptimizer:
    """
    Translates predicted demand into optimal prep quantity by balancing:
    - Cost of Overage (Waste): Cost of unsold inventory
    - Cost of Underage (Stockout): Lost profit from unfulfilled demand
    """
    def __init__(self, rmse_error: float = 5.507):
        # Default standard deviation of forecast residual (RMSE from Random Forest)
        self.sigma = rmse_error

    def calculate_optimal_prep(self, 
                               predicted_demand: float, 
                               selling_price: float, 
                               ingredient_cost: float, 
                               available_stock: float = None) -> dict:
        """
        Calculates optimal preparation quantity Q* using Newsvendor optimization formula.
        """
        # 1. Calculate financial trade-offs
        underage_cost = max(0.0, selling_price - ingredient_cost)  # Lost profit (Cu)
        overage_cost = max(0.01, ingredient_cost)                   # Waste cost (Co)

        # 2. Critical Fractile (Target Service Level)
        critical_fractile = underage_cost / (underage_cost + overage_cost)

        # 3. Z-score standard normal percentile
        z_score = norm.ppf(critical_fractile)

        # 4. Optimal Prep Quantity Q*
        raw_optimal_q = predicted_demand + (z_score * self.sigma)
        recommended_prep = max(0, int(round(raw_optimal_q)))

        # 5. Inventory Stock Check
        stock_status = "OK"
        shortage_qty = 0
        final_prep = recommended_prep

        if available_stock is not None:
            if recommended_prep > available_stock:
                stock_status = "INSUFFICIENT_STOCK"
                shortage_qty = int(recommended_prep - available_stock)
                final_prep = int(available_stock)

        # 6. Expected waste and stockout estimate
        expected_waste = max(0, final_prep - int(round(predicted_demand)))
        expected_lost_sales = max(0, int(round(predicted_demand)) - final_prep)

        return {
            "predicted_demand": round(predicted_demand, 1),
            "critical_fractile": round(critical_fractile, 3),
            "z_score": round(z_score, 2),
            "unconstrained_prep_qty": recommended_prep,
            "final_recommended_prep": final_prep,
            "expected_waste_units": expected_waste,
            "expected_lost_sales_units": expected_lost_sales,
            "stock_status": stock_status,
            "shortage_qty": shortage_qty
        }


if __name__ == "__main__":
    # Test simulation
    optimizer = NewsvendorOptimizer(rmse_error=5.507)

    # Example: Chicken Biryani
    sample = optimizer.calculate_optimal_prep(
        predicted_demand=152.0,
        selling_price=220.0,
        ingredient_cost=90.0,
        available_stock=130.0
    )

    print("=== NEWSVENDOR OPTIMIZER TEST OUTPUT ===")
    for k, v in sample.items():
        print(f"{k}: {v}")