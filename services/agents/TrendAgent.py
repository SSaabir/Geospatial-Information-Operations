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
import time
from sqlalchemy import create_engine, exc  # For PostgreSQL connection
from sqlalchemy.engine.base import Engine
from typing import Optional, Union
from dotenv import load_dotenv
import logging

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

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendAgent:
    def __init__(self, db_uri=None, retry_attempts=3, retry_delay=1):
        """
        Initialize the Trend Analyzer Agent
        
        Args:
            db_uri (str): PostgreSQL connection URI
            retry_attempts (int): Number of connection retry attempts
            retry_delay (float): Initial delay between retries in seconds (will increase exponentially)
        """
        self.db_uri = db_uri if db_uri else os.getenv("DATABASE_URL")
        self.df = None
        self.analysis_results = {}
        self.engine: Optional[Engine] = None
        self.connected = False
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Connect and load the data
        self.connect_and_load_data()
    
    def connect_to_db(self) -> tuple[bool, str]:
        """
        Establish connection to the PostgreSQL database with retry logic
        
        Returns:
            tuple[bool, str]: (success status, error message if any)
        """
        delay = self.retry_delay
        for attempt in range(self.retry_attempts):
            try:
                if self.engine is None:
                    self.engine = create_engine(self.db_uri)
                
                # Removed database connection test
                self.connected = True
                return True, ""
                
            except exc.SQLAlchemyError as e:
                error_msg = f"Database connection attempt {attempt + 1} failed: {str(e)}"
                print(error_msg)
                
                if attempt < self.retry_attempts - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                self.engine = None
                self.connected = False
                
        return False, f"Failed to connect after {self.retry_attempts} attempts"

    def load_data_from_csv(self, csv_path: str = "data/history_colombo.csv") -> tuple[bool, str]:
        """
        Fallback method to load data from CSV file
        
        Args:
            csv_path (str): Path to the CSV file
            
        Returns:
            tuple[bool, str]: (success status, error message if any)
        """
        try:
            if not os.path.exists(csv_path):
                return False, f"CSV file not found at {csv_path}"
                
            self.df = pd.read_csv(csv_path)
            print(f"Data loaded from CSV with shape: {self.df.shape}")
            
            if 'datetime' in self.df.columns:
                self.df['datetime'] = pd.to_datetime(self.df['datetime'])
                self.df.set_index('datetime', inplace=True)
            
            return True, ""
            
        except Exception as e:
            return False, f"Error loading CSV data: {str(e)}"
    
    def connect_and_load_data(self) -> bool:
        """
        Load and preprocess climate data from PostgreSQL database with fallback to CSV
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Try database connection first
        success, error_msg = self.connect_to_db()
        
        if success:
            try:
                # Query the weather_data table
                query = "SELECT * FROM weather_data"
                self.df = pd.read_sql(query, self.engine)
                print(f"Data loaded successfully from PostgreSQL with shape: {self.df.shape}")
                
                # Check if datetime column exists
                if 'datetime' in self.df.columns:
                    self.df['datetime'] = pd.to_datetime(self.df['datetime'])
                    self.df.set_index('datetime', inplace=True)
                    print(f"Date range: {self.df.index.min()} to {self.df.index.max()}")
                else:
                    print("Warning: No datetime column found. Using index as time reference.")
                
                print(f"Data columns: {list(self.df.columns)}")
                return True
                
            except Exception as e:
                print(f"Error loading data from PostgreSQL: {e}")
                self.connected = False
                self.engine = None
                
                # Try CSV fallback
                print("Attempting to load data from CSV fallback...")
                csv_success, csv_error = self.load_data_from_csv()
                
                if csv_success:
                    print("Successfully loaded data from CSV fallback")
                    return True
                else:
                    print(f"CSV fallback failed: {csv_error}")
                    return False
        else:
            print(f"Database connection failed: {error_msg}")
            print("Attempting to load data from CSV fallback...")
            csv_success, csv_error = self.load_data_from_csv()
            
            if csv_success:
                print("Successfully loaded data from CSV fallback")
                return True
            else:
                print(f"CSV fallback failed: {csv_error}")
                return False
    
    def filter_data_by_date(self, start_date=None, end_date=None):
        """
        Filter data by date range and validate data quality
        
        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            
        Returns:
            pandas.DataFrame: Filtered and validated dataframe or None if error
        """
        if self.df is None:
            print("No data available for filtering")
            return None
            
        try:
            filtered_df = self.df.copy()
            
            # Ensure datetime index
            if not isinstance(filtered_df.index, pd.DatetimeIndex):
                if 'datetime' in filtered_df.columns:
                    filtered_df['datetime'] = pd.to_datetime(filtered_df['datetime'], errors='coerce')
                    filtered_df.set_index('datetime', inplace=True)
                else:
                    print("Warning: No valid datetime column found")
                    return None
            
            # Convert string dates to datetime objects
            if start_date:
                try:
                    start_dt = pd.to_datetime(start_date)
                    filtered_df = filtered_df[filtered_df.index >= start_dt]
                except Exception as e:
                    print(f"Invalid start date {start_date}: {e}")
                    return None
                    
            if end_date:
                try:
                    end_dt = pd.to_datetime(end_date)
                    filtered_df = filtered_df[filtered_df.index <= end_dt]
                except Exception as e:
                    print(f"Invalid end date {end_date}: {e}")
                    return None
            
            # Validate we have enough data
            if len(filtered_df) == 0:
                print("No data available for the specified date range")
                return None
            
            # Replace None values with NaN for proper pandas handling
            numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
            filtered_df[numeric_cols] = filtered_df[numeric_cols].replace([None], np.nan)
            
            print(f"Filtered data shape: {filtered_df.shape}")
            print(f"Date range: {filtered_df.index.min()} to {filtered_df.index.max()}")
            return filtered_df
            
        except Exception as e:
            print(f"Error filtering data: {e}")
            return None
    
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
        # Check if DataFrame is None
        if self.df is None:
            logger.error("DataFrame is None. Ensure data is loaded before analysis.")
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
                
            # Calculate basic statistics (handle NaN and None values)
            col_data = filtered_df[col].replace([None], np.nan).dropna()
            if len(col_data) == 0:
                continue
                
            # Safely calculate statistics with error handling
            try:
                stats = {
                    'mean': float(col_data.mean()) if not col_data.empty else None,
                    'median': float(col_data.median()) if not col_data.empty else None,
                    'std': float(col_data.std()) if len(col_data) > 1 else 0.0,
                    'min': float(col_data.min()) if not col_data.empty else None,
                    'max': float(col_data.max()) if not col_data.empty else None,
                    'count': int(len(col_data)),
                    'missing': int(filtered_df[col].isna().sum()),
                }
                
                # Only add valid statistics (non-None values)
                results[col] = {k: v for k, v in stats.items() if v is not None}
                
                # Calculate trend only if we have enough data
                if len(col_data) >= 2:
                    trend_data = self._calculate_trend(col_data)
                    if trend_data and not any(v is None for v in trend_data.values()):
                        results[col]['trend'] = trend_data
                    else:
                        results[col]['trend'] = {
                            "slope": 0,
                            "intercept": float(col_data.iloc[0]) if not col_data.empty else 0,
                            "r_value": 0,
                            "p_value": 1,
                            "error": "Insufficient valid data for trend calculation"
                        }
            except Exception as e:
                results[col] = {
                    'error': f"Failed to calculate statistics: {str(e)}",
                    'count': int(len(col_data)),
                    'missing': int(filtered_df[col].isna().sum())
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
            dict: Trend analysis results with numeric values only (no None values)
        """
        def safe_float(value, default=0.0):
            """Convert value to float safely, returning default if conversion fails"""
            try:
                result = float(value)
                return 0.0 if np.isnan(result) or np.isinf(result) else result
            except (TypeError, ValueError):
                return default

        # Handle insufficient data case
        if len(series) < 2:
            first_value = safe_float(series.iloc[0] if len(series) == 1 else 0.0)
            return {
                "slope": 0.0,
                "intercept": first_value,
                "r_value": 0.0,
                "p_value": 1.0,
                "std_err": 0.0,
                "note": "Insufficient data"
            }
        
        x = np.arange(len(series))
        y = series.values
        
        # Handle NaN values
        mask = ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            first_valid = safe_float(y[0] if len(y) > 0 else 0.0)
            return {
                "slope": 0.0,
                "intercept": first_valid,
                "r_value": 0.0,
                "p_value": 1.0,
                "std_err": 0.0,
                "note": "Insufficient data after NaN removal"
            }
        
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            return {
                "slope": safe_float(slope),
                "intercept": safe_float(intercept),
                "r_value": safe_float(r_value),
                "p_value": safe_float(p_value),
                "std_err": safe_float(std_err)
            }
        except Exception as e:
            return {
                "slope": 0.0,
                "intercept": 0.0,
                "r_value": 0.0,
                "p_value": 1.0, 
                "std_err": 0.0,
                "note": f"Error calculating trend: {str(e)}"
            }
    
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
    
    def generate_smart_visualizations(self, user_query: str, start_date=None, end_date=None, output_dir="visualizations"):
        """
        Intelligently generate visualizations based on query intent and data characteristics
        
        Args:
            user_query (str): The user's natural language query
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            output_dir (str): Directory to save visualizations
            
        Returns:
            dict: Paths to generated visualizations with metadata
        """
        if self.df is None or self.df.empty:
            return {"error": "No data available for visualization"}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        query_lower = user_query.lower()
        plot_paths = {}
        
        # Analyze query intent with priority ordering
        # "trend between X and Y" should be correlation, not comparison
        is_correlation = any(word in query_lower for word in ['correlation', 'correlate', 'relationship', 'association', 'connection', 'pattern'])
        is_trend_over_time = any(phrase in query_lower for phrase in ['over time', 'temporal', 'time series', 'evolution'])
        is_comparison = any(word in query_lower for word in ['compare', 'difference', 'versus', 'vs']) and 'by' in query_lower
        is_distribution = any(word in query_lower for word in ['distribution', 'histogram', 'spread', 'range'])
        
        # Special case: "trend between X and Y" without time context = correlation
        has_trend_between = 'trend' in query_lower and 'between' in query_lower
        if has_trend_between and not is_trend_over_time:
            is_correlation = True
            is_comparison = False
        
        # Get data characteristics
        has_datetime_index = isinstance(self.df.index, pd.DatetimeIndex)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        
        # Extract mentioned features from query
        mentioned_features = []
        for col in self.df.columns:
            if col.lower() in query_lower or col.lower().replace('_', ' ') in query_lower:
                mentioned_features.append(col)
        
        try:
            # 1. CORRELATION ANALYSIS
            if is_correlation and len(numeric_cols) >= 2:
                logger.info("📊 Generating correlation visualizations...")
                
                # Scatter plot for pairwise correlations
                if len(mentioned_features) >= 2:
                    x_col = mentioned_features[0]
                    y_col = mentioned_features[1]
                elif len(numeric_cols) >= 2:
                    x_col = numeric_cols[0]
                    y_col = numeric_cols[1]
                
                if x_col in numeric_cols and y_col in numeric_cols:
                    plt.figure(figsize=(10, 6))
                    valid_data = self.df[[x_col, y_col]].dropna()
                    
                    if len(valid_data) >= 2:
                        plt.scatter(valid_data[x_col], valid_data[y_col], alpha=0.6, s=100, edgecolors='black')
                        plt.xlabel(x_col.replace('_', ' ').title(), fontsize=12)
                        plt.ylabel(y_col.replace('_', ' ').title(), fontsize=12)
                        plt.title(f'Correlation Analysis: {x_col.title()} vs {y_col.title()}', fontsize=14, fontweight='bold')
                        plt.grid(True, alpha=0.3)
                        
                        # Calculate and display correlation
                        correlation = valid_data[x_col].corr(valid_data[y_col])
                        plt.text(0.05, 0.95, f'Pearson Correlation: {correlation:.3f}', 
                                transform=plt.gca().transAxes, 
                                fontsize=11,
                                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
                        
                        # Add trend line
                        z = np.polyfit(valid_data[x_col], valid_data[y_col], 1)
                        p = np.poly1d(z)
                        plt.plot(valid_data[x_col], p(valid_data[x_col]), "r--", alpha=0.8, linewidth=2, label='Trend Line')
                        plt.legend()
                        
                        scatter_path = f'{output_dir}/correlation_scatter_{x_col}_{y_col}.png'
                        plt.savefig(scatter_path, dpi=100, bbox_inches='tight')
                        plt.close()
                        
                        plot_paths['correlation_scatter'] = scatter_path
                        logger.info(f"✅ Generated scatter plot: {scatter_path}")
                
                # Correlation heatmap for all numeric columns
                if len(numeric_cols) > 2:
                    plt.figure(figsize=(12, 10))
                    corr_data = self.df[numeric_cols].dropna()
                    
                    if len(corr_data) >= 2:
                        corr_matrix = corr_data.corr()
                        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f', 
                                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
                        plt.title('Correlation Matrix - All Numeric Features', fontsize=14, fontweight='bold')
                        plt.tight_layout()
                        
                        heatmap_path = f'{output_dir}/correlation_heatmap_full.png'
                        plt.savefig(heatmap_path, dpi=100, bbox_inches='tight')
                        plt.close()
                        
                        plot_paths['correlation_heatmap'] = heatmap_path
                        logger.info(f"✅ Generated heatmap: {heatmap_path}")
            
            # 2. TIME-SERIES TREND ANALYSIS
            elif is_trend_over_time and has_datetime_index and len(numeric_cols) >= 1:
                logger.info("📈 Generating time-series trend visualizations...")
                
                # Filter by date range if provided
                filtered_df = self.filter_data_by_date(start_date, end_date)
                if filtered_df is None or len(filtered_df) < 2:
                    filtered_df = self.df
                
                # Generate trend plots for mentioned features or all numeric columns
                features_to_plot = mentioned_features if mentioned_features else numeric_cols[:5]  # Limit to 5
                
                for col in features_to_plot:
                    if col in numeric_cols:
                        plt.figure(figsize=(14, 6))
                        
                        # Handle missing values
                        plot_data = filtered_df[col].dropna()
                        if len(plot_data) < 2:
                            continue
                        
                        plt.plot(plot_data.index, plot_data.values, linewidth=2, marker='o', markersize=4)
                        plt.xlabel('Date', fontsize=12)
                        plt.ylabel(col.replace('_', ' ').title(), fontsize=12)
                        plt.title(f'Trend Analysis: {col.replace("_", " ").title()} Over Time', fontsize=14, fontweight='bold')
                        plt.grid(True, alpha=0.3)
                        plt.xticks(rotation=45)
                        
                        # Add trend line
                        x_numeric = np.arange(len(plot_data))
                        z = np.polyfit(x_numeric, plot_data.values, 1)
                        p = np.poly1d(z)
                        plt.plot(plot_data.index, p(x_numeric), "r--", alpha=0.8, linewidth=2, label='Trend Line')
                        plt.legend()
                        
                        plt.tight_layout()
                        
                        trend_path = f'{output_dir}/trend_{col}.png'
                        plt.savefig(trend_path, dpi=100, bbox_inches='tight')
                        plt.close()
                        
                        plot_paths[f'trend_{col}'] = trend_path
                        logger.info(f"✅ Generated trend plot: {trend_path}")
            
            # 3. COMPARISON / CATEGORICAL ANALYSIS
            elif is_comparison or (len(categorical_cols) > 0 and len(numeric_cols) > 0):
                logger.info("📊 Generating comparison visualizations...")
                
                # Find best categorical and numeric columns
                cat_col = categorical_cols[0] if categorical_cols else None
                num_col = mentioned_features[0] if mentioned_features and mentioned_features[0] in numeric_cols else numeric_cols[0]
                
                if cat_col and num_col:
                    plt.figure(figsize=(12, 6))
                    
                    # Group by category and calculate statistics
                    grouped = self.df.groupby(cat_col)[num_col].agg(['mean', 'std', 'count'])
                    grouped = grouped[grouped['count'] > 0]  # Remove empty groups
                    
                    if len(grouped) > 0:
                        # Bar plot with error bars
                        ax = grouped['mean'].plot(kind='bar', yerr=grouped['std'], 
                                                 color='skyblue', edgecolor='black', 
                                                 capsize=5, error_kw={'linewidth': 2})
                        plt.xlabel(cat_col.replace('_', ' ').title(), fontsize=12)
                        plt.ylabel(f'Average {num_col.replace("_", " ").title()}', fontsize=12)
                        plt.title(f'Comparison: {num_col.title()} by {cat_col.title()}', fontsize=14, fontweight='bold')
                        plt.xticks(rotation=45, ha='right')
                        plt.grid(True, alpha=0.3, axis='y')
                        
                        # Add value labels on bars
                        for i, (idx, row) in enumerate(grouped.iterrows()):
                            ax.text(i, row['mean'], f'{row["mean"]:.1f}', 
                                   ha='center', va='bottom', fontsize=10)
                        
                        plt.tight_layout()
                        
                        comparison_path = f'{output_dir}/comparison_{num_col}_by_{cat_col}.png'
                        plt.savefig(comparison_path, dpi=100, bbox_inches='tight')
                        plt.close()
                        
                        plot_paths['comparison'] = comparison_path
                        logger.info(f"✅ Generated comparison plot: {comparison_path}")
            
            # 4. DISTRIBUTION ANALYSIS
            elif is_distribution and len(numeric_cols) >= 1:
                logger.info("📊 Generating distribution visualizations...")
                
                features_to_plot = mentioned_features if mentioned_features else numeric_cols[:3]
                
                for col in features_to_plot:
                    if col in numeric_cols:
                        plt.figure(figsize=(12, 6))
                        
                        plot_data = self.df[col].dropna()
                        if len(plot_data) < 2:
                            continue
                        
                        # Histogram with KDE
                        plt.subplot(1, 2, 1)
                        plt.hist(plot_data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
                        plt.xlabel(col.replace('_', ' ').title(), fontsize=11)
                        plt.ylabel('Frequency', fontsize=11)
                        plt.title(f'Distribution: {col.title()}', fontsize=12, fontweight='bold')
                        plt.grid(True, alpha=0.3, axis='y')
                        
                        # Box plot
                        plt.subplot(1, 2, 2)
                        plt.boxplot(plot_data, vert=True)
                        plt.ylabel(col.replace('_', ' ').title(), fontsize=11)
                        plt.title(f'Box Plot: {col.title()}', fontsize=12, fontweight='bold')
                        plt.grid(True, alpha=0.3, axis='y')
                        
                        plt.tight_layout()
                        
                        dist_path = f'{output_dir}/distribution_{col}.png'
                        plt.savefig(dist_path, dpi=100, bbox_inches='tight')
                        plt.close()
                        
                        plot_paths[f'distribution_{col}'] = dist_path
                        logger.info(f"✅ Generated distribution plot: {dist_path}")
            
            # 5. DEFAULT: GENERAL OVERVIEW
            else:
                logger.info("📊 Generating general overview visualizations...")
                
                # Simple visualization based on what's available
                if len(numeric_cols) >= 2:
                    # Scatter matrix or correlation
                    return self.generate_smart_visualizations(
                        "correlation analysis", start_date, end_date, output_dir
                    )
                elif len(numeric_cols) >= 1:
                    # Distribution
                    return self.generate_smart_visualizations(
                        "distribution analysis", start_date, end_date, output_dir
                    )
        
        except Exception as e:
            logger.error(f"❌ Visualization generation error: {e}", exc_info=True)
            return {"error": f"Visualization generation failed: {str(e)}"}
        
        if not plot_paths:
            logger.warning("⚠️ No visualizations generated - insufficient data or unclear intent")
            return {"warning": "No visualizations generated - data may be insufficient or query unclear"}
        
        return plot_paths
    
    def get_data_info(self):
        """
        Get basic information about the loaded dataset and trigger data collection if needed
        
        Returns:
            dict: Dataset information
        """
        # Check if we need fresh data
        if self.df is None or self.df.empty:
            # Import here to avoid circular imports
            from trend import run_trend_agent
            print("No data available, attempting to collect fresh data...")
            try:
                # Attempt to collect fresh data
                _ = run_trend_agent("collect_fresh_data", self.db_uri, auto_collect=True)
                # Reload data after collection
                self.connect_and_load_data()
            except Exception as e:
                return {
                    "error": "No data available",
                    "details": str(e),
                    "action_taken": "Attempted to collect fresh data but failed"
                }
        
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
trend_agent_instance: Optional[TrendAgent] = None

def get_trend_agent(force_reconnect: bool = False) -> TrendAgent:
    """
    Get or create a global TrendAgent instance
    
    Args:
        force_reconnect (bool): Force a reconnection attempt if True
        
    Returns:
        TrendAgent: The global TrendAgent instance
    """
    global trend_agent_instance
    
    if trend_agent_instance is None or force_reconnect:
        # Create new instance with default retry settings
        trend_agent_instance = TrendAgent(retry_attempts=3, retry_delay=1)
        
    # If we have an instance but it's not connected, try to reconnect
    elif not trend_agent_instance.connected:
        success, _ = trend_agent_instance.connect_to_db()
        if not success and force_reconnect:
            # If reconnection failed and force_reconnect is True, create new instance
            trend_agent_instance = TrendAgent(retry_attempts=3, retry_delay=1)
            
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


def run_trend_analysis_agent(query: str, start_date: str = None, end_date: str = None, collector_result: Optional[dict] = None) -> str:
    """
    Run the trend analysis agent with the given parameters.
    
    Args:
        query (str): Description of the analysis to perform
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
        collector_result (dict): Data collected by the Collector agent (optional)
    
    Returns:
        str: JSON string with comprehensive analysis results
    """
    try:
        # Ensure TrendAgent is initialized with collector_result if provided
        agent = TrendAgent()
        if collector_result:
            agent.df = pd.DataFrame(collector_result)
        elif agent.df is None or agent.df.empty:
            raise ValueError("No data provided to TrendAgent. Ensure collector_result is passed.")

        # Create initial state
        initial_state = {
            "input": query,
            "start_date": start_date,
            "end_date": end_date,
            "analysis_results": None,
            "visualizations": None,
            "data_info": None,
            "output": "",
            "error": None,
            "agent": agent  # Pass the agent to the state
        }
        
        # Ensure data is passed from the Collector
        if "collector_result" not in initial_state or not initial_state["collector_result"]:
            raise ValueError("Collector result is missing or empty. Ensure data is passed from the Collector.")

        # Initialize TrendAgent with the collected data
        agent = TrendAgent()
        agent.df = pd.DataFrame(initial_state["collector_result"])

        # Pass the agent to the graph's initial state
        initial_state["agent"] = agent
        
        # Run the graph
        result = trend_app.invoke(initial_state)
        return result["output"]
        
    except Exception as e:
        return json.dumps({"error": f"Trend analysis agent failed: {str(e)}"}, default=str)