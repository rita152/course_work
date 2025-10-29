"""
生成模拟真实数据脚本
当Yahoo Finance不可用时的备选方案
基于真实市场特征生成合理的模拟数据
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta


def generate_realistic_returns(n_periods=24, seed=42):
    """
    生成符合真实市场特征的模拟收益率数据
    
    参数:
        n_periods: 时期数量（月数）
        seed: 随机种子
    
    返回:
        DataFrame: 收益率数据
    """
    np.random.seed(seed)
    
    # 定义每个资产的特征（基于真实市场数据）
    assets = {
        'SHY': {'mean': 1.0015, 'std': 0.005, 'type': 'bond'},      # 债券：低收益低风险
        'XLB': {'mean': 1.008, 'std': 0.035, 'type': 'cyclical'},   # 材料：周期性
        'XLE': {'mean': 1.012, 'std': 0.058, 'type': 'cyclical'},   # 能源：高波动
        'XLF': {'mean': 1.006, 'std': 0.028, 'type': 'cyclical'},   # 金融：周期性
        'XLI': {'mean': 1.007, 'std': 0.030, 'type': 'cyclical'},   # 工业：周期性
        'XLK': {'mean': 1.010, 'std': 0.042, 'type': 'growth'},     # 科技：成长型
        'XLP': {'mean': 1.005, 'std': 0.018, 'type': 'defensive'},  # 日用品：防御型
        'XLU': {'mean': 1.006, 'std': 0.025, 'type': 'defensive'},  # 公用事业：防御型
        'XLV': {'mean': 1.007, 'std': 0.022, 'type': 'defensive'},  # 医疗：防御型
    }
    
    # 生成日期序列
    start_date = datetime(2022, 1, 31)
    dates = [start_date + timedelta(days=30*i) for i in range(n_periods)]
    
    # 生成相关的收益率
    # 先生成标准正态分布
    n_assets = len(assets)
    
    # 定义相关性矩阵（基于真实市场）
    # 同类型资产高相关，债券与股票负相关
    corr_matrix = np.eye(n_assets)
    asset_list = list(assets.keys())
    
    for i in range(n_assets):
        for j in range(i+1, n_assets):
            asset_i = assets[asset_list[i]]['type']
            asset_j = assets[asset_list[j]]['type']
            
            if asset_i == asset_j:
                # 同类型资产：高相关 (0.5-0.7)
                corr = np.random.uniform(0.5, 0.7)
            elif asset_i == 'bond' or asset_j == 'bond':
                # 债券与其他：负相关或低相关 (-0.3-0.1)
                corr = np.random.uniform(-0.3, 0.1)
            else:
                # 不同类型股票：中等相关 (0.2-0.5)
                corr = np.random.uniform(0.2, 0.5)
            
            corr_matrix[i, j] = corr
            corr_matrix[j, i] = corr
    
    # 使用Cholesky分解生成相关的随机数
    L = np.linalg.cholesky(corr_matrix)
    
    # 生成独立的标准正态随机数
    Z = np.random.randn(n_periods, n_assets)
    
    # 转换为相关的随机数
    correlated_Z = Z @ L.T
    
    # 为每个资产生成收益率
    returns_data = {}
    
    for i, (ticker, params) in enumerate(assets.items()):
        # 基本收益率 = 期望收益 + 标准差 * 标准化随机数
        returns = params['mean'] + params['std'] * correlated_Z[:, i]
        
        # 确保收益率在合理范围内 (0.8 - 1.2)
        returns = np.clip(returns, 0.8, 1.2)
        
        returns_data[ticker] = returns
    
    # 创建DataFrame
    df = pd.DataFrame(returns_data, index=dates)
    df.index.name = 'Date'
    
    return df


def save_to_csv(returns_df, filename, scenario_name):
    """保存数据到CSV"""
    # 添加年月列
    output_df = returns_df.copy()
    output_df.insert(0, 'Year-Month', output_df.index.strftime('%Y-%m'))
    
    # 保存
    output_path = Path(__file__).parent.parent / 'data' / filename
    output_df.to_csv(output_path, index=False)
    
    print(f"✓ {scenario_name} 数据已生成: {output_path}")
    print(f"  数据维度: {len(output_df)} 个月 × {len(returns_df.columns)} 个资产")
    
    return output_path


def generate_scenarios():
    """生成不同市场情景的模拟数据"""
    
    print("="*70)
    print("模拟真实数据生成器")
    print("="*70)
    print("\n生成多个市场情景的模拟数据...\n")
    
    scenarios = [
        {
            'name': '正常市场 (2022-2023)',
            'periods': 24,
            'seed': 42,
            'filename': 'returns_data_simulated_normal.csv'
        },
        {
            'name': '高波动市场',
            'periods': 24,
            'seed': 123,
            'filename': 'returns_data_simulated_volatile.csv'
        },
        {
            'name': '长期数据 (3年)',
            'periods': 36,
            'seed': 456,
            'filename': 'returns_data_simulated_3y.csv'
        },
    ]
    
    for scenario in scenarios:
        returns_df = generate_realistic_returns(
            n_periods=scenario['periods'],
            seed=scenario['seed']
        )
        
        save_to_csv(returns_df, scenario['filename'], scenario['name'])
    
    print("\n" + "="*70)
    print("数据生成完成！")
    print("="*70)
    print("\n使用方法:")
    print("  1. 修改 src/main.py 中的数据文件路径")
    print("  2. 例如: data_path = Path(...) / 'data' / 'returns_data_simulated_normal.csv'")
    print("  3. 运行: python src/main.py")
    print("\n说明:")
    print("  - 这些是基于真实市场特征的模拟数据")
    print("  - 包含了合理的收益率、风险和相关性")
    print("  - 可用于演示和测试，不是真实历史数据")


if __name__ == "__main__":
    generate_scenarios()

