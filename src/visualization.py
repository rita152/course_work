"""
可视化模块
功能：生成各种图表来展示优化结果和分析
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

# 设置字体和显示参数
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300  # 统一设置为300 DPI
plt.rcParams['savefig.dpi'] = 300  # 保存时也使用300 DPI

# 设置seaborn样式
sns.set_style("whitegrid")
sns.set_palette("husl")


class Visualizer:
    """投资组合优化结果可视化器"""
    
    def __init__(self, output_dir="../results"):
        """
        初始化可视化器
        
        参数:
            output_dir: 图表输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def plot_efficient_frontier(self, mad_results, variance_results=None, 
                               single_assets_mad=None, single_assets_var=None,
                               save_name="efficient_frontier.png"):
        """
        绘制有效前沿图
        
        参数:
            mad_results: MAD模型优化结果列表
            variance_results: 方差模型优化结果列表（可选）
            single_assets_mad: 单资产组合MAD风险-收益点（可选）
            single_assets_var: 单资产组合方差风险-收益点（可选）
            save_name: 保存文件名
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制MAD模型有效前沿
        mad_risks = [r['mad_risk'] for r in mad_results]
        mad_returns = [r['expected_return'] for r in mad_results]
        ax.plot(mad_risks, mad_returns, 'b-o', linewidth=2, markersize=6, 
                label='MAD Model Efficient Frontier', alpha=0.8)
        
        # 绘制方差模型有效前沿
        if variance_results:
            var_stds = [r['std_dev'] for r in variance_results]
            var_returns = [r['expected_return'] for r in variance_results]
            ax.plot(var_stds, var_returns, 'r-s', linewidth=2, markersize=6,
                    label='Variance Model Efficient Frontier', alpha=0.8)
        
        # 绘制单资产组合点
        if single_assets_mad:
            single_mad_risks = [p['mad_risk'] for p in single_assets_mad]
            single_returns = [p['expected_return'] for p in single_assets_mad]
            ax.scatter(single_mad_risks, single_returns, c='green', s=100, 
                      marker='*', label='Single Asset Portfolios', zorder=5, alpha=0.7)
            
            # 标注资产名称
            for p in single_assets_mad:
                ax.annotate(p['asset'], 
                           (p['mad_risk'], p['expected_return']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.7)
        
        ax.set_xlabel('Risk (MAD / Std Dev)', fontsize=12)
        ax.set_ylabel('Expected Return', fontsize=12)
        ax.set_title('Efficient Frontier of Portfolio Optimization', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存: {save_name}")
    
    def plot_portfolio_composition(self, results, asset_names, 
                                  save_name="portfolio_composition.png"):
        """
        绘制不同μ值下的投资组合配置（堆叠柱状图）
        
        参数:
            results: 优化结果列表
            asset_names: 资产名称列表
            save_name: 保存文件名
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 准备数据
        mu_values = [r['mu'] for r in results]
        weights_matrix = np.array([r['weights'] for r in results])
        
        # 创建堆叠柱状图
        x = np.arange(len(mu_values))
        width = 0.8
        
        bottom = np.zeros(len(mu_values))
        colors = plt.cm.Set3(np.linspace(0, 1, len(asset_names)))
        
        for i, asset in enumerate(asset_names):
            values = weights_matrix[:, i] * 100  # 转换为百分比
            ax.bar(x, values, width, bottom=bottom, label=asset, 
                   color=colors[i], alpha=0.8)
            bottom += values
        
        ax.set_xlabel('Risk Aversion Parameter μ', fontsize=12)
        ax.set_ylabel('Allocation (%)', fontsize=12)
        ax.set_title('Portfolio Composition for Different μ Values', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{mu:.2f}' for mu in mu_values], rotation=45)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存: {save_name}")
    
    def plot_mu_sensitivity(self, results, save_name="mu_sensitivity.png"):
        """
        绘制μ参数敏感性分析图
        
        参数:
            results: 优化结果列表
            save_name: 保存文件名
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        mu_values = [r['mu'] for r in results]
        returns = [r['expected_return'] for r in results]
        risks = [r['mad_risk'] for r in results]
        objectives = [r['objective_value'] for r in results]
        
        # 子图1: μ vs 期望收益
        axes[0, 0].semilogx(mu_values, returns, 'b-o', linewidth=2, markersize=6)
        axes[0, 0].set_xlabel('μ (log scale)', fontsize=11)
        axes[0, 0].set_ylabel('Expected Return', fontsize=11)
        axes[0, 0].set_title('Impact of μ on Expected Return', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 子图2: μ vs MAD风险
        axes[0, 1].semilogx(mu_values, risks, 'r-s', linewidth=2, markersize=6)
        axes[0, 1].set_xlabel('μ (log scale)', fontsize=11)
        axes[0, 1].set_ylabel('MAD Risk', fontsize=11)
        axes[0, 1].set_title('Impact of μ on Risk', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 子图3: μ vs 目标函数值
        axes[1, 0].semilogx(mu_values, objectives, 'g-^', linewidth=2, markersize=6)
        axes[1, 0].set_xlabel('μ (log scale)', fontsize=11)
        axes[1, 0].set_ylabel('Objective Value', fontsize=11)
        axes[1, 0].set_title('Impact of μ on Objective', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 子图4: 风险-收益权衡比
        risk_return_ratio = [ret / max(risk, 1e-6) for ret, risk in zip(returns, risks)]
        axes[1, 1].semilogx(mu_values, risk_return_ratio, 'm-d', linewidth=2, markersize=6)
        axes[1, 1].set_xlabel('μ (log scale)', fontsize=11)
        axes[1, 1].set_ylabel('Return/Risk Ratio', fontsize=11)
        axes[1, 1].set_title('Impact of μ on Return-Risk Ratio', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存: {save_name}")
    
    def plot_portfolio_pie(self, weights, asset_names, mu_value,
                          save_name="portfolio_pie.png"):
        """
        绘制特定μ值下的投资组合配置饼图
        
        参数:
            weights: 投资权重向量
            asset_names: 资产名称列表
            mu_value: μ值
            save_name: 保存文件名
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 只显示权重大于1%的资产
        threshold = 0.01
        filtered_weights = []
        filtered_names = []
        other_weight = 0
        
        for w, name in zip(weights, asset_names):
            if w >= threshold:
                filtered_weights.append(w)
                filtered_names.append(f'{name}\n({w*100:.1f}%)')
            else:
                other_weight += w
        
        if other_weight >= 0.001:
            filtered_weights.append(other_weight)
            filtered_names.append(f'Others\n({other_weight*100:.1f}%)')
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(filtered_weights)))
        
        wedges, texts, autotexts = ax.pie(filtered_weights, labels=filtered_names,
                                          autopct='%1.1f%%', startangle=90,
                                          colors=colors, textprops={'fontsize': 10})
        
        ax.set_title(f'Portfolio Allocation (μ = {mu_value})', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存: {save_name}")
    
    def plot_correlation_heatmap(self, corr_matrix, asset_names,
                                save_name="correlation_heatmap.png"):
        """
        绘制资产相关系数热力图
        
        参数:
            corr_matrix: 相关系数矩阵
            asset_names: 资产名称列表
            save_name: 保存文件名
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1,
                   xticklabels=asset_names, yticklabels=asset_names,
                   cbar_kws={"shrink": 0.8}, ax=ax)
        
        ax.set_title('Asset Return Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存: {save_name}")
    
    def plot_model_comparison(self, mad_results, variance_results,
                            save_name="model_comparison.png"):
        """
        绘制MAD模型与方差模型的对比图
        
        参数:
            mad_results: MAD模型结果列表
            variance_results: 方差模型结果列表
            save_name: 保存文件名
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 子图1: 有效前沿对比
        mad_risks = [r['mad_risk'] for r in mad_results]
        mad_returns = [r['expected_return'] for r in mad_results]
        var_stds = [r['std_dev'] for r in variance_results]
        var_returns = [r['expected_return'] for r in variance_results]
        
        axes[0].plot(mad_risks, mad_returns, 'b-o', linewidth=2, 
                    markersize=5, label='MAD Model', alpha=0.8)
        axes[0].plot(var_stds, var_returns, 'r-s', linewidth=2,
                    markersize=5, label='Variance Model', alpha=0.8)
        axes[0].set_xlabel('Risk Measure', fontsize=11)
        axes[0].set_ylabel('Expected Return', fontsize=11)
        axes[0].set_title('Efficient Frontier Comparison', fontsize=12, fontweight='bold')
        axes[0].legend(fontsize=10)
        axes[0].grid(True, alpha=0.3)
        
        # 子图2: 求解时间对比
        mu_values = [r['mu'] for r in mad_results]
        mad_times = [r['solve_time'] for r in mad_results]
        var_times = [r['solve_time'] for r in variance_results]
        
        x = np.arange(len(mu_values))
        width = 0.35
        
        axes[1].bar(x - width/2, mad_times, width, label='MAD Model', alpha=0.8)
        axes[1].bar(x + width/2, var_times, width, label='Variance Model', alpha=0.8)
        axes[1].set_xlabel('μ Value Index', fontsize=11)
        axes[1].set_ylabel('Solve Time (seconds)', fontsize=11)
        axes[1].set_title('Computational Efficiency Comparison', fontsize=12, fontweight='bold')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels([f'{mu:.1f}' for mu in mu_values], rotation=45)
        axes[1].legend(fontsize=10)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"已保存: {save_name}")
    
    def create_results_summary(self, results, asset_names, 
                              save_name="results_summary.csv"):
        """
        创建结果汇总表格并保存为CSV
        
        参数:
            results: 优化结果列表
            asset_names: 资产名称列表
            save_name: 保存文件名
        """
        data = []
        for r in results:
            row = {
                'μ': r['mu'],
                '期望收益': r['expected_return'],
                'MAD风险': r.get('mad_risk', r.get('std_dev', 0)),
                '目标函数值': r['objective_value'],
                '求解时间': r['solve_time']
            }
            # 添加各资产权重
            for i, name in enumerate(asset_names):
                row[name] = r['weights'][i]
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(self.output_dir / save_name, index=False, encoding='utf-8-sig')
        print(f"已保存: {save_name}")
        return df


if __name__ == "__main__":
    # 测试代码
    print("可视化模块已加载")

