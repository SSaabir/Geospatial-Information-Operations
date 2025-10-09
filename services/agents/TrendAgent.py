import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
import json
from sqlalchemy import create_engine  # NEW: For PostgreSQL connection
from dotenv import load_dotenv

# LangChain and LangGraph imports
from langgraph.graph import StateGraph, END, START
from langchain.agents import initialize_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from typing import TypedDict, Optional, List
from langchain_groq import ChatGroq
from langchain.tools import tool

# Load environment variables
load_dotenv()

# Initialize LLM for LangChain integration
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct",
               groq_api_key=os.getenv("GROQ_API_KEY"))

class TrendAgent:
    def __init__(self, db_uri=None):
        """
        Initialize the Trend Analyzer Agent
        
        Args:
            db_uri (str): PostgreSQL connection URI
        """
        self.db_uri = db_uri if db_uri else os.getenv("DATABASE_URL")
        self.df = None
        self.analysis_results = {}
        
        self.load_data()
    
    def load_data(self):
        """
        Load and preprocess climate data from PostgreSQL database
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create SQLAlchemy engine
            engine = create_engine(self.db_uri)
            # Query the weather_data table
            query = "SELECT * FROM weather_data"
            self.df = pd.read_sql(query, engine)
            print(f"Data loaded successfully from PostgreSQL with shape: {self.df.shape}")
            
            # Check if datetime column exists
            if 'datetime' in self.df.columns:
                self.df['datetime'] = pd.to_datetime(self.df['datetime'])
                self.df.set_index('datetime', inplace=True)
                print(f"Date range: {self.df.index.min()} to {self.df.index.max()}")
            else:
                print("Warning: No datetime column found. Using index as time reference.")
            
            # Basic data info
            print(f"Data columns: {list(self.df.columns)}")
            return True
            
        except Exception as e:
            print(f"Error loading data from PostgreSQL: {e}")
            return False
    
    def filter_data_by_date(self, start_date=None, end_date=None):
        """
        Filter data by date range
        
        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            
        Returns:
            pandas.DataFrame: Filtered dataframe or None if error
        """
        if self.df is None:
            print("No data available for filtering")
            return None
            
        filtered_df = self.df.copy()
        
        # Convert string dates to datetime objects
        if start_date:
            try:
                start_dt = pd.to_datetime(start_date)
                filtered_df = filtered_df[filtered_df.index >= start_dt]
            except:
                print(f"Invalid start date: {start_date}")
                
        if end_date:
            try:
                end_dt = pd.to_datetime(end_date)
                filtered_df = filtered_df[filtered_df.index <= end_dt]
            except:
                print(f"Invalid end date: {end_date}")
                
        print(f"Filtered data shape: {filtered_df.shape}")
        return filtered_df
    
    def analyze_trends(self, start_date=None, end_date=None, features=None):
        """
        Analyze climate trends for the specified date range
        
        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            features (list, str, or None): Specific feature(s) to analyze. 
                                          If None, analyzes all numeric columns.
                                          Can be a single string or list of strings.
            
        Returns:
            dict: Analysis results
        """
        if self.df is None:
            return {"error": "No data available for analysis"}
        
        # Filter data by date range if provided
        filtered_df = self.filter_data_by_date(start_date, end_date)
        if filtered_df is None or len(filtered_df) == 0:
            return {"error": "No data available for the selected date range"}
        
        results = {
            "date_range": {
                "start": str(filtered_df.index.min()),
                "end": str(filtered_df.index.max())
            },
            "data_points": len(filtered_df)
        }
        
        # Handle feature selection
        if features is not None:
            # Convert single string to list
            if isinstance(features, str):
                features = [features]
            
            # Validate features exist in dataframe
            valid_features = [f for f in features if f in filtered_df.columns]
            if not valid_features:
                available_cols = list(filtered_df.columns)
                return {
                    "error": f"None of the requested features exist in the dataset.",
                    "requested_features": features,
                    "available_columns": available_cols
                }
            
            # Filter to only numeric columns from the requested features
            numeric_cols = [f for f in valid_features 
                           if filtered_df[f].dtype in [np.float64, np.int64, np.float32, np.int32]]
            
            if not numeric_cols:
                return {
                    "error": f"Requested features are not numeric columns.",
                    "requested_features": features,
                    "valid_features": valid_features
                }
        else:
            # Default behavior: analyze all numeric columns
            numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Skip columns with too many NaN values
            if filtered_df[col].isna().sum() / len(filtered_df) > 0.8:  # Skip if more than 80% NaN
                continue
                
            # Calculate basic statistics (handle NaN values)
            col_data = filtered_df[col].dropna()
            if len(col_data) == 0:
                continue
                
            results[col] = {
                'mean': float(col_data.mean()),
                'median': float(col_data.median()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'count': int(len(col_data)),
                'missing': int(filtered_df[col].isna().sum()),
                'trend': self._calculate_trend(col_data)
            }
        
        # Calculate correlations (only between columns with sufficient data)
        valid_numeric_cols = [col for col in numeric_cols 
                             if col in results and results[col]['count'] > 100]
        
        if len(valid_numeric_cols) > 1:
            # Create a dataframe with only valid columns and drop rows with any NaN
            corr_df = filtered_df[valid_numeric_cols].dropna()
            if len(corr_df) > 10:  # Only calculate correlation if we have enough data
                corr_matrix = corr_df.corr()
                # Convert to serializable format
                corr_dict = {}
                for row in corr_matrix.index:
                    corr_dict[row] = {}
                    for col in corr_matrix.columns:
                        value = corr_matrix.loc[row, col]
                        corr_dict[row][col] = None if pd.isna(value) else float(value)
                results['correlations'] = corr_dict
        
        self.analysis_results = results
        return results
    
    def _calculate_trend(self, series):
        """
        Calculate linear trend for a time series (internal method)
        
        Args:
            series (pandas.Series): Time series data
            
        Returns:
            dict: Trend analysis results
        """
        if len(series) < 2:
            return {"slope": 0, "intercept": series.iloc[0] if len(series) == 1 else 0, 
                    "r_value": 0, "p_value": 1, "error": "Insufficient data"}
        
        x = np.arange(len(series))
        y = series.values
        
        # Handle NaN values
        mask = ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {"slope": 0, "intercept": y[0] if len(y) == 1 else 0, 
                    "r_value": 0, "p_value": 1, "error": "Insufficient data after NaN removal"}
        
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            return {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_value": float(r_value),
                "p_value": float(p_value),
                "std_err": float(std_err)
            }
        except Exception as e:
            return {"slope": 0, "intercept": 0, "r_value": 0, "p_value": 1, 
                    "error": f"Error calculating trend: {str(e)}"}
    
    def generate_visualizations(self, start_date=None, end_date=None, output_dir="visualizations", features=None):
        """
        Generate climate trend visualizations
        
        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            output_dir (str): Directory to save visualizations
            features (list, str, or None): Specific feature(s) to visualize. 
                                          If None, visualizes all numeric columns.
            
        Returns:
            dict: Paths to generated visualizations
        """
        if self.df is None:
            return {"error": "No data available for visualization"}
        
        # Filter data by date range if provided
        filtered_df = self.filter_data_by_date(start_date, end_date)
        if filtered_df is None or len(filtered_df) == 0:
            return {"error": "No data available for the selected date range"}
        
        # Create visualization directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Handle feature selection (same logic as analyze_trends)
        if features is not None:
            if isinstance(features, str):
                features = [features]
            
            valid_features = [f for f in features if f in filtered_df.columns]
            if not valid_features:
                return {
                    "error": f"None of the requested features exist in the dataset.",
                    "requested_features": features,
                    "available_columns": list(filtered_df.columns)
                }
            
            numeric_cols = [f for f in valid_features 
                           if filtered_df[f].dtype in [np.float64, np.int64, np.float32, np.int32]]
            
            if not numeric_cols:
                return {
                    "error": f"Requested features are not numeric columns.",
                    "requested_features": features
                }
        else:
            # Default: all numeric columns
            numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
        
        plot_paths = {}
        
        for col in numeric_cols:
            # Skip columns with too many NaN values
            if filtered_df[col].isna().sum() / len(filtered_df) > 0.8:
                continue
                
            plt.figure(figsize=(12, 6))
            
            # For large datasets, show a subset or aggregated data
            if len(filtered_df) > 1000:
                # Resample for better visualization
                if pd.infer_freq(filtered_df.index) is not None:
                    # Try to resample based on inferred frequency
                    try:
                        resampled = filtered_df[col].resample('M').mean()
                        plt.plot(resampled.index, resampled.values, linewidth=1)
                        plt.title(f'{col.capitalize()} Over Time (Monthly Average)')
                    except:
                        # If resampling fails, just plot a subset
                        subset = filtered_df[col].iloc[::len(filtered_df)//1000]
                        plt.plot(subset.index, subset.values, linewidth=1)
                        plt.title(f'{col.capitalize()} Over Time (Subset)')
                else:
                    # Just plot a subset
                    subset = filtered_df[col].iloc[::len(filtered_df)//1000]
                    plt.plot(subset.index, subset.values, linewidth=1)
                    plt.title(f'{col.capitalize()} Over Time (Subset)')
            else:
                plt.plot(filtered_df.index, filtered_df[col], linewidth=1)
                plt.title(f'{col.capitalize()} Over Time')
            
            plt.xlabel('Date')
            plt.ylabel(col.capitalize())
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save plot
            filename = f'{output_dir}/{col}_trend.png'
            plt.savefig(filename, dpi=100, bbox_inches='tight')
            plot_paths[col] = filename
            plt.close()
        
        # Generate correlation heatmap if multiple numeric columns
        valid_numeric_cols = [col for col in numeric_cols 
                             if filtered_df[col].isna().sum() / len(filtered_df) <= 0.8]
        
        if len(valid_numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            # Use only rows with no missing values in these columns
            corr_data = filtered_df[valid_numeric_cols].dropna()
            if len(corr_data) > 10:
                corr_matrix = corr_data.corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
                plt.title('Correlation Matrix of Climate Variables')
                plt.tight_layout()
                
                filename = f'{output_dir}/correlation_heatmap.png'
                plt.savefig(filename, dpi=100, bbox_inches='tight')
                plot_paths['correlation'] = filename
            plt.close()
        
        return plot_paths
    
    def get_data_info(self):
        """
        Get basic information about the loaded dataset
        
        Returns:
            dict: Dataset information
        """
        if self.df is None:
            return {"error": "No data available"}
        
        info = {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "numeric_columns": list(self.df.select_dtypes(include=[np.number]).columns),
            "data_types": {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }
        
        # Add date range if we have a datetime index
        if hasattr(self.df.index, 'min') and hasattr(self.df.index, 'max'):
            info["date_range"] = {
                "start": str(self.df.index.min()),
                "end": str(self.df.index.max())
            }
        
        # Add info about missing values
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        info["missing_values"] = {}
        for col in numeric_cols:
            missing_count = self.df[col].isna().sum()
            missing_percent = (missing_count / len(self.df)) * 100
            info["missing_values"][col] = {
                "count": int(missing_count),
                "percent": float(missing_percent)
            }
        
        return info
    
    def export_results(self, output_path="trend_analysis_results.json"):
        """
        Export analysis results to JSON file
        
        Args:
            output_path (str): Path to output JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.analysis_results:
            print("No analysis results to export")
            return False
        
        try:
            # Convert to JSON-serializable format
            def sanitize_json(obj):
                if isinstance(obj, (np.float32, np.float64, float)):
                    return None if np.isnan(obj) or np.isinf(obj) else obj
                if isinstance(obj, (np.int32, np.int64, int)):
                    return int(obj)
                if isinstance(obj, dict):
                    return {k: sanitize_json(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [sanitize_json(item) for item in obj]
                return obj
            
            with open(output_path, 'w') as f:
                json.dump(sanitize_json(self.analysis_results), f, indent=2)
            
            print(f"Results exported to {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False


# Global instance for tools
trend_agent_instance = None

def get_trend_agent():
    """Get or create a global TrendAgent instance"""
    global trend_agent_instance
    if trend_agent_instance is None:
        trend_agent_instance = TrendAgent()
    return trend_agent_instance


# Define TrendState for LangGraph
class TrendState(TypedDict):
    input: str  # input query/parameters
    start_date: Optional[str]  # start date for analysis
    end_date: Optional[str]  # end date for analysis
    analysis_results: Optional[dict]  # trend analysis results
    visualizations: Optional[dict]  # visualization paths
    data_info: Optional[dict]  # dataset information
    output: str  # final formatted output
    error: Optional[str]  # error message if any


# LangChain tools for trend analysis
@tool("analyze_climate_trends", return_direct=True)
def analyze_climate_trends_tool(tool_input: str) -> str:
    """
    Analyze climate trends for a specified date range and optional features.
    tool_input format: "start_date=YYYY-MM-DD;end_date=YYYY-MM-DD;features=temp,humidity" 
    or "features=temperature" or just "analyze" for full dataset
    """
    try:
        agent = get_trend_agent()
        
        # Parse input parameters
        start_date, end_date, features = None, None, None
        if "=" in tool_input:
            params = dict(item.split("=") for item in tool_input.split(";") if "=" in item)
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            features_str = params.get("features")
            
            # Parse features (can be comma-separated list)
            if features_str:
                features = [f.strip() for f in features_str.split(",")]
        
        # Perform analysis with optional features parameter
        results = agent.analyze_trends(start_date, end_date, features)
        return json.dumps(results, default=str)
        
    except Exception as e:
        return json.dumps({"error": f"Analysis failed: {str(e)}"})


@tool("generate_trend_visualizations", return_direct=True)
def generate_trend_visualizations_tool(tool_input: str) -> str:
    """
    Generate climate trend visualizations.
    tool_input format: "start_date=YYYY-MM-DD;end_date=YYYY-MM-DD;output_dir=path;features=temp,humidity" 
    or "generate" for defaults
    """
    try:
        agent = get_trend_agent()
        
        # Parse input parameters
        start_date, end_date, output_dir, features = None, None, "visualizations", None
        if "=" in tool_input:
            params = dict(item.split("=") for item in tool_input.split(";") if "=" in item)
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            output_dir = params.get("output_dir", "visualizations")
            features_str = params.get("features")
            
            # Parse features (can be comma-separated list)
            if features_str:
                features = [f.strip() for f in features_str.split(",")]
        
        # Generate visualizations with optional features parameter
        plot_paths = agent.generate_visualizations(start_date, end_date, output_dir, features)
        return json.dumps(plot_paths, default=str)
        
    except Exception as e:
        return json.dumps({"error": f"Visualization generation failed: {str(e)}"})


@tool("get_dataset_info", return_direct=True)
def get_dataset_info_tool(tool_input: str) -> str:
    """
    Get basic information about the loaded climate dataset.
    tool_input: any string (parameter is ignored)
    """
    try:
        agent = get_trend_agent()
        info = agent.get_data_info()
        return json.dumps(info, default=str)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get dataset info: {str(e)}"})


@tool("export_trend_results", return_direct=True)
def export_trend_results_tool(tool_input: str) -> str:
    """
    Export trend analysis results to JSON file.
    tool_input format: "output_path=filename.json" or just filename
    """
    try:
        agent = get_trend_agent()
        
        # Parse output path
        output_path = "trend_analysis_results.json"
        if "=" in tool_input:
            params = dict(item.split("=") for item in tool_input.split(";") if "=" in item)
            output_path = params.get("output_path", output_path)
        elif tool_input.strip():
            output_path = tool_input.strip()
        
        # Export results
        success = agent.export_results(output_path)
        return json.dumps({"success": success, "output_path": output_path})
        
    except Exception as e:
        return json.dumps({"error": f"Export failed: {str(e)}"})


# Create tools list
trend_tools = [
    analyze_climate_trends_tool,
    generate_trend_visualizations_tool,
    get_dataset_info_tool,
    export_trend_results_tool
]

# Initialize trend agent with tools
trend_analyzer = initialize_agent(
    trend_tools, llm, agent="zero-shot-react-description", verbose=True
)


# Define LangGraph nodes
def data_info_node(state: TrendState) -> TrendState:
    """Node to get dataset information"""
    try:
        result = get_dataset_info_tool.invoke("info")
        state["data_info"] = json.loads(result)
        if "error" in state["data_info"]:
            state["error"] = state["data_info"]["error"]
    except Exception as e:
        state["error"] = f"Data info node failed: {str(e)}"
    return state


def analysis_node(state: TrendState) -> TrendState:
    """Node to perform trend analysis"""
    try:
        # Build tool input from state
        tool_input = ""
        parts = []
        
        if state.get("start_date") and state.get("end_date"):
            parts.append(f"start_date={state['start_date']}")
            parts.append(f"end_date={state['end_date']}")
        
        # Add features if specified in input query
        if state.get("input"):
            # Try to extract feature from input
            from trend import normalize_feature_name
            agent = get_trend_agent()
            words = state["input"].lower().split()
            for word in words:
                if word not in ['analyze', 'trend', 'trends', 'analysis', 'for', 'of', 'the', 'last', 'day', 'days']:
                    normalized = normalize_feature_name(word, agent.df.columns if agent.df is not None else [])
                    if normalized:
                        parts.append(f"features={normalized}")
                        break
        
        tool_input = ";".join(parts) if parts else "analyze"
        
        result = analyze_climate_trends_tool.invoke(tool_input)
        state["analysis_results"] = json.loads(result)
        if "error" in state["analysis_results"]:
            state["error"] = state["analysis_results"]["error"]
    except Exception as e:
        state["error"] = f"Analysis node failed: {str(e)}"
    return state


def visualization_node(state: TrendState) -> TrendState:
    """Node to generate visualizations"""
    try:
        # Build tool input from state
        parts = []
        
        if state.get("start_date") and state.get("end_date"):
            parts.append(f"start_date={state['start_date']}")
            parts.append(f"end_date={state['end_date']}")
            parts.append("output_dir=visualizations")
        
        # Add features if specified in input query
        if state.get("input"):
            # Try to extract feature from input
            from trend import normalize_feature_name
            agent = get_trend_agent()
            words = state["input"].lower().split()
            for word in words:
                if word not in ['analyze', 'trend', 'trends', 'analysis', 'for', 'of', 'the', 'last', 'day', 'days']:
                    normalized = normalize_feature_name(word, agent.df.columns if agent.df is not None else [])
                    if normalized:
                        parts.append(f"features={normalized}")
                        break
        
        tool_input = ";".join(parts) if parts else "generate"
        
        result = generate_trend_visualizations_tool.invoke(tool_input)
        state["visualizations"] = json.loads(result)
        if "error" in state["visualizations"]:
            state["error"] = state["visualizations"]["error"]
    except Exception as e:
        state["error"] = f"Visualization node failed: {str(e)}"
    return state


def output_compilation_node(state: TrendState) -> TrendState:
    """Node to compile final output"""
    try:
        if state.get("error"):
            state["output"] = f"Error: {state['error']}"
        else:
            # Compile comprehensive output
            output_data = {
                "dataset_info": state.get("data_info", {}),
                "analysis_results": state.get("analysis_results", {}),
                "visualizations": state.get("visualizations", {}),
                "parameters": {
                    "start_date": state.get("start_date"),
                    "end_date": state.get("end_date")
                }
            }
            state["output"] = json.dumps(output_data, indent=2, default=str)
    except Exception as e:
        state["output"] = f"Output compilation failed: {str(e)}"
    return state


# Create StateGraph
graph = StateGraph(TrendState)

# Add nodes
graph.add_node("data_info", data_info_node)
graph.add_node("analysis", analysis_node)
graph.add_node("visualization", visualization_node)
graph.add_node("output", output_compilation_node)

# Add edges
graph.add_edge(START, "data_info")
graph.add_edge("data_info", "analysis")
graph.add_edge("analysis", "visualization")
graph.add_edge("visualization", "output")
graph.add_edge("output", END)

# Compile the graph
trend_app = graph.compile()


def run_trend_analysis_agent(query: str, start_date: str = None, end_date: str = None) -> str:
    """
    Run the trend analysis agent with the given parameters.
    
    Args:
        query (str): Description of the analysis to perform
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
    
    Returns:
        str: JSON string with comprehensive analysis results
    """
    try:
        # Create initial state
        initial_state = {
            "input": query,
            "start_date": start_date,
            "end_date": end_date,
            "analysis_results": None,
            "visualizations": None,
            "data_info": None,
            "output": "",
            "error": None
        }
        
        # Run the graph
        result = trend_app.invoke(initial_state)
        return result["output"]
        
    except Exception as e:
        return json.dumps({"error": f"Trend analysis agent failed: {str(e)}"}, default=str)