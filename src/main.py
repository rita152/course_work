"""
主程序
功能：集成所有模块，执行完整的投资组合优化分析
"""

import numpy as np
from pathlib import Path
import time

from data_processor import DataProcessor
from mad_optimizer import MADOptimizer
from variance_optimizer import VarianceOptimizer
from visualization import Visualizer


def main():
    """主函数"""
    print("="*70)
    print(" " * 15 + "投资组合优化系统")
    print(" " * 10 + "基于MAD风险度量的线性规划方法")
    print("="*70)
    
    # ========== 1. 数据加载与预处理 ==========
    print("\n" + "="*70)
    print("步骤 1: 数据加载与预处理")
    print("="*70)
    
    data_path = Path(__file__).parent.parent / "data" / "returns_data.csv"
    processor = DataProcessor(data_path)
    
    print("\n汇总统计信息:")
    print(processor.get_summary_statistics().to_string(index=False))
    
    # ========== 2. MAD模型优化 ==========
    print("\n" + "="*70)
    print("步骤 2: MAD模型优化")
    print("="*70)
    
    mad_optimizer = MADOptimizer(processor)
    
    # 定义μ值范围（对数尺度）
    mu_values = np.logspace(-1, 2.5, 30)  # 从0.1到约316
    
    print(f"\n计算MAD模型有效前沿...")
    mad_results = mad_optimizer.optimize_efficient_frontier(mu_values, verbose=False)
    
    # 获取单资产组合信息
    single_assets_mad = mad_optimizer.get_single_asset_portfolios()
    
    # 展示几个关键点的详细结果
    print("\n关键μ值的优化结果:")
    print(f"{'μ':>8} {'期望收益':>12} {'MAD风险':>12} {'目标值':>12}")
    print("-" * 50)
    key_indices = [0, len(mad_results)//4, len(mad_results)//2, 3*len(mad_results)//4, -1]
    for idx in key_indices:
        r = mad_results[idx]
        print(f"{r['mu']:8.2f} {r['expected_return']:12.6f} {r['mad_risk']:12.6f} {r['objective_value']:12.6f}")
    
    # 展示中等风险偏好的投资组合配置
    mid_idx = len(mad_results) // 2
    print(f"\n中等风险偏好 (μ = {mad_results[mid_idx]['mu']:.2f}) 的投资组合配置:")
    for i, name in enumerate(processor.get_asset_names()):
        weight = mad_results[mid_idx]['weights'][i]
        if weight > 0.01:
            print(f"  {name}: {weight*100:.2f}%")
    
    # ========== 3. 方差模型优化（对比） ==========
    print("\n" + "="*70)
    print("步骤 3: 方差模型优化（用于对比）")
    print("="*70)
    
    variance_optimizer = VarianceOptimizer(processor)
    
    print(f"\n计算方差模型有效前沿...")
    variance_results = variance_optimizer.optimize_efficient_frontier(mu_values, verbose=False)
    
    single_assets_var = variance_optimizer.get_single_asset_portfolios()
    
    # ========== 4. 深入分析 ==========
    print("\n" + "="*70)
    print("步骤 4: 深入分析")
    print("="*70)
    
    # 4.1 参数μ影响分析
    print("\n4.1 参数μ影响分析:")
    print(f"  - μ从{mu_values[0]:.2f}增加到{mu_values[-1]:.2f}时:")
    print(f"    期望收益: {mad_results[0]['expected_return']:.6f} → {mad_results[-1]['expected_return']:.6f}")
    print(f"    MAD风险: {mad_results[0]['mad_risk']:.6f} → {mad_results[-1]['mad_risk']:.6f}")
    print(f"  - 收益增加: {(mad_results[-1]['expected_return'] - mad_results[0]['expected_return']):.6f}")
    print(f"  - 风险增加: {(mad_results[-1]['mad_risk'] - mad_results[0]['mad_risk']):.6f}")
    
    # 4.2 模型对比分析
    print("\n4.2 MAD模型 vs 方差模型对比:")
    avg_mad_time = np.mean([r['solve_time'] for r in mad_results])
    avg_var_time = np.mean([r['solve_time'] for r in variance_results])
    print(f"  - MAD模型平均求解时间: {avg_mad_time:.4f}秒")
    print(f"  - 方差模型平均求解时间: {avg_var_time:.4f}秒")
    print(f"  - 效率比较: MAD模型约为方差模型的{avg_mad_time/avg_var_time:.2f}倍")
    
    # 4.3 分散投资效果分析
    print("\n4.3 分散投资效果分析:")
    print("  单资产投资组合风险-收益:")
    for p in single_assets_mad:
        print(f"    {p['asset']}: 收益={p['expected_return']:.6f}, MAD风险={p['mad_risk']:.6f}")
    
    # 找到MAD风险最小的组合
    min_risk_idx = np.argmin([r['mad_risk'] for r in mad_results])
    print(f"\n  最小风险组合 (μ = {mad_results[min_risk_idx]['mu']:.2f}):")
    print(f"    收益={mad_results[min_risk_idx]['expected_return']:.6f}, 风险={mad_results[min_risk_idx]['mad_risk']:.6f}")
    print("    配置:", end="")
    for i, name in enumerate(processor.get_asset_names()):
        w = mad_results[min_risk_idx]['weights'][i]
        if w > 0.01:
            print(f" {name}({w*100:.1f}%)", end="")
    print()
    
    # 4.4 相关性分析
    print("\n4.4 资产相关性分析:")
    corr_matrix = processor.get_correlation_matrix()
    print("  最高正相关资产对:")
    max_corr = -1
    max_pair = None
    asset_names = processor.get_asset_names()
    for i in range(len(asset_names)):
        for j in range(i+1, len(asset_names)):
            if corr_matrix[i, j] > max_corr:
                max_corr = corr_matrix[i, j]
                max_pair = (asset_names[i], asset_names[j])
    print(f"    {max_pair[0]} - {max_pair[1]}: {max_corr:.4f}")
    
    print("  最低相关（或负相关）资产对:")
    min_corr = 1
    min_pair = None
    for i in range(len(asset_names)):
        for j in range(i+1, len(asset_names)):
            if corr_matrix[i, j] < min_corr:
                min_corr = corr_matrix[i, j]
                min_pair = (asset_names[i], asset_names[j])
    print(f"    {min_pair[0]} - {min_pair[1]}: {min_corr:.4f}")
    
    # ========== 5. 可视化结果 ==========
    print("\n" + "="*70)
    print("步骤 5: 生成可视化图表")
    print("="*70)
    
    visualizer = Visualizer(output_dir=Path(__file__).parent.parent / "results")
    
    # 5.1 有效前沿图
    print("\n生成有效前沿图...")
    visualizer.plot_efficient_frontier(
        mad_results, 
        variance_results, 
        single_assets_mad,
        save_name="efficient_frontier.png"
    )
    
    # 5.2 投资组合配置图
    print("生成投资组合配置图...")
    # 选择部分μ值以便更清晰展示
    selected_indices = [i for i in range(0, len(mad_results), max(1, len(mad_results)//15))]
    selected_results = [mad_results[i] for i in selected_indices]
    visualizer.plot_portfolio_composition(
        selected_results,
        processor.get_asset_names(),
        save_name="portfolio_composition.png"
    )
    
    # 5.3 μ参数敏感性分析图
    print("生成μ参数敏感性分析图...")
    visualizer.plot_mu_sensitivity(
        mad_results,
        save_name="mu_sensitivity.png"
    )
    
    # 5.4 特定μ值的饼图
    print("生成投资组合配置饼图...")
    mid_idx = len(mad_results) // 2
    visualizer.plot_portfolio_pie(
        mad_results[mid_idx]['weights'],
        processor.get_asset_names(),
        mad_results[mid_idx]['mu'],
        save_name=f"portfolio_pie_mu_{mad_results[mid_idx]['mu']:.1f}.png"
    )
    
    # 5.5 相关系数热力图
    print("生成相关系数热力图...")
    visualizer.plot_correlation_heatmap(
        corr_matrix,
        processor.get_asset_names(),
        save_name="correlation_heatmap.png"
    )
    
    # 5.6 模型对比图
    print("生成模型对比图...")
    visualizer.plot_model_comparison(
        mad_results,
        variance_results,
        save_name="model_comparison.png"
    )
    
    # 5.7 结果汇总表格
    print("生成结果汇总表格...")
    visualizer.create_results_summary(
        mad_results,
        processor.get_asset_names(),
        save_name="mad_results_summary.csv"
    )
    visualizer.create_results_summary(
        variance_results,
        processor.get_asset_names(),
        save_name="variance_results_summary.csv"
    )
    
    # ========== 6. 总结 ==========
    print("\n" + "="*70)
    print("分析完成！")
    print("="*70)
    print(f"\n主要发现:")
    print(f"1. 有效前沿包含{len(mad_results)}个帕累托最优组合")
    print(f"2. 期望收益范围: [{mad_results[0]['expected_return']:.6f}, {mad_results[-1]['expected_return']:.6f}]")
    print(f"3. MAD风险范围: [{mad_results[0]['mad_risk']:.6f}, {mad_results[-1]['mad_risk']:.6f}]")
    print(f"4. 通过分散投资，可以在不降低收益的情况下显著降低风险")
    print(f"5. 所有图表和结果已保存到 results/ 目录")
    
    print("\n投资建议:")
    print("- 保守型投资者 (低μ): 选择低风险组合，接受较低收益")
    print("- 平衡型投资者 (中μ): 在风险和收益之间取得平衡")
    print("- 激进型投资者 (高μ): 追求高收益，承担较高风险")
    print("\n建议根据个人风险承受能力，从有效前沿上选择合适的投资组合。")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    print(f"\n总运行时间: {elapsed_time:.2f}秒")
    print("="*70)

