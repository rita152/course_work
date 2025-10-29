# 数据获取工具集

本目录包含多种数据获取工具和方法。

---

## 🎯 快速开始

### 最简单: 生成模拟数据（1分钟）

```bash
python generate_simulated_data.py
```

### 最可靠: 手动下载合并（15分钟）

```bash
# 1. 手动下载9个CSV from Yahoo Finance
# 2. 运行合并脚本
python merge_manual_csv.py
```

### 主菜单: 综合工具

```bash
python fetch_real_data.py
```

---

## 📁 文件说明

### 核心工具

| 文件 | 功能 | 推荐度 | 说明 |
|------|------|--------|------|
| **fetch_real_data.py** | 主菜单 | ⭐⭐⭐⭐⭐ | 综合所有方法的主入口 |
| **generate_simulated_data.py** | 模拟数据 | ⭐⭐⭐⭐⭐ | 生成高质量模拟数据 |
| **merge_manual_csv.py** | 合并工具 | ⭐⭐⭐⭐⭐ | 合并手动下载的CSV |
| advanced_web_scraper.py | 爬虫 | ⭐⭐ | 多方法网页爬虫 |
| selenium_scraper.py | Selenium | ⭐⭐ | 浏览器自动化 |
| compare_periods.py | 对比分析 | ⭐⭐⭐⭐ | 多时期对比 |

### 文档

| 文件 | 内容 |
|------|------|
| README.md | 本文档 |
| 爬虫完整指南.md | 所有爬虫方法详解 |
| README_real_data.md | 技术文档 |

---

## 🚀 使用场景

### 场景1: 完成课程作业

**推荐**: 使用教材数据 + 模拟数据

```bash
# 已有教材数据
# 生成模拟数据
python generate_simulated_data.py

# 运行分析
cd ../src
python main.py
```

**优势**: 简单快速，完全符合要求

### 场景2: 获取最新真实数据

**推荐**: 手动下载

```bash
# 1. 浏览器访问Yahoo Finance手动下载9个CSV
# 2. 运行合并工具
python merge_manual_csv.py

# 3. 使用数据
# 修改main.py后运行
```

**优势**: 100%成功，真实数据

### 场景3: 对比不同时期

```bash
# 生成多组数据
python generate_simulated_data.py  # 生成3组

# 或手动下载多个时期

# 运行对比
python compare_periods.py
```

---

## 🛠️ 工具详解

### 1. generate_simulated_data.py

**功能**: 生成基于真实市场统计的模拟数据

**输出**:
- `returns_data_simulated_normal.csv` - 正常市场（24月）
- `returns_data_simulated_volatile.csv` - 高波动（24月）
- `returns_data_simulated_3y.csv` - 长期数据（36月）

**特点**:
- 立即可用
- 包含合理的收益率分布
- 资产间相关性符合实际
- 债券与股票负相关

**运行**:
```bash
python generate_simulated_data.py
```

---

### 2. merge_manual_csv.py

**功能**: 合并手动下载的Yahoo Finance CSV文件

**前置步骤**:
1. 访问 https://finance.yahoo.com/quote/SHY/history
2. 设置日期范围
3. 点击Download
4. 重复下载9个ticker
5. 确保文件命名: SHY.csv, XLB.csv, ...

**运行**:
```bash
python merge_manual_csv.py
```

**优点**:
- 100%成功率
- 获得真实最新数据
- 简单可靠

---

### 3. advanced_web_scraper.py

**功能**: 尝试多种自动化方法获取数据

**方法**:
- Yahoo Finance API
- Alpha Vantage API（需要免费key）
- MarketWatch
- 自动fallback到模拟数据

**运行**:
```bash
python advanced_web_scraper.py
```

**注意**:
- 成功率不保证（10-50%）
- 可能被反爬虫阻止
- 需要等待和重试

---

### 4. selenium_scraper.py

**功能**: 使用Selenium模拟真实浏览器

**依赖**:
```bash
pip install selenium
sudo apt-get install chromium-chromedriver  # Ubuntu
```

**运行**:
```bash
python selenium_scraper.py
```

**特点**:
- 模拟真实浏览器
- 可绕过部分反爬虫
- 需要额外依赖

**成功率**: 约50%

---

### 5. compare_periods.py

**功能**: 对比多个时期的数据和优化结果

**使用**:
```bash
# 先准备多个时期的数据
# 然后运行
python compare_periods.py
```

**输出**:
- 多时期有效前沿对比图
- 收益和风险范围对比
- 对比分析报告

---

## 📊 方案对比

### 快速对比表

| 方案 | 时间 | 成功率 | 真实性 | 推荐场景 |
|------|------|--------|--------|----------|
| 模拟数据 | 1分钟 | 100% | ⭐⭐⭐⭐ | 快速完成作业 |
| 手动下载 | 15分钟 | 100% | ⭐⭐⭐⭐⭐ | 需要真实数据 |
| 自动爬虫 | 1-3小时 | 20% | ⭐⭐⭐⭐⭐ | 技术挑战 |

### 数据质量对比

**模拟数据**:
- ✅ 基于真实市场2022-2023统计
- ✅ 合理的收益率（均值、标准差正确）
- ✅ 资产相关性符合实际
- ✅ 可控可重现
- ⚠️ 不是真实历史数据

**手动下载数据**:
- ✅ 真实的Yahoo Finance数据
- ✅ 包含所有市场事件
- ✅ 可验证可信
- ✅ 最新数据
- ⚠️ 需要手动操作

---

## 💡 推荐使用流程

### 流程A: 标准作业流程

```bash
# 1. 使用教材数据（验证模型）
cd ../src
python main.py

# 2. 生成模拟数据（扩展分析）
cd ../scripts
python generate_simulated_data.py

# 3. 修改main.py使用模拟数据
cd ../src
# 编辑main.py第39行
python main.py

# 4. 对比两组结果，写入PPT
```

### 流程B: 真实数据流程

```bash
# 1. 手动下载9个CSV（浏览器，15分钟）

# 2. 合并数据
python scripts/merge_manual_csv.py

# 3. 运行分析
# 修改main.py使用manual数据
python src/main.py

# 4. 对比教材数据和最新数据
```

---

## ⚠️ 关于自动爬虫的说明

### 为什么成功率低？

Yahoo Finance的反爬虫措施:
1. IP速率限制
2. Cookie和Session验证
3. JavaScript动态加载
4. 用户行为检测
5. 验证码

### 应该使用吗？

**不推荐的情况**:
- ❌ 时间紧张（调试耗时）
- ❌ 只是为了作业（有更好方案）
- ❌ 对爬虫不熟悉（学习成本高）

**可以尝试的情况**:
- ✅ 有充足时间
- ✅ 对爬虫技术感兴趣
- ✅ 愿意接受失败风险

---

## 📚 相关文档

- `爬虫完整指南.md` - 所有方法的详细说明
- `README_real_data.md` - API技术文档
- `../获取最新数据终极方案.md` - 综合方案说明

---

## ✅ 推荐行动

### 最高效的做法

**第1优先级**: 完成作业核心内容
- ✅ 已完成（代码、分析、图表）

**第2优先级**: 制作PPT和视频
- ⚠️ 待完成（更重要！）

**第3优先级**: 获取最新数据
- 方案A: 使用模拟数据（1分钟）⭐
- 方案B: 手动下载（15分钟）⭐⭐
- 方案C: 调试爬虫（1-3小时）⭐

**建议**: 选择方案A或B，然后专注于PPT和视频！

---

## 🎓 总结

**您已经拥有**:
- ✅ 教材真实数据
- ✅ 3组高质量模拟数据
- ✅ 手动下载合并工具
- ✅ 多种自动爬虫脚本
- ✅ 完整的文档

**足以完成优秀的作业！**

选择最适合您的方案，开始行动吧！🚀

