#!/usr/bin/env python3
"""
Data Analysis and Visualization Tool
A comprehensive Python application for analyzing and visualizing datasets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DataAnalyzer:
    """Main class for data analysis and visualization"""
    
    def __init__(self, data_path: str = None):
        self.data = None
        self.data_path = data_path
        self.analysis_results = {}
        
    def load_data(self, data_path: str = None) -> bool:
        """Load data from various file formats"""
        try:
            if data_path:
                self.data_path = data_path
            
            if not self.data_path:
                return False
                
            file_extension = self.data_path.split('.')[-1].lower()
            
            if file_extension == 'csv':
                self.data = pd.read_csv(self.data_path)
            elif file_extension in ['xlsx', 'xls']:
                self.data = pd.read_excel(self.data_path)
            elif file_extension == 'json':
                self.data = pd.read_json(self.data_path)
            else:
                print(f"Unsupported file format: {file_extension}")
                return False
                
            print(f"Data loaded successfully! Shape: {self.data.shape}")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_sample_data(self) -> None:
        """Generate sample dataset for demonstration"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=1000, freq='D')
        
        self.data = pd.DataFrame({
            'date': dates,
            'sales': np.random.normal(1000, 200, 1000),
            'customers': np.random.poisson(50, 1000),
            'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], 1000),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 1000),
            'satisfaction_score': np.random.uniform(1, 5, 1000)
        })
        
        print("Sample data generated successfully!")
    
    def basic_statistics(self) -> Dict:
        """Calculate basic statistical measures"""
        if self.data is None:
            return {}
            
        stats = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'data_types': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'numeric_summary': self.data.describe().to_dict() if self.data.select_dtypes(include=[np.number]).shape[1] > 0 else {},
            'categorical_summary': {}
        }
        
        # Categorical columns summary
        categorical_cols = self.data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            stats['categorical_summary'][col] = {
                'unique_values': self.data[col].nunique(),
                'most_common': self.data[col].value_counts().head(5).to_dict()
            }
        
        self.analysis_results['basic_statistics'] = stats
        return stats
    
    def correlation_analysis(self) -> pd.DataFrame:
        """Perform correlation analysis on numeric columns"""
        if self.data is None:
            return pd.DataFrame()
            
        numeric_data = self.data.select_dtypes(include=[np.number])
        if numeric_data.shape[1] < 2:
            print("Not enough numeric columns for correlation analysis")
            return pd.DataFrame()
            
        correlation_matrix = numeric_data.corr()
        self.analysis_results['correlation_matrix'] = correlation_matrix
        return correlation_matrix
    
    def create_visualizations(self, save_path: str = "visualizations") -> None:
        """Create comprehensive visualizations"""
        if self.data is None:
            print("No data loaded for visualization")
            return
            
        # Create directory for saving plots
        os.makedirs(save_path, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Distribution plots for numeric columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Distribution Analysis', fontsize=16, fontweight='bold')
            
            for i, col in enumerate(numeric_cols[:4]):
                row, col_idx = i // 2, i % 2
                sns.histplot(self.data[col], kde=True, ax=axes[row, col_idx])
                axes[row, col_idx].set_title(f'Distribution of {col}')
                axes[row, col_idx].set_xlabel(col)
                axes[row, col_idx].set_ylabel('Frequency')
            
            plt.tight_layout()
            plt.savefig(f'{save_path}/distributions.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Correlation heatmap
        correlation_matrix = self.correlation_analysis()
        if not correlation_matrix.empty:
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5)
            plt.title('Correlation Heatmap', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f'{save_path}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Time series analysis (if date column exists)
        date_cols = self.data.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0] if len(numeric_cols) > 0 else None
            
            if numeric_col:
                plt.figure(figsize=(15, 6))
                self.data.plot(x=date_col, y=numeric_col, figsize=(15, 6))
                plt.title(f'{numeric_col} Over Time', fontsize=16, fontweight='bold')
                plt.xlabel('Date')
                plt.ylabel(numeric_col)
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f'{save_path}/time_series.png', dpi=300, bbox_inches='tight')
                plt.close()
        
        # 4. Categorical analysis
        categorical_cols = self.data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Categorical Analysis', fontsize=16, fontweight='bold')
            
            for i, col in enumerate(categorical_cols[:4]):
                row, col_idx = i // 2, i % 2
                value_counts = self.data[col].value_counts()
                axes[row, col_idx].pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
                axes[row, col_idx].set_title(f'Distribution of {col}')
            
            plt.tight_layout()
            plt.savefig(f'{save_path}/categorical_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Visualizations saved to {save_path}/")
    
    def export_analysis_report(self, output_path: str = "analysis_report.json") -> None:
        """Export analysis results to JSON file"""
        if not self.analysis_results:
            print("No analysis results to export")
            return
            
        # Add timestamp
        self.analysis_results['analysis_timestamp'] = datetime.now().isoformat()
        self.analysis_results['data_info'] = {
            'shape': self.data.shape if self.data is not None else None,
            'columns': list(self.data.columns) if self.data is not None else None
        }
        
        with open(output_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"Analysis report exported to {output_path}")

def main():
    """Main function to demonstrate the data analysis tool"""
    print("=== Data Analysis and Visualization Tool ===\n")
    
    # Initialize analyzer
    analyzer = DataAnalyzer()
    
    # Generate sample data
    print("Generating sample dataset...")
    analyzer.generate_sample_data()
    
    # Perform basic statistics
    print("\nCalculating basic statistics...")
    stats = analyzer.basic_statistics()
    print(f"Dataset shape: {stats['shape']}")
    print(f"Columns: {stats['columns']}")
    
    # Correlation analysis
    print("\nPerforming correlation analysis...")
    correlation_matrix = analyzer.correlation_analysis()
    if not correlation_matrix.empty:
        print("Correlation analysis completed!")
    
    # Create visualizations
    print("\nCreating visualizations...")
    analyzer.create_visualizations()
    
    # Export report
    print("\nExporting analysis report...")
    analyzer.export_analysis_report()
    
    print("\n=== Analysis Complete ===")
    print("Check the 'visualizations' folder for generated plots")
    print("Check 'analysis_report.json' for detailed results")

if __name__ == "__main__":
    main()