"""
合并手动下载的CSV文件
将9个单独的ticker CSV合并为一个收益率文件
"""

import pandas as pd
import numpy as np
from pathlib import Path


def merge_manual_downloads(download_dir, output_filename='returns_data_manual.csv'):
    """
    合并手动下载的Yahoo Finance CSV文件
    
    参数:
        download_dir: 下载文件存放目录（绝对路径）
        output_filename: 输出文件名
    
    使用说明:
        1. 从Yahoo Finance手动下载9个ticker的CSV
        2. 将它们放在同一个目录
        3. CSV文件命名为: SHY.csv, XLB.csv, XLE.csv, 等
        4. 运行此脚本
    """
    
    tickers = ['SHY', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV']
    
    print("="*70)
    print("合并手动下载的数据")
    print("="*70)
    print(f"\n下载目录: {download_dir}")
    print(f"目标ticker: {', '.join(tickers)}\n")
    
    download_path = Path(download_dir)
    
    if not download_path.exists():
        print(f"❌ 目录不存在: {download_dir}")
        print("\n请提供正确的下载目录路径")
        return
    
    all_data = {}
    
    # 读取每个CSV文件
    for ticker in tickers:
        file_path = download_path / f"{ticker}.csv"
        
        if not file_path.exists():
            print(f"⚠️  未找到: {ticker}.csv")
            continue
        
        try:
            # 读取CSV
            df = pd.read_csv(file_path)
            
            # 解析日期
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # 提取调整后收盘价
            if 'Adj Close' in df.columns:
                all_data[ticker] = df['Adj Close']
                print(f"✓ {ticker}: {len(df)} 数据点")
            else:
                print(f"⚠️  {ticker}: 缺少'Adj Close'列")
                
        except Exception as e:
            print(f"✗ {ticker}: 错误 - {str(e)[:40]}")
    
    if len(all_data) == 0:
        print("\n❌ 没有成功读取任何文件")
        print("\n请检查:")
        print("  1. 文件命名是否正确 (SHY.csv, XLB.csv, ...)")
        print("  2. 文件是否在指定目录")
        print("  3. CSV格式是否正确")
        return
    
    print(f"\n成功读取: {len(all_data)}/{len(tickers)} 个ticker")
    
    # 合并所有数据
    print("\n合并数据...")
    df_combined = pd.DataFrame(all_data)
    
    # 只保留所有ticker都有数据的日期
    df_combined = df_combined.dropna()
    print(f"  有效日期范围: {df_combined.index.min().date()} 至 {df_combined.index.max().date()}")
    print(f"  总数据点: {len(df_combined)}")
    
    # 转换为月度收益率
    print("\n计算月度收益率...")
    monthly_prices = df_combined.resample('ME').last()
    monthly_returns = monthly_prices / monthly_prices.shift(1)
    monthly_returns = monthly_returns.dropna()
    
    print(f"  月度数据点: {len(monthly_returns)}")
    
    # 准备输出
    output_df = monthly_returns.copy()
    output_df.insert(0, 'Year-Month', output_df.index.strftime('%Y-%m'))
    
    # 保存
    output_path = Path(__file__).parent.parent / 'data' / output_filename
    output_df.to_csv(output_path, index=False)
    
    print(f"\n✓ 数据已保存: {output_path}")
    print(f"  数据维度: {len(output_df)} 月 × {len(monthly_returns.columns)} 资产")
    
    # 显示统计
    print("\n" + "="*70)
    print("数据统计:")
    print("="*70)
    stats = pd.DataFrame({
        '资产': monthly_returns.columns,
        '平均收益': monthly_returns.mean().values,
        '标准差': monthly_returns.std().values,
        '最小值': monthly_returns.min().values,
        '最大值': monthly_returns.max().values,
    })
    print(stats.to_string(index=False))
    
    # 预览
    print("\n数据预览（前5行）:")
    print(output_df.head().to_string())
    
    print("\n" + "="*70)
    print("✓ 完成！")
    print("="*70)
    print(f"\n使用方法:")
    print(f"  修改 src/main.py 使用: data/{output_filename}")


def main():
    """主函数"""
    
    print("\n" + "="*70)
    print("Yahoo Finance手动下载数据合并工具")
    print("="*70)
    
    print("\n📝 手动下载步骤:")
    print("\n1. 打开浏览器访问:")
    print("   https://finance.yahoo.com/quote/SHY/history")
    print("\n2. 设置日期范围 (例如: Jan 01, 2022 - Dec 31, 2023)")
    print("\n3. 点击 'Download' 按钮下载CSV")
    print("\n4. 重复上述步骤下载所有9个ticker:")
    print("   SHY, XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV")
    print("\n5. 将下载的CSV文件重命名为: SHY.csv, XLB.csv, ...")
    print("\n6. 将所有CSV文件放在同一个目录")
    print("\n7. 运行此脚本合并数据")
    
    print("\n" + "="*70)
    
    # 获取下载目录
    print("\nCSV文件位置选项:")
    print("1. ~/Downloads (默认)")
    print("2. 项目的 manual_downloads/ 目录")
    print("3. 自定义路径")
    
    choice = input("\n选择 (默认1): ").strip() or '1'
    
    if choice == '1':
        import os
        download_dir = os.path.expanduser('~/Downloads')
    elif choice == '2':
        download_dir = str(Path(__file__).parent.parent / 'manual_downloads')
        Path(download_dir).mkdir(exist_ok=True)
        print(f"\n📁 请将下载的CSV文件放入: {download_dir}")
        input("\n✓ 完成后按Enter继续...")
    else:
        download_dir = input("请输入CSV文件目录的完整路径: ").strip()
    
    # 执行合并
    merge_manual_downloads(download_dir)


if __name__ == "__main__":
    main()

