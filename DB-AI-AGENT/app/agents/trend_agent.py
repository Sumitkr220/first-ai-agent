import logging
from typing import Dict, Any, List, Optional

from app.services.trend_analysis import trend_analysis_service

try:
    import plotly.graph_objects as go
    import plotly.express as px
except Exception as e:  # pragma: no cover
    raise RuntimeError("Plotly is required for chart generation. Please install plotly.") from e


logger = logging.getLogger(__name__)


class TrendAgent:
    """Agent that computes trend data directly and produces Plotly charts (no HTTP).

    Supported trend types:
    - quarterly: Quarterly sales and revenue over a year range
    - monthly: Monthly sales and revenue for a given year
    - purchase_methods: Trends per purchase method across quarters
    - products: Product performance trends; selects top-N products by total revenue
    """

    def __init__(self, top_n_products: int = 5):
        self.top_n_products = top_n_products

    # Public API
    def build_chart(
        self,
        trend_type: str,
        *,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        year: Optional[int] = None,
    ) -> go.Figure:
        trend_type = (trend_type or "").lower().strip()
        if trend_type == "quarterly":
            if start_year is None or end_year is None:
                raise ValueError("quarterly requires start_year and end_year")
            data = trend_analysis_service.get_quarterly_sales_trend(start_year, end_year)
            return self._chart_quarterly(data)

        if trend_type == "monthly":
            if year is None:
                raise ValueError("monthly requires year")
            data = trend_analysis_service.get_monthly_sales_trend(year)
            return self._chart_monthly(data)

        if trend_type in ("purchase_methods", "purchase-methods", "purchase_methods_trend"):
            if start_year is None or end_year is None:
                raise ValueError("purchase_methods requires start_year and end_year")
            data = trend_analysis_service.get_purchase_method_trend(start_year, end_year)
            return self._chart_purchase_methods(data)

        if trend_type in ("products", "product_trends", "product-performance"):
            if start_year is None or end_year is None:
                raise ValueError("products requires start_year and end_year")
            data = trend_analysis_service.get_product_performance_trend(start_year, end_year)
            return self._chart_products(data)

        raise ValueError(f"Unsupported trend_type: {trend_type}")

    # Chart builders
    def _chart_quarterly(self, data: Dict[str, Any]) -> go.Figure:
        if not data.get("success"):
            raise RuntimeError(f"Trend computation failed: {data.get('error')}")

        quarters = [q["period"] for q in data.get("quarterly_data", [])]
        sales = [q["sales_count"] for q in data.get("quarterly_data", [])]
        revenue = [q["revenue"] for q in data.get("quarterly_data", [])]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Sales Count", x=quarters, y=sales, yaxis="y", offsetgroup=1))
        fig.add_trace(go.Bar(name="Revenue", x=quarters, y=revenue, yaxis="y2", offsetgroup=2))

        fig.update_layout(
            title=f"Quarterly Sales and Revenue ({data.get('period')})",
            xaxis_title="Quarter",
            yaxis=dict(title="Sales Count"),
            yaxis2=dict(title="Revenue", overlaying="y", side="right"),
            barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=60, r=40, l=60, b=60),
        )
        return fig

    def _chart_monthly(self, data: Dict[str, Any]) -> go.Figure:
        if not data.get("success"):
            raise RuntimeError(f"Trend computation failed: {data.get('error')}")

        months = [m["month_name"] for m in data.get("monthly_data", [])]
        sales = [m["sales_count"] for m in data.get("monthly_data", [])]
        revenue = [m["revenue"] for m in data.get("monthly_data", [])]

        fig = go.Figure()
        fig.add_trace(go.Scatter(name="Sales Count", x=months, y=sales, mode="lines+markers", yaxis="y"))
        fig.add_trace(go.Scatter(name="Revenue", x=months, y=revenue, mode="lines+markers", yaxis="y2"))

        fig.update_layout(
            title=f"Monthly Sales and Revenue ({data.get('year')})",
            xaxis_title="Month",
            yaxis=dict(title="Sales Count"),
            yaxis2=dict(title="Revenue", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=60, r=40, l=60, b=60),
        )
        return fig

    def _chart_purchase_methods(self, data: Dict[str, Any]) -> go.Figure:
        if not data.get("success"):
            raise RuntimeError(f"Trend computation failed: {data.get('error')}")

        method_trends: Dict[str, List[Dict[str, Any]]] = data.get("method_trends", {})
        # Build unified x-axis (sorted by period order)
        all_periods: List[str] = sorted({t["period"] for trends in method_trends.values() for t in trends})

        fig = go.Figure()
        for method, trends in method_trends.items():
            period_to_count = {t["period"]: t["count"] for t in trends}
            counts = [period_to_count.get(p, 0) for p in all_periods]
            fig.add_trace(go.Scatter(name=f"{method} (count)", x=all_periods, y=counts, mode="lines+markers"))

        fig.update_layout(
            title="Purchase Method Trends (Count per Quarter)",
            xaxis_title="Quarter",
            yaxis=dict(title="Sales Count"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=60, r=40, l=60, b=60),
        )
        return fig

    def _chart_products(self, data: Dict[str, Any]) -> go.Figure:
        if not data.get("success"):
            raise RuntimeError(f"Trend computation failed: {data.get('error')}")

        product_trends: Dict[str, List[Dict[str, Any]]] = data.get("product_trends", {})

        # Rank products by total revenue and select top-N
        def total_rev(trends: List[Dict[str, Any]]) -> float:
            return float(sum(t.get("revenue", 0.0) for t in trends))

        ranked = sorted(product_trends.items(), key=lambda kv: total_rev(kv[1]), reverse=True)[: self.top_n_products]

        # Unified periods
        all_periods: List[str] = sorted({t["period"] for _, trends in ranked for t in trends})

        fig = go.Figure()
        for product, trends in ranked:
            period_to_revenue = {t["period"]: t.get("revenue", 0.0) for t in trends}
            series = [period_to_revenue.get(p, 0.0) for p in all_periods]
            fig.add_trace(go.Scatter(name=product, x=all_periods, y=series, mode="lines+markers"))

        fig.update_layout(
            title=f"Top {self.top_n_products} Product Revenue Trends",
            xaxis_title="Quarter",
            yaxis=dict(title="Revenue"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=60, r=40, l=60, b=60),
        )
        return fig


# Global instance for convenience
trend_agent = TrendAgent()

