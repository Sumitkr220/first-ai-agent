#!/usr/bin/env python3
"""
Demo script for Trend Analysis Features
"""

import requests
import json
from datetime import datetime

def demo_trend_analysis():
    """Demo all trend analysis features."""
    base_url = "http://localhost:8000/api/v1"
    
    print("🚀 DB-AI-AGENT Trend Analysis Demo")
    print("=" * 50)
    
    # Test quarterly trends
    print("\n📈 1. Quarterly Sales Trends (2023-2024)")
    print("-" * 40)
    
    response = requests.get(f"{base_url}/trends/quarterly?start_year=2023&end_year=2024")
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            trend_data = data["data"]
            print(f"📊 Period: {trend_data['period']}")
            print(f"💰 Total Revenue: ${trend_data['total_revenue']:,.2f}")
            print(f"📦 Total Sales: {trend_data['total_sales']:,}")
            print(f"📈 Average Quarterly Sales: {trend_data['summary']['avg_quarterly_sales']:.0f}")
            print(f"💵 Average Quarterly Revenue: ${trend_data['summary']['avg_quarterly_revenue']:,.2f}")
            
            print("\n📋 Quarterly Breakdown:")
            for quarter in trend_data["quarterly_data"]:
                growth = quarter.get("growth_rate", 0)
                growth_icon = "📈" if growth > 0 else "📉" if growth < 0 else "➡️"
                print(f"  {quarter['period']}: {quarter['sales_count']} sales, "
                      f"${quarter['revenue']:,.2f} revenue, {growth_icon} {growth}% growth")
            
            best = trend_data["summary"]["best_quarter"]
            worst = trend_data["summary"]["worst_quarter"]
            print(f"\n🏆 Best Quarter: {best['period']} ({best['sales_count']} sales, ${best['revenue']:,.2f})")
            print(f"📉 Worst Quarter: {worst['period']} ({worst['sales_count']} sales, ${worst['revenue']:,.2f})")
        else:
            print(f"❌ Error: {data['data']['error']}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    # Test monthly trends
    print("\n\n📅 2. Monthly Sales Trends (2024)")
    print("-" * 40)
    
    response = requests.get(f"{base_url}/trends/monthly?year=2024")
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            monthly_data = data["data"]["monthly_data"]
            print(f"📊 Year: {data['data']['year']}")
            
            # Find best and worst months
            best_month = max(monthly_data, key=lambda x: x["sales_count"])
            worst_month = min(monthly_data, key=lambda x: x["sales_count"])
            
            print(f"🏆 Best Month: {best_month['month_name']} ({best_month['sales_count']} sales, ${best_month['revenue']:,.2f})")
            print(f"📉 Worst Month: {worst_month['month_name']} ({worst_month['sales_count']} sales, ${worst_month['revenue']:,.2f})")
            
            print("\n📋 Monthly Breakdown:")
            for month in monthly_data:
                print(f"  {month['month_name']}: {month['sales_count']} sales, ${month['revenue']:,.2f} revenue")
        else:
            print(f"❌ Error: {data['data']['error']}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    # Test purchase method trends
    print("\n\n💳 3. Purchase Method Trends (2023-2024)")
    print("-" * 40)
    
    response = requests.get(f"{base_url}/trends/purchase-methods?start_year=2023&end_year=2024")
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            method_trends = data["data"]["method_trends"]
            
            for method, trends in method_trends.items():
                total_count = sum(t["count"] for t in trends)
                total_revenue = sum(t["revenue"] for t in trends)
                print(f"\n📱 {method.title()}:")
                print(f"  📊 Total: {total_count} sales, ${total_revenue:,.2f} revenue")
                
                # Show quarterly breakdown
                for trend in trends[-4:]:  # Last 4 quarters
                    print(f"    {trend['period']}: {trend['count']} sales, ${trend['revenue']:,.2f}")
        else:
            print(f"❌ Error: {data['data']['error']}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    # Test product trends
    print("\n\n🛍️ 4. Product Performance Trends (2023-2024)")
    print("-" * 40)
    
    response = requests.get(f"{base_url}/trends/products?start_year=2023&end_year=2024")
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            product_trends = data["data"]["product_trends"]
            
            # Calculate total performance for each product
            product_summary = {}
            for product, trends in product_trends.items():
                total_quantity = sum(t["quantity"] for t in trends)
                total_revenue = sum(t["revenue"] for t in trends)
                avg_price = sum(t["avg_price"] for t in trends) / len(trends) if trends else 0
                
                product_summary[product] = {
                    "total_quantity": total_quantity,
                    "total_revenue": total_revenue,
                    "avg_price": avg_price
                }
            
            # Sort by revenue
            sorted_products = sorted(product_summary.items(), key=lambda x: x[1]["total_revenue"], reverse=True)
            
            print("📊 Top Products by Revenue:")
            for i, (product, summary) in enumerate(sorted_products[:5], 1):
                print(f"  {i}. {product}: {summary['total_quantity']} units, "
                      f"${summary['total_revenue']:,.2f} revenue, "
                      f"${summary['avg_price']:.2f} avg price")
        else:
            print(f"❌ Error: {data['data']['error']}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    print("\n\n✅ Trend Analysis Demo Complete!")
    print("=" * 50)
    print("💡 You can now use these endpoints in your applications:")
    print("  • GET /api/v1/trends/quarterly - Quarterly sales trends")
    print("  • GET /api/v1/trends/monthly - Monthly sales trends")
    print("  • GET /api/v1/trends/purchase-methods - Purchase method trends")
    print("  • GET /api/v1/trends/products - Product performance trends")
    print("\n🌐 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    demo_trend_analysis() 