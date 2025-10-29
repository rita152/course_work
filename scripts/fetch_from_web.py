"""
直接从网页获取金融数据
使用requests库抓取Yahoo Finance网页数据
不依赖yfinance库
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import time
import json
import re


class WebDataFetcher:
    """从网页直接获取数据"""
    
    def __init__(self):
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
        
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def fetch_ticker_data(self, ticker, start_date, end_date):
        """
        从Yahoo Finance网页获取单个ticker的数据
        
        参数:
            ticker: 股票代码
            start_date: 开始日期 (datetime对象)
            end_date: 结束日期 (datetime对象)
        
        返回:
            DataFrame: 历史价格数据
        """
        # 转换日期为时间戳
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        
        # 构建URL（Yahoo Finance的下载URL）
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
        params = {
            'period1': period1,
            'period2': period2,
            'interval': '1d',  # 日度数据
            'events': 'history',
            'includeAdjustedClose': 'true'
        }
        
        try:
            # 发送请求
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # 解析CSV数据
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                
                # 设置日期为索引
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                return df
            else:
                print(f"    ✗ HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"    ✗ 错误: {str(e)[:50]}")
            return None
    
    def fetch_all_data(self, start_date, end_date, delay=3):
        """
        获取所有ticker的数据
        
        参数:
            start_date: 开始日期字符串 'YYYY-MM-DD'
            end_date: 结束日期字符串 'YYYY-MM-DD'
            delay: 每次请求间延迟（秒）
        
        返回:
            dict: {ticker: DataFrame}
        """
        print("="*70)
        print("从网页直接获取数据")
        print("="*70)
        
        # 转换日期
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        print(f"\n数据范围: {start_date} 至 {end_date}")
        print(f"投资标的: {', '.join(self.tickers.keys())}")
        print("\n开始下载（逐个ticker，避免被封IP）...\n")
        
        all_data = {}
        failed = []
        
        for i, ticker in enumerate(self.tickers.keys(), 1):
            print(f"  [{i}/{len(self.tickers)}] {ticker} ... ", end="", flush=True)
            
            df = self.fetch_ticker_data(ticker, start_dt, end_dt)
            
            if df is not None and not df.empty:
                all_data[ticker] = df['Adj Close']
                print(f"✓ ({len(df)} 数据点)")
            else:
                print("✗ 失败")
                failed.append(ticker)
            
            # 延迟，避免被封
            if i < len(self.tickers):
                time.sleep(delay)
        
        if not all_data:
            raise Exception("所有ticker都下载失败！可能被Yahoo Finance封禁。")
        
        if failed:
            print(f"\n⚠️  {len(failed)} 个ticker失败: {', '.join(failed)}")
            print("    继续使用成功的数据...")
        
        return all_data
    
    def convert_to_monthly_returns(self, daily_data):
        """
        将日度数据转换为月度收益率
        
        参数:
            daily_data: {ticker: Series} 日度价格数据
        
        返回:
            DataFrame: 月度收益率
        """
        print("\n转换为月度收益率...")
        
        # 合并所有数据
        df = pd.DataFrame(daily_data)
        
        # 重采样为月末
        monthly_prices = df.resample('ME').last()
        
        # 计算月度收益率
        monthly_returns = monthly_prices / monthly_prices.shift(1)
        monthly_returns = monthly_returns.dropna()
        
        print(f"✓ 月度数据点数: {len(monthly_returns)}")
        
        return monthly_returns
    
    def save_to_csv(self, returns_df, filename):
        """保存为CSV"""
        output_df = returns_df.copy()
        output_df.insert(0, 'Year-Month', output_df.index.strftime('%Y-%m'))
        
        output_path = Path(__file__).parent.parent / 'data' / filename
        output_df.to_csv(output_path, index=False)
        
        print(f"\n数据已保存: {output_path}")
        print(f"数据维度: {len(output_df)} 个月 × {len(returns_df.columns)} 个资产")
        
        return output_path


def main():
    """主函数"""
    
    print("\n" + "="*70)
    print("网页数据获取工具")
    print("="*70)
    print("\n可选时间段:")
    print("1. 教材原始 (2005-05 to 2007-04)")
    print("2. 最近2年 (2022-01 to 2023-12)")
    print("3. 最近3年 (2021-01 to 2023-12)")
    print("4. 自定义时间段")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    periods = {
        '1': ('2005-05-01', '2007-04-30', 'returns_data_web_original.csv'),
        '2': ('2022-01-01', '2023-12-31', 'returns_data_web_recent_2y.csv'),
        '3': ('2021-01-01', '2023-12-31', 'returns_data_web_recent_3y.csv'),
    }
    
    if choice in periods:
        start_date, end_date, filename = periods[choice]
    elif choice == '4':
        start_date = input("开始日期 (YYYY-MM-DD): ").strip()
        end_date = input("结束日期 (YYYY-MM-DD): ").strip()
        filename = input("文件名 (如: data.csv): ").strip()
    else:
        print("无效选择，使用默认")
        start_date, end_date, filename = periods['2']
    
    try:
        fetcher = WebDataFetcher()
        
        # 获取数据
        daily_data = fetcher.fetch_all_data(start_date, end_date, delay=3)
        
        # 转换为月度收益率
        monthly_returns = fetcher.convert_to_monthly_returns(daily_data)
        
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
        
        # 保存
        output_path = fetcher.save_to_csv(monthly_returns, filename)
        
        # 预览
        print("\n" + "="*70)
        print("数据预览:")
        print("="*70)
        print(monthly_returns.head())
        
        print("\n" + "="*70)
        print("✓ 数据获取成功！")
        print("="*70)
        print(f"\n使用方法:")
        print(f"  修改 src/main.py 使用: data/{filename}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n可能的原因:")
        print("  1. Yahoo Finance服务不可用")
        print("  2. 网络连接问题")
        print("  3. IP被临时封禁（等待1-2小时）")
        print("\n建议:")
        print("  - 使用模拟数据: python scripts/generate_simulated_data.py")
        print("  - 或等待后重试")


if __name__ == "__main__":
    main()

