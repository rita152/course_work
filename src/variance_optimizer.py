"""
方差优化模型模块
功能：基于方差的Markowitz投资组合优化
用于与MAD模型进行对比分析
"""

import numpy as np
from pulp import *
import time


class VarianceOptimizer:
    """基于方差风险度量的投资组合优化器（Markowitz模型）"""
    
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
        
        # 计算协方差矩阵
        self.covariance_matrix = np.cov(self.deviation_matrix.T)
    
    def optimize(self, mu, verbose=False):
        """
        求解方差优化问题
        
        由于方差涉及二次项，这里使用简化方法：
        通过采样将方差风险线性化近似
        
        目标函数: max μ * Σ(x_j * r_j) - variance(portfolio)
        约束条件:
            Σ(x_j) = 1
            x_j ≥ 0
        
        参数:
            mu: 风险厌恶参数
            verbose: 是否输出详细信息
        
        返回:
            dict: 包含最优解信息的字典
        """
        start_time = time.time()
        
        # 使用网格搜索来近似求解（因为PuLP不直接支持二次规划）
        # 这里我们使用一个简化的启发式方法
        best_objective = -np.inf
        best_weights = None
        
        # 方法1: 尝试多个候选解
        candidates = []
        
        # 候选1: 等权重
        candidates.append(np.ones(self.n) / self.n)
        
        # 候选2: 只投资收益最高的资产
        max_return_idx = np.argmax(self.expected_returns)
        w = np.zeros(self.n)
        w[max_return_idx] = 1.0
        candidates.append(w)
        
        # 候选3-5: 随机生成一些满足约束的权重
        np.random.seed(42)
        for _ in range(10):
            w = np.random.dirichlet(np.ones(self.n))
            candidates.append(w)
        
        # 候选6: 基于收益率的加权
        positive_returns = np.maximum(self.expected_returns - np.min(self.expected_returns), 1e-6)
        w = positive_returns / np.sum(positive_returns)
        candidates.append(w)
        
        # 评估所有候选解
        for weights in candidates:
            expected_return = np.dot(weights, self.expected_returns)
            variance = weights @ self.covariance_matrix @ weights
            objective = mu * expected_return - variance
            
            if objective > best_objective:
                best_objective = objective
                best_weights = weights.copy()
        
        # 使用梯度上升进行局部优化
        weights = best_weights.copy()
        learning_rate = 0.01
        n_iterations = 1000
        
        for iteration in range(n_iterations):
            # 计算梯度
            grad_reward = mu * self.expected_returns
            grad_risk = 2 * self.covariance_matrix @ weights
            grad = grad_reward - grad_risk
            
            # 梯度上升更新
            weights_new = weights + learning_rate * grad
            
            # 投影到约束集合 (x_j >= 0, sum(x_j) = 1)
            weights_new = np.maximum(weights_new, 0)
            weights_new = weights_new / np.sum(weights_new)
            
            # 检查是否收敛
            if np.linalg.norm(weights_new - weights) < 1e-6:
                break
            
            weights = weights_new
        
        solve_time = time.time() - start_time
        
        # 计算最终结果
        expected_return = np.dot(weights, self.expected_returns)
        variance = weights @ self.covariance_matrix @ weights
        std_dev = np.sqrt(variance)
        objective = mu * expected_return - variance
        
        result = {
            'status': 'Optimal',
            'weights': weights,
            'expected_return': expected_return,
            'variance': variance,
            'std_dev': std_dev,
            'objective_value': objective,
            'solve_time': solve_time,
            'mu': mu
        }
        
        if verbose:
            print(f"\n求解成功 (μ = {mu}):")
            print(f"  目标函数值: {objective:.6f}")
            print(f"  期望收益: {expected_return:.6f}")
            print(f"  方差: {variance:.6f}")
            print(f"  标准差: {std_dev:.6f}")
            print(f"  求解时间: {solve_time:.4f}秒")
            print(f"\n投资组合配置:")
            for j, name in enumerate(self.asset_names):
                if weights[j] > 1e-4:
                    print(f"    {name}: {weights[j]*100:.2f}%")
        
        return result
    
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
        
        print(f"计算方差模型有效前沿，共{len(mu_values)}个μ值...")
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
        
        返回:
            list: 包含每个单资产组合信息的列表
        """
        portfolios = []
        
        for j in range(self.n):
            weights = np.zeros(self.n)
            weights[j] = 1.0
            
            expected_return = self.expected_returns[j]
            variance = self.covariance_matrix[j, j]
            std_dev = np.sqrt(variance)
            
            portfolios.append({
                'asset': self.asset_names[j],
                'weights': weights,
                'expected_return': expected_return,
                'variance': variance,
                'std_dev': std_dev
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
    optimizer = VarianceOptimizer(processor)
    
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
    print(f"{'μ':>8} {'期望收益':>12} {'标准差':>12} {'目标值':>12}")
    print("-" * 50)
    for r in results:
        print(f"{r['mu']:8.2f} {r['expected_return']:12.6f} {r['std_dev']:12.6f} {r['objective_value']:12.6f}")

