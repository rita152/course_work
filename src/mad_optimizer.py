"""
MAD优化模型模块
功能：基于平均绝对偏差(MAD)的投资组合优化
模型基于教材公式(13.3)
"""

import numpy as np
from pulp import *
import time


class MADOptimizer:
    """基于MAD风险度量的投资组合优化器"""
    
    def __init__(self, data_processor):
        """
        初始化优化器
        
        参数:
            data_processor: DataProcessor实例
        """
        self.data_processor = data_processor
        self.T, self.n = data_processor.get_dimensions()
        self.expected_returns = data_processor.get_expected_returns()
        self.deviation_matrix = data_processor.get_deviation_matrix()
        self.asset_names = data_processor.get_asset_names()
    
    def optimize(self, mu, verbose=False):
        """
        求解MAD优化问题
        
        目标函数: max μ * Σ(x_j * r_j) - (1/T) * Σ(y_t)
        约束条件:
            -y_t ≤ Σ(x_j * D_tj) ≤ y_t,  for all t
            Σ(x_j) = 1
            x_j ≥ 0, y_t ≥ 0
        
        参数:
            mu: 风险厌恶参数（μ值越大，越重视收益）
            verbose: 是否输出详细信息
        
        返回:
            dict: 包含最优解信息的字典
        """
        start_time = time.time()
        
        # 创建问题
        prob = LpProblem("Portfolio_MAD", LpMaximize)
        
        # 决策变量
        # x_j: 投资在资产j的比例
        x = [LpVariable(f"x_{j}", lowBound=0) for j in range(self.n)]
        
        # y_t: 第t期的绝对偏差
        y = [LpVariable(f"y_{t}", lowBound=0) for t in range(self.T)]
        
        # 目标函数: max μ * Σ(x_j * r_j) - (1/T) * Σ(y_t)
        reward = lpSum([mu * self.expected_returns[j] * x[j] for j in range(self.n)])
        risk = (1.0 / self.T) * lpSum(y)
        prob += reward - risk, "Objective"
        
        # 约束1: Σ(x_j) = 1 (投资比例之和为1)
        prob += lpSum(x) == 1, "Budget_Constraint"
        
        # 约束2: -y_t ≤ Σ(x_j * D_tj) ≤ y_t (绝对值约束)
        for t in range(self.T):
            deviation = lpSum([self.deviation_matrix[t, j] * x[j] for j in range(self.n)])
            prob += deviation <= y[t], f"Upper_Bound_{t}"
            prob += deviation >= -y[t], f"Lower_Bound_{t}"
        
        # 求解
        if verbose:
            prob.solve(PULP_CBC_CMD(msg=1))
        else:
            prob.solve(PULP_CBC_CMD(msg=0))
        
        solve_time = time.time() - start_time
        
        # 提取结果
        if prob.status == LpStatusOptimal:
            weights = np.array([x[j].varValue for j in range(self.n)])
            y_values = np.array([y[t].varValue for t in range(self.T)])
            
            # 计算风险和收益
            expected_return = np.dot(weights, self.expected_returns)
            mad_risk = np.mean(y_values)
            
            result = {
                'status': 'Optimal',
                'weights': weights,
                'expected_return': expected_return,
                'mad_risk': mad_risk,
                'objective_value': value(prob.objective),
                'solve_time': solve_time,
                'mu': mu
            }
            
            if verbose:
                print(f"\n求解成功 (μ = {mu}):")
                print(f"  目标函数值: {result['objective_value']:.6f}")
                print(f"  期望收益: {expected_return:.6f}")
                print(f"  MAD风险: {mad_risk:.6f}")
                print(f"  求解时间: {solve_time:.4f}秒")
                print(f"\n投资组合配置:")
                for j, name in enumerate(self.asset_names):
                    if weights[j] > 1e-4:  # 只显示非零权重
                        print(f"    {name}: {weights[j]*100:.2f}%")
            
            return result
        else:
            print(f"优化失败: {LpStatus[prob.status]}")
            return None
    
    def optimize_efficient_frontier(self, mu_values, verbose=False):
        """
        计算有效前沿
        
        参数:
            mu_values: μ值列表
            verbose: 是否输出详细信息
        
        返回:
            list: 包含所有优化结果的列表
        """
        results = []
        
        print(f"计算有效前沿，共{len(mu_values)}个μ值...")
        for i, mu in enumerate(mu_values):
            if verbose or (i + 1) % 5 == 0:
                print(f"  进度: {i+1}/{len(mu_values)}, μ = {mu:.4f}")
            
            result = self.optimize(mu, verbose=False)
            if result:
                results.append(result)
        
        print(f"完成！成功求解{len(results)}个点。")
        return results
    
    def get_single_asset_portfolios(self):
        """
        获取所有单资产投资组合的风险-收益特征
        用于对比分散投资的优势
        
        返回:
            list: 包含每个单资产组合信息的列表
        """
        portfolios = []
        
        for j in range(self.n):
            weights = np.zeros(self.n)
            weights[j] = 1.0
            
            expected_return = self.expected_returns[j]
            mad_risk = self.data_processor.calculate_mad_risk(weights)
            
            portfolios.append({
                'asset': self.asset_names[j],
                'weights': weights,
                'expected_return': expected_return,
                'mad_risk': mad_risk
            })
        
        return portfolios


if __name__ == "__main__":
    # 测试代码
    import sys
    sys.path.append('..')
    from src.data_processor import DataProcessor
    
    # 加载数据
    data_path = "../data/returns_data.csv"
    processor = DataProcessor(data_path)
    
    # 创建优化器
    optimizer = MADOptimizer(processor)
    
    # 测试单个μ值
    print("\n" + "="*60)
    print("测试 μ = 10 的优化结果:")
    print("="*60)
    result = optimizer.optimize(mu=10, verbose=True)
    
    # 测试有效前沿
    print("\n" + "="*60)
    print("测试有效前沿计算:")
    print("="*60)
    mu_values = [0.5, 1, 2, 5, 10, 20, 50, 100]
    results = optimizer.optimize_efficient_frontier(mu_values, verbose=False)
    
    print("\n有效前沿结果汇总:")
    print(f"{'μ':>8} {'期望收益':>12} {'MAD风险':>12} {'目标值':>12}")
    print("-" * 50)
    for r in results:
        print(f"{r['mu']:8.2f} {r['expected_return']:12.6f} {r['mad_risk']:12.6f} {r['objective_value']:12.6f}")

