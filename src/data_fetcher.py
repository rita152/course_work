"""
数据获取模块
从雅虎财经获取ETF历史数据，并计算月度收益率
"""

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os


class DataFetcher:
    """数据获取类，负责从雅虎财经获取ETF数据"""
    
    def __init__(self, tickers=None, start_date=None, end_date=None, delay=2.5):
        """
        初始化数据获取器
        
        参数:
            tickers: ETF代码列表，默认使用教材中的9个标的
            start_date: 开始日期，默认为3年前
            end_date: 结束日期，默认为今天
            delay: 每次请求后的延时（秒），防止被限流
        """
        # 默认使用教材中的9个ETF标的
        if tickers is None:
            self.tickers = ['SHY', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV']
        else:
            self.tickers = tickers
        
        # 设置时间范围
        if end_date is None:
            self.end_date = datetime.now()
        else:
            self.end_date = pd.to_datetime(end_date)
            
        if start_date is None:
            self.start_date = self.end_date - timedelta(days=3*365)  # 默认3年
        else:
            self.start_date = pd.to_datetime(start_date)
        
        self.delay = delay
        self.price_data = None
        self.returns_data = None
        
    def fetch_data(self, save_path='../data/raw/price_data.csv'):
        """
        获取价格数据
        
        参数:
            save_path: 保存路径
        """
        print(f"开始获取 {len(self.tickers)} 个标的的数据...")
        print(f"时间范围: {self.start_date.date()} 到 {self.end_date.date()}")
        
        all_data = {}
        
        for i, ticker in enumerate(self.tickers, 1):
            try:
                print(f"[{i}/{len(self.tickers)}] 正在获取 {ticker} 的数据...", end=' ')
                
                # 下载数据
                data = yf.download(
                    ticker,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False,
                    auto_adjust=False
                )
                
                if not data.empty:
                    # 使用调整后的收盘价
                    if isinstance(data.columns, pd.MultiIndex):
                        # 多标的下载返回MultiIndex
                        adj_close = data['Adj Close'][ticker] if ('Adj Close', ticker) in data.columns else data[('Adj Close', ticker)]
                    else:
                        # 单标的下载返回简单列名
                        adj_close = data['Adj Close']
                    
                    all_data[ticker] = adj_close
                    print(f"成功 (共 {len(data)} 条记录)")
                else:
                    print(f"失败: 无数据")
                
                # 延时，防止被限流
                if i < len(self.tickers):
                    print(f"   等待 {self.delay} 秒...")
                    time.sleep(self.delay)
                    
            except Exception as e:
                print(f"失败: {str(e)}")
                continue
        
        # 合并数据
        self.price_data = pd.DataFrame(all_data)
        
        # 删除有缺失值的行
        self.price_data = self.price_data.dropna()
        
        print(f"\n数据获取完成！共 {len(self.price_data)} 个交易日")
        print(f"包含标的: {', '.join(self.price_data.columns.tolist())}")
        
        # 保存原始价格数据
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self.price_data.to_csv(save_path)
            print(f"价格数据已保存至: {save_path}")
        
        return self.price_data
    
    def calculate_monthly_returns(self, save_path='../data/processed/monthly_returns.csv'):
        """
        计算月度收益率
        
        参数:
            save_path: 保存路径
        
        返回:
            月度收益率DataFrame
        """
        if self.price_data is None:
            raise ValueError("请先调用 fetch_data() 获取价格数据")
        
        print("\n计算月度收益率...")
        
        # 重采样到月度（取每月最后一个交易日的价格）
        # 使用ME代替已弃用的M
        monthly_prices = self.price_data.resample('ME').last()
        
        # 计算收益率: R(t) = P(t) / P(t-1)
        self.returns_data = monthly_prices / monthly_prices.shift(1)
        
        # 删除第一行（没有前一期数据）
        self.returns_data = self.returns_data.iloc[1:]
        
        print(f"月度收益率计算完成！共 {len(self.returns_data)} 个月")
        print(f"\n收益率统计:")
        print(self.returns_data.describe())
        
        # 保存收益率数据
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self.returns_data.to_csv(save_path)
            print(f"\n收益率数据已保存至: {save_path}")
        
        return self.returns_data
    
    def load_data(self, price_path='../data/raw/price_data.csv', 
                  returns_path='../data/processed/monthly_returns.csv'):
        """
        从文件加载已保存的数据
        
        参数:
            price_path: 价格数据文件路径
            returns_path: 收益率数据文件路径
        """
        if os.path.exists(price_path):
            self.price_data = pd.read_csv(price_path, index_col=0, parse_dates=True)
            print(f"价格数据已从 {price_path} 加载")
        
        if os.path.exists(returns_path):
            self.returns_data = pd.read_csv(returns_path, index_col=0, parse_dates=True)
            print(f"收益率数据已从 {returns_path} 加载")
        
        return self.price_data, self.returns_data
    
    def get_summary_statistics(self):
        """获取数据摘要统计"""
        if self.returns_data is None:
            raise ValueError("请先计算月度收益率")
        
        # 计算期望收益（均值）
        mean_returns = self.returns_data.mean()
        
        # 计算收益率标准差
        std_returns = self.returns_data.std()
        
        # 计算年化收益率（假设每月复利）
        annualized_returns = (mean_returns ** 12) - 1
        
        # 计算年化波动率
        annualized_vol = std_returns * np.sqrt(12)
        
        summary = pd.DataFrame({
            '月均收益率': mean_returns,
            '月收益率标准差': std_returns,
            '年化收益率': annualized_returns,
            '年化波动率': annualized_vol
        })
        
        return summary


if __name__ == '__main__':
    # 测试代码
    fetcher = DataFetcher()
    
    # 获取数据
    price_data = fetcher.fetch_data()
    
    # 计算月度收益率
    returns = fetcher.calculate_monthly_returns()
    
    # 显示摘要统计
    print("\n" + "="*60)
    print("数据摘要统计:")
    print("="*60)
    summary = fetcher.get_summary_statistics()
    print(summary)

