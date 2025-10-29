#!/bin/bash

# 投资组合优化系统 - 运行脚本

echo "======================================================================"
echo "              投资组合选择优化系统"
echo "           基于MAD风险度量的线性规划方法"
echo "======================================================================"
echo ""

# 检查conda环境
if ! conda env list | grep -q "cource_work"; then
    echo "错误: conda环境 'cource_work' 不存在！"
    echo "请先创建环境: conda create -n cource_work python=3.10"
    exit 1
fi

echo "1. 激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate cource_work

echo "2. 检查依赖包..."
pip list | grep -q "pulp" || {
    echo "   安装依赖包..."
    pip install -r requirements.txt
}

echo "3. 运行优化程序..."
cd src
python main.py

echo ""
echo "======================================================================"
echo "程序运行完成！"
echo "======================================================================"
echo ""
echo "结果文件保存在 results/ 目录："
echo "  - efficient_frontier.png          有效前沿图"
echo "  - portfolio_composition.png       投资组合配置图"
echo "  - mu_sensitivity.png              μ参数敏感性分析"
echo "  - portfolio_pie_mu_X.png          投资组合饼图"
echo "  - correlation_heatmap.png         资产相关系数热力图"
echo "  - model_comparison.png            模型对比图"
echo "  - mad_results_summary.csv         MAD模型结果数据"
echo "  - variance_results_summary.csv    方差模型结果数据"
echo ""
echo "详细说明请查看 README.md"
echo ""

