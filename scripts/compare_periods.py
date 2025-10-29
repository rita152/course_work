"""
不同时期数据对比分析脚本
对比教材数据与真实数据的投资组合优化结果
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.data_processor import DataProcessor
from src.mad_optimizer import MADOptimizer


def analyze_period(data_file, period_name, mu_values):
    """
    分析单个时期的数据
    
    参数:
        data_file: 数据文件名
        period_name: 时期名称
        mu_values: μ值列表
    
    返回:
        dict: 分析结果
    """
    print(f"\n{'='*70}")
    print(f"分析时期: {period_name}")
    print(f"{'='*70}")
    
    data_path = Path(__file__).parent.parent / "data" / data_file
    
    if not data_path.exists():
        print(f"警告: 数据文件不存在 - {data_file}")
        print("请先运行 fetch_real_data.py 获取数据")
        return None
    
    # 加载数据
    processor = DataProcessor(data_path)
    
    # 创建优化器
    optimizer = MADOptimizer(processor)
    
    # 优化
    print(f"\n运行优化（{len(mu_values)}个μ值）...")
    results = optimizer.optimize_efficient_frontier(mu_values, verbose=False)
    
    # 汇总结果
    summary = {
        'period_name': period_name,
        'data_file': data_file,
        'n_assets': processor.n,
        'n_periods': processor.T,
        'expected_returns': processor.expected_returns,
        'asset_names': processor.asset_names,
        'results': results,
        'min_risk': min([r['mad_risk'] for r in results]),
        'max_return': max([r['expected_return'] for r in results]),
        'min_return': min([r['expected_return'] for r in results]),
        'max_risk': max([r['mad_risk'] for r in results]),
    }
    
    print(f"✓ 完成")
    print(f"  期望收益范围: [{summary['min_return']:.6f}, {summary['max_return']:.6f}]")
    print(f"  MAD风险范围: [{summary['min_risk']:.6f}, {summary['max_risk']:.6f}]")
    
    return summary


def plot_comparison(summaries, save_path):
    """
    绘制对比图
    
    参数:
        summaries: 多个时期的分析结果列表
        save_path: 保存路径
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(summaries)))
    
    # 子图1: 有效前沿对比
    ax = axes[0, 0]
    for i, summary in enumerate(summaries):
        if summary is None:
            continue
        risks = [r['mad_risk'] for r in summary['results']]
        returns = [r['expected_return'] for r in summary['results']]
        ax.plot(risks, returns, 'o-', linewidth=2, markersize=4,
                label=summary['period_name'], color=colors[i], alpha=0.8)
    
    ax.set_xlabel('MAD Risk', fontsize=12)
    ax.set_ylabel('Expected Return', fontsize=12)
    ax.set_title('Efficient Frontier Comparison Across Different Periods', 
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 子图2: 收益分布对比
    ax = axes[0, 1]
    period_names = [s['period_name'] for s in summaries if s is not None]
    min_returns = [s['min_return'] for s in summaries if s is not None]
    max_returns = [s['max_return'] for s in summaries if s is not None]
    
    x = np.arange(len(period_names))
    width = 0.35
    
    ax.bar(x - width/2, min_returns, width, label='Min Return', alpha=0.8)
    ax.bar(x + width/2, max_returns, width, label='Max Return', alpha=0.8)
    
    ax.set_xlabel('Period', fontsize=12)
    ax.set_ylabel('Return', fontsize=12)
    ax.set_title('Return Range Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(period_names, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 子图3: 风险分布对比
    ax = axes[1, 0]
    min_risks = [s['min_risk'] for s in summaries if s is not None]
    max_risks = [s['max_risk'] for s in summaries if s is not None]
    
    ax.bar(x - width/2, min_risks, width, label='Min Risk', alpha=0.8)
    ax.bar(x + width/2, max_risks, width, label='Max Risk', alpha=0.8)
    
    ax.set_xlabel('Period', fontsize=12)
    ax.set_ylabel('MAD Risk', fontsize=12)
    ax.set_title('Risk Range Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(period_names, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 子图4: 资产期望收益对比
    ax = axes[1, 1]
    for i, summary in enumerate(summaries):
        if summary is None:
            continue
        ax.plot(summary['asset_names'], summary['expected_returns'], 
               'o-', linewidth=2, markersize=6,
               label=summary['period_name'], color=colors[i], alpha=0.8)
    
    ax.set_xlabel('Asset', fontsize=12)
    ax.set_ylabel('Expected Return', fontsize=12)
    ax.set_title('Asset Expected Returns Across Periods', 
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n对比图已保存: {save_path}")


def main():
    """主函数"""
    print("="*70)
    print("不同时期投资组合优化对比分析")
    print("="*70)
    
    # 定义要对比的时期
    periods = [
        ('returns_data.csv', 'Textbook Period (2005-2007)'),
        ('returns_data_recent_2y.csv', 'Recent 2 Years (2022-2023)'),
        ('returns_data_with_crisis.csv', 'Financial Crisis (2007-2009)'),
        ('returns_data_with_covid.csv', 'COVID Period (2019-2021)'),
    ]
    
    # μ值范围
    mu_values = np.logspace(-1, 2, 15)  # 减少点数加快计算
    
    # 分析每个时期
    summaries = []
    for data_file, period_name in periods:
        summary = analyze_period(data_file, period_name, mu_values)
        summaries.append(summary)
    
    # 过滤掉None（数据不存在的时期）
    valid_summaries = [s for s in summaries if s is not None]
    
    if len(valid_summaries) < 2:
        print("\n警告: 需要至少2个时期的数据才能进行对比")
        print("请运行 scripts/fetch_real_data.py 获取更多数据")
        return
    
    # 生成对比图
    save_path = Path(__file__).parent.parent / "results" / "period_comparison.png"
    plot_comparison(valid_summaries, save_path)
    
    # 生成对比报告
    print("\n" + "="*70)
    print("对比分析报告")
    print("="*70)
    
    for summary in valid_summaries:
        print(f"\n{summary['period_name']}:")
        print(f"  数据点数: {summary['n_periods']}个月")
        print(f"  收益范围: [{summary['min_return']:.6f}, {summary['max_return']:.6f}]")
        print(f"  风险范围: [{summary['min_risk']:.6f}, {summary['max_risk']:.6f}]")
        print(f"  最佳资产: {summary['asset_names'][np.argmax(summary['expected_returns'])]}")
        print(f"  最高收益: {np.max(summary['expected_returns']):.6f}")
    
    print("\n" + "="*70)
    print("分析完成！")
    print("="*70)
    print(f"对比图保存在: {save_path}")


if __name__ == "__main__":
    main()

