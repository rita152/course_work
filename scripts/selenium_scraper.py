"""
Selenium爬虫 - 模拟真实浏览器
这是最强大的爬虫方案，可以绕过大部分反爬虫限制
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import time
import sys


def check_selenium():
    """检查Selenium是否可用"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✓ Selenium已安装")
        return True
    except ImportError:
        print("✗ Selenium未安装")
        print("\n安装方法:")
        print("  pip install selenium")
        print("  # 还需要下载ChromeDriver:")
        print("  # Ubuntu: sudo apt-get install chromium-chromedriver")
        print("  # 或从 https://chromedriver.chromium.org/ 下载")
        return False


def fetch_with_selenium(ticker, start_date, end_date):
    """
    使用Selenium获取数据
    
    参数:
        ticker: 股票代码
        start_date: 开始日期
        end_date: 结束日期
    
    返回:
        Series: 价格数据
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import os
    
    # Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 后台运行
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # 禁用自动化检测
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # 尝试使用chromedriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # 构建URL
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        
        # 方法1: 直接访问下载链接
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval=1d&events=history"
        
        driver.get(url)
        time.sleep(3)
        
        # 获取页面内容
        page_source = driver.page_source
        
        driver.quit()
        
        # 解析CSV内容
        if 'Date,Open' in page_source or 'Date' in page_source:
            # 提取CSV内容
            from io import StringIO
            # 移除HTML标签
            import re
            csv_match = re.search(r'Date,.*?(?=</pre>|$)', page_source, re.DOTALL)
            if csv_match:
                csv_content = csv_match.group(0)
                df = pd.read_csv(StringIO(csv_content))
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                return df['Adj Close']
        
        return None
        
    except Exception as e:
        print(f"Selenium错误: {e}")
        return None


def main():
    """主函数"""
    
    print("="*70)
    print("Selenium爬虫 - 真实浏览器模拟")
    print("="*70)
    
    # 检查依赖
    if not check_selenium():
        print("\n请先安装Selenium和ChromeDriver")
        print("\n或使用模拟数据:")
        print("  python scripts/generate_simulated_data.py")
        return
    
    tickers = ['SHY', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV']
    
    print(f"\n将尝试获取 {len(tickers)} 个ticker的数据")
    print("预计耗时: 约5-10分钟（每个ticker约30-60秒）")
    
    choice = input("\n继续? [y/N]: ").strip().lower()
    if choice != 'y':
        print("已取消")
        return
    
    # 日期范围
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    print(f"\n开始爬取...")
    print(f"日期范围: {start_date.date()} 至 {end_date.date()}\n")
    
    all_data = {}
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker} ... ", end="", flush=True)
        
        data = fetch_with_selenium(ticker, start_date, end_date)
        
        if data is not None:
            all_data[ticker] = data
            print(f"✓ ({len(data)} 数据点)")
        else:
            print("✗ 失败")
        
        # 延迟避免被封
        if i < len(tickers):
            wait_time = np.random.uniform(5, 10)
            print(f"    等待 {wait_time:.1f}秒...")
            time.sleep(wait_time)
    
    if len(all_data) >= 5:
        print(f"\n✓ 成功 {len(all_data)}/{len(tickers)} 个ticker")
        
        # 合并并转月度
        df = pd.DataFrame(all_data)
        monthly = df.resample('ME').last()
        returns = monthly / monthly.shift(1)
        returns = returns.dropna()
        
        # 保存
        output_df = returns.copy()
        output_df.insert(0, 'Year-Month', output_df.index.strftime('%Y-%m'))
        
        output_path = Path(__file__).parent.parent / 'data' / 'returns_data_selenium.csv'
        output_df.to_csv(output_path, index=False)
        
        print(f"\n数据已保存: {output_path}")
        print(f"数据维度: {len(output_df)} 月 × {len(returns.columns)} 资产")
        
    else:
        print(f"\n✗ 成功率过低 ({len(all_data)}/{len(tickers)})")
        print("建议使用模拟数据")


if __name__ == "__main__":
    main()

