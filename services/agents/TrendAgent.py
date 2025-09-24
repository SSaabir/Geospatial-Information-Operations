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

class TrendAgent:
    def __init__(self, db_uri="postgresql+psycopg2://postgres:Mathu1312@localhost:5432/GISDb"):
        """
        Initialize the Trend Analyzer Agent
        
        Args:
            db_uri (str): PostgreSQL connection URI
        """
        self.db_uri = db_uri
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
    
    def analyze_trends(self, start_date=None, end_date=None):
        """
        Analyze climate trends for the specified date range
        
        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            
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
        
        # Analyze each numeric column
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
    
    def generate_visualizations(self, start_date=None, end_date=None, output_dir="visualizations"):
        """
        Generate climate trend visualizations
        
        Args:
            start_date (str): Start date in format 'YYYY-MM-DD'
            end_date (str): End date in format 'YYYY-MM-DD'
            output_dir (str): Directory to save visualizations
            
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
        
        # Generate time series plots for each numeric column
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