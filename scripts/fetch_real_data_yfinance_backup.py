"""
获取真实金融数据脚本
使用yfinance库从Yahoo Finance获取ETF历史数据
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
import time

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))


class RealDataFetcher:
    """真实金融数据获取器"""
    
    def __init__(self):
        # 教材中的9个投资标的
        self.tickers = {
            'SHY': '3-Year Treasury Bond ETF',
            'XLB': 'Materials Sector ETF',
            'XLE': 'Energy Sector ETF', 
            'XLF': 'Financial Sector ETF',
            'XLI': 'Industrial Sector ETF',
            'XLK': 'Technology Sector ETF',
            'XLP': 'Consumer Staples ETF',
            'XLU': 'Utilities Sector ETF',
            'XLV': 'Healthcare Sector ETF'
        }
    
    def fetch_data(self, start_date, end_date, period='monthly', retry=3, delay=2):
        """
        获取历史数据（带重试和延迟机制）
        
        参数:
            start_date: 开始日期 (格式: 'YYYY-MM-DD')
            end_date: 结束日期 (格式: 'YYYY-MM-DD')
            period: 数据周期 ('daily', 'weekly', 'monthly')
            retry: 重试次数
            delay: 每次请求间延迟（秒）
        
        返回:
            DataFrame: 月度收益率数据
        """
        print("="*70)
        print("开始获取真实金融数据...")
        print("="*70)
        
        # 获取原始价格数据
        print(f"\n数据范围: {start_date} 至 {end_date}")
        print(f"投资标的: {', '.join(self.tickers.keys())}")
        print("\n正在下载数据（逐个下载以避免速率限制）...")
        
        # 逐个ticker下载数据，避免速率限制
        all_data = {}
        failed_tickers = []
        
        for i, ticker in enumerate(self.tickers.keys(), 1):
            print(f"  [{i}/{len(self.tickers)}] 下载 {ticker}...", end=" ")
            
            for attempt in range(retry):
                try:
                    # 下载单个ticker
                    ticker_data = yf.download(
                        ticker,
                        start=start_date,
                        end=end_date,
                        progress=False,
                        show_errors=False
                    )
                    
                    if not ticker_data.empty:
                        all_data[ticker] = ticker_data['Adj Close']
                        print("✓")
                        break
                    else:
                        if attempt < retry - 1:
                            print(f"空数据，重试{attempt+1}...", end=" ")
                            time.sleep(delay)
                        else:
                            print("✗ (无数据)")
                            failed_tickers.append(ticker)
                            
                except Exception as e:
                    if attempt < retry - 1:
                        print(f"失败，等待{delay}秒后重试...", end=" ")
                        time.sleep(delay)
                    else:
                        print(f"✗ ({str(e)[:30]}...)")
                        failed_tickers.append(ticker)
            
            # 每个ticker之间延迟，避免速率限制
            if i < len(self.tickers):
                time.sleep(delay)
        
        # 检查是否有成功下载的数据
        if not all_data:
            raise Exception("所有ticker都下载失败！请稍后重试或检查网络连接。")
        
        if failed_tickers:
            print(f"\n⚠️  警告: {len(failed_tickers)}个ticker下载失败: {', '.join(failed_tickers)}")
            print("    继续使用成功下载的数据...")
        
        # 合并所有数据
        adj_close = pd.DataFrame(all_data)
        
        print(f"\n数据下载完成！")
        print(f"成功: {len(all_data)}/{len(self.tickers)} 个ticker")
        print(f"原始数据点数: {len(adj_close)}")
        
        # 根据周期重采样
        if period == 'monthly':
            # 重采样为月末数据 (使用'ME'代替已弃用的'M')
            monthly_prices = adj_close.resample('ME').last()
            print(f"月度数据点数: {len(monthly_prices)}")
            
            # 计算月度收益率 (R_j(t) = P(t) / P(t-1))
            monthly_returns = monthly_prices / monthly_prices.shift(1)
            monthly_returns = monthly_returns.dropna()
            
            print(f"有效月度收益率数据: {len(monthly_returns)}")
            
            return monthly_returns
        
        elif period == 'weekly':
            weekly_prices = adj_close.resample('W').last()
            weekly_returns = weekly_prices / weekly_prices.shift(1)
            weekly_returns = weekly_returns.dropna()
            return weekly_returns
        
        else:  # daily
            daily_returns = adj_close / adj_close.shift(1)
            daily_returns = daily_returns.dropna()
            return daily_returns
    
    def save_to_csv(self, returns_df, filename):
        """
        保存数据为CSV格式（与教材格式一致）
        
        参数:
            returns_df: 收益率DataFrame
            filename: 保存文件名
        """
        # 添加日期列
        output_df = returns_df.copy()
        output_df.insert(0, 'Year-Month', output_df.index.strftime('%Y-%m'))
        
        # 保存
        output_path = Path(__file__).parent.parent / 'data' / filename
        output_df.to_csv(output_path, index=False)
        
        print(f"\n数据已保存到: {output_path}")
        print(f"数据维度: {len(output_df)} 个月 × {len(self.tickers)} 个资产")
        
        return output_path
    
    def get_data_statistics(self, returns_df):
        """
        获取数据统计信息
        
        参数:
            returns_df: 收益率DataFrame
        
        返回:
            DataFrame: 统计信息
        """
        stats = pd.DataFrame({
            '资产': returns_df.columns,
            '平均收益率': returns_df.mean().values,
            '标准差': returns_df.std().values,
            '最小值': returns_df.min().values,
            '最大值': returns_df.max().values,
            '数据点数': [len(returns_df)] * len(returns_df.columns)
        })
        
        return stats


def main():
    """主函数 - 提供多个时间段选项"""
    
    fetcher = RealDataFetcher()
    
    print("\n" + "="*70)
    print("真实金融数据获取工具")
    print("="*70)
    print("\n可选的时间段：")
    print("1. 教材原始时期 (2005-05 to 2007-04) - 24个月")
    print("2. 金融危机前 (2006-01 to 2007-12) - 24个月")
    print("3. 包含金融危机 (2007-01 to 2009-12) - 36个月")
    print("4. 疫情前时期 (2018-01 to 2019-12) - 24个月")
    print("5. 包含疫情 (2019-01 to 2021-12) - 36个月")
    print("6. 最近2年 (2022-01 to 2023-12) - 24个月")
    print("7. 最近3年 (2021-01 to 2023-12) - 36个月")
    print("8. 自定义时间段")
    
    choice = input("\n请选择时间段 (1-8): ").strip()
    
    # 预定义时间段
    periods = {
        '1': ('2005-05-01', '2007-04-30', 'returns_data_original.csv'),
        '2': ('2006-01-01', '2007-12-31', 'returns_data_pre_crisis.csv'),
        '3': ('2007-01-01', '2009-12-31', 'returns_data_with_crisis.csv'),
        '4': ('2018-01-01', '2019-12-31', 'returns_data_pre_covid.csv'),
        '5': ('2019-01-01', '2021-12-31', 'returns_data_with_covid.csv'),
        '6': ('2022-01-01', '2023-12-31', 'returns_data_recent_2y.csv'),
        '7': ('2021-01-01', '2023-12-31', 'returns_data_recent_3y.csv'),
    }
    
    if choice in periods:
        start_date, end_date, filename = periods[choice]
    elif choice == '8':
        start_date = input("请输入开始日期 (YYYY-MM-DD): ").strip()
        end_date = input("请输入结束日期 (YYYY-MM-DD): ").strip()
        filename = input("请输入保存文件名 (如: returns_data_custom.csv): ").strip()
    else:
        print("无效选择，使用默认时期（教材原始）")
        start_date, end_date, filename = periods['1']
    
    # 获取数据
    try:
        returns_df = fetcher.fetch_data(start_date, end_date, period='monthly')
        
        # 显示统计信息
        print("\n" + "="*70)
        print("数据统计信息:")
        print("="*70)
        stats = fetcher.get_data_statistics(returns_df)
        print(stats.to_string(index=False))
        
        # 保存数据
        output_path = fetcher.save_to_csv(returns_df, filename)
        
        # 显示前几行数据
        print("\n" + "="*70)
        print("数据预览（前5行）:")
        print("="*70)
        print(returns_df.head())
        
        print("\n" + "="*70)
        print("数据获取成功！")
        print("="*70)
        print(f"\n您可以使用以下命令运行优化分析:")
        print(f"  1. 将 src/main.py 中的数据文件路径改为: data/{filename}")
        print(f"  2. 运行: python src/main.py")
        print("\n或者创建一个新的分析脚本，对比不同时期的结果。")
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n可能的原因:")
        print("  1. 没有安装yfinance: pip install yfinance")
        print("  2. 网络连接问题")
        print("  3. 日期格式错误")
        print("  4. Yahoo Finance服务暂时不可用")


if __name__ == "__main__":
    main()

