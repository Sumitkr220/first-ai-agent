#!/usr/bin/env python3
import argparse
import os
import sys

# Ensure app imports work when running from project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.agents.trend_agent import trend_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate trend chart without using the HTTP API")
    parser.add_argument("trend_type", choices=[
        "quarterly", "monthly", "purchase_methods", "purchase-methods", "products"
    ], help="Type of trend to generate")
    parser.add_argument("--start-year", type=int, help="Start year (for quarterly, purchase_methods, products)")
    parser.add_argument("--end-year", type=int, help="End year (for quarterly, purchase_methods, products)")
    parser.add_argument("--year", type=int, help="Year (for monthly)")
    parser.add_argument("--output", type=str, default="trend_chart.html", help="Output HTML file path")
    parser.add_argument("--top-n", type=int, default=5, help="Top N products for product trends")

    args = parser.parse_args()

    # Configure agent
    if args.trend_type in ("products",):
        trend_agent.top_n_products = args.top_n

    fig = trend_agent.build_chart(
        args.trend_type,
        start_year=args.start_year,
        end_year=args.end_year,
        year=args.year,
    )
    fig.write_html(args.output, include_plotlyjs="cdn")
    print(f"✅ Chart generated: {args.output}")


if __name__ == "__main__":
    main()

