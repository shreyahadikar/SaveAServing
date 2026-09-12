import os
import re
from groq import Groq

class AICopilotEngine:
    DEFAULT_FALLBACK_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]

    def __init__(self, api_key: str = None, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model_name = model_name
        self.client = None
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"⚠️ Groq client initialization failed: {e}")
        else:
            print("ℹ️ GROQ_API_KEY not detected. Copilot running in smart operational fallback mode.")

    def _call_groq_completion(self, prompt: str, temperature: float = 0.3, max_tokens: int = 600) -> str:
        if not self.client:
            raise RuntimeError("Groq client not initialized (missing API Key).")

        models_to_try = [self.model_name] + [m for m in self.DEFAULT_FALLBACK_MODELS if m != self.model_name]
        
        last_exception = None
        for model in models_to_try:
            try:
                res = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return res.choices[0].message.content
            except Exception as e:
                last_exception = e
                continue

        raise last_exception or RuntimeError("Failed to query all configured Groq models.")

    def generate_recommendation_explanation(self, item_name: str, context_data: dict, opt_data: dict) -> str:
        final_prep = opt_data.get('final_recommended_prep', 'N/A')
        predicted_demand = opt_data.get('predicted_demand', 'N/A')

        if not self.client:
            return (
                f"For {item_name}, baseline predicted demand is {predicted_demand} units. "
                f"The recommended optimal prep target is {final_prep} units based on critical ratio calculations."
            )

        prompt = f"""
You are an expert restaurant AI operations manager. 
Provide a concise executive summary for the head chef based on these metrics.
IMPORTANT: Use standard Markdown formatting only. Do NOT output HTML tags. Do NOT truncate responses mid-sentence.

- Menu Item: {item_name}
- Selling Price: ₹{context_data.get('selling_price', 'N/A')}
- Cost: ₹{context_data.get('ingredient_cost', 'N/A')}
- Baseline Forecast Demand: {predicted_demand} units
- Target Optimal Prep (Q*): {opt_data.get('unconstrained_prep_qty', 'N/A')} units
- Final Constrained Prep: {final_prep} units
- Inventory Status: {opt_data.get('stock_status', 'Unknown')}
"""
        try:
            return self._call_groq_completion(prompt=prompt, temperature=0.3, max_tokens=400)
        except Exception:
            return f"Baseline demand for {item_name} is {predicted_demand} units. Recommended prep is set to {final_prep} units."

    def answer_scenario_query(self, query: str, opt_data: dict) -> str:
        item = opt_data.get("item_name", "the selected item")
        demand = float(opt_data.get("predicted_demand", 0))
        prep = opt_data.get("final_recommended_prep", 0)

        q_lower = query.lower()

        if not self.client:
            match = re.search(r'(\d+(?:\.\d+)?)%', q_lower)
            pct = float(match.group(1)) if match else 10.0

            if "discount" in q_lower or "promo" in q_lower or "offer" in q_lower:
                if "don't" in q_lower or "dont" in q_lower or "skip" in q_lower:
                    reduced_demand = round(demand * 0.85, 1)
                    return (
                        f"### 📊 Scenario Analysis: Skipping Discount for {item}\n\n"
                        f"* **Projected Demand Shift:** Decreases to baseline **{reduced_demand} units**.\n"
                        f"* **Inventory Impact:** Stock of {prep} units is fully secure against waste.\n"
                    )
                else:
                    boosted_demand = round(demand * (1 + pct / 100.0), 1)
                    return (
                        f"### 📊 Scenario Analysis: {pct}% Discount on {item}\n\n"
                        f"* **Projected Demand Shift:** Increases to **{boosted_demand} units**.\n"
                        f"* **Current Prep Limit:** {prep} units available.\n"
                    )
            return f"### 🔍 Insight for {item}\n\n* **Baseline Demand:** {demand} units\n* **Recommended Prep:** {prep} units"

        prompt = f"""
You are the Head Chef Copilot and AI Restaurant Operations Manager. 
Answer the manager's what-if query concisely and completely using Markdown formatting and a clean Markdown comparison table if applicable. Ensure you do not cut off mid-sentence or mid-table.

Context:
- Selected Menu Item: {item}
- Baseline Forecast Demand: {demand} units
- Recommended Prep Target: {prep} units

Manager Query: {query}
"""
        try:
            # Increased max_tokens to 800 to prevent table truncation
            return self._call_groq_completion(prompt=prompt, temperature=0.4, max_tokens=50000)
        except Exception:
            return f"Baseline demand for {item} stands at {demand} units with a recommended prep target of {prep} units."