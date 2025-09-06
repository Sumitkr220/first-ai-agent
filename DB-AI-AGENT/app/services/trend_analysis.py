#!/usr/bin/env python3
"""
Trend Analysis Service for Sales Data
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bson import Decimal128

from app.database.connection import db_manager

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Service for analyzing sales trends and patterns."""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def get_quarterly_sales_trend(self, start_year: int = 2023, end_year: int = 2024) -> Dict[str, Any]:
        """Get quarterly sales trends over specified years."""
        try:
            collection = self.db_manager.get_collection("sales")
            
            # Create date range
            start_date = datetime(start_year, 1, 1)
            end_date = datetime(end_year, 12, 31, 23, 59, 59)
            
            pipeline = [
                {
                    "$match": {
                        "saleDate": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$saleDate"},
                            "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}
                        },
                        "total_sales": {"$sum": 1},
                        "total_revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}},
                        "avg_satisfaction": {"$avg": "$customer.satisfaction"}
                    }
                },
                {"$sort": {"_id.year": 1, "_id.quarter": 1}}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Process results
            quarterly_data = []
            total_sales = 0
            total_revenue = 0
            
            for result in results:
                year = result["_id"]["year"]
                quarter = result["_id"]["quarter"]
                sales_count = result["total_sales"]
                revenue = float(result["total_revenue"]) if result["total_revenue"] else 0
                avg_satisfaction = float(result["avg_satisfaction"]) if result["avg_satisfaction"] else 0
                
                quarterly_data.append({
                    "period": f"Q{quarter} {year}",
                    "year": year,
                    "quarter": quarter,
                    "sales_count": sales_count,
                    "revenue": revenue,
                    "avg_satisfaction": round(avg_satisfaction, 2)
                })
                
                total_sales += sales_count
                total_revenue += revenue
            
            # Calculate growth rates
            for i in range(1, len(quarterly_data)):
                prev_sales = quarterly_data[i-1]["sales_count"]
                curr_sales = quarterly_data[i]["sales_count"]
                growth_rate = ((curr_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
                quarterly_data[i]["growth_rate"] = round(growth_rate, 2)
            
            return {
                "success": True,
                "period": f"{start_year}-{end_year}",
                "total_sales": total_sales,
                "total_revenue": round(total_revenue, 2),
                "quarterly_data": quarterly_data,
                "summary": {
                    "avg_quarterly_sales": round(total_sales / len(quarterly_data), 2),
                    "avg_quarterly_revenue": round(total_revenue / len(quarterly_data), 2),
                    "best_quarter": max(quarterly_data, key=lambda x: x["sales_count"]),
                    "worst_quarter": min(quarterly_data, key=lambda x: x["sales_count"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error in quarterly sales trend analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "quarterly_data": []
            }
    
    def get_monthly_sales_trend(self, year: int = 2024) -> Dict[str, Any]:
        """Get monthly sales trends for a specific year."""
        try:
            collection = self.db_manager.get_collection("sales")
            
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            
            pipeline = [
                {
                    "$match": {
                        "saleDate": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$saleDate"},
                            "month": {"$month": "$saleDate"}
                        },
                        "total_sales": {"$sum": 1},
                        "total_revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}},
                        "avg_satisfaction": {"$avg": "$customer.satisfaction"}
                    }
                },
                {"$sort": {"_id.year": 1, "_id.month": 1}}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Process results
            monthly_data = []
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
            for result in results:
                month = result["_id"]["month"]
                sales_count = result["total_sales"]
                revenue = float(result["total_revenue"]) if result["total_revenue"] else 0
                avg_satisfaction = float(result["avg_satisfaction"]) if result["avg_satisfaction"] else 0
                
                monthly_data.append({
                    "month": month,
                    "month_name": month_names[month - 1],
                    "sales_count": sales_count,
                    "revenue": revenue,
                    "avg_satisfaction": round(avg_satisfaction, 2)
                })
            
            return {
                "success": True,
                "year": year,
                "monthly_data": monthly_data
            }
            
        except Exception as e:
            logger.error(f"Error in monthly sales trend analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "monthly_data": []
            }
    
    def get_purchase_method_trend(self, start_year: int = 2023, end_year: int = 2024) -> Dict[str, Any]:
        """Get trends by purchase method."""
        try:
            collection = self.db_manager.get_collection("sales")
            
            start_date = datetime(start_year, 1, 1)
            end_date = datetime(end_year, 12, 31, 23, 59, 59)
            
            pipeline = [
                {
                    "$match": {
                        "saleDate": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": {
                            "purchaseMethod": "$purchaseMethod",
                            "year": {"$year": "$saleDate"},
                            "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}
                        },
                        "count": {"$sum": 1},
                        "revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}}
                    }
                },
                {"$sort": {"_id.purchaseMethod": 1, "_id.year": 1, "_id.quarter": 1}}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Group by purchase method
            method_trends = {}
            for result in results:
                method = result["_id"]["purchaseMethod"]
                year = result["_id"]["year"]
                quarter = result["_id"]["quarter"]
                count = result["count"]
                revenue = float(result["revenue"]) if result["revenue"] else 0
                
                if method not in method_trends:
                    method_trends[method] = []
                
                method_trends[method].append({
                    "period": f"Q{quarter} {year}",
                    "count": count,
                    "revenue": revenue
                })
            
            return {
                "success": True,
                "method_trends": method_trends
            }
            
        except Exception as e:
            logger.error(f"Error in purchase method trend analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "method_trends": {}
            }
    
    def get_product_performance_trend(self, start_year: int = 2023, end_year: int = 2024) -> Dict[str, Any]:
        """Get product performance trends."""
        try:
            collection = self.db_manager.get_collection("sales")
            
            start_date = datetime(start_year, 1, 1)
            end_date = datetime(end_year, 12, 31, 23, 59, 59)
            
            pipeline = [
                {
                    "$match": {
                        "saleDate": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": {
                            "product": "$items.name",
                            "year": {"$year": "$saleDate"},
                            "quarter": {"$ceil": {"$divide": [{"$month": "$saleDate"}, 3]}}
                        },
                        "total_quantity": {"$sum": "$items.quantity"},
                        "total_revenue": {"$sum": {"$multiply": [{"$toDouble": "$items.price"}, "$items.quantity"]}},
                        "avg_price": {"$avg": {"$toDouble": "$items.price"}}
                    }
                },
                {"$sort": {"_id.product": 1, "_id.year": 1, "_id.quarter": 1}}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Group by product
            product_trends = {}
            for result in results:
                product = result["_id"]["product"]
                year = result["_id"]["year"]
                quarter = result["_id"]["quarter"]
                quantity = result["total_quantity"]
                revenue = float(result["total_revenue"]) if result["total_revenue"] else 0
                avg_price = float(result["avg_price"]) if result["avg_price"] else 0
                
                if product not in product_trends:
                    product_trends[product] = []
                
                product_trends[product].append({
                    "period": f"Q{quarter} {year}",
                    "quantity": quantity,
                    "revenue": revenue,
                    "avg_price": avg_price
                })
            
            return {
                "success": True,
                "product_trends": product_trends
            }
            
        except Exception as e:
            logger.error(f"Error in product performance trend analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "product_trends": {}
            }


# Global trend analysis service instance
trend_analysis_service = TrendAnalysisService() 