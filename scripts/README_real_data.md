# 真实数据获取和分析指南

## 功能说明

本脚本可以从Yahoo Finance获取真实的ETF历史数据，替换教材中的示例数据进行分析。

## 安装依赖

```bash
conda activate cource_work
pip install yfinance
```

或者重新安装所有依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1: 交互式获取（推荐）

```bash
cd /home/zhangpeng/cource_work/portfolio_selection
python scripts/fetch_real_data.py
```

然后按照提示选择时间段：

**预设时间段**:
1. **教材原始时期** (2005-05 to 2007-04) - 验证模型
2. **金融危机前** (2006-01 to 2007-12) - 牛市数据
3. **包含金融危机** (2007-01 to 2009-12) - 含极端风险
4. **疫情前时期** (2018-01 to 2019-12) - 正常时期
5. **包含疫情** (2019-01 to 2021-12) - 疫情影响
6. **最近2年** (2022-01 to 2023-12) - 最新数据
7. **最近3年** (2021-01 to 2023-12) - 包含通胀期
8. **自定义时间段** - 自己指定日期

### 方法2: 直接在Python中使用

```python
from scripts.fetch_real_data import RealDataFetcher

# 创建获取器
fetcher = RealDataFetcher()

# 获取数据
returns_df = fetcher.fetch_data(
    start_date='2022-01-01',
    end_date='2023-12-31',
    period='monthly'
)

# 保存数据
fetcher.save_to_csv(returns_df, 'returns_data_2023.csv')

# 查看统计
stats = fetcher.get_data_statistics(returns_df)
print(stats)
```

## 支持的投资标的

| 代码 | 名称 | 说明 |
|------|------|------|
| SHY | 3-Year Treasury Bond ETF | 短期国债 |
| XLB | Materials Sector ETF | 材料行业 |
| XLE | Energy Sector ETF | 能源行业 |
| XLF | Financial Sector ETF | 金融行业 |
| XLI | Industrial Sector ETF | 工业行业 |
| XLK | Technology Sector ETF | 科技行业 |
| XLP | Consumer Staples ETF | 日用消费品 |
| XLU | Utilities Sector ETF | 公用事业 |
| XLV | Healthcare Sector ETF | 医疗保健 |

这些都是真实的美股ETF，数据来自Yahoo Finance。

## 使用真实数据运行分析

获取数据后，修改主程序使用新数据：

### 方法1: 修改main.py

编辑 `src/main.py`，修改数据文件路径：

```python
# 原来的
data_path = Path(__file__).parent.parent / "data" / "returns_data.csv"

# 改为
data_path = Path(__file__).parent.parent / "data" / "returns_data_recent_2y.csv"
```

然后运行：
```bash
python src/main.py
```

### 方法2: 创建对比分析

我们提供了一个对比分析脚本，可以同时分析多个时期：

```bash
python scripts/compare_periods.py
```

## 数据格式

生成的CSV文件格式与教材一致：

```csv
Year-Month,SHY,XLB,XLE,XLF,XLI,XLK,XLP,XLU,XLV
2022-01,1.002,0.985,1.126,0.967,0.982,0.894,0.992,0.951,0.973
2022-02,0.998,1.018,1.089,0.983,1.023,0.965,1.012,1.035,0.989
...
```

每个值表示：该月末价格 / 上月末价格（月度收益率）

## 不同时期的特点

### 金融危机期 (2007-2009)
- **特点**: 极端风险，大幅波动
- **现象**: 能源XLE暴跌，债券SHY避险
- **教训**: 分散投资的重要性

### 疫情期 (2019-2021)
- **特点**: V型反转，科技股强势
- **现象**: XLK（科技）表现优异
- **教训**: 市场快速恢复能力

### 最近期 (2022-2023)
- **特点**: 高通胀，加息周期
- **现象**: 债券和股票同跌
- **教训**: 传统分散策略失效

## 分析建议

### 1. 对比不同时期

获取多个时期的数据，对比：
- 有效前沿的位置和形状
- 最优投资组合的变化
- 不同行业的表现

### 2. 滚动窗口分析

使用滚动窗口（如24个月）：
- 模拟实际投资决策
- 观察模型稳定性
- 发现市场规律变化

### 3. 压力测试

使用包含危机的数据：
- 测试模型在极端情况下的表现
- 评估风险控制效果
- 优化风险参数μ

## 注意事项

### ⚠️ 数据质量
- Yahoo Finance数据可能有缺失或延迟
- 建议验证关键日期的数据
- 可以对比多个数据源

### ⚠️ 市场环境变化
- 历史数据不能预测未来
- 不同时期市场结构不同
- 需要定期更新模型

### ⚠️ 技术限制
- 需要稳定的网络连接
- Yahoo Finance可能限制访问频率
- 建议缓存已下载的数据

## 示例：完整工作流

```bash
# 1. 安装依赖
pip install yfinance

# 2. 获取最近2年数据
python scripts/fetch_real_data.py
# 选择选项6

# 3. 运行分析（使用新数据）
# 编辑src/main.py修改数据路径
python src/main.py

# 4. 查看结果
ls -lh results/

# 5. 对比教材数据和真实数据
python scripts/compare_periods.py
```

## 扩展功能

### 添加更多ETF

编辑 `fetch_real_data.py`，在 `tickers` 字典中添加：

```python
self.tickers = {
    'SHY': '3-Year Treasury Bond ETF',
    # ... 原有的
    'QQQ': 'NASDAQ-100 ETF',  # 新增
    'SPY': 'S&P 500 ETF',     # 新增
}
```

### 使用其他数据周期

修改 `period` 参数：
- `'daily'`: 日度数据
- `'weekly'`: 周度数据
- `'monthly'`: 月度数据（默认）

### 导出到其他格式

在脚本中添加：
```python
# Excel格式
returns_df.to_excel('data.xlsx')

# JSON格式
returns_df.to_json('data.json')
```

## 故障排除

### 问题1: ModuleNotFoundError: No module named 'yfinance'
**解决**: `pip install yfinance`

### 问题2: 网络连接错误
**解决**: 
- 检查网络连接
- 尝试使用VPN
- 稍后重试

### 问题3: 数据缺失
**解决**:
- 检查日期范围是否合理
- 某些早期数据可能不存在
- 使用较新的日期范围

### 问题4: 下载速度慢
**解决**:
- 减少时间跨度
- 分批下载
- 使用缓存

## 相关资源

- Yahoo Finance: https://finance.yahoo.com/
- yfinance文档: https://github.com/ranaroussi/yfinance
- ETF列表: https://etfdb.com/

---

**提示**: 真实数据会让分析更有实际意义，但也更复杂。建议先用教材数据验证模型，再用真实数据进行扩展分析。

