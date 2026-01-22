# Group18--Transportation-Boundaries-and-On-Time-Delivery
GIS 大作业：城市扩张与地表覆盖变化分析
项目简介
本作业利用 GIS 技术对 Shanghai 市及周边地区的地表覆盖数据进行时序分析，研究城市扩张对地表覆盖的影响。核心任务包括数据预处理、分类、变化检测、统计分析以及可视化呈现。项目结构设计注重模块化，便于同学们复用和扩展。

数据来源：公开GIS/遥感数据源（课程要求数据集或公开影像数据），并结合现有研究方法进行分析与可视化。

研究内容要点（与 PPT 对应的核心方向）：

地表覆盖分类与变化检测
城市扩张趋势分析
各类地表覆盖的时序统计与可视化
空间分异性与驱动因素初步探讨（如人口、交通、土地利用政策等）
🎯 研究目标
通过多时间点的地表覆盖数据，分析城市扩张的时空演化
量化不同年份/区划的地表覆盖变化
评估不同地表覆盖类型的变化速率与驱动因素
提供可复现的分析流程与可视化结果
📁 项目结构
bash
gis_project/
├── data/                                    # 数据文件
│   ├── landcover_YYYY.csv                 # 不同时间点的地表覆盖数据（CSV/shapefile等）
│   ├── boundary.shp                         # 区域边界（矢量）
│   └── metadata.md                          # 数据集元数据说明
├── src/                                     # 源代码
│   ├── preprocessing.py                      # 数据清洗与对齐（时间对齐、坐标系统一等）
│   ├── classification.py                     # 地表覆盖分类流程（如监督/非监督学习）
│   ├── change_detection.py                   # 变化检测与转化矩阵计算
│   └── visualization.py                      # 可视化绘图（时序图、热力图、分布图等）
├── figures/                                 # 生成的图表与可视化产出
│   ├── fig1_change_map.png                   # 时序变化地图
│   ├── fig2_class_distribution.png          # 分类分布图
│   ├── fig3_transition_matrix.png           # 转换矩阵热力图
│   ├── fig4_time_series.png                 # 时序趋势图
│   └── fig5_spatial_distribution.png        # 空间分布图
├── docs/                                    # 文档
│   ├── analysis_report.md                    # 数据分析报告（摘要、方法、结果、结论）
│   └── methodology.md                        # 方法学与工作流说明
├── notebooks/                               # Jupyter 笔记本（可选）
│   └── exploratory_analysis.ipynb
├── README.md                                # 项目总览（本文件）
└── requirements.txt                         # 依赖包列表
注：具体的文件名和结构可按你 PPT 的实际内容微调，上述为一个可复用且清晰的模板。

🔧 环境配置（示例）
Python 版本：3.8+

依赖包（示例，依据实际项目需求调整）:

pandas>=1.5.0
geopandas>=0.10.0
numpy>=1.20.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.2.0
rasterio>=1.2.0 (若处理栅格数据)
安装步骤（推荐虚拟环境）:

Clone/下载仓库
创建并进入虚拟环境
Linux/macOS: python -m venv venv && source venv/bin/activate
Windows: python -m venv venv && venv\Scripts\activate
安装依赖
pip install -r requirements.txt
🚀 使用方法
数据预处理

运行 preprocessing.py：对不同时间点的数据进行坐标系统一、分辨率对齐、区域裁切等预处理。
输入：原始地表覆盖数据、区域边界等
输出：对齐后的数据集，存放在 data/ 或中间产物目录
地表覆盖分类

运行 classification.py：根据数据特点进行监督或非监督分类，得到各时间点的地表覆盖标签。
输入：预处理后的栅格/矢量数据
输出：各时间点的地表覆盖结果（如 CSV/GeoJSON/GeoTIFF）
变化检测

运行 change_detection.py：计算年度/区划之间的转化矩阵，识别主要变化类型（如建筑用地扩张、水体减少等）。
输入：各时间点地表覆盖结果
输出：转化矩阵、变化统计
可视化与报告

运行 visualization.py：生成时序趋势图、分类分布、转化矩阵热力图、变化地图等，并保存至 figures/
输出：多张图表，供分析报告使用
生成分析报告

将分析要点整理成 docs/analysis_report.md，包含方法简介、主要发现与结论
🗺 主要发现（示例要点）
城市扩张与地表覆盖变化的定量趋势（请用你们的实际结果填充）
不同时间点的地表覆盖分布特征
主要区域的变化驱动因素（如交通节点、土地使用政策等的初步关联）
请在实际提交中，将“示例要点”替换为你们在作业中得到的具体结论和统计数据。

📈 可视化图表说明
fig1_change_map.png：各时间点的地表覆盖变化地图，展示扩张区域与缩小区域
fig2_class_distribution.png：地表覆盖类别在各时间点的分布
fig3_transition_matrix.png：转化矩阵（来源地表覆盖与目标地表覆盖的转换概率）
fig4_time_series.png：关键指标（如建筑用地面积、绿地面积等）的时间序列
fig5_spatial_distribution.png：某一区域的空间分布对比
💡 未来工作
引入机器学习用于自动化分类与更高精度的变化检测
增加更多时间点的数据以提升统计显著性
做更细粒度的空间分异性分析（如按区/街道级别）
将分析结果嵌入交互式仪表盘（如 Streamlit/Dash）
👥 团队成员
[姓名1]（学号/学生号）
[姓名2]（学号/学生号）
[姓名3]（学号/学生号）
