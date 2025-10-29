"""
投资组合模型模块
基于教材13.3节的线性规划模型实现
"""

import pandas as pd
import numpy as np
from pulp import *


class PortfolioOptimizer:
    """
    投资组合优化器
    基于MAD (Mean Absolute Deviation) 风险度量的线性规划模型
    """
    
    def __init__(self, returns_data):
        """
        初始化优化器
        
        参数:
            returns_data: 月度收益率DataFrame，行为时间，列为资产
        """
        self.returns = returns_data
        self.n_assets = len(returns_data.columns)  # 资产数量 n
        self.n_periods = len(returns_data)  # 时间期数 T
        self.asset_names = returns_data.columns.tolist()
        
        # 计算期望收益 r_j = (1/T) * sum(R_j(t))
        self.mean_returns = returns_data.mean().values
        
        # 计算偏差矩阵 D_tj = R_j(t) - r_j
        self.deviations = (returns_data - self.mean_returns).values
        
        print(f"投资组合优化器初始化完成")
        print(f"  资产数量: {self.n_assets}")
        print(f"  时间期数: {self.n_periods}")
        print(f"  资产列表: {', '.join(self.asset_names)}")
        
    def build_model(self, mu):
        """
        构建线性规划模型
        
        模型:
            maximize: μ * Σ(x_j * r_j) - (1/T) * Σ(y_t)
            
            subject to:
                -y_t ≤ Σ(x_j * D_tj) ≤ y_t,  for t=1,...,T
                Σ(x_j) = 1
                x_j ≥ 0,  for j=1,...,n
                y_t ≥ 0,  for t=1,...,T
        
        参数:
            mu: 风险厌恶参数（收益权重）
            
        返回:
            prob: PuLP问题对象
        """
        # 创建问题
        prob = LpProblem("Portfolio_Optimization", LpMaximize)
        
        # 决策变量
        # x_j: 资产j的配置比例
        x = [LpVariable(f"x_{j}", lowBound=0) for j in range(self.n_assets)]
        
        # y_t: 第t期的绝对偏差
        y = [LpVariable(f"y_{t}", lowBound=0) for t in range(self.n_periods)]
        
        # 目标函数: maximize μ * reward - risk
        # reward = Σ(x_j * r_j)
        reward = lpSum([x[j] * self.mean_returns[j] for j in range(self.n_assets)])
        
        # risk = (1/T) * Σ(y_t)
        risk = (1.0 / self.n_periods) * lpSum(y)
        
        prob += mu * reward - risk, "Objective"
        
        # 约束条件
        # 1. 配置比例之和为1
        prob += lpSum(x) == 1, "Budget_Constraint"
        
        # 2. 绝对偏差约束: -y_t ≤ Σ(x_j * D_tj) ≤ y_t
        for t in range(self.n_periods):
            deviation_t = lpSum([x[j] * self.deviations[t, j] for j in range(self.n_assets)])
            prob += deviation_t <= y[t], f"Upper_Deviation_{t}"
            prob += deviation_t >= -y[t], f"Lower_Deviation_{t}"
        
        return prob, x, y
    
    def solve(self, mu, verbose=False):
        """
        求解优化问题
        
        参数:
            mu: 风险厌恶参数
            verbose: 是否显示求解器输出
            
        返回:
            result: 包含最优解的字典
        """
        # 构建模型
        prob, x_vars, y_vars = self.build_model(mu)
        
        # 求解
        if verbose:
            prob.solve(PULP_CBC_CMD(msg=1))
        else:
            prob.solve(PULP_CBC_CMD(msg=0))
        
        # 检查求解状态
        if prob.status != 1:
            print(f"警告: 求解失败，状态码 {prob.status}")
            return None
        
        # 提取最优解
        optimal_weights = np.array([x_vars[j].varValue for j in range(self.n_assets)])
        optimal_y = np.array([y_vars[t].varValue for t in range(self.n_periods)])
        
        # 计算期望收益和风险
        expected_return = np.dot(optimal_weights, self.mean_returns)
        risk_mad = np.mean(optimal_y)
        
        # 计算目标函数值
        objective_value = mu * expected_return - risk_mad
        
        result = {
            'mu': mu,
            'weights': optimal_weights,
            'expected_return': expected_return,
            'risk_mad': risk_mad,
            'objective_value': objective_value,
            'status': LpStatus[prob.status]
        }
        
        return result
    
    def solve_parametric(self, mu_values=None, verbose=False):
        """
        参数化求解：对不同的μ值求解最优组合
        
        参数:
            mu_values: μ值列表，默认使用对数刻度
            verbose: 是否显示详细信息
            
        返回:
            results_df: 所有求解结果的DataFrame
        """
        if mu_values is None:
            # 使用对数刻度生成μ值
            mu_values = np.logspace(-1, 1.5, 100)  # 从0.1到约31.6，100个点
        
        print(f"\n开始参数化求解，共 {len(mu_values)} 个μ值...")
        
        results = []
        
        for i, mu in enumerate(mu_values, 1):
            if verbose or i % 5 == 0:
                print(f"[{i}/{len(mu_values)}] 求解 μ = {mu:.4f}...", end=' ')
            
            result = self.solve(mu, verbose=False)
            
            if result is not None:
                results.append(result)
                if verbose or i % 5 == 0:
                    print(f"收益 = {result['expected_return']:.6f}, 风险 = {result['risk_mad']:.6f}")
            else:
                if verbose or i % 5 == 0:
                    print("失败")
        
        print(f"\n参数化求解完成！成功求解 {len(results)} 个问题")
        
        # 整理结果
        results_df = self._organize_results(results)
        
        return results_df
    
    def _organize_results(self, results):
        """整理求解结果"""
        data = {
            'mu': [r['mu'] for r in results],
            'expected_return': [r['expected_return'] for r in results],
            'risk_mad': [r['risk_mad'] for r in results],
            'objective_value': [r['objective_value'] for r in results]
        }
        
        # 添加每个资产的配置权重
        for j, asset_name in enumerate(self.asset_names):
            data[f'weight_{asset_name}'] = [r['weights'][j] for r in results]
        
        df = pd.DataFrame(data)
        return df
    
    def get_benchmark_strategies(self):
        """
        计算基准策略
        
        返回:
            benchmarks: 包含各基准策略的字典
        """
        benchmarks = {}
        
        # 1. 等权重策略
        equal_weights = np.ones(self.n_assets) / self.n_assets
        equal_return = np.dot(equal_weights, self.mean_returns)
        equal_risk = self._calculate_mad_risk(equal_weights)
        
        benchmarks['equal_weight'] = {
            'name': '等权重策略',
            'weights': equal_weights,
            'expected_return': equal_return,
            'risk_mad': equal_risk
        }
        
        # 2. 最高收益资产策略
        max_return_idx = np.argmax(self.mean_returns)
        max_return_weights = np.zeros(self.n_assets)
        max_return_weights[max_return_idx] = 1.0
        max_return_return = self.mean_returns[max_return_idx]
        max_return_risk = self._calculate_mad_risk(max_return_weights)
        
        benchmarks['max_return'] = {
            'name': '最高收益资产',
            'asset': self.asset_names[max_return_idx],
            'weights': max_return_weights,
            'expected_return': max_return_return,
            'risk_mad': max_return_risk
        }
        
        # 3. 最小风险策略 (mu = 0)
        min_risk_result = self.solve(mu=0.0)
        if min_risk_result:
            benchmarks['min_risk'] = {
                'name': '最小风险策略',
                'weights': min_risk_result['weights'],
                'expected_return': min_risk_result['expected_return'],
                'risk_mad': min_risk_result['risk_mad']
            }
        
        return benchmarks
    
    def _calculate_mad_risk(self, weights):
        """计算给定权重的MAD风险"""
        portfolio_deviations = np.dot(self.deviations, weights)
        mad_risk = np.mean(np.abs(portfolio_deviations))
        return mad_risk
    
    def calculate_sharpe_ratio(self, weights, risk_free_rate=0.0):
        """
        计算夏普比率
        
        参数:
            weights: 投资组合权重
            risk_free_rate: 无风险利率（月度）
        """
        portfolio_return = np.dot(weights, self.mean_returns)
        portfolio_risk = self._calculate_mad_risk(weights)
        
        if portfolio_risk > 0:
            sharpe = (portfolio_return - risk_free_rate) / portfolio_risk
        else:
            sharpe = np.inf
        
        return sharpe


if __name__ == '__main__':
    # 测试代码
    print("投资组合模型测试")
    print("="*60)
    
    # 创建示例数据
    np.random.seed(42)
    dates = pd.date_range('2021-01-01', periods=24, freq='M')
    assets = ['Asset_A', 'Asset_B', 'Asset_C']
    
    # 生成随机收益率数据
    returns_data = pd.DataFrame(
        np.random.uniform(0.95, 1.05, (24, 3)),
        index=dates,
        columns=assets
    )
    
    # 创建优化器
    optimizer = PortfolioOptimizer(returns_data)
    
    # 测试单个μ值
    print("\n测试单个μ值求解:")
    result = optimizer.solve(mu=5.0, verbose=True)
    print(f"最优权重: {result['weights']}")
    print(f"期望收益: {result['expected_return']:.6f}")
    print(f"风险(MAD): {result['risk_mad']:.6f}")
    
    # 测试参数化求解
    print("\n测试参数化求解:")
    results_df = optimizer.solve_parametric(mu_values=[0.1, 1.0, 10.0])
    print(results_df)

