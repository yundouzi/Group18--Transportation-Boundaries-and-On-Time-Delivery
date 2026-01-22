import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
import warnings
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径
input_file = r"C:\Users\sq\Desktop\11.27\final.csv"
output_dir = r"C:\Users\sq\Desktop\11.27\4，二环为基准"

# 创建输出文件夹
os.makedirs(output_dir, exist_ok=True)

# 读取数据
print("正在读取数据...")
try:
    df = pd.read_csv(input_file, encoding='utf-8')
    print("使用UTF-8编码读取成功")
except UnicodeDecodeError:
    try:
        df = pd.read_csv(input_file, encoding='gbk')
        print("使用GBK编码读取成功")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(input_file, encoding='latin1')
            print("使用latin1编码读取成功")
        except Exception as e:
            print(f"读取文件失败: {e}")
            exit()

print(f"数据读取完成，共 {len(df)} 条记录")
print(f"数据列名: {list(df.columns)}")

# 显示数据基本信息
print("\n数据基本信息:")
print(df.info())

# 显示前几行数据
print("\n前5行数据:")
print(df.head())

# 检查必要的列是否存在
required_cols = ['i_count', 'j_count', 'POP_j', 'BORDER', 'DIS_ij', '环线', 'OD_ij']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print(f"警告: 缺少必要的列: {missing_cols}")
    print(f"可用列: {list(df.columns)}")
    
    # 尝试寻找相似的列名
    print("\n尝试寻找相似的列名...")
    all_cols = list(df.columns)
    for required in missing_cols:
        similar = []
        if required == '环线':
            similar = [col for col in all_cols if '环' in col or 'ring' in col.lower()]
        elif required == 'OD_ij':
            similar = [col for col in all_cols if 'OD' in col or '流量' in col]
        else:
            similar = [col for col in all_cols if required.lower().replace('_', '') in col.lower().replace('_', '')]
        
        if similar:
            print(f"  对于 '{required}'，找到相似列: {similar}")
            # 询问用户是否使用第一个匹配的列
            use_col = similar[0]
            print(f"  将使用 '{use_col}' 作为 '{required}'")
            df.rename(columns={use_col: required}, inplace=True)
        else:
            print(f"  未找到与 '{required}' 相似的列")
    
    # 重新检查是否所有必要列都存在
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"错误: 仍然缺少必要的列: {missing_cols}")
        exit()

# 数据预处理
print("\n正在预处理数据...")

# 只保留OD_ij > 0的观测值，因为ln(0)是未定义的
df = df[df['OD_ij'] > 0]
print(f"删除OD_ij <= 0的记录后，剩余 {len(df)} 条记录")

# 只保留POP_j > 0的观测值，因为ln(0)是未定义的
df = df[df['POP_j'] > 0]
print(f"删除POP_j <= 0的记录后，剩余 {len(df)} 条记录")

# 创建因变量: ln(OD_ij)
df['ln_OD_ij'] = np.log(df['OD_ij'])

# 创建自变量
# 1. ln(i_count)
df['ln_i_count'] = np.log(df['i_count'])

# 2. ln(j_count + 1)
df['ln_j_count_plus1'] = np.log(df['j_count'] + 1)

# 3. ln(POP_j)
df['ln_POP_j'] = np.log(df['POP_j'])

# 查看环线列的唯一值
print("\n环线列的唯一值:")
print(df['环线'].unique())

# 将环线转换为虚拟变量 (二环为基准类别)
df['Ring_3'] = (df['环线'] == '三环').astype(int)
df['Ring_4'] = (df['环线'] == '四环').astype(int)
df['Ring_5'] = (df['环线'] == '五环').astype(int)

print("\n环线分布:")
print(df['环线'].value_counts())

# 删除缺失值
clean_cols = ['ln_OD_ij', 'ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij', 'Ring_3', 'Ring_4', 'Ring_5']
df_clean = df.dropna(subset=clean_cols)
print(f"清洗后数据条数: {len(df_clean)} (原始: {len(df)})")

# 描述性统计
print("\n描述性统计:")
desc_stats = df_clean[clean_cols].describe()
print(desc_stats)

# 保存描述性统计到文件
desc_stats.to_excel(os.path.join(output_dir, '描述性统计.xlsx'))

# 相关性分析
print("\n相关性矩阵:")
corr_matrix = df_clean[clean_cols].corr()
print(corr_matrix)

# 保存相关性矩阵
corr_matrix.to_excel(os.path.join(output_dir, '相关性矩阵.xlsx'))

# 绘制相关性热图
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('变量相关性热图')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '相关性热图.png'), dpi=300, bbox_inches='tight')
plt.close()

# 准备回归数据
# 根据更新后的回归模型构建X
X_columns = ['ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij', 'Ring_3', 'Ring_4', 'Ring_5']
X = df_clean[X_columns]
y = df_clean['ln_OD_ij']

# 添加常数项
X = sm.add_constant(X)

# 执行OLS回归
print("\n正在执行回归分析...")
print(f"使用自变量: {X_columns}")
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
    '变量': ['const'] + X_columns,
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
fig, axes = plt.subplots(3, 3, figsize=(15, 15))

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

# 4-9. 每个自变量的残差图
for i, col in enumerate(X_columns[:6]):  # 前6个自变量
    row = (i // 3) + 1
    col_idx = i % 3
    axes[row, col_idx].scatter(df_clean[col], residuals, alpha=0.5)
    axes[row, col_idx].axhline(y=0, color='r', linestyle='--')
    axes[row, col_idx].set_xlabel(col)
    axes[row, col_idx].set_ylabel('残差')
    axes[row, col_idx].set_title(f'残差 vs {col}')

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
    'ln_j_count_plus1': 'ln(j_count+1)',
    'ln_POP_j': 'ln(POP_j)',
    'BORDER': 'BORDER',
    'DIS_ij': 'DIS_ij',
    'Ring_3': 'Ring_3',
    'Ring_4': 'Ring_4',
    'Ring_5': 'Ring_5'
}

for col in X_columns:
    coef = results.params[col]
    var_name = variable_names.get(col, col)
    equation += f" + {coef:.4f}*{var_name}"

print("\n回归方程:")
print(equation)

# 保存回归方程
with open(os.path.join(output_dir, '回归方程.txt'), 'w', encoding='utf-8') as f:
    f.write("回归模型:\n")
    f.write("ln(OD_ij) = β0 + β1 × ln(i_count) + β2 × ln(j_count+1) + β3 × ln(POP_j) + β4 × BORDER + β5 × DIS_ij + β6 × Ring_3 + β7 × Ring_4 + β8 × Ring_5 + ε\n\n")
    f.write("估计的回归方程:\n")
    f.write(equation + "\n\n")
    f.write("变量说明:\n")
    f.write("ln(OD_ij): OD流量的自然对数\n")
    f.write("const (β0): 常数项/截距项\n")
    f.write("ln_i_count (β1): ln(i_count)\n")
    f.write("ln_j_count_plus1 (β2): ln(j_count+1)\n")
    f.write("ln_POP_j (β3): ln(POP_j)\n")
    f.write("BORDER (β4): 边界效应\n")
    f.write("DIS_ij (β5): i-j距离\n")
    f.write("Ring_3 (β6): 三环虚拟变量（相对于二环基准组）\n")
    f.write("Ring_4 (β7): 四环虚拟变量（相对于二环基准组）\n")
    f.write("Ring_5 (β8): 五环虚拟变量（相对于二环基准组）\n")
    f.write("ε: 随机误差项\n")

# 计算方差膨胀因子(VIF)（检测多重共线性）
print("\n计算方差膨胀因子(VIF)...")
vif_data = pd.DataFrame()
vif_data["变量"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print(vif_data)

# 保存VIF结果
vif_data.to_excel(os.path.join(output_dir, '方差膨胀因子(VIF).xlsx'), index=False)

# 绘制变量分布图
variables_to_plot = ['ln_i_count', 'ln_j_count_plus1', 'ln_POP_j', 'BORDER', 'DIS_ij', 'Ring_3', 'Ring_4', 'Ring_5', 'ln_OD_ij']

num_plots = len(variables_to_plot)
if num_plots > 0:
    # 确定子图布局
    nrows = (num_plots + 2) // 3  # 向上取整
    fig, axes = plt.subplots(nrows, 3, figsize=(15, 5*nrows))
    axes = axes.flatten() if nrows > 1 else [axes]
    
    titles = {
        'ln_i_count': 'ln(i_count)',
        'ln_j_count_plus1': 'ln(j_count+1)',
        'ln_POP_j': 'ln(POP_j)',
        'BORDER': '边界效应',
        'DIS_ij': '距离',
        'Ring_3': '三环虚拟变量',
        'Ring_4': '四环虚拟变量',
        'Ring_5': '五环虚拟变量',
        'ln_OD_ij': 'ln(OD_ij)'
    }
    
    for i, var in enumerate(variables_to_plot):
        ax = axes[i]
        if var in ['BORDER', 'Ring_3', 'Ring_4', 'Ring_5']:
            # 对于分类变量，使用条形图
            df_clean[var].value_counts().sort_index().plot(kind='bar', ax=ax)
            ax.set_xlabel(var)
            ax.set_ylabel('频数')
        else:
            # 对于连续变量，使用直方图
            df_clean[var].hist(bins=30, edgecolor='black', alpha=0.7, ax=ax)
            ax.set_xlabel(var)
            ax.set_ylabel('频数')
        ax.set_title(titles.get(var, var))
    
    # 隐藏多余的子图
    for i in range(num_plots, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '变量分布图.png'), dpi=300, bbox_inches='tight')
    plt.close()

# 环线对比分析
print("\n=== 环线对比分析 ===")
ring_summary = df_clean.groupby('环线').agg({
    'ln_OD_ij': ['mean', 'std', 'count'],
    'ln_i_count': 'mean',
    'ln_j_count_plus1': 'mean',
    'ln_POP_j': 'mean',
    'BORDER': 'mean',
    'DIS_ij': 'mean'
}).round(4)

print(ring_summary)
ring_summary.to_excel(os.path.join(output_dir, '环线对比分析.xlsx'))

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

# 保存重要变量分析
if not sig_vars.empty:
    sig_vars.to_excel(os.path.join(output_dir, '显著变量分析.xlsx'), index=False)

# 系数解释
print("\n=== 系数解释 ===")
for idx, coef in enumerate(results.params):
    col_name = results.params.index[idx]
    print(f"{col_name}: {coef:.6f}")

# 输出回归公式（详细版）
print("\n=== 详细回归公式 ===")
formula_parts = []
for idx, coef in enumerate(results.params):
    col_name = results.params.index[idx]
    if col_name == 'const':
        formula_parts.append(f"{coef:.4f}")
    else:
        formula_parts.append(f"{coef:.6f} × {col_name}")

regression_formula = "ln(OD_ij) = " + " + ".join(formula_parts) + " + ε"
print(regression_formula)

print(f"\n=== 处理完成 ===")