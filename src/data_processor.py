"""
数据处理模块
功能：加载历史收益率数据，计算期望收益和偏差矩阵
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DataProcessor:
    """投资组合数据处理器"""
    
    def __init__(self, data_path):
        """
        初始化数据处理器
        
        参数:
            data_path: 数据文件路径
        """
        self.data_path = Path(data_path)
        self.returns_df = None
        self.asset_names = None
        self.returns_matrix = None  # R_j(t): T x n 矩阵
        self.expected_returns = None  # r_j: n维向量
        self.deviation_matrix = None  # D_tj = R_j(t) - r_j: T x n 矩阵
        self.T = None  # 时间序列长度
        self.n = None  # 资产数量
        
        self._load_data()
        self._calculate_statistics()
    
    def _load_data(self):
        """加载数据文件"""
        self.returns_df = pd.read_csv(self.data_path)
        
        # 提取资产名称（排除日期列）
        self.asset_names = [col for col in self.returns_df.columns if col != 'Year-Month']
        self.n = len(self.asset_names)
        
        # 提取收益率矩阵
        self.returns_matrix = self.returns_df[self.asset_names].values
        self.T = len(self.returns_matrix)
        
        print(f"数据加载成功:")
        print(f"  - 资产数量: {self.n}")
        print(f"  - 时间周期: {self.T}")
        print(f"  - 资产名称: {', '.join(self.asset_names)}")
    
    def _calculate_statistics(self):
        """计算统计量：期望收益和偏差矩阵"""
        # 计算期望收益 r_j = (1/T) * Σ R_j(t)
        self.expected_returns = np.mean(self.returns_matrix, axis=0)
        
        # 计算偏差矩阵 D_tj = R_j(t) - r_j
        self.deviation_matrix = self.returns_matrix - self.expected_returns
        
        print(f"\n期望收益率:")
        for i, asset in enumerate(self.asset_names):
            print(f"  {asset}: {self.expected_returns[i]:.6f}")
    
    def get_returns_matrix(self):
        """返回收益率矩阵 R_j(t)"""
        return self.returns_matrix
    
    def get_expected_returns(self):
        """返回期望收益向量 r_j"""
        return self.expected_returns
    
    def get_deviation_matrix(self):
        """返回偏差矩阵 D_tj"""
        return self.deviation_matrix
    
    def get_asset_names(self):
        """返回资产名称列表"""
        return self.asset_names
    
    def get_dimensions(self):
        """返回维度信息 (T, n)"""
        return self.T, self.n
    
    def calculate_mad_risk(self, weights):
        """
        计算给定投资组合的MAD风险
        
        参数:
            weights: 投资权重向量 (长度为n)
        
        返回:
            MAD风险值
        """
        portfolio_deviations = self.deviation_matrix @ weights
        mad_risk = np.mean(np.abs(portfolio_deviations))
        return mad_risk
    
    def calculate_variance_risk(self, weights):
        """
        计算给定投资组合的方差风险
        
        参数:
            weights: 投资权重向量 (长度为n)
        
        返回:
            方差风险值
        """
        portfolio_deviations = self.deviation_matrix @ weights
        variance = np.var(portfolio_deviations)
        return variance
    
    def calculate_portfolio_return(self, weights):
        """
        计算给定投资组合的期望收益
        
        参数:
            weights: 投资权重向量 (长度为n)
        
        返回:
            期望收益值
        """
        return np.dot(weights, self.expected_returns)
    
    def get_correlation_matrix(self):
        """
        计算资产间的相关系数矩阵
        
        返回:
            相关系数矩阵
        """
        return np.corrcoef(self.deviation_matrix.T)
    
    def get_summary_statistics(self):
        """
        获取数据汇总统计信息
        
        返回:
            包含统计信息的DataFrame
        """
        stats = {
            '资产': self.asset_names,
            '期望收益': self.expected_returns,
            '标准差': np.std(self.deviation_matrix, axis=0),
            '最小值': np.min(self.returns_matrix, axis=0),
            '最大值': np.max(self.returns_matrix, axis=0)
        }
        return pd.DataFrame(stats)


if __name__ == "__main__":
    # 测试代码
    data_path = "../data/returns_data.csv"
    processor = DataProcessor(data_path)
    
    print("\n" + "="*60)
    print("汇总统计信息:")
    print("="*60)
    print(processor.get_summary_statistics().to_string(index=False))
    
    print("\n" + "="*60)
    print("相关系数矩阵:")
    print("="*60)
    corr_matrix = processor.get_correlation_matrix()
    corr_df = pd.DataFrame(corr_matrix, 
                          index=processor.asset_names,
                          columns=processor.asset_names)
    print(corr_df.to_string())

