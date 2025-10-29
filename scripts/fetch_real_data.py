"""
数据获取主脚本 - 综合所有方法
优先级: 模拟数据生成 > 手动合并 > 自动爬取
"""

import sys
from pathlib import Path
import subprocess


def show_menu():
    """显示菜单"""
    print("\n" + "="*70)
    print("                    数据获取工具")
    print("="*70)
    print("\n可用方案:")
    print("\n1. 生成模拟数据 ⭐⭐⭐")
    print("   - 耗时: 1分钟")
    print("   - 成功率: 100%")
    print("   - 数据: 基于真实市场统计的高质量模拟数据")
    print("   - 推荐: 立即可用，适合作业")
    
    print("\n2. 手动下载数据合并 ⭐⭐⭐⭐⭐")
    print("   - 耗时: 15分钟")
    print("   - 成功率: 100%")
    print("   - 数据: 真实的Yahoo Finance数据")
    print("   - 推荐: 最可靠的获取真实数据方法")
    
    print("\n3. 自动网页爬虫（高级）⭐")
    print("   - 耗时: 30-60分钟")
    print("   - 成功率: 10-50%")
    print("   - 数据: 真实数据（如果成功）")
    print("   - 注意: 可能被反爬虫阻止")
    
    print("\n4. 查看当前已有数据")
    print("   - 查看data/目录下所有可用数据")
    
    print("\n5. 退出")
    
    print("\n" + "="*70)
    print("\n💡 建议:")
    print("  - 快速完成作业: 选1（模拟数据）")
    print("  - 获取真实数据: 选2（手动下载）")
    print("  - 技术挑战: 选3（自动爬虫，成功率低）")
    print("\n" + "="*70)


def option_1_simulated():
    """方案1: 生成模拟数据"""
    print("\n正在生成模拟数据...")
    subprocess.run([sys.executable, 'scripts/generate_simulated_data.py'])


def option_2_manual():
    """方案2: 手动下载合并"""
    print("\n" + "="*70)
    print("手动下载数据指南")
    print("="*70)
    
    print("\n📝 步骤:")
    print("\n第1步: 在浏览器中访问以下链接并下载CSV:")
    
    tickers = ['SHY', 'XLB', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV']
    for ticker in tickers:
        print(f"  ✓ https://finance.yahoo.com/quote/{ticker}/history")
    
    print("\n第2步: 在每个页面:")
    print("  - 设置日期范围 (如: 2022-01-01 to 2023-12-31)")
    print("  - 点击 'Download' 按钮")
    print("  - 确保文件命名为: SHY.csv, XLB.csv, ...")
    
    print("\n第3步: 将所有CSV文件放在 ~/Downloads 目录")
    
    print("\n" + "="*70)
    ready = input("\n是否已完成下载? [y/N]: ").strip().lower()
    
    if ready == 'y':
        print("\n运行合并脚本...")
        subprocess.run([sys.executable, 'scripts/merge_manual_csv.py'])
    else:
        print("\n提示: 完成下载后运行:")
        print("  python scripts/merge_manual_csv.py")


def option_3_crawler():
    """方案3: 自动爬虫"""
    print("\n" + "="*70)
    print("自动爬虫选项")
    print("="*70)
    
    print("\n可用的爬虫:")
    print("1. 高级爬虫 (多方法尝试)")
    print("2. Selenium爬虫 (需要安装ChromeDriver)")
    
    choice = input("\n选择 [1/2]: ").strip()
    
    if choice == '1':
        print("\n运行高级爬虫...")
        subprocess.run([sys.executable, 'scripts/advanced_web_scraper.py'])
    elif choice == '2':
        print("\n运行Selenium爬虫...")
        print("⚠️  确保已安装: pip install selenium")
        print("⚠️  确保已安装ChromeDriver")
        subprocess.run([sys.executable, 'scripts/selenium_scraper.py'])
    else:
        print("无效选择")


def option_4_check_data():
    """方案4: 查看现有数据"""
    data_dir = Path('data')
    
    print("\n" + "="*70)
    print("当前可用的数据文件:")
    print("="*70 + "\n")
    
    csv_files = sorted(data_dir.glob('*.csv'))
    
    if not csv_files:
        print("  (无数据文件)")
    else:
        for i, file_path in enumerate(csv_files, 1):
            size = file_path.stat().st_size / 1024
            print(f"{i}. {file_path.name}")
            print(f"   大小: {size:.1f} KB")
            
            # 读取第一行查看列数
            try:
                import pandas as pd
                df = pd.read_csv(file_path, nrows=1)
                n_months = len(pd.read_csv(file_path)) - 1  # 减去表头
                n_assets = len(df.columns) - 1  # 减去日期列
                print(f"   维度: {n_months} 月 × {n_assets} 资产")
            except:
                pass
            print()
    
    print("="*70)
    print("\n使用任一数据文件:")
    print("  修改 src/main.py 第39行的文件名")
    print("  然后运行: python src/main.py")


def main():
    """主函数"""
    
    while True:
        show_menu()
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == '1':
            option_1_simulated()
            break
        elif choice == '2':
            option_2_manual()
            break
        elif choice == '3':
            option_3_crawler()
            break
        elif choice == '4':
            option_4_check_data()
            input("\n按Enter返回菜单...")
        elif choice == '5':
            print("\n再见！")
            break
        else:
            print("\n❌ 无效选择，请输入1-5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出...")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
