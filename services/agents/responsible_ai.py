"""
Responsible AI Framework for Geospatial Weather Operations
Implements bias detection, fairness monitoring, transparency, and ethical decision-making
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from sqlalchemy import create_engine, text
from langchain.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM for ethical reasoning
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2  # Low temperature for consistent ethical decisions
)

class EthicsLevel(Enum):
    """Ethics compliance levels"""
    COMPLIANT = "compliant"
    MINOR_CONCERN = "minor_concern"
    MAJOR_CONCERN = "major_concern"
    CRITICAL_VIOLATION = "critical_violation"

class BiasType(Enum):
    """Types of bias in AI systems"""
    GEOGRAPHICAL = "geographical"
    TEMPORAL = "temporal"
    DEMOGRAPHIC = "demographic"
    SOCIOECONOMIC = "socioeconomic"
    ALGORITHMIC = "algorithmic"
    CONFIRMATION = "confirmation"
    SELECTION = "selection"

class FairnessMetric(Enum):
    """Fairness metrics for evaluation"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    CALIBRATION = "calibration"
    PREDICTION_PARITY = "prediction_parity"

@dataclass
class BiasDetectionResult:
    """Result of bias detection analysis"""
    bias_type: BiasType
    severity: float  # 0.0 to 1.0
    affected_groups: List[str]
    description: str
    evidence: Dict[str, Any]
    mitigation_strategies: List[str]

@dataclass
class FairnessAssessment:
    """Fairness assessment result"""
    metric: FairnessMetric
    score: float  # 0.0 to 1.0, higher is more fair
    groups_compared: List[str]
    statistical_significance: bool
    confidence_interval: Tuple[float, float]
    interpretation: str

@dataclass
class EthicsReport:
    """Comprehensive ethics assessment report"""
    id: str
    timestamp: datetime
    model_name: str
    dataset_description: str
    bias_detections: List[BiasDetectionResult]
    fairness_assessments: List[FairnessAssessment]
    transparency_score: float
    explainability_score: float
    overall_ethics_level: EthicsLevel
    recommendations: List[str]
    audit_trail: List[str]

class ResponsibleAIState(TypedDict):
    """State for responsible AI workflow"""
    model_predictions: Optional[Any]
    training_data: Optional[Any]
    model_metadata: Optional[Dict]
    bias_analysis: Optional[Dict]
    fairness_metrics: Optional[Dict]
    transparency_report: Optional[Dict]
    ethics_assessment: Optional[Dict]
    output: str
    error: Optional[str]

class ResponsibleAIFramework:
    """Comprehensive framework for responsible AI in weather operations"""
    
    def __init__(self, db_uri: str = None):
        """Initialize responsible AI framework"""
        self.db_uri = db_uri or os.getenv("DATABASE_URL")
        self.protected_attributes = ['region', 'province', 'district', 'urban_rural']
        self.setup_ethics_monitoring()
    
    def setup_ethics_monitoring(self):
        """Initialize ethics monitoring infrastructure"""
        try:
            if self.db_uri:
                self.engine = create_engine(self.db_uri)
                self.create_ethics_tables()
        except Exception as e:
            logger.error(f"Failed to setup ethics monitoring: {e}")
    
    def create_ethics_tables(self):
        """Create ethics monitoring tables"""
        try:
            with self.engine.connect() as conn:
                # Ethics reports table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ethics_reports (
                        id VARCHAR(50) PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_name VARCHAR(100),
                        dataset_description TEXT,
                        overall_ethics_level VARCHAR(20),
                        transparency_score FLOAT,
                        explainability_score FLOAT,
                        bias_count INTEGER DEFAULT 0,
                        fairness_violations INTEGER DEFAULT 0,
                        recommendations JSONB,
                        full_report JSONB
                    )
                """))
                
                # Bias detection log
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS bias_detection_log (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_name VARCHAR(100),
                        bias_type VARCHAR(50),
                        severity FLOAT,
                        affected_groups JSONB,
                        description TEXT,
                        evidence JSONB,
                        mitigation_applied BOOLEAN DEFAULT FALSE
                    )
                """))
                
                # Fairness metrics log
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS fairness_metrics_log (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_name VARCHAR(100),
                        metric_type VARCHAR(50),
                        score FLOAT,
                        groups_compared JSONB,
                        statistical_significance BOOLEAN,
                        interpretation TEXT
                    )
                """))
                
                # AI decision audit trail
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_decision_audit (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_name VARCHAR(100),
                        input_data JSONB,
                        prediction JSONB,
                        confidence_score FLOAT,
                        explanation JSONB,
                        human_reviewed BOOLEAN DEFAULT FALSE,
                        ethical_flags JSONB
                    )
                """))
                
                conn.commit()
                logger.info("Ethics monitoring tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create ethics tables: {e}")
    
    def detect_geographical_bias(self, data: pd.DataFrame, predictions: pd.DataFrame = None) -> List[BiasDetectionResult]:
        """Detect geographical bias in weather data or predictions"""
        bias_results = []
        
        try:
            if 'location' in data.columns or 'region' in data.columns:
                location_col = 'location' if 'location' in data.columns else 'region'
                
                # Analyze data distribution across locations
                location_counts = data[location_col].value_counts()
                min_count = location_counts.min()
                max_count = location_counts.max()
                
                # Check for significant imbalance
                if max_count / min_count > 5:  # Arbitrary threshold
                    bias_results.append(BiasDetectionResult(
                        bias_type=BiasType.GEOGRAPHICAL,
                        severity=min(1.0, (max_count / min_count - 1) / 10),
                        affected_groups=[loc for loc, count in location_counts.items() if count < location_counts.median()],
                        description=f"Geographical data imbalance detected. {location_counts.idxmax()} has {max_count} samples while {location_counts.idxmin()} has only {min_count}.",
                        evidence={
                            "location_counts": location_counts.to_dict(),
                            "imbalance_ratio": max_count / min_count,
                            "underrepresented_locations": location_counts[location_counts < location_counts.median()].to_dict()
                        },
                        mitigation_strategies=[
                            "Increase data collection from underrepresented regions",
                            "Apply stratified sampling techniques",
                            "Use regional weighting in model training",
                            "Implement location-specific model validation"
                        ]
                    ))
                
                # Analyze prediction accuracy across locations if predictions provided
                if predictions is not None and 'actual' in predictions.columns and 'predicted' in predictions.columns:
                    for location in data[location_col].unique():
                        location_mask = data[location_col] == location
                        location_predictions = predictions[location_mask]
                        
                        if len(location_predictions) > 10:  # Minimum sample size
                            mae = np.mean(np.abs(location_predictions['actual'] - location_predictions['predicted']))
                            overall_mae = np.mean(np.abs(predictions['actual'] - predictions['predicted']))
                            
                            if mae > overall_mae * 1.5:  # 50% worse than average
                                bias_results.append(BiasDetectionResult(
                                    bias_type=BiasType.GEOGRAPHICAL,
                                    severity=min(1.0, (mae / overall_mae - 1)),
                                    affected_groups=[location],
                                    description=f"Model performance significantly worse for {location}. MAE: {mae:.3f} vs overall: {overall_mae:.3f}",
                                    evidence={
                                        "location_mae": mae,
                                        "overall_mae": overall_mae,
                                        "performance_ratio": mae / overall_mae,
                                        "sample_size": len(location_predictions)
                                    },
                                    mitigation_strategies=[
                                        f"Increase training data for {location}",
                                        f"Develop location-specific model for {location}",
                                        "Apply domain adaptation techniques",
                                        "Review local weather patterns and adjust features"
                                    ]
                                ))
        
        except Exception as e:
            logger.error(f"Geographical bias detection failed: {e}")
        
        return bias_results
    
    def detect_temporal_bias(self, data: pd.DataFrame, predictions: pd.DataFrame = None) -> List[BiasDetectionResult]:
        """Detect temporal bias in weather data or predictions"""
        bias_results = []
        
        try:
            if 'date' in data.columns or 'datetime' in data.columns:
                date_col = 'date' if 'date' in data.columns else 'datetime'
                data[date_col] = pd.to_datetime(data[date_col])
                
                # Check for seasonal bias
                data['month'] = data[date_col].dt.month
                data['season'] = data['month'].apply(self._get_season)
                
                season_counts = data['season'].value_counts()
                min_count = season_counts.min()
                max_count = season_counts.max()
                
                if max_count / min_count > 2:
                    bias_results.append(BiasDetectionResult(
                        bias_type=BiasType.TEMPORAL,
                        severity=min(1.0, (max_count / min_count - 1) / 3),
                        affected_groups=[season for season, count in season_counts.items() if count < season_counts.median()],
                        description=f"Seasonal data imbalance detected. {season_counts.idxmax()} season has {max_count} samples while {season_counts.idxmin()} has only {min_count}.",
                        evidence={
                            "season_counts": season_counts.to_dict(),
                            "imbalance_ratio": max_count / min_count
                        },
                        mitigation_strategies=[
                            "Ensure balanced seasonal data collection",
                            "Apply temporal stratification in training",
                            "Use seasonal weighting in model evaluation",
                            "Implement season-specific model validation"
                        ]
                    ))
                
                # Check for recent data bias (recency bias)
                recent_threshold = datetime.now() - timedelta(days=365)
                recent_data_ratio = len(data[data[date_col] > recent_threshold]) / len(data)
                
                if recent_data_ratio > 0.8:  # More than 80% recent data
                    bias_results.append(BiasDetectionResult(
                        bias_type=BiasType.TEMPORAL,
                        severity=min(1.0, (recent_data_ratio - 0.5) * 2),
                        affected_groups=["historical_periods"],
                        description=f"Recency bias detected. {recent_data_ratio:.1%} of data is from the last year, potentially underrepresenting historical patterns.",
                        evidence={
                            "recent_data_ratio": recent_data_ratio,
                            "data_date_range": {
                                "min": data[date_col].min().isoformat(),
                                "max": data[date_col].max().isoformat()
                            }
                        },
                        mitigation_strategies=[
                            "Include more historical data in training",
                            "Apply temporal stratification",
                            "Use time-based cross-validation",
                            "Consider climate change trends in modeling"
                        ]
                    ))
        
        except Exception as e:
            logger.error(f"Temporal bias detection failed: {e}")
        
        return bias_results
    
    def _get_season(self, month: int) -> str:
        """Map month to season (Northern Hemisphere)"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def calculate_fairness_metrics(self, predictions: pd.DataFrame, protected_attribute: str) -> List[FairnessAssessment]:
        """Calculate fairness metrics across protected groups"""
        fairness_assessments = []
        
        try:
            if protected_attribute not in predictions.columns:
                return fairness_assessments
            
            groups = predictions[protected_attribute].unique()
            
            for group_a in groups:
                for group_b in groups:
                    if group_a != group_b:
                        # Demographic Parity
                        positive_rate_a = self._calculate_positive_rate(predictions, protected_attribute, group_a)
                        positive_rate_b = self._calculate_positive_rate(predictions, protected_attribute, group_b)
                        
                        demographic_parity_score = 1 - abs(positive_rate_a - positive_rate_b)
                        
                        fairness_assessments.append(FairnessAssessment(
                            metric=FairnessMetric.DEMOGRAPHIC_PARITY,
                            score=demographic_parity_score,
                            groups_compared=[group_a, group_b],
                            statistical_significance=self._test_statistical_significance(
                                predictions, protected_attribute, group_a, group_b
                            ),
                            confidence_interval=(
                                max(0, demographic_parity_score - 0.1),
                                min(1, demographic_parity_score + 0.1)
                            ),
                            interpretation=self._interpret_fairness_score(demographic_parity_score, FairnessMetric.DEMOGRAPHIC_PARITY)
                        ))
                        
                        # Equal Opportunity (if ground truth available)
                        if 'actual' in predictions.columns:
                            equal_opportunity_score = self._calculate_equal_opportunity(
                                predictions, protected_attribute, group_a, group_b
                            )
                            
                            fairness_assessments.append(FairnessAssessment(
                                metric=FairnessMetric.EQUAL_OPPORTUNITY,
                                score=equal_opportunity_score,
                                groups_compared=[group_a, group_b],
                                statistical_significance=self._test_statistical_significance(
                                    predictions, protected_attribute, group_a, group_b
                                ),
                                confidence_interval=(
                                    max(0, equal_opportunity_score - 0.1),
                                    min(1, equal_opportunity_score + 0.1)
                                ),
                                interpretation=self._interpret_fairness_score(equal_opportunity_score, FairnessMetric.EQUAL_OPPORTUNITY)
                            ))
        
        except Exception as e:
            logger.error(f"Fairness metrics calculation failed: {e}")
        
        return fairness_assessments
    
    def _calculate_positive_rate(self, predictions: pd.DataFrame, protected_attribute: str, group: str) -> float:
        """Calculate positive prediction rate for a group"""
        group_data = predictions[predictions[protected_attribute] == group]
        if len(group_data) == 0:
            return 0.0
        
        # Assuming binary predictions or threshold-based
        if 'predicted' in group_data.columns:
            return (group_data['predicted'] > 0.5).mean()
        return 0.5
    
    def _calculate_equal_opportunity(self, predictions: pd.DataFrame, protected_attribute: str, group_a: str, group_b: str) -> float:
        """Calculate equal opportunity metric"""
        # Equal opportunity: TPR should be equal across groups
        try:
            group_a_data = predictions[predictions[protected_attribute] == group_a]
            group_b_data = predictions[predictions[protected_attribute] == group_b]
            
            # Calculate True Positive Rates
            tpr_a = self._calculate_tpr(group_a_data)
            tpr_b = self._calculate_tpr(group_b_data)
            
            return 1 - abs(tpr_a - tpr_b)
        except:
            return 0.5
    
    def _calculate_tpr(self, data: pd.DataFrame) -> float:
        """Calculate True Positive Rate"""
        if 'actual' not in data.columns or 'predicted' not in data.columns:
            return 0.5
        
        positive_actual = data[data['actual'] > 0.5]
        if len(positive_actual) == 0:
            return 0.0
        
        true_positives = len(positive_actual[positive_actual['predicted'] > 0.5])
        return true_positives / len(positive_actual)
    
    def _test_statistical_significance(self, predictions: pd.DataFrame, protected_attribute: str, group_a: str, group_b: str) -> bool:
        """Test statistical significance of difference between groups"""
        try:
            group_a_data = predictions[predictions[protected_attribute] == group_a]['predicted']
            group_b_data = predictions[predictions[protected_attribute] == group_b]['predicted']
            
            _, p_value = stats.ttest_ind(group_a_data, group_b_data)
            return p_value < 0.05
        except:
            return False
    
    def _interpret_fairness_score(self, score: float, metric: FairnessMetric) -> str:
        """Interpret fairness score"""
        if score >= 0.9:
            return f"Excellent {metric.value}: Groups are treated very fairly"
        elif score >= 0.8:
            return f"Good {metric.value}: Minor fairness concerns"
        elif score >= 0.6:
            return f"Moderate {metric.value}: Noticeable fairness issues"
        else:
            return f"Poor {metric.value}: Significant fairness violations detected"
    
    def generate_transparency_report(self, model_metadata: Dict, predictions: pd.DataFrame = None) -> Dict:
        """Generate model transparency report"""
        try:
            report = {
                "model_information": {
                    "name": model_metadata.get("name", "Unknown"),
                    "version": model_metadata.get("version", "1.0"),
                    "algorithm": model_metadata.get("algorithm", "Unknown"),
                    "training_date": model_metadata.get("training_date", datetime.now().isoformat()),
                    "last_updated": datetime.now().isoformat()
                },
                "data_sources": model_metadata.get("data_sources", []),
                "feature_importance": model_metadata.get("feature_importance", {}),
                "performance_metrics": model_metadata.get("performance_metrics", {}),
                "limitations": model_metadata.get("limitations", []),
                "intended_use": model_metadata.get("intended_use", "Weather prediction and analysis"),
                "ethical_considerations": {
                    "bias_mitigation": "Geographical and temporal bias detection implemented",
                    "fairness_monitoring": "Continuous fairness assessment across regions",
                    "transparency_measures": "Full model documentation and explainability",
                    "human_oversight": "Human expert review required for critical decisions"
                }
            }
            
            # Add prediction statistics if available
            if predictions is not None and 'predicted' in predictions.columns:
                report["prediction_statistics"] = {
                    "total_predictions": len(predictions),
                    "mean_prediction": float(predictions['predicted'].mean()),
                    "std_prediction": float(predictions['predicted'].std()),
                    "min_prediction": float(predictions['predicted'].min()),
                    "max_prediction": float(predictions['predicted'].max())
                }
                
                if 'confidence' in predictions.columns:
                    report["confidence_statistics"] = {
                        "mean_confidence": float(predictions['confidence'].mean()),
                        "low_confidence_ratio": float((predictions['confidence'] < 0.7).mean())
                    }
            
            return report
        except Exception as e:
            logger.error(f"Transparency report generation failed: {e}")
            return {"error": str(e)}
    
    def assess_explainability(self, model_predictions: Any, feature_importance: Dict = None) -> Dict:
        """Assess model explainability"""
        try:
            explainability_report = {
                "interpretability_score": 0.0,
                "explanation_methods": [],
                "feature_analysis": {},
                "recommendations": []
            }
            
            # Assess feature importance availability
            if feature_importance:
                explainability_report["feature_analysis"] = feature_importance
                explainability_report["interpretability_score"] += 0.4
                explainability_report["explanation_methods"].append("Feature Importance Analysis")
            
            # Check for prediction confidence
            if hasattr(model_predictions, 'confidence') or (isinstance(model_predictions, dict) and 'confidence' in model_predictions):
                explainability_report["interpretability_score"] += 0.2
                explainability_report["explanation_methods"].append("Prediction Confidence Scores")
            
            # Check for uncertainty quantification
            if hasattr(model_predictions, 'uncertainty') or (isinstance(model_predictions, dict) and 'uncertainty' in model_predictions):
                explainability_report["interpretability_score"] += 0.2
                explainability_report["explanation_methods"].append("Uncertainty Quantification")
            
            # Base interpretability for simple models
            explainability_report["interpretability_score"] += 0.2
            explainability_report["explanation_methods"].append("Model Architecture Transparency")
            
            # Generate recommendations based on score
            if explainability_report["interpretability_score"] < 0.6:
                explainability_report["recommendations"].extend([
                    "Implement SHAP (SHapley Additive exPlanations) values",
                    "Add LIME (Local Interpretable Model-agnostic Explanations)",
                    "Provide uncertainty quantification",
                    "Create feature contribution visualizations"
                ])
            
            return explainability_report
        except Exception as e:
            logger.error(f"Explainability assessment failed: {e}")
            return {"error": str(e)}
    
    def generate_ethics_report(self, model_name: str, training_data: pd.DataFrame, 
                             predictions: pd.DataFrame = None, model_metadata: Dict = None) -> EthicsReport:
        """Generate comprehensive ethics assessment report"""
        try:
            report_id = hashlib.md5(f"{model_name}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
            
            # Detect biases
            all_bias_results = []
            all_bias_results.extend(self.detect_geographical_bias(training_data, predictions))
            all_bias_results.extend(self.detect_temporal_bias(training_data, predictions))
            
            # Calculate fairness metrics
            all_fairness_assessments = []
            for protected_attr in self.protected_attributes:
                if protected_attr in training_data.columns:
                    if predictions is not None:
                        all_fairness_assessments.extend(
                            self.calculate_fairness_metrics(predictions, protected_attr)
                        )
            
            # Generate transparency report
            transparency_report = self.generate_transparency_report(model_metadata or {}, predictions)
            transparency_score = 0.8 if "error" not in transparency_report else 0.3
            
            # Assess explainability
            explainability_assessment = self.assess_explainability(predictions, 
                                                                 model_metadata.get("feature_importance") if model_metadata else None)
            explainability_score = explainability_assessment.get("interpretability_score", 0.5)
            
            # Determine overall ethics level
            critical_biases = [b for b in all_bias_results if b.severity > 0.7]
            major_fairness_violations = [f for f in all_fairness_assessments if f.score < 0.6]
            
            if critical_biases or len(major_fairness_violations) > 2:
                overall_ethics_level = EthicsLevel.CRITICAL_VIOLATION
            elif len(all_bias_results) > 3 or len(major_fairness_violations) > 0:
                overall_ethics_level = EthicsLevel.MAJOR_CONCERN
            elif len(all_bias_results) > 1 or transparency_score < 0.6:
                overall_ethics_level = EthicsLevel.MINOR_CONCERN
            else:
                overall_ethics_level = EthicsLevel.COMPLIANT
            
            # Generate recommendations
            recommendations = []
            for bias in all_bias_results:
                recommendations.extend(bias.mitigation_strategies)
            
            if transparency_score < 0.7:
                recommendations.extend([
                    "Improve model documentation",
                    "Provide more detailed feature explanations",
                    "Implement regular transparency audits"
                ])
            
            if explainability_score < 0.6:
                recommendations.extend(explainability_assessment.get("recommendations", []))
            
            # Create ethics report
            ethics_report = EthicsReport(
                id=report_id,
                timestamp=datetime.now(),
                model_name=model_name,
                dataset_description=f"Training data with {len(training_data)} samples",
                bias_detections=all_bias_results,
                fairness_assessments=all_fairness_assessments,
                transparency_score=transparency_score,
                explainability_score=explainability_score,
                overall_ethics_level=overall_ethics_level,
                recommendations=list(set(recommendations)),  # Remove duplicates
                audit_trail=[
                    f"Ethics assessment completed at {datetime.now().isoformat()}",
                    f"Bias detections: {len(all_bias_results)}",
                    f"Fairness assessments: {len(all_fairness_assessments)}",
                    f"Overall level: {overall_ethics_level.value}"
                ]
            )
            
            # Store report in database
            self.store_ethics_report(ethics_report)
            
            return ethics_report
            
        except Exception as e:
            logger.error(f"Ethics report generation failed: {e}")
            # Return minimal report with error
            return EthicsReport(
                id="error",
                timestamp=datetime.now(),
                model_name=model_name,
                dataset_description="Error in assessment",
                bias_detections=[],
                fairness_assessments=[],
                transparency_score=0.0,
                explainability_score=0.0,
                overall_ethics_level=EthicsLevel.CRITICAL_VIOLATION,
                recommendations=["Review ethics assessment system"],
                audit_trail=[f"Assessment failed: {str(e)}"]
            )
    
    def store_ethics_report(self, report: EthicsReport):
        """Store ethics report in database"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO ethics_reports 
                        (id, timestamp, model_name, dataset_description, overall_ethics_level,
                         transparency_score, explainability_score, bias_count, fairness_violations,
                         recommendations, full_report)
                        VALUES (:id, :timestamp, :model_name, :dataset_description, :ethics_level,
                                :transparency_score, :explainability_score, :bias_count, :fairness_violations,
                                :recommendations, :full_report)
                    """), {
                        "id": report.id,
                        "timestamp": report.timestamp,
                        "model_name": report.model_name,
                        "dataset_description": report.dataset_description,
                        "ethics_level": report.overall_ethics_level.value,
                        "transparency_score": report.transparency_score,
                        "explainability_score": report.explainability_score,
                        "bias_count": len(report.bias_detections),
                        "fairness_violations": len([f for f in report.fairness_assessments if f.score < 0.6]),
                        "recommendations": json.dumps(report.recommendations),
                        "full_report": json.dumps(asdict(report), default=str)
                    })
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to store ethics report: {e}")

# Global responsible AI framework instance
responsible_ai_instance = None

def get_responsible_ai_framework():
    """Get or create global responsible AI framework instance"""
    global responsible_ai_instance
    if responsible_ai_instance is None:
        responsible_ai_instance = ResponsibleAIFramework()
    return responsible_ai_instance

# LangChain tools for responsible AI operations
@tool("assess_model_ethics", return_direct=True)
def assess_model_ethics_tool(tool_input: str) -> str:
    """
    Assess model ethics including bias detection and fairness analysis.
    tool_input: JSON string with model_name, training_data, predictions, and metadata
    """
    try:
        framework = get_responsible_ai_framework()
        input_data = json.loads(tool_input)
        
        model_name = input_data.get("model_name", "unnamed_model")
        training_data = pd.DataFrame(input_data.get("training_data", []))
        predictions = pd.DataFrame(input_data.get("predictions", [])) if input_data.get("predictions") else None
        model_metadata = input_data.get("metadata", {})
        
        ethics_report = framework.generate_ethics_report(
            model_name, training_data, predictions, model_metadata
        )
        
        return json.dumps(asdict(ethics_report), default=str)
    except Exception as e:
        return json.dumps({"error": f"Ethics assessment failed: {str(e)}"})

@tool("detect_bias", return_direct=True)
def detect_bias_tool(tool_input: str) -> str:
    """
    Detect bias in training data or model predictions.
    tool_input: JSON string with data and bias_types to check
    """
    try:
        framework = get_responsible_ai_framework()
        input_data = json.loads(tool_input)
        
        data = pd.DataFrame(input_data.get("data", []))
        predictions = pd.DataFrame(input_data.get("predictions", [])) if input_data.get("predictions") else None
        
        bias_results = []
        if "geographical" in input_data.get("bias_types", ["geographical", "temporal"]):
            bias_results.extend(framework.detect_geographical_bias(data, predictions))
        if "temporal" in input_data.get("bias_types", ["geographical", "temporal"]):
            bias_results.extend(framework.detect_temporal_bias(data, predictions))
        
        return json.dumps([asdict(bias) for bias in bias_results], default=str)
    except Exception as e:
        return json.dumps({"error": f"Bias detection failed: {str(e)}"})

@tool("calculate_fairness", return_direct=True)
def calculate_fairness_tool(tool_input: str) -> str:
    """
    Calculate fairness metrics for model predictions.
    tool_input: JSON string with predictions and protected_attribute
    """
    try:
        framework = get_responsible_ai_framework()
        input_data = json.loads(tool_input)
        
        predictions = pd.DataFrame(input_data.get("predictions", []))
        protected_attribute = input_data.get("protected_attribute", "region")
        
        fairness_assessments = framework.calculate_fairness_metrics(predictions, protected_attribute)
        
        return json.dumps([asdict(assessment) for assessment in fairness_assessments], default=str)
    except Exception as e:
        return json.dumps({"error": f"Fairness calculation failed: {str(e)}"})

# Responsible AI tools list
responsible_ai_tools = [
    assess_model_ethics_tool,
    detect_bias_tool,
    calculate_fairness_tool
]

# LangGraph workflow for responsible AI
def bias_detection_node(state: ResponsibleAIState) -> ResponsibleAIState:
    """Detect bias in data and predictions"""
    try:
        if state.get("training_data") or state.get("model_predictions"):
            tool_input = json.dumps({
                "data": state.get("training_data", []),
                "predictions": state.get("model_predictions", []),
                "bias_types": ["geographical", "temporal"]
            })
            
            result = detect_bias_tool.invoke(tool_input)
            state["bias_analysis"] = json.loads(result)
    except Exception as e:
        state["error"] = f"Bias detection node failed: {str(e)}"
    
    return state

def fairness_assessment_node(state: ResponsibleAIState) -> ResponsibleAIState:
    """Assess fairness metrics"""
    try:
        if state.get("model_predictions"):
            for protected_attr in ["region", "location", "province"]:
                tool_input = json.dumps({
                    "predictions": state.get("model_predictions", []),
                    "protected_attribute": protected_attr
                })
                
                result = calculate_fairness_tool.invoke(tool_input)
                fairness_data = json.loads(result)
                
                if "fairness_metrics" not in state:
                    state["fairness_metrics"] = {}
                state["fairness_metrics"][protected_attr] = fairness_data
    except Exception as e:
        state["error"] = f"Fairness assessment node failed: {str(e)}"
    
    return state

def ethics_evaluation_node(state: ResponsibleAIState) -> ResponsibleAIState:
    """Generate comprehensive ethics evaluation"""
    try:
        tool_input = json.dumps({
            "model_name": state.get("model_metadata", {}).get("name", "unnamed_model"),
            "training_data": state.get("training_data", []),
            "predictions": state.get("model_predictions", []),
            "metadata": state.get("model_metadata", {})
        })
        
        result = assess_model_ethics_tool.invoke(tool_input)
        state["ethics_assessment"] = json.loads(result)
        
        # Generate summary output
        ethics_data = state["ethics_assessment"]
        state["output"] = json.dumps({
            "ethics_level": ethics_data.get("overall_ethics_level"),
            "transparency_score": ethics_data.get("transparency_score"),
            "explainability_score": ethics_data.get("explainability_score"),
            "bias_count": len(ethics_data.get("bias_detections", [])),
            "fairness_violations": len([f for f in ethics_data.get("fairness_assessments", []) if f.get("score", 1.0) < 0.6]),
            "recommendations": ethics_data.get("recommendations", []),
            "timestamp": datetime.now().isoformat()
        }, default=str)
        
    except Exception as e:
        state["error"] = f"Ethics evaluation node failed: {str(e)}"
    
    return state

# Lazy initialization to prevent duplicate node errors
def _create_responsible_ai_workflow():
    """Create and return the compiled responsible AI workflow"""
    responsible_ai_workflow = StateGraph(ResponsibleAIState)
    
    # Add nodes
    responsible_ai_workflow.add_node("bias_detection", bias_detection_node)
    responsible_ai_workflow.add_node("fairness_assessment", fairness_assessment_node)
    responsible_ai_workflow.add_node("ethics_evaluation", ethics_evaluation_node)
    
    # Add edges
    responsible_ai_workflow.add_edge(START, "bias_detection")
    responsible_ai_workflow.add_edge("bias_detection", "fairness_assessment")
    responsible_ai_workflow.add_edge("fairness_assessment", "ethics_evaluation")
    responsible_ai_workflow.add_edge("ethics_evaluation", END)
    
    return responsible_ai_workflow.compile()

_responsible_ai_app_instance = None

def _get_responsible_ai_app():
    """Get or create the responsible AI workflow"""
    global _responsible_ai_app_instance
    if _responsible_ai_app_instance is None:
        _responsible_ai_app_instance = _create_responsible_ai_workflow()
    return _responsible_ai_app_instance

def run_responsible_ai_assessment(model_predictions: Any, training_data: Any = None, model_metadata: Dict = None) -> str:
    """
    Run comprehensive responsible AI assessment
    
    Args:
        model_predictions: Model predictions data
        training_data: Training dataset (optional)
        model_metadata: Model metadata and information
        
    Returns:
        str: JSON string with responsible AI assessment results
    """
    try:
        initial_state = ResponsibleAIState(
            model_predictions=model_predictions,
            training_data=training_data,
            model_metadata=model_metadata or {},
            bias_analysis=None,
            fairness_metrics=None,
            transparency_report=None,
            ethics_assessment=None,
            output="",
            error=None
        )
        
        responsible_ai_app = _get_responsible_ai_app()
        result = responsible_ai_app.invoke(initial_state)
        return result["output"]
        
    except Exception as e:
        return json.dumps({
            "error": f"Responsible AI assessment failed: {str(e)}",
            "ethics_level": "critical_violation",
            "timestamp": datetime.now().isoformat()
        }, default=str)

# Test function
if __name__ == "__main__":
    # Test responsible AI framework
    test_data = [
        {"region": "Colombo", "temperature": 28.5, "humidity": 75.2, "predicted": 29.1, "actual": 28.8},
        {"region": "Kandy", "temperature": 24.1, "humidity": 82.1, "predicted": 24.8, "actual": 24.3},
        {"region": "Galle", "temperature": 29.2, "humidity": 78.5, "predicted": 29.5, "actual": 29.0}
    ]
    
    test_metadata = {
        "name": "weather_prediction_model",
        "version": "1.0",
        "algorithm": "Random Forest",
        "feature_importance": {"temperature": 0.4, "humidity": 0.3, "pressure": 0.3}
    }
    
    print("🤖 Testing Responsible AI Framework...")
    result = run_responsible_ai_assessment(test_data, test_data, test_metadata)
    print(f"Ethics Assessment Result:\n{result}")