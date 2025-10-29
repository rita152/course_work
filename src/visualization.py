"""
可视化模块
生成投资组合分析的各种图表
"""

# 首先导入warnings并过滤matplotlib的字体警告
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# 设置中文字体（macOS系统）
# 使用系统中实际存在的中文字体
plt.rcParams['font.sans-serif'] = ['STHeiti', 'Songti SC', 'Kaiti SC', 'Heiti TC', 'SimSong']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置绘图风格
sns.set_style("whitegrid")
sns.set_palette("husl")


class PortfolioVisualizer:
    """投资组合可视化类"""
    
    def __init__(self, results_df, asset_names, output_dir='../results/figures'):
        """
        初始化可视化器
        
        参数:
            results_df: 参数化求解结果DataFrame
            asset_names: 资产名称列表
            output_dir: 图表输出目录
        """
        self.results = results_df
        self.asset_names = asset_names
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"可视化器初始化完成，输出目录: {output_dir}")
    
    def plot_efficient_frontier(self, benchmarks=None, save=True):
        """
        Plot efficient frontier
        
        Parameters:
            benchmarks: benchmark strategies dictionary
            save: whether to save the plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot efficient frontier
        ax.plot(self.results['risk_mad'], self.results['expected_return'], 
                'b-o', linewidth=2, markersize=4, label='Efficient Frontier', alpha=0.7)
        
        # Mark minimum risk and maximum return points
        min_risk_idx = self.results['risk_mad'].idxmin()
        max_return_idx = self.results['expected_return'].idxmax()
        
        ax.plot(self.results.loc[min_risk_idx, 'risk_mad'],
                self.results.loc[min_risk_idx, 'expected_return'],
                'g*', markersize=15, label='Min Risk Portfolio')
        
        ax.plot(self.results.loc[max_return_idx, 'risk_mad'],
                self.results.loc[max_return_idx, 'expected_return'],
                'r*', markersize=15, label='Max Return Portfolio')
        
        # Plot benchmark strategies
        if benchmarks:
            colors = {'equal_weight': 'orange', 'max_return': 'red', 'min_risk': 'green'}
            markers = {'equal_weight': 's', 'max_return': '^', 'min_risk': 'D'}
            labels = {'equal_weight': 'Equal Weight', 'max_return': 'Max Return Asset', 'min_risk': 'Min Risk'}
            
            for key, benchmark in benchmarks.items():
                if key in colors:
                    ax.plot(benchmark['risk_mad'], benchmark['expected_return'],
                            markers[key], color=colors[key], markersize=12,
                            label=labels.get(key, benchmark.get('name', key)), alpha=0.8)
        
        ax.set_xlabel('Risk (MAD)', fontsize=12)
        ax.set_ylabel('Expected Return', fontsize=12)
        ax.set_title('Portfolio Efficient Frontier', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'efficient_frontier.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Efficient frontier plot saved: {filepath}")
        
        return fig, ax
    
    def plot_weights_evolution(self, save=True):
        """
        Plot portfolio weights evolution with different mu values
        
        Parameters:
            save: whether to save the plot
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Extract weight columns
        weight_cols = [col for col in self.results.columns if col.startswith('weight_')]
        weights_data = self.results[weight_cols].values.T
        
        # Create stacked area plot
        mu_values = self.results['mu'].values
        
        ax.stackplot(mu_values, weights_data, 
                     labels=self.asset_names, alpha=0.8)
        
        ax.set_xlabel('Risk Aversion Parameter (mu)', fontsize=12)
        ax.set_ylabel('Portfolio Weight', fontsize=12)
        ax.set_title('Asset Allocation Weights vs Risk Aversion Parameter', fontsize=14, fontweight='bold')
        ax.set_xscale('log')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 1])
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'weights_evolution.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Weights evolution plot saved: {filepath}")
        
        return fig, ax
    
    def plot_mu_sensitivity(self, save=True):
        """
        Plot parameter mu sensitivity analysis
        
        Parameters:
            save: whether to save the plot
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
        
        mu_values = self.results['mu'].values
        
        # 1. Expected return vs mu
        ax1.plot(mu_values, self.results['expected_return'], 'b-o', linewidth=2, markersize=4)
        ax1.set_ylabel('Expected Return', fontsize=11)
        ax1.set_title('Impact of Risk Aversion Parameter (mu) on Return and Risk', fontsize=14, fontweight='bold')
        ax1.set_xscale('log')
        ax1.grid(True, alpha=0.3)
        
        # 2. Risk vs mu
        ax2.plot(mu_values, self.results['risk_mad'], 'r-o', linewidth=2, markersize=4)
        ax2.set_ylabel('Risk (MAD)', fontsize=11)
        ax2.set_xscale('log')
        ax2.grid(True, alpha=0.3)
        
        # 3. Objective function value vs mu
        ax3.plot(mu_values, self.results['objective_value'], 'g-o', linewidth=2, markersize=4)
        ax3.set_xlabel('Risk Aversion Parameter (mu)', fontsize=12)
        ax3.set_ylabel('Objective Value', fontsize=11)
        ax3.set_xscale('log')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'mu_sensitivity.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Mu sensitivity plot saved: {filepath}")
        
        return fig, (ax1, ax2, ax3)
    
    def plot_strategy_comparison(self, benchmarks, save=True):
        """
        Plot strategy comparison
        
        Parameters:
            benchmarks: benchmark strategies dictionary
            save: whether to save the plot
        """
        # Select representative optimized portfolios
        idx_min_risk = self.results['risk_mad'].idxmin()
        idx_max_return = self.results['expected_return'].idxmax()
        idx_balanced = (self.results['mu'] - 1.0).abs().idxmin()  # Balanced portfolio with mu~1
        
        strategies = {
            'Min Risk Optimized': {
                'return': self.results.loc[idx_min_risk, 'expected_return'],
                'risk': self.results.loc[idx_min_risk, 'risk_mad']
            },
            'Balanced Optimized': {
                'return': self.results.loc[idx_balanced, 'expected_return'],
                'risk': self.results.loc[idx_balanced, 'risk_mad']
            },
            'Max Return Optimized': {
                'return': self.results.loc[idx_max_return, 'expected_return'],
                'risk': self.results.loc[idx_max_return, 'risk_mad']
            }
        }
        
        # Add benchmark strategies
        bench_labels = {'equal_weight': 'Equal Weight', 'max_return': 'Single Best Asset', 'min_risk': 'Min Risk Benchmark'}
        for key, benchmark in benchmarks.items():
            label = bench_labels.get(key, benchmark.get('name', key))
            strategies[label] = {
                'return': benchmark['expected_return'],
                'risk': benchmark['risk_mad']
            }
        
        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 1. Return comparison
        strategy_names = list(strategies.keys())
        returns = [strategies[s]['return'] for s in strategy_names]
        
        bars1 = ax1.barh(strategy_names, returns, color=sns.color_palette("husl", len(strategies)))
        ax1.set_xlabel('Expected Return', fontsize=11)
        ax1.set_title('Expected Return Comparison Across Strategies', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{width:.5f}', ha='left', va='center', fontsize=9)
        
        # 2. Risk comparison
        risks = [strategies[s]['risk'] for s in strategy_names]
        
        bars2 = ax2.barh(strategy_names, risks, color=sns.color_palette("husl", len(strategies)))
        ax2.set_xlabel('Risk (MAD)', fontsize=11)
        ax2.set_title('Risk Comparison Across Strategies', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{width:.5f}', ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'strategy_comparison.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Strategy comparison plot saved: {filepath}")
        
        return fig, (ax1, ax2)
    
    def plot_weight_heatmap(self, n_portfolios=15, save=True):
        """
        Plot asset allocation weights heatmap
        
        Parameters:
            n_portfolios: number of portfolios to display
            save: whether to save the plot
        """
        # Select evenly distributed portfolios
        indices = np.linspace(0, len(self.results)-1, n_portfolios, dtype=int)
        selected_results = self.results.iloc[indices]
        
        # Extract weight data
        weight_cols = [col for col in self.results.columns if col.startswith('weight_')]
        weights_matrix = selected_results[weight_cols].values
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(weights_matrix.T, aspect='auto', cmap='YlOrRd')
        
        # Set axis labels
        ax.set_xticks(range(len(selected_results)))
        ax.set_xticklabels([f"mu={mu:.2f}" for mu in selected_results['mu']], 
                          rotation=45, ha='right', fontsize=9)
        ax.set_yticks(range(len(self.asset_names)))
        ax.set_yticklabels(self.asset_names, fontsize=10)
        
        ax.set_xlabel('Risk Aversion Parameter (mu)', fontsize=11)
        ax.set_ylabel('Asset', fontsize=11)
        ax.set_title('Asset Allocation Heatmap for Different Risk Aversion Levels', fontsize=13, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Portfolio Weight', fontsize=10)
        
        # Add values in cells
        for i in range(len(selected_results)):
            for j in range(len(self.asset_names)):
                text = ax.text(i, j, f'{weights_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, 'weight_heatmap.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Weight heatmap saved: {filepath}")
        
        return fig, ax
    
    def plot_all(self, benchmarks=None):
        """
        Generate all plots
        
        Parameters:
            benchmarks: benchmark strategies dictionary
        """
        print("\nGenerating all plots...")
        print("="*60)
        
        self.plot_efficient_frontier(benchmarks=benchmarks)
        self.plot_weights_evolution()
        self.plot_mu_sensitivity()
        
        if benchmarks:
            self.plot_strategy_comparison(benchmarks)
        
        self.plot_weight_heatmap()
        
        print("="*60)
        print("All plots generated successfully!")
        
        plt.close('all')


if __name__ == '__main__':
    # 测试代码
    print("可视化模块测试")
    print("="*60)
    
    # 创建示例数据
    np.random.seed(42)
    n = 20
    
    results_data = {
        'mu': np.logspace(-1, 1, n),
        'expected_return': np.linspace(1.001, 1.010, n),
        'risk_mad': np.linspace(0.02, 0.01, n),
        'objective_value': np.random.rand(n)
    }
    
    assets = ['SHY', 'XLB', 'XLE']
    for asset in assets:
        results_data[f'weight_{asset}'] = np.random.dirichlet(np.ones(len(assets)), n)[:, assets.index(asset)]
    
    results_df = pd.DataFrame(results_data)
    
    # 创建可视化器
    viz = PortfolioVisualizer(results_df, assets, output_dir='../results/test_figures')
    
    # 测试各个图表
    viz.plot_efficient_frontier()
    viz.plot_weights_evolution()
    viz.plot_mu_sensitivity()
    
    print("\n测试完成！")

