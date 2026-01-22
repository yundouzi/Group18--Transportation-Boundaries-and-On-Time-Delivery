import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建保存结果的目录
output_dir = r'C:\Users\sq\Desktop\2-5\自变量比较'
os.makedirs(output_dir, exist_ok=True)

# 定义文件路径和环线名称
ring_data = {
    '二环': r'C:\Users\sq\Desktop\2-5\end2-od.xlsx',
    '三环': r'C:\Users\sq\Desktop\2-5\end3-od.xlsx', 
    '四环': r'C:\Users\sq\Desktop\2-5\end4-od.xlsx',
    '五环': r'C:\Users\sq\Desktop\2-5\end5-od.xlsx'
}

# 可能的列名模式
possible_names = {
    'o_count': ['o_count', '出栅格d_count', '出发地人口', 'O_count', '出发栅格d_count'],
    'd_count': ['d_count', '到达栅格d_count', '目的地人口', 'D_count', '到达栅格d_count'],
    'POPj': ['POPj', '到达栅格工作人口', '工作人口', '就业人口', '到达栅格工作人口'],
    'BORDER': ['BORDER', '边界', 'border', '边界']
}

print("开始读取和分析各环线数据...")

# 存储各环线的统计信息，避免存储整个数据集
ring_stats = {}

for ring_name, file_path in ring_data.items():
    print(f"\n正在处理{ring_name}数据...")
    
    try:
        # 读取数据时只读取需要的列，减少内存使用
        df = pd.read_excel(file_path)
        print(f"{ring_name}数据读取成功，共{len(df)}行，{len(df.columns)}列")
        
        # 查找需要的列
        found_columns = {}
        for col_type, possible_list in possible_names.items():
            for possible_name in possible_list:
                if possible_name in df.columns:
                    found_columns[col_type] = possible_name
                    break
        
        if len(found_columns) < 4:
            print(f"警告: {ring_name}缺少必要的列，跳过该环线")
            continue
        
        # 只提取需要的列
        df_clean = df[list(found_columns.values())].copy()
        df_clean.columns = ['o_count', 'd_count', 'POPj', 'BORDER']
        
        # 删除缺失值
        df_clean = df_clean.dropna()
        print(f"{ring_name}有效数据: {len(df_clean)}行")
        
        # 对大数据集进行抽样，减少内存使用
        sample_size = min(5000, len(df_clean))  # 最多抽样5000个点
        if len(df_clean) > sample_size:
            df_sample = df_clean.sample(n=sample_size, random_state=42)
        else:
            df_sample = df_clean
        
        # 计算统计信息并释放内存
        ring_stats[ring_name] = {
            'count': len(df_clean),
            'o_count': {
                'mean': df_clean['o_count'].mean(),
                'median': df_clean['o_count'].median(),
                'std': df_clean['o_count'].std(),
                'min': df_clean['o_count'].min(),
                'max': df_clean['o_count'].max(),
                'data': df_sample['o_count'].values  # 只保存抽样数据用于绘图
            },
            'd_count': {
                'mean': df_clean['d_count'].mean(),
                'median': df_clean['d_count'].median(),
                'std': df_clean['d_count'].std(),
                'min': df_clean['d_count'].min(),
                'max': df_clean['d_count'].max(),
                'data': df_sample['d_count'].values
            },
            'POPj': {
                'mean': df_clean['POPj'].mean(),
                'median': df_clean['POPj'].median(),
                'std': df_clean['POPj'].std(),
                'min': df_clean['POPj'].min(),
                'max': df_clean['POPj'].max(),
                'data': df_sample['POPj'].values
            },
            'BORDER': {
                'counts': df_clean['BORDER'].value_counts().to_dict(),
                'proportions': (df_clean['BORDER'].value_counts(normalize=True) * 100).to_dict()
            }
        }
        
        # 计算相关系数（只计算连续变量）
        ring_stats[ring_name]['correlations'] = {
            'o_d': df_clean['o_count'].corr(df_clean['d_count']),
            'o_p': df_clean['o_count'].corr(df_clean['POPj']),
            'd_p': df_clean['d_count'].corr(df_clean['POPj'])
        }
        
        # 释放内存
        del df, df_clean, df_sample
        
    except Exception as e:
        print(f"读取{ring_name}数据失败: {e}")

if not ring_stats:
    print("错误: 没有成功读取任何环线数据")
    exit()

print(f"\n成功处理 {len(ring_stats)} 个环线的数据")

# 分别绘制每个图表，避免内存溢出

def create_distribution_comparison():
    """创建分布比较图，分成四个单独的子图"""
    # o_count分布比较
    plt.figure(figsize=(10, 6))
    for ring_name, stats in ring_stats.items():
        plt.hist(stats['o_count']['data'], bins=20, alpha=0.6, label=ring_name, density=True)
    plt.xlabel('o_count')
    plt.ylabel('密度')
    plt.title('各环线o_count分布比较')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线o_count分布比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')  # 降低DPI减少内存
    plt.close()
    print(f"o_count分布比较图已保存到: {plot_path}")
    
    # d_count分布比较
    plt.figure(figsize=(10, 6))
    for ring_name, stats in ring_stats.items():
        plt.hist(stats['d_count']['data'], bins=20, alpha=0.6, label=ring_name, density=True)
    plt.xlabel('d_count')
    plt.ylabel('密度')
    plt.title('各环线d_count分布比较')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线d_count分布比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"d_count分布比较图已保存到: {plot_path}")
    
    # POPj分布比较
    plt.figure(figsize=(10, 6))
    for ring_name, stats in ring_stats.items():
        plt.hist(stats['POPj']['data'], bins=20, alpha=0.6, label=ring_name, density=True)
    plt.xlabel('POPj')
    plt.ylabel('密度')
    plt.title('各环线POPj分布比较')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线POPj分布比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"POPj分布比较图已保存到: {plot_path}")

def create_border_comparison():
    """创建BORDER分布比较图"""
    plt.figure(figsize=(12, 8))
    
    # 获取所有环线的BORDER值
    border_values = set()
    for stats in ring_stats.values():
        border_values.update(stats['BORDER']['counts'].keys())
    border_values = sorted(border_values)
    
    # 创建子图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    for i, (ring_name, stats) in enumerate(ring_stats.items()):
        row = i // 2
        col = i % 2
        
        # 获取该环线的BORDER计数
        counts = [stats['BORDER']['counts'].get(b, 0) for b in border_values]
        proportions = [stats['BORDER']['proportions'].get(b, 0) for b in border_values]
        
        # 条形图
        bars = axes[row, col].bar(border_values, counts, alpha=0.7, color=['lightblue', 'salmon'][:len(border_values)])
        axes[row, col].set_xlabel('BORDER')
        axes[row, col].set_ylabel('频数')
        axes[row, col].set_title(f'{ring_name} - BORDER分布')
        axes[row, col].grid(True, alpha=0.3)
        
        # 添加数值标签
        for j, v in enumerate(counts):
            axes[row, col].text(border_values[j], v + 0.01 * max(counts), str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线BORDER分布比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"BORDER分布比较图已保存到: {plot_path}")
    
    # 创建BORDER比例对比图
    plt.figure(figsize=(10, 6))
    width = 0.2
    x = np.arange(len(border_values))
    
    for i, (ring_name, stats) in enumerate(ring_stats.items()):
        proportions = [stats['BORDER']['proportions'].get(b, 0) for b in border_values]
        plt.bar(x + i * width, proportions, width, label=ring_name, alpha=0.7)
    
    plt.xlabel('BORDER')
    plt.ylabel('比例 (%)')
    plt.title('各环线BORDER比例对比')
    plt.xticks(x + width * (len(ring_stats) - 1) / 2, border_values)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线BORDER比例对比.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"BORDER比例对比图已保存到: {plot_path}")

def create_boxplot_comparison():
    """创建箱线图比较"""
    # o_count箱线图
    plt.figure(figsize=(8, 6))
    data_to_plot = [stats['o_count']['data'] for stats in ring_stats.values()]
    plt.boxplot(data_to_plot, labels=ring_stats.keys())
    plt.ylabel('o_count')
    plt.title('各环线o_count箱线图比较')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线o_count箱线图比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"o_count箱线图比较已保存到: {plot_path}")
    
    # d_count箱线图
    plt.figure(figsize=(8, 6))
    data_to_plot = [stats['d_count']['data'] for stats in ring_stats.values()]
    plt.boxplot(data_to_plot, labels=ring_stats.keys())
    plt.ylabel('d_count')
    plt.title('各环线d_count箱线图比较')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线d_count箱线图比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"d_count箱线图比较已保存到: {plot_path}")
    
    # POPj箱线图
    plt.figure(figsize=(8, 6))
    data_to_plot = [stats['POPj']['data'] for stats in ring_stats.values()]
    plt.boxplot(data_to_plot, labels=ring_stats.keys())
    plt.ylabel('POPj')
    plt.title('各环线POPj箱线图比较')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线POPj箱线图比较.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"POPj箱线图比较已保存到: {plot_path}")

def create_stat_comparison():
    """创建统计指标对比图"""
    ring_names = list(ring_stats.keys())
    x = np.arange(len(ring_names))
    width = 0.25
    
    # 均值对比
    plt.figure(figsize=(10, 6))
    o_means = [stats['o_count']['mean'] for stats in ring_stats.values()]
    d_means = [stats['d_count']['mean'] for stats in ring_stats.values()]
    p_means = [stats['POPj']['mean'] for stats in ring_stats.values()]
    
    plt.bar(x - width, o_means, width, label='o_count', alpha=0.7)
    plt.bar(x, d_means, width, label='d_count', alpha=0.7)
    plt.bar(x + width, p_means, width, label='POPj', alpha=0.7)
    
    plt.xlabel('环线')
    plt.ylabel('均值')
    plt.title('各环线自变量均值对比')
    plt.xticks(x, ring_names)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线自变量均值对比.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"自变量均值对比图已保存到: {plot_path}")

def create_sample_count_plot():
    """创建样本数量对比图"""
    plt.figure(figsize=(8, 6))
    sample_counts = [stats['count'] for stats in ring_stats.values()]
    ring_names = list(ring_stats.keys())
    plt.bar(ring_names, sample_counts, alpha=0.7, color=['red', 'blue', 'green', 'orange'])
    plt.xlabel('环线')
    plt.ylabel('样本数量')
    plt.title('各环线样本数量对比')
    for i, v in enumerate(sample_counts):
        plt.text(i, v + 0.01 * max(sample_counts), str(v), ha='center', va='bottom')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线样本数量对比图.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"样本数量对比图已保存到: {plot_path}")

def create_correlation_plot():
    """创建相关系数对比图"""
    plt.figure(figsize=(10, 6))
    ring_names = list(ring_stats.keys())
    
    # 提取相关系数
    corr_o_d = [stats['correlations']['o_d'] for stats in ring_stats.values()]
    corr_o_p = [stats['correlations']['o_p'] for stats in ring_stats.values()]
    corr_d_p = [stats['correlations']['d_p'] for stats in ring_stats.values()]
    
    x = np.arange(len(ring_names))
    width = 0.25
    
    plt.bar(x - width, corr_o_d, width, label='o_count与d_count', alpha=0.7)
    plt.bar(x, corr_o_p, width, label='o_count与POPj', alpha=0.7)
    plt.bar(x + width, corr_d_p, width, label='d_count与POPj', alpha=0.7)
    
    plt.xlabel('环线')
    plt.ylabel('相关系数')
    plt.title('各环线自变量间相关系数对比')
    plt.xticks(x, ring_names)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, '各环线自变量相关系数对比图.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"相关系数对比图已保存到: {plot_path}")

# 执行绘图函数
print("\n开始生成图表...")
create_distribution_comparison()
create_border_comparison()
create_boxplot_comparison()
create_stat_comparison()
create_sample_count_plot()
create_correlation_plot()

# 生成详细的分析报告
analysis_report = f"""
北京不同环线自变量分布特征分析报告
====================================

数据概况:
--------
总样本数量: {sum([stats['count'] for stats in ring_stats.values()])}
各环线样本分布:
"""

for ring_name, stats in ring_stats.items():
    analysis_report += f"  {ring_name}: {stats['count']} 样本\n"

analysis_report += """
各环线描述性统计:
---------------
"""

for ring_name, stats in ring_stats.items():
    analysis_report += f"""
{ring_name}环线:
  样本数: {stats['count']}
  o_count: 均值={stats['o_count']['mean']:.2f}, 中位数={stats['o_count']['median']:.2f}, 标准差={stats['o_count']['std']:.2f}
  d_count: 均值={stats['d_count']['mean']:.2f}, 中位数={stats['d_count']['median']:.2f}, 标准差={stats['d_count']['std']:.2f}
  POPj: 均值={stats['POPj']['mean']:.2f}, 中位数={stats['POPj']['median']:.2f}, 标准差={stats['POPj']['std']:.2f}
  BORDER分布:
"""

    for border_value, count in stats['BORDER']['counts'].items():
        proportion = stats['BORDER']['proportions'].get(border_value, 0)
        analysis_report += f"    BORDER={border_value}: {count} ({proportion:.2f}%)\n"

analysis_report += """
相关性分析:
---------
"""

for ring_name, stats in ring_stats.items():
    corr = stats['correlations']
    analysis_report += f"""
{ring_name}环线相关系数:
  o_count与d_count: {corr['o_d']:.4f}
  o_count与POPj: {corr['o_p']:.4f}
  d_count与POPj: {corr['d_p']:.4f}
"""

# 添加分析结论
analysis_report += """
分析结论:
-------

1. 分布特征比较:
"""

# 创建样本数量的字典
sample_counts_dict = {ring_name: stats['count'] for ring_name, stats in ring_stats.items()}

# o_count分析
o_count_means = {ring: stats['o_count']['mean'] for ring, stats in ring_stats.items()}
max_o_ring = max(o_count_means, key=o_count_means.get)
min_o_ring = min(o_count_means, key=o_count_means.get)

analysis_report += f"""
- o_count(出发地人口):
  * 均值变化: {max_o_ring}环线最高({o_count_means[max_o_ring]:.2f}), {min_o_ring}环线最低({o_count_means[min_o_ring]:.2f})
"""

# d_count分析
d_count_means = {ring: stats['d_count']['mean'] for ring, stats in ring_stats.items()}
max_d_ring = max(d_count_means, key=d_count_means.get)
min_d_ring = min(d_count_means, key=d_count_means.get)

analysis_report += f"""
- d_count(目的地人口):
  * 均值变化: {max_d_ring}环线最高({d_count_means[max_d_ring]:.2f}), {min_d_ring}环线最低({d_count_means[min_d_ring]:.2f})
"""

# POPj分析
popj_means = {ring: stats['POPj']['mean'] for ring, stats in ring_stats.items()}
max_p_ring = max(popj_means, key=popj_means.get)
min_p_ring = min(popj_means, key=popj_means.get)

analysis_report += f"""
- POPj(工作人口):
  * 均值变化: {max_p_ring}环线最高({popj_means[max_p_ring]:.2f}), {min_p_ring}环线最低({popj_means[min_p_ring]:.2f})
"""

# BORDER分析
# 计算各环线BORDER=1的比例
border_proportions = {}
for ring_name, stats in ring_stats.items():
    border_1_count = stats['BORDER']['counts'].get(1, 0)
    border_proportions[ring_name] = (border_1_count / stats['count']) * 100 if stats['count'] > 0 else 0

max_border_ring = max(border_proportions, key=border_proportions.get) if border_proportions else None
min_border_ring = min(border_proportions, key=border_proportions.get) if border_proportions else None

if max_border_ring and min_border_ring:
    analysis_report += f"""
- BORDER(边界):
  * 边界栅格比例: {max_border_ring}环线最高({border_proportions[max_border_ring]:.2f}%), {min_border_ring}环线最低({border_proportions[min_border_ring]:.2f}%)
"""

# 添加总体趋势分析
max_sample_ring = max(sample_counts_dict, key=sample_counts_dict.get)
min_sample_ring = min(sample_counts_dict, key=sample_counts_dict.get)

analysis_report += f"""
2. 总体趋势:
- 样本分布: {max_sample_ring}环线样本最多({sample_counts_dict[max_sample_ring]}个)，{min_sample_ring}环线样本最少({sample_counts_dict[min_sample_ring]}个)
- 数据离散程度: 各环线标准差分析显示数据分布特征
- 相关性特征: 各环线自变量间相关性存在差异
- 边界分布: 各环线边界栅格比例存在明显差异

3. 建议:
- 针对不同环线的分布特征，可以考虑在回归模型中引入环线作为控制变量
- 对于分布差异较大的环线，建议分别建立模型或使用分层分析
- 边界变量在不同环线的分布差异可能反映了城市空间结构特征
- 进一步分析环线特征与交通流量的关系，为城市规划提供参考
"""

print(analysis_report)

# 保存分析报告
report_file = os.path.join(output_dir, '北京不同环线自变量分布特征分析报告.txt')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(analysis_report)

print(f"分析报告已保存到: {report_file}")
print(f"\n所有分析结果已保存到目录: {output_dir}")

# 显示完成信息
print("\n分析完成！所有图表和分析报告已生成。")