import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径
input_file = r"C:\Users\sq\Desktop\grid2\grid2.xlsx"
output_dir = r"C:\Users\sq\Desktop\grid2\12.2结果5ln（设施点+1）"

# 创建输出文件夹
os.makedirs(output_dir, exist_ok=True)

# 读取数据
print("正在读取数据...")
df = pd.read_excel(input_file, engine='openpyxl')
print(f"数据读取完成，共 {len(df)} 条记录")
print(f"数据列名: {list(df.columns)}")

# 显示数据基本信息
print("\n数据基本信息:")
print(df.info())

# 显示前几行数据
print("\n前5行数据:")
print(df.head())

# 检查必要的列是否存在 - 更新为实际的列名
required_cols = ['i_count', 'j_count', 'POP_j', 'BORDER', 'DIS_ij', 'OD_ij']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"错误: 缺少必要的列: {missing_cols}")
    print(f"可用列: {list(df.columns)}")
    
    # 尝试寻找相似的列名
    print("\n尝试寻找相似的列名...")
    all_cols = list(df.columns)
    for required in required_cols:
        if required not in all_cols:
            similar = [col for col in all_cols if required.lower().replace('_', '') in col.lower().replace('_', '')]
            if similar:
                print(f"  对于 '{required}'，找到相似列: {similar}")
    
    exit()

# 数据预处理
print("\n正在预处理数据...")

# 创建因变量: ln(OD_ij)
# 为了防止取对数时出现无穷值，对OD_ij加1
df['ln_OD'] = np.log(df['OD_ij'] + 1)

# 创建自变量
# 1. ln(i_count)
df['ln_i_count'] = np.log(df['i_count'])

# 2. ln(j_count + 1)
df['ln_j_count_plus1'] = np.log(df['j_count'] + 1)

# 3. ln(POP_j)
df['ln_POP_j'] = np.log(df['POP_j'])

# 4. BORDER (已经是0/1变量，直接使用)
# 5. DIS_ij (距离变量，直接使用) - 更新为DIS_ij

# 删除缺失值
df_clean = df.dropna(subset=['ln_OD', 'ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij'])
print(f"清洗后数据条数: {len(df_clean)}")

# 描述性统计
print("\n描述性统计:")
desc_stats = df_clean[['ln_OD', 'ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij']].describe()
print(desc_stats)

# 保存描述性统计到文件
desc_stats.to_excel(os.path.join(output_dir, '描述性统计.xlsx'))

# 相关性分析
print("\n相关性矩阵:")
corr_matrix = df_clean[['ln_OD', 'ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij']].corr()
print(corr_matrix)

# 保存相关性矩阵
corr_matrix.to_excel(os.path.join(output_dir, '相关性矩阵.xlsx'))

# 绘制相关性热图
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('变量相关性热图')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '相关性热图.png'), dpi=300, bbox_inches='tight')
plt.close()

# 准备回归数据 - 更新为使用DIS_ij
X = df_clean[['ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij']]
y = df_clean['ln_OD']

# 添加常数项
X = sm.add_constant(X)

# 执行OLS回归
print("\n正在执行回归分析...")
model = sm.OLS(y, X)
results = model.fit()

# 显示回归结果
print("\n回归结果:")
print(results.summary())

# 保存回归结果到文本文件
with open(os.path.join(output_dir, '回归结果.txt'), 'w', encoding='utf-8') as f:
    f.write(str(results.summary()))

# 保存回归结果到Excel
results_df = pd.DataFrame({
    '变量': ['const'] + list(X.columns[1:]),
    '系数': results.params.values,
    '标准误': results.bse.values,
    't值': results.tvalues.values,
    'P值': results.pvalues.values,
    '95%置信区间下限': results.conf_int()[0].values,
    '95%置信区间上限': results.conf_int()[1].values
})

results_df.to_excel(os.path.join(output_dir, '回归系数.xlsx'), index=False)

# 残差分析
print("\n残差分析...")
residuals = results.resid
fitted = results.fittedvalues

# 绘制残差图
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 1. 残差 vs 拟合值
axes[0, 0].scatter(fitted, residuals, alpha=0.5)
axes[0, 0].axhline(y=0, color='r', linestyle='--')
axes[0, 0].set_xlabel('拟合值')
axes[0, 0].set_ylabel('残差')
axes[0, 0].set_title('残差 vs 拟合值')

# 2. 残差QQ图
stats.probplot(residuals, dist="norm", plot=axes[0, 1])
axes[0, 1].set_title('残差QQ图')

# 3. 残差直方图
axes[0, 2].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
axes[0, 2].set_xlabel('残差')
axes[0, 2].set_ylabel('频数')
axes[0, 2].set_title('残差直方图')

# 4. 每个自变量的残差图
for i, col in enumerate(X.columns[1:4]):  # 前3个连续变量
    axes[1, i].scatter(df_clean[col], residuals, alpha=0.5)
    axes[1, i].axhline(y=0, color='r', linestyle='--')
    axes[1, i].set_xlabel(col)
    axes[1, i].set_ylabel('残差')
    axes[1, i].set_title(f'残差 vs {col}')

# 调整布局
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '残差分析图.png'), dpi=300, bbox_inches='tight')
plt.close()

# 模型诊断统计
print("\n模型诊断统计:")
print(f"R-squared: {results.rsquared:.4f}")
print(f"Adj. R-squared: {results.rsquared_adj:.4f}")
print(f"F-statistic: {results.fvalue:.2f}")
print(f"Prob (F-statistic): {results.f_pvalue:.4e}")
print(f"AIC: {results.aic:.2f}")
print(f"BIC: {results.bic:.2f}")

# 保存模型诊断统计
diagnostics = pd.DataFrame({
    '指标': ['R-squared', 'Adj. R-squared', 'F-statistic', 'Prob (F-statistic)', 'AIC', 'BIC', '观测数'],
    '值': [results.rsquared, results.rsquared_adj, results.fvalue, results.f_pvalue, results.aic, results.bic, len(df_clean)]
})
diagnostics.to_excel(os.path.join(output_dir, '模型诊断统计.xlsx'), index=False)

# 绘制拟合效果图
plt.figure(figsize=(10, 6))
plt.scatter(fitted, y, alpha=0.5, label='观测值')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', label='完美拟合线')
plt.xlabel('拟合值')
plt.ylabel('实际值')
plt.title('拟合效果图')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '拟合效果图.png'), dpi=300, bbox_inches='tight')
plt.close()

# 预测值和实际值对比
comparison_df = pd.DataFrame({
    '实际值': y.values,
    '拟合值': fitted.values,
    '残差': residuals.values,
    '标准化残差': (residuals - residuals.mean()) / residuals.std()
})
comparison_df.to_excel(os.path.join(output_dir, '预测对比.xlsx'), index=False)

# 回归方程
equation = f"ln(OD_ij) = {results.params['const']:.4f}"
variable_names = {
    'ln_i_count': 'ln(i_count)',
    'ln_j_count_plus1': 'ln(j_count + 1)',
    'ln_POP_j': 'ln(POP_j)',
    'BORDER': 'BORDER',
    'DIS_ij': 'DIS_ij'
}

for col in X.columns[1:]:
    coef = results.params[col]
    var_name = variable_names.get(col, col)
    equation += f" + {coef:.4f}*{var_name}"

print("\n回归方程:")
print(equation)

# 保存回归方程
with open(os.path.join(output_dir, '回归方程.txt'), 'w', encoding='utf-8') as f:
    f.write("回归方程:\n")
    f.write(equation + "\n\n")
    f.write("变量说明:\n")
    f.write("ln_i_count = ln(i_count)\n")
    f.write("ln_j_count_plus1 = ln(j_count + 1)\n")
    f.write("ln_POP_j = ln(POP_j)\n")
    f.write("BORDER = BORDER (0/1变量)\n")
    f.write("DIS_ij = 距离 (km)\n")

# 变量的描述性统计和VIF计算（检测多重共线性）
print("\n计算方差膨胀因子(VIF)...")
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 计算VIF
vif_data = pd.DataFrame()
vif_data["变量"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print(vif_data)

# 保存VIF结果
vif_data.to_excel(os.path.join(output_dir, '方差膨胀因子(VIF).xlsx'), index=False)

# 绘制变量分布图
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
variables_to_plot = ['ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij', 'ln_OD']
titles = ['ln(i_count)', 'ln(j_count+1)', 'ln(POP_j)', '边界效应', '距离', 'ln(OD_ij)']

for i, (var, title) in enumerate(zip(variables_to_plot, titles)):
    ax = axes[i//3, i%3]
    if var == 'BORDER':
        # 对于分类变量，使用条形图
        df_clean[var].value_counts().sort_index().plot(kind='bar', ax=ax)
        ax.set_xlabel(var)
        ax.set_ylabel('频数')
    else:
        # 对于连续变量，使用直方图
        df_clean[var].hist(bins=30, edgecolor='black', alpha=0.7, ax=ax)
        ax.set_xlabel(var)
        ax.set_ylabel('频数')
    ax.set_title(title)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, '变量分布图.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"\n所有结果已保存到: {output_dir}")

# 显示重要变量
print("\n重要变量分析:")
sig_vars = results_df[results_df['P值'] < 0.05]
print(f"在95%置信水平下显著的变量 ({len(sig_vars)}个):")
for _, row in sig_vars.iterrows():
    var = row['变量']
    coef = row['系数']
    pval = row['P值']
    significance = "非常显著" if pval < 0.001 else "显著" if pval < 0.01 else "较显著" if pval < 0.05 else ""
    direction = "正向" if coef > 0 else "负向"
    print(f"  {var}: 系数={coef:.4f}, P值={pval:.4e} ({significance}, {direction}影响)")