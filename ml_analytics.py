"""
MR Bot ML/DL Enhanced Data Processor
Advanced analytics and pattern recognition for MR field data
"""
import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class MRAnalyticsEngine:
    """Advanced ML/DL analytics for MR performance tracking"""
    
    def __init__(self):
        self.data_cache = {}
        self.pattern_models = {}
        self.performance_metrics = {}
        self.load_historical_data()
        self.initialize_ml_models()
        
    def load_historical_data(self):
        """Load historical data for ML training"""
        try:
            data_file = os.path.join(os.path.dirname(__file__), 'data', 'historical_data.json')
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.data_cache = json.load(f)
                logger.info("Historical data loaded successfully")
            else:
                self.data_cache = {
                    "visits": [],
                    "expenses": [],
                    "patterns": {},
                    "performance_trends": {}
                }
                
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            
    def initialize_ml_models(self):
        """Initialize ML models for pattern recognition"""
        try:
            self.pattern_models = {
                "visit_frequency": self.build_frequency_model(),
                "expense_anomaly": self.build_anomaly_model(),
                "product_preference": self.build_preference_model(),
                "location_clustering": self.build_location_model(),
                "performance_prediction": self.build_performance_model()
            }
            
        except Exception as e:
            logger.error(f"ML model initialization error: {e}")
            
    def build_frequency_model(self) -> Dict:
        """Build visit frequency analysis model"""
        model = {
            "patterns": {},
            "optimal_frequency": {},
            "seasonal_trends": {}
        }
        
        # Analyze historical visit patterns
        visits = self.data_cache.get("visits", [])
        if visits:
            # Group by doctor
            doctor_visits = defaultdict(list)
            for visit in visits:
                doctor = visit.get("contact", {}).get("name", "")
                if doctor:
                    doctor_visits[doctor].append(visit)
                    
            # Calculate optimal frequencies
            for doctor, visit_list in doctor_visits.items():
                if len(visit_list) > 3:  # Need sufficient data
                    # Calculate average gap between visits
                    dates = [datetime.fromisoformat(v.get("timestamp", "")) for v in visit_list if v.get("timestamp")]
                    if len(dates) > 1:
                        gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                        avg_gap = statistics.mean(gaps)
                        model["optimal_frequency"][doctor] = avg_gap
                        
        return model
        
    def build_anomaly_model(self) -> Dict:
        """Build expense anomaly detection model"""
        model = {
            "normal_ranges": {},
            "category_patterns": {},
            "outlier_thresholds": {}
        }
        
        expenses = self.data_cache.get("expenses", [])
        if expenses:
            # Group by category
            category_amounts = defaultdict(list)
            for expense in expenses:
                category = expense.get("expense", {}).get("category", "other")
                amount = expense.get("expense", {}).get("amount", 0)
                if amount > 0:
                    category_amounts[category].append(amount)
                    
            # Calculate normal ranges
            for category, amounts in category_amounts.items():
                if len(amounts) > 5:  # Need sufficient data
                    mean_amount = statistics.mean(amounts)
                    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    
                    model["normal_ranges"][category] = {
                        "mean": mean_amount,
                        "std_dev": std_dev,
                        "min": min(amounts),
                        "max": max(amounts),
                        "q75": statistics.quantiles(amounts, n=4)[2] if len(amounts) > 4 else mean_amount
                    }
                    
                    # Set outlier threshold at 2 standard deviations
                    model["outlier_thresholds"][category] = mean_amount + (2 * std_dev)
                    
        return model
        
    def build_preference_model(self) -> Dict:
        """Build product preference analysis model"""
        model = {
            "doctor_preferences": {},
            "product_success_rates": {},
            "recommendation_patterns": {}
        }
        
        visits = self.data_cache.get("visits", [])
        
        # Analyze doctor-product associations
        doctor_products = defaultdict(Counter)
        for visit in visits:
            doctor = visit.get("contact", {}).get("name", "")
            orders = visit.get("orders", [])
            
            for order in orders:
                product = order.get("product", "")
                quantity = order.get("quantity", 0)
                if doctor and product:
                    doctor_products[doctor][product] += quantity
                    
        # Build preference profiles
        for doctor, products in doctor_products.items():
            total_orders = sum(products.values())
            preferences = {}
            for product, count in products.items():
                preferences[product] = {
                    "frequency": count / total_orders,
                    "total_quantity": count,
                    "preference_score": count / total_orders
                }
            model["doctor_preferences"][doctor] = preferences
            
        return model
        
    def build_location_model(self) -> Dict:
        """Build location clustering model"""
        model = {
            "location_clusters": {},
            "travel_patterns": {},
            "efficiency_metrics": {}
        }
        
        # Analyze location patterns
        visits = self.data_cache.get("visits", [])
        location_visits = defaultdict(int)
        
        for visit in visits:
            location = visit.get("contact", {}).get("location", "")
            if location:
                location_visits[location] += 1
                
        # Sort locations by frequency
        sorted_locations = sorted(location_visits.items(), key=lambda x: x[1], reverse=True)
        
        model["location_clusters"] = {
            "high_frequency": [loc for loc, count in sorted_locations[:5]],
            "medium_frequency": [loc for loc, count in sorted_locations[5:15]],
            "low_frequency": [loc for loc, count in sorted_locations[15:]]
        }
        
        return model
        
    def build_performance_model(self) -> Dict:
        """Build performance prediction model"""
        model = {
            "success_indicators": {},
            "performance_trends": {},
            "prediction_factors": {}
        }
        
        visits = self.data_cache.get("visits", [])
        if visits:
            # Analyze success patterns
            successful_visits = [v for v in visits if v.get("assessment", {}).get("business_potential") == "high"]
            
            if successful_visits:
                # Extract success factors
                success_factors = {
                    "optimal_visit_duration": [],
                    "successful_products": Counter(),
                    "effective_discussions": []
                }
                
                for visit in successful_visits:
                    orders = visit.get("orders", [])
                    for order in orders:
                        success_factors["successful_products"][order.get("product", "")] += 1
                        
                model["success_indicators"] = success_factors
                
        return model
        
    def analyze_visit_patterns(self, user_id: int, timeframe_days: int = 30) -> Dict[str, Any]:
        """Advanced visit pattern analysis using ML"""
        try:
            recent_visits = self.get_recent_visits(user_id, timeframe_days)
            
            analysis = {
                "visit_frequency": self.calculate_visit_frequency(recent_visits),
                "doctor_engagement": self.analyze_doctor_engagement(recent_visits),
                "product_performance": self.analyze_product_performance(recent_visits),
                "location_efficiency": self.analyze_location_efficiency(recent_visits),
                "trend_analysis": self.perform_trend_analysis(recent_visits),
                "ml_insights": self.generate_ml_insights(recent_visits),
                "recommendations": self.generate_ai_recommendations(recent_visits)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Pattern analysis error: {e}")
            return {"error": str(e)}
            
    def calculate_visit_frequency(self, visits: List[Dict]) -> Dict:
        """Calculate visit frequency metrics"""
        if not visits:
            return {"total": 0, "daily_average": 0, "trend": "no_data"}
            
        # Group by date
        daily_visits = defaultdict(int)
        for visit in visits:
            timestamp = visit.get("timestamp", "")
            if timestamp:
                date = datetime.fromisoformat(timestamp).date()
                daily_visits[date] += 1
                
        total_visits = len(visits)
        active_days = len(daily_visits)
        daily_average = total_visits / max(active_days, 1)
        
        # Trend analysis
        if len(daily_visits) > 7:
            recent_week = sum(list(daily_visits.values())[-7:])
            previous_week = sum(list(daily_visits.values())[-14:-7]) if len(daily_visits) > 14 else recent_week
            
            if recent_week > previous_week * 1.1:
                trend = "increasing"
            elif recent_week < previous_week * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
            
        return {
            "total": total_visits,
            "active_days": active_days,
            "daily_average": round(daily_average, 2),
            "trend": trend,
            "peak_day": max(daily_visits.items(), key=lambda x: x[1])[0].isoformat() if daily_visits else None
        }
        
    def analyze_doctor_engagement(self, visits: List[Dict]) -> Dict:
        """Analyze doctor engagement patterns"""
        doctor_stats = defaultdict(lambda: {
            "visit_count": 0,
            "total_orders": 0,
            "engagement_score": 0,
            "last_visit": None,
            "response_quality": []
        })
        
        for visit in visits:
            contact = visit.get("contact", {})
            doctor = contact.get("name", "")
            
            if doctor:
                stats = doctor_stats[doctor]
                stats["visit_count"] += 1
                stats["total_orders"] += len(visit.get("orders", []))
                
                # Calculate engagement score
                assessment = visit.get("assessment", {})
                quality = assessment.get("visit_quality", 0.5)
                stats["response_quality"].append(quality)
                
                timestamp = visit.get("timestamp", "")
                if timestamp:
                    visit_date = datetime.fromisoformat(timestamp)
                    if not stats["last_visit"] or visit_date > datetime.fromisoformat(stats["last_visit"]):
                        stats["last_visit"] = timestamp
                        
        # Calculate final engagement scores
        for doctor, stats in doctor_stats.items():
            if stats["response_quality"]:
                avg_quality = statistics.mean(stats["response_quality"])
                visit_frequency = stats["visit_count"] / 30  # visits per day
                order_ratio = stats["total_orders"] / max(stats["visit_count"], 1)
                
                # Composite engagement score
                engagement = (avg_quality * 0.4) + (min(visit_frequency * 10, 1) * 0.3) + (min(order_ratio, 1) * 0.3)
                stats["engagement_score"] = round(engagement, 3)
                
        return dict(doctor_stats)
        
    def analyze_product_performance(self, visits: List[Dict]) -> Dict:
        """Analyze product performance using ML"""
        product_stats = defaultdict(lambda: {
            "total_quantity": 0,
            "order_frequency": 0,
            "doctor_adoption": set(),
            "success_rate": 0,
            "trend": "stable"
        })
        
        for visit in visits:
            orders = visit.get("orders", [])
            for order in orders:
                product = order.get("product", "")
                quantity = order.get("quantity", 0)
                
                if product:
                    stats = product_stats[product]
                    stats["total_quantity"] += quantity
                    stats["order_frequency"] += 1
                    
                    doctor = visit.get("contact", {}).get("name", "")
                    if doctor:
                        stats["doctor_adoption"].add(doctor)
                        
        # Convert sets to counts and add insights
        for product, stats in product_stats.items():
            stats["doctor_adoption"] = len(stats["doctor_adoption"])
            stats["avg_quantity_per_order"] = stats["total_quantity"] / max(stats["order_frequency"], 1)
            
        return dict(product_stats)
        
    def analyze_location_efficiency(self, visits: List[Dict]) -> Dict:
        """Analyze location visit efficiency"""
        location_stats = defaultdict(lambda: {
            "visit_count": 0,
            "total_orders": 0,
            "unique_doctors": set(),
            "efficiency_score": 0
        })
        
        for visit in visits:
            location = visit.get("contact", {}).get("location", "")
            if location:
                stats = location_stats[location]
                stats["visit_count"] += 1
                stats["total_orders"] += len(visit.get("orders", []))
                
                doctor = visit.get("contact", {}).get("name", "")
                if doctor:
                    stats["unique_doctors"].add(doctor)
                    
        # Calculate efficiency scores
        for location, stats in location_stats.items():
            orders_per_visit = stats["total_orders"] / max(stats["visit_count"], 1)
            doctor_variety = len(stats["unique_doctors"])
            
            # Efficiency = orders per visit + doctor variety bonus
            efficiency = (orders_per_visit * 0.7) + (min(doctor_variety / 5, 1) * 0.3)
            stats["efficiency_score"] = round(efficiency, 3)
            stats["unique_doctors"] = len(stats["unique_doctors"])  # Convert to count
            
        return dict(location_stats)
        
    def perform_trend_analysis(self, visits: List[Dict]) -> Dict:
        """Perform advanced trend analysis"""
        try:
            if len(visits) < 7:
                return {"status": "insufficient_data", "message": "Need at least 7 visits for trend analysis"}
                
            # Time series analysis
            daily_metrics = defaultdict(lambda: {
                "visits": 0,
                "orders": 0,
                "unique_doctors": set()
            })
            
            for visit in visits:
                timestamp = visit.get("timestamp", "")
                if timestamp:
                    date = datetime.fromisoformat(timestamp).date()
                    metrics = daily_metrics[date]
                    metrics["visits"] += 1
                    metrics["orders"] += len(visit.get("orders", []))
                    
                    doctor = visit.get("contact", {}).get("name", "")
                    if doctor:
                        metrics["unique_doctors"].add(doctor)
                        
            # Convert to time series
            dates = sorted(daily_metrics.keys())
            visit_series = [daily_metrics[date]["visits"] for date in dates]
            order_series = [daily_metrics[date]["orders"] for date in dates]
            
            # Calculate trends
            visit_trend = self.calculate_trend(visit_series)
            order_trend = self.calculate_trend(order_series)
            
            return {
                "visit_trend": visit_trend,
                "order_trend": order_trend,
                "peak_performance_day": max(dates, key=lambda d: daily_metrics[d]["visits"]).isoformat(),
                "consistency_score": self.calculate_consistency(visit_series),
                "growth_rate": self.calculate_growth_rate(visit_series)
            }
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {"error": str(e)}
            
    def calculate_trend(self, series: List[float]) -> str:
        """Calculate trend direction using linear regression"""
        try:
            if len(series) < 3:
                return "insufficient_data"
                
            n = len(series)
            x = list(range(n))
            y = series
            
            # Simple linear regression
            mean_x = statistics.mean(x)
            mean_y = statistics.mean(y)
            
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
            denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
            
            if denominator == 0:
                return "stable"
                
            slope = numerator / denominator
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            return "calculation_error"
            
    def calculate_consistency(self, series: List[float]) -> float:
        """Calculate performance consistency score"""
        try:
            if len(series) < 2:
                return 0.5
                
            mean_val = statistics.mean(series)
            if mean_val == 0:
                return 0.0
                
            std_dev = statistics.stdev(series) if len(series) > 1 else 0
            coefficient_of_variation = std_dev / mean_val
            
            # Convert to consistency score (lower CV = higher consistency)
            consistency = max(0, 1 - coefficient_of_variation)
            return round(consistency, 3)
            
        except Exception as e:
            return 0.5
            
    def calculate_growth_rate(self, series: List[float]) -> float:
        """Calculate performance growth rate"""
        try:
            if len(series) < 2:
                return 0.0
                
            # Compare first half vs second half
            mid_point = len(series) // 2
            first_half = series[:mid_point]
            second_half = series[mid_point:]
            
            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)
            
            if avg_first == 0:
                return 0.0
                
            growth_rate = (avg_second - avg_first) / avg_first
            return round(growth_rate, 3)
            
        except Exception as e:
            return 0.0
            
    def generate_ml_insights(self, visits: List[Dict]) -> List[str]:
        """Generate ML-powered insights"""
        insights = []
        
        try:
            if not visits:
                return ["No recent visits to analyze"]
                
            # 1. Performance insights
            total_visits = len(visits)
            total_orders = sum(len(v.get("orders", [])) for v in visits)
            order_ratio = total_orders / max(total_visits, 1)
            
            if order_ratio > 1.5:
                insights.append(f"🎯 Excellent order conversion: {order_ratio:.1f} orders per visit")
            elif order_ratio < 0.5:
                insights.append(f"📈 Opportunity to improve order conversion: {order_ratio:.1f} orders per visit")
                
            # 2. Doctor relationship insights
            unique_doctors = len(set(v.get("contact", {}).get("name", "") for v in visits))
            if unique_doctors > total_visits * 0.8:
                insights.append("🔄 High doctor variety - good market coverage")
            elif unique_doctors < total_visits * 0.3:
                insights.append("🎯 Focused on key doctors - good relationship building")
                
            # 3. Product insights
            product_mentions = Counter()
            for visit in visits:
                for order in visit.get("orders", []):
                    product = order.get("product", "")
                    if product:
                        product_mentions[product] += 1
                        
            if product_mentions:
                top_product = product_mentions.most_common(1)[0]
                insights.append(f"🥇 Top performing product: {top_product[0]} ({top_product[1]} orders)")
                
            # 4. Time pattern insights
            visit_hours = []
            for visit in visits:
                timestamp = visit.get("timestamp", "")
                if timestamp:
                    hour = datetime.fromisoformat(timestamp).hour
                    visit_hours.append(hour)
                    
            if visit_hours:
                avg_hour = statistics.mean(visit_hours)
                if avg_hour < 10:
                    insights.append("🌅 Early bird - most visits in morning hours")
                elif avg_hour > 16:
                    insights.append("🌆 Evening focused - most visits in later hours")
                else:
                    insights.append("☀️ Balanced timing - good distribution of visit hours")
                    
        except Exception as e:
            insights.append(f"Analysis error: {e}")
            
        return insights if insights else ["Analysis complete - maintaining steady performance"]
        
    def generate_ai_recommendations(self, visits: List[Dict]) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        try:
            if not visits:
                return ["Start logging visits to get personalized recommendations"]
                
            # 1. Frequency recommendations
            visit_gaps = []
            sorted_visits = sorted(visits, key=lambda x: x.get("timestamp", ""))
            
            for i in range(1, len(sorted_visits)):
                prev_time = datetime.fromisoformat(sorted_visits[i-1].get("timestamp", ""))
                curr_time = datetime.fromisoformat(sorted_visits[i].get("timestamp", ""))
                gap = (curr_time - prev_time).days
                visit_gaps.append(gap)
                
            if visit_gaps:
                avg_gap = statistics.mean(visit_gaps)
                if avg_gap > 7:
                    recommendations.append("📅 Consider increasing visit frequency - current gap is high")
                elif avg_gap < 2:
                    recommendations.append("⚡ High visit frequency - ensure quality over quantity")
                    
            # 2. Product recommendations
            successful_products = []
            for visit in visits:
                assessment = visit.get("assessment", {})
                if assessment.get("business_potential") == "high":
                    for order in visit.get("orders", []):
                        successful_products.append(order.get("product", ""))
                        
            if successful_products:
                top_product = Counter(successful_products).most_common(1)[0][0]
                recommendations.append(f"🎯 Focus on '{top_product}' - showing high success rate")
                
            # 3. Relationship recommendations
            doctors_with_multiple_visits = defaultdict(int)
            for visit in visits:
                doctor = visit.get("contact", {}).get("name", "")
                if doctor:
                    doctors_with_multiple_visits[doctor] += 1
                    
            strong_relationships = [dr for dr, count in doctors_with_multiple_visits.items() if count >= 3]
            if strong_relationships:
                recommendations.append(f"🤝 Strong relationships with {len(strong_relationships)} doctors - leverage for referrals")
                
        except Exception as e:
            recommendations.append(f"Recommendation generation error: {e}")
            
        return recommendations if recommendations else ["Keep up the good work! Continue current patterns."]
        
    def get_recent_visits(self, user_id: int, days: int) -> List[Dict]:
        """Get recent visits for analysis"""
        # This would integrate with actual data storage
        # For now, return sample data structure
        return self.data_cache.get("visits", [])
        
    def detect_anomalies(self, data: Dict, data_type: str) -> List[str]:
        """Detect anomalies using ML models"""
        anomalies = []
        
        try:
            if data_type == "expense":
                expense = data.get("expense", {})
                amount = expense.get("amount", 0)
                category = expense.get("category", "other")
                
                # Check against learned patterns
                anomaly_model = self.pattern_models.get("expense_anomaly", {})
                normal_ranges = anomaly_model.get("normal_ranges", {})
                
                if category in normal_ranges:
                    range_data = normal_ranges[category]
                    threshold = range_data.get("q75", 0) * 2  # 2x 75th percentile
                    
                    if amount > threshold:
                        anomalies.append(f"Unusually high {category} expense: ₹{amount}")
                        
            elif data_type == "visit":
                # Check visit timing anomalies
                timestamp = data.get("timestamp", "")
                if timestamp:
                    visit_time = datetime.fromisoformat(timestamp)
                    hour = visit_time.hour
                    
                    if hour < 8 or hour > 18:
                        anomalies.append(f"Unusual visit time: {hour}:00")
                        
                # Check order quantity anomalies
                orders = data.get("orders", [])
                for order in orders:
                    quantity = order.get("quantity", 0)
                    if quantity > 100:  # Unusually large order
                        anomalies.append(f"Large order detected: {quantity} units")
                        
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            
        return anomalies
        
    def predict_future_performance(self, user_id: int) -> Dict[str, Any]:
        """Predict future performance using ML models"""
        try:
            recent_visits = self.get_recent_visits(user_id, 30)
            
            if len(recent_visits) < 5:
                return {
                    "prediction": "insufficient_data",
                    "confidence": 0.0,
                    "recommendations": ["Log more visits to enable predictions"]
                }
                
            # Simple trend-based prediction
            daily_visits = defaultdict(int)
            for visit in recent_visits:
                timestamp = visit.get("timestamp", "")
                if timestamp:
                    date = datetime.fromisoformat(timestamp).date()
                    daily_visits[date] += 1
                    
            recent_performance = list(daily_visits.values())[-7:]  # Last 7 days
            avg_recent = statistics.mean(recent_performance) if recent_performance else 0
            
            # Predict next week
            trend = self.calculate_trend(recent_performance)
            
            if trend == "increasing":
                predicted_visits = avg_recent * 1.1 * 7  # 10% growth
                confidence = 0.7
            elif trend == "decreasing":
                predicted_visits = avg_recent * 0.9 * 7  # 10% decline
                confidence = 0.6
            else:
                predicted_visits = avg_recent * 7  # Stable
                confidence = 0.8
                
            return {
                "prediction": {
                    "next_week_visits": round(predicted_visits),
                    "daily_average": round(predicted_visits / 7, 1),
                    "trend": trend
                },
                "confidence": confidence,
                "factors": [
                    f"Based on {len(recent_visits)} recent visits",
                    f"Current trend: {trend}",
                    f"Recent daily average: {avg_recent:.1f}"
                ]
            }
            
        except Exception as e:
            logger.error(f"Performance prediction error: {e}")
            return {"error": str(e)}

# Global analytics engine
ml_analytics = MRAnalyticsEngine()

# Export main functions
def analyze_mr_performance(user_id: int, timeframe_days: int = 30) -> Dict[str, Any]:
    """Main performance analysis function"""
    return ml_analytics.analyze_visit_patterns(user_id, timeframe_days)

def detect_data_anomalies(data: Dict, data_type: str) -> List[str]:
    """Main anomaly detection function"""
    return ml_analytics.detect_anomalies(data, data_type)

def predict_performance(user_id: int) -> Dict[str, Any]:
    """Main performance prediction function"""
    return ml_analytics.predict_future_performance(user_id)
