"""
投资组合优化主程序
基于线性规划的Portfolio Selection问题建模、求解与分析
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import DataFetcher
from portfolio_model import PortfolioOptimizer
from visualization import PortfolioVisualizer


def main():
    """主函数"""
    
    print("="*80)
    print(" " * 25 + "投资组合优化系统")
    print(" " * 15 + "Portfolio Selection using Linear Programming")
    print("="*80)
    print()
    
    # ==================== 第一步：数据获取 ====================
    print("\n" + "="*80)
    print("第一步：数据获取")
    print("="*80)
    
    # 检查是否已有数据
    price_file = 'data/raw/price_data.csv'
    returns_file = 'data/processed/monthly_returns.csv'
    
    fetcher = DataFetcher(delay=2.5)  # 设置延时2.5秒
    
    if os.path.exists(returns_file):
        print(f"\n检测到已有数据文件: {returns_file}")
        choice = input("是否重新获取数据？(y/n，默认n): ").strip().lower()
        
        if choice == 'y':
            print("\n重新获取数据...")
            price_data = fetcher.fetch_data(save_path=price_file)
            returns_data = fetcher.calculate_monthly_returns(save_path=returns_file)
        else:
            print("\n加载已有数据...")
            price_data, returns_data = fetcher.load_data(price_file, returns_file)
    else:
        print("\n首次运行，开始获取数据...")
        price_data = fetcher.fetch_data(save_path=price_file)
        returns_data = fetcher.calculate_monthly_returns(save_path=returns_file)
    
    # 显示数据摘要
    print("\n" + "-"*80)
    print("数据摘要统计:")
    print("-"*80)
    summary = fetcher.get_summary_statistics()
    print(summary.to_string())
    
    # ==================== 第二步：模型构建与求解 ====================
    print("\n" + "="*80)
    print("第二步：投资组合优化模型构建与求解")
    print("="*80)
    
    # 创建优化器
    optimizer = PortfolioOptimizer(returns_data)
    
    # 参数化求解
    print("\n开始参数化求解...")
    mu_values = np.logspace(-1, 1.5, 100)  # 从0.1到31.6，100个点（更精细的有效前沿）
    results_df = optimizer.solve_parametric(mu_values=mu_values, verbose=True)
    
    # 保存求解结果
    results_file = 'results/analysis/optimization_results.csv'
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    results_df.to_csv(results_file, index=False)
    print(f"\n求解结果已保存至: {results_file}")
    
    # 显示部分结果
    print("\n" + "-"*80)
    print("部分优化结果展示:")
    print("-"*80)
    display_cols = ['mu', 'expected_return', 'risk_mad', 'objective_value']
    print(results_df[display_cols].head(10).to_string(index=False))
    print("...")
    print(results_df[display_cols].tail(5).to_string(index=False))
    
    # ==================== 第三步：基准策略计算 ====================
    print("\n" + "="*80)
    print("第三步：基准策略计算")
    print("="*80)
    
    benchmarks = optimizer.get_benchmark_strategies()
    
    print("\n基准策略结果:")
    print("-"*80)
    for key, benchmark in benchmarks.items():
        print(f"\n{benchmark['name']}:")
        if 'asset' in benchmark:
            print(f"  选择资产: {benchmark['asset']}")
        print(f"  期望收益: {benchmark['expected_return']:.6f}")
        print(f"  风险(MAD): {benchmark['risk_mad']:.6f}")
        print(f"  配置权重: {dict(zip(optimizer.asset_names, benchmark['weights']))}")
    
    # ==================== 第四步：策略对比分析 ====================
    print("\n" + "="*80)
    print("第四步：策略对比分析")
    print("="*80)
    
    # 选择几个代表性的优化组合进行对比
    idx_min_risk = results_df['risk_mad'].idxmin()
    idx_max_return = results_df['expected_return'].idxmax()
    idx_balanced = (results_df['mu'] - 1.0).abs().idxmin()
    
    print("\n代表性优化组合:")
    print("-"*80)
    
    print(f"\n1. 最小风险优化组合 (μ = {results_df.loc[idx_min_risk, 'mu']:.4f}):")
    print(f"   期望收益: {results_df.loc[idx_min_risk, 'expected_return']:.6f}")
    print(f"   风险(MAD): {results_df.loc[idx_min_risk, 'risk_mad']:.6f}")
    
    print(f"\n2. 平衡优化组合 (μ = {results_df.loc[idx_balanced, 'mu']:.4f}):")
    print(f"   期望收益: {results_df.loc[idx_balanced, 'expected_return']:.6f}")
    print(f"   风险(MAD): {results_df.loc[idx_balanced, 'risk_mad']:.6f}")
    
    print(f"\n3. 最大收益优化组合 (μ = {results_df.loc[idx_max_return, 'mu']:.4f}):")
    print(f"   期望收益: {results_df.loc[idx_max_return, 'expected_return']:.6f}")
    print(f"   风险(MAD): {results_df.loc[idx_max_return, 'risk_mad']:.6f}")
    
    # 计算夏普比率
    print("\n夏普比率对比 (风险调整收益):")
    print("-"*80)
    
    strategies_for_sharpe = {
        '最小风险优化': results_df.loc[idx_min_risk],
        '平衡优化': results_df.loc[idx_balanced],
        '最大收益优化': results_df.loc[idx_max_return],
        '等权重策略': benchmarks['equal_weight'],
        '最高收益资产': benchmarks['max_return']
    }
    
    for name, strategy in strategies_for_sharpe.items():
        if isinstance(strategy, pd.Series):
            # 从results_df中提取权重
            weight_cols = [col for col in results_df.columns if col.startswith('weight_')]
            weights = strategy[weight_cols].values
        else:
            weights = strategy['weights']
        
        sharpe = optimizer.calculate_sharpe_ratio(weights)
        risk = optimizer._calculate_mad_risk(weights)
        ret = np.dot(weights, optimizer.mean_returns)
        
        print(f"{name:20s}: 收益={ret:.6f}, 风险={risk:.6f}, 夏普比率={sharpe:.4f}")
    
    # ==================== 第五步：可视化分析 ====================
    print("\n" + "="*80)
    print("第五步：生成可视化图表")
    print("="*80)
    
    visualizer = PortfolioVisualizer(
        results_df, 
        optimizer.asset_names,
        output_dir='results/figures'
    )
    
    visualizer.plot_all(benchmarks=benchmarks)
    
    # ==================== 第六步：生成分析报告 ====================
    print("\n" + "="*80)
    print("第六步：生成分析报告")
    print("="*80)
    
    report = generate_report(
        returns_data, 
        results_df, 
        benchmarks, 
        optimizer,
        summary
    )
    
    report_file = 'results/analysis/analysis_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n分析报告已保存至: {report_file}")
    
    # ==================== 完成 ====================
    print("\n" + "="*80)
    print(" " * 30 + "分析完成！")
    print("="*80)
    print("\n生成的文件:")
    print(f"  1. 价格数据: {price_file}")
    print(f"  2. 收益率数据: {returns_file}")
    print(f"  3. 优化结果: {results_file}")
    print(f"  4. 分析报告: {report_file}")
    print(f"  5. 可视化图表: results/figures/")
    print("\n请查看 results/ 目录获取所有结果。")
    print("="*80)


def generate_report(returns_data, results_df, benchmarks, optimizer, summary):
    """生成分析报告"""
    
    report = []
    report.append("="*80)
    report.append("投资组合优化分析报告")
    report.append("Portfolio Selection Optimization Analysis Report")
    report.append("="*80)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n" + "="*80)
    
    # 1. 数据概况
    report.append("\n一、数据概况")
    report.append("-"*80)
    report.append(f"资产数量: {len(optimizer.asset_names)}")
    report.append(f"资产列表: {', '.join(optimizer.asset_names)}")
    report.append(f"数据期数: {len(returns_data)} 个月")
    report.append(f"数据时间范围: {returns_data.index[0].date()} 至 {returns_data.index[-1].date()}")
    
    report.append("\n各资产统计信息:")
    report.append(summary.to_string())
    
    # 2. 模型说明
    report.append(f"\n\n二、优化模型")
    report.append("-"*80)
    report.append("基于Mean Absolute Deviation (MAD)的线性规划模型:")
    report.append("\n目标函数:")
    report.append("  maximize: μ * Σ(x_j * r_j) - (1/T) * Σ(y_t)")
    report.append("\n约束条件:")
    report.append("  -y_t ≤ Σ(x_j * (R_j(t) - r_j)) ≤ y_t,  for t=1,...,T")
    report.append("  Σ(x_j) = 1")
    report.append("  x_j ≥ 0,  for j=1,...,n")
    report.append("  y_t ≥ 0,  for t=1,...,T")
    report.append("\n其中:")
    report.append("  x_j: 资产j的配置比例")
    report.append("  r_j: 资产j的期望收益")
    report.append("  y_t: 第t期的绝对偏差")
    report.append("  μ: 风险厌恶参数（收益权重）")
    
    # 3. 优化结果
    report.append(f"\n\n三、参数化优化结果")
    report.append("-"*80)
    report.append(f"求解的μ值范围: {results_df['mu'].min():.4f} ~ {results_df['mu'].max():.4f}")
    report.append(f"求解的组合数量: {len(results_df)}")
    report.append(f"\n期望收益范围: {results_df['expected_return'].min():.6f} ~ {results_df['expected_return'].max():.6f}")
    report.append(f"风险(MAD)范围: {results_df['risk_mad'].min():.6f} ~ {results_df['risk_mad'].max():.6f}")
    
    # 4. 关键组合
    idx_min_risk = results_df['risk_mad'].idxmin()
    idx_max_return = results_df['expected_return'].idxmax()
    idx_balanced = (results_df['mu'] - 1.0).abs().idxmin()
    
    report.append(f"\n\n四、关键投资组合")
    report.append("-"*80)
    
    report.append(f"\n1. 最小风险组合 (μ = {results_df.loc[idx_min_risk, 'mu']:.4f}):")
    report.append(f"   期望收益: {results_df.loc[idx_min_risk, 'expected_return']:.6f}")
    report.append(f"   风险(MAD): {results_df.loc[idx_min_risk, 'risk_mad']:.6f}")
    weight_cols = [col for col in results_df.columns if col.startswith('weight_')]
    weights = results_df.loc[idx_min_risk, weight_cols].values
    report.append("   配置权重:")
    for i, asset in enumerate(optimizer.asset_names):
        if weights[i] > 0.001:
            report.append(f"     {asset}: {weights[i]:.4f} ({weights[i]*100:.2f}%)")
    
    report.append(f"\n2. 平衡组合 (μ ≈ 1.0, 实际 μ = {results_df.loc[idx_balanced, 'mu']:.4f}):")
    report.append(f"   期望收益: {results_df.loc[idx_balanced, 'expected_return']:.6f}")
    report.append(f"   风险(MAD): {results_df.loc[idx_balanced, 'risk_mad']:.6f}")
    weights = results_df.loc[idx_balanced, weight_cols].values
    report.append("   配置权重:")
    for i, asset in enumerate(optimizer.asset_names):
        if weights[i] > 0.001:
            report.append(f"     {asset}: {weights[i]:.4f} ({weights[i]*100:.2f}%)")
    
    report.append(f"\n3. 最大收益组合 (μ = {results_df.loc[idx_max_return, 'mu']:.4f}):")
    report.append(f"   期望收益: {results_df.loc[idx_max_return, 'expected_return']:.6f}")
    report.append(f"   风险(MAD): {results_df.loc[idx_max_return, 'risk_mad']:.6f}")
    weights = results_df.loc[idx_max_return, weight_cols].values
    report.append("   配置权重:")
    for i, asset in enumerate(optimizer.asset_names):
        if weights[i] > 0.001:
            report.append(f"     {asset}: {weights[i]:.4f} ({weights[i]*100:.2f}%)")
    
    # 5. 基准策略对比
    report.append(f"\n\n五、基准策略对比")
    report.append("-"*80)
    
    for key, benchmark in benchmarks.items():
        report.append(f"\n{benchmark['name']}:")
        if 'asset' in benchmark:
            report.append(f"  选择资产: {benchmark['asset']}")
        report.append(f"  期望收益: {benchmark['expected_return']:.6f}")
        report.append(f"  风险(MAD): {benchmark['risk_mad']:.6f}")
        sharpe = optimizer.calculate_sharpe_ratio(benchmark['weights'])
        report.append(f"  夏普比率: {sharpe:.4f}")
    
    # 6. 主要发现
    report.append(f"\n\n六、主要发现与结论")
    report.append("-"*80)
    
    # 找出最高夏普比率的组合
    sharpe_ratios = []
    for idx in results_df.index:
        weights = results_df.loc[idx, weight_cols].values
        sharpe = optimizer.calculate_sharpe_ratio(weights)
        sharpe_ratios.append(sharpe)
    
    best_sharpe_idx = np.argmax(sharpe_ratios)
    
    report.append(f"\n1. 有效前沿特征:")
    report.append(f"   - 通过改变风险厌恶参数μ，可以生成从低风险低收益到高风险高收益的投资组合")
    report.append(f"   - 最优夏普比率组合 (μ = {results_df.loc[best_sharpe_idx, 'mu']:.4f}):")
    report.append(f"     收益 = {results_df.loc[best_sharpe_idx, 'expected_return']:.6f}")
    report.append(f"     风险 = {results_df.loc[best_sharpe_idx, 'risk_mad']:.6f}")
    report.append(f"     夏普比率 = {sharpe_ratios[best_sharpe_idx]:.4f}")
    
    report.append(f"\n2. 多元化效应:")
    report.append(f"   - 优化后的投资组合通过分散化降低了风险")
    report.append(f"   - 相比单一资产策略，优化组合在相同收益水平下风险更低")
    
    report.append(f"\n3. 参数μ的影响:")
    report.append(f"   - μ → 0: 模型侧重于最小化风险，忽略收益")
    report.append(f"   - μ → ∞: 模型侧重于最大化收益，忽略风险")
    report.append(f"   - μ ≈ 1: 在风险和收益之间取得平衡")
    
    report.append(f"\n4. 实践建议:")
    report.append(f"   - 保守型投资者: 建议选择μ < 1的组合，优先控制风险")
    report.append(f"   - 激进型投资者: 建议选择μ > 5的组合，追求更高收益")
    report.append(f"   - 平衡型投资者: 建议选择μ ≈ 1-3的组合")
    
    report.append("\n" + "="*80)
    report.append("报告结束")
    report.append("="*80)
    
    return '\n'.join(report)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()

