import os
import re

from groq import Groq


class AICopilotEngine:

    DEFAULT_FALLBACK_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
    ]

    def __init__(
        self,
        api_key: str = None,
        model_name: str = "llama-3.3-70b-versatile",
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model_name = model_name
        self.client = None

        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Groq client initialization failed: {e}")
        else:
            print(
                "GROQ_API_KEY not detected. "
                "Copilot running in smart operational fallback mode."
            )

    def _call_groq_completion(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 600,
    ) -> str:

        if not self.client:
            raise RuntimeError(
                "Groq client not initialized (missing API Key)."
            )

        models_to_try = [
            self.model_name
        ] + [
            m for m in self.DEFAULT_FALLBACK_MODELS
            if m != self.model_name
        ]

        last_exception = None

        for model in models_to_try:
            try:
                res = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                return res.choices[0].message.content or ""

            except Exception as e:
                last_exception = e
                continue

        raise last_exception or RuntimeError(
            "Failed to query all configured Groq models."
        )

    def _clean_markdown(self, text: str) -> str:
        """
        Clean common malformed Markdown produced by the AI.
        Keeps normal Markdown such as headings, bullets and tables.
        """

        if not text:
            return ""

        # Remove HTML wrappers if the model returns them.
        text = re.sub(
            r"</?(div|span|p)[^>]*>",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Remove code-fence wrappers when the entire response
        # has accidentally been returned as a Markdown/code block.
        text = re.sub(r"^\s*```(?:markdown|md)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)

        # Fix escaped Markdown emphasis.
        text = text.replace(r"\*\*", "**")
        text = text.replace(r"\*", "*")

        # Fix malformed constructions such as:
        # `8.00=**480**`
        # The backtick should not surround the calculation.
        text = re.sub(
            r"`([^`\n]*?)=\s*\*\*([^*]+)\*\*`",
            r"\1 = **\2**",
            text,
        )

        # Fix cases where a backtick starts before an expression
        # and closes after the bold result.
        text = re.sub(
            r"`([^`\n]*?)\*\*([^*]+)\*\*",
            r"\1**\2**",
            text,
        )

        # Remove stray backticks immediately around bold numbers.
        text = re.sub(
            r"`\s*(\*\*[^*]+\*\*)\s*`",
            r"\1",
            text,
        )

        # Clean excessive blank lines.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def generate_recommendation_explanation(
        self,
        item_name: str,
        context_data: dict,
        opt_data: dict,
    ) -> str:

        final_prep = opt_data.get(
            "final_recommended_prep",
            "N/A",
        )

        predicted_demand = opt_data.get(
            "predicted_demand",
            "N/A",
        )

        if not self.client:
            return (
                f"For {item_name}, baseline predicted demand is "
                f"{predicted_demand} units. "
                f"The recommended optimal prep target is "
                f"{final_prep} units based on critical ratio calculations."
            )

        prompt = f"""
You are an expert restaurant AI operations manager.

Provide a concise executive summary for the head chef.

Use ONLY clean standard Markdown.

STRICT FORMATTING RULES:
- Use plain English and standard Markdown only.
- Do NOT use LaTeX.
- Do NOT use mathematical notation such as \text{}, \times, \Delta, \approx, or [ ... ].
- Do NOT use square brackets for equations.
- Do NOT use code fences.
- Do NOT use HTML.
- Write calculations in simple readable text.
- Use × for multiplication if needed.
- Use → for steps if useful.
- Use **bold** for important numbers.
- If a calculation is needed, write it like:
  Price change = -15%
  Expected demand change = 22.5%
  New demand = 59.8 × 1.225 = **73.3 units**
- Never output raw LaTeX.
- Keep the answer concise and complete.
Menu Item: {item_name}
Selling Price: ₹{context_data.get('selling_price', 'N/A')}
Ingredient Cost: ₹{context_data.get('ingredient_cost', 'N/A')}
Baseline Forecast Demand: {predicted_demand} units
Target Optimal Prep (Q*): {opt_data.get('unconstrained_prep_qty', 'N/A')} units
Final Constrained Prep: {final_prep} units
Inventory Status: {opt_data.get('stock_status', 'Unknown')}
"""

        try:
            response = self._call_groq_completion(
                prompt=prompt,
                temperature=0.3,
                max_tokens=400,
            )

            return self._clean_markdown(response)

        except Exception:
            return (
                f"Baseline demand for {item_name} is "
                f"{predicted_demand} units. "
                f"Recommended prep is set to {final_prep} units."
            )

    def answer_scenario_query(
        self,
        query: str,
        opt_data: dict,
    ) -> str:

        item = opt_data.get(
            "item_name",
            "the selected item",
        )

        demand = float(
            opt_data.get(
                "predicted_demand",
                0,
            )
        )

        prep = opt_data.get(
            "final_recommended_prep",
            0,
        )

        q_lower = query.lower()

        # ---------------------------------------------------------
        # SMART FALLBACK MODE
        # ---------------------------------------------------------
        if not self.client:

            match = re.search(
                r"(\d+(?:\.\d+)?)%",
                q_lower,
            )

            pct = float(match.group(1)) if match else 10.0

            if (
                "discount" in q_lower
                or "promo" in q_lower
                or "offer" in q_lower
            ):

                if (
                    "don't" in q_lower
                    or "dont" in q_lower
                    or "skip" in q_lower
                ):

                    reduced_demand = round(
                        demand * 0.85,
                        1,
                    )

                    return (
                        f"### 📊 Scenario Analysis: "
                        f"Skipping Discount for {item}\n\n"
                        f"- **Projected Demand:** "
                        f"Decreases to **{reduced_demand} units**.\n"
                        f"- **Inventory Impact:** "
                        f"Stock of **{prep} units** is "
                        f"fully secure against waste."
                    )

                else:

                    boosted_demand = round(
                        demand * (1 + pct / 100.0),
                        1,
                    )

                    return (
                        f"### 📊 Scenario Analysis: "
                        f"{pct}% Discount on {item}\n\n"
                        f"- **Projected Demand:** "
                        f"Increases to **{boosted_demand} units**.\n"
                        f"- **Current Prep Limit:** "
                        f"**{prep} units** available."
                    )

            return (
                f"### 🔍 Insight for {item}\n\n"
                f"- **Baseline Demand:** {demand} units\n"
                f"- **Recommended Prep:** {prep} units"
            )

        # ---------------------------------------------------------
        # GROQ MODE
        # ---------------------------------------------------------

        prompt = f"""
You are the Head Chef Copilot and AI Restaurant Operations Manager.

Answer the manager's what-if query concisely and completely.

Use clean standard Markdown.

STRICT FORMATTING RULES:
- Do NOT use HTML.
- Do NOT use code fences.
- Do NOT put calculations inside backticks.
- Use **bold** for important numbers and conclusions.
- If a comparison is useful, create a clean Markdown table.
- Every Markdown table must have:
  1. A header row
  2. A separator row
  3. Matching numbers of columns
- Do NOT put Markdown bold markers inside backticks.
- Never write malformed expressions such as:
  `8.00=**480**`
- Correct format:
  8.00 × 60 = **480**
- Do not escape normal Markdown characters.
- Finish the response completely.

Context:

Selected Menu Item: {item}

Baseline Forecast Demand: {demand} units

Recommended Prep Target: {prep} units

Manager Query:
{query}
"""

        try:

            response = self._call_groq_completion(
                prompt=prompt,
                temperature=0.4,
                max_tokens=5000,
            )

            return self._clean_markdown(response)

        except Exception:

            return (
                f"Baseline demand for {item} stands at "
                f"{demand} units with a recommended prep "
                f"target of {prep} units."
            )