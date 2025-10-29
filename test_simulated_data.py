"""
测试模拟数据
快速验证模拟数据是否可用
"""

from pathlib import Path
import sys
sys.path.append('src')

from data_processor import DataProcessor
from mad_optimizer import MADOptimizer
import numpy as np

print("="*70)
print("测试模拟数据")
print("="*70)

# 使用模拟数据
data_path = Path("data/returns_data_simulated_normal.csv")

print(f"\n加载数据: {data_path}")
processor = DataProcessor(data_path)

print("\n汇总统计:")
print(processor.get_summary_statistics().to_string(index=False))

# 快速优化测试
print("\n运行快速优化测试...")
optimizer = MADOptimizer(processor)

# 测试3个μ值
mu_values = [1, 10, 50]
for mu in mu_values:
    result = optimizer.optimize(mu, verbose=False)
    print(f"  μ={mu:3d}: 收益={result['expected_return']:.6f}, 风险={result['mad_risk']:.6f}")

print("\n✓ 模拟数据测试成功！可以正常使用。")
print("\n使用方法:")
print("  1. 修改 src/main.py 第39行")
print("  2. 改为: data_path = Path(...) / 'data' / 'returns_data_simulated_normal.csv'")
print("  3. 运行: python src/main.py")

