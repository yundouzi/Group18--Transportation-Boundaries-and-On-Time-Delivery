
# Group18: 识别、量化与比较交通边界对即时配送的阻碍效应——以北京市为例

## 📚 项目简介

本项目深入探讨了北京市不同类型的交通边界（如二环、三环、四环、五环、快速路、河流等）对即时配送服务效率的影响。我们旨在通过地理空间分析和统计建模，识别、量化并比较这些交通边界所带来的配送阻碍效应，特别关注不同环线区域内、区域间以及不同方向上的效应差异。研究结果将为优化即时配送网络、提升城市物流效率以及支撑智慧城市规划提供数据驱动的洞察和决策依据。

**研究区域**: 北京市

**数据来源**:
- 即时配送平台订单数据（脱敏后）
- 交通路网数据（OpenStreetMap 等）
- 城市POI数据
- 行政区划与自然地理边界数据
- 地理编码服务

---

## 🎯 研究目标

- **交通边界识别**: 识别并数字化北京市主要的交通边界，包括各环路、河流、铁路等。
- **阻碍效应量化**: 开发方法量化不同交通边界对即时配送时间及效率的影响，例如通过模型计算穿过边界的额外时间成本。
- **空间效应比较**: 比较不同类型交通边界（如二环 vs 三环，环路 vs 河流）以及同一边界不同方向（如由内向外 vs 由外向内）的阻碍效应差异。
- **驱动因素分析**: 探究影响边界阻碍效应的潜在因素，例如道路设施、路口密度、交通管制等。
- **优化建议**: 基于量化结果，为即时配送平台和城市规划提供优化策略。

---

## 📁 项目结构

```
traffic_boundary_delivery/
├── data/                                    # 原始数据与处理后的数据
│   ├── raw/                                 # 原始订单数据、路网、POI等
│   ├── processed/                           # 经过清洗、匹配、地理编码后的数据
│   └── boundaries/                          # 数字化后的交通边界（shp文件等）
│
├── src/                                     # 源代码
│   ├── data_preprocessing.py               # 数据清洗、匹配、地理编码、OD对生成
│   ├── boundary_identification.py          # 交通边界数字化与拓扑关系构建
│   ├── impedance_modeling.py               # 配送阻碍效应量化模型（如线性回归、GWR）
│   ├── spatial_analysis.py                 # 空间统计与方向性分析
│   └── visualization.py                    # 结果可视化脚本
│
├── figures/                                 # 生成的图表与可视化产出
│   ├── boundary_maps/                      # 各类交通边界可视化图
│   ├── impedance_effect_maps/              # 阻碍效应空间分布图
│   ├── comparison_charts/                  # 阻碍效应比较图表（环线、方向等）
│   ├── regression_results/                 # 回归模型结果图表
│   └── report_figures/                     # 报告专用图表
│
├── docs/                                    # 文档与报告
│   ├── research_report.md                  # 详细研究报告（基于Word文档内容）
│   └── methodology_appendix.md             # 方法学附录
│
├── notebooks/                               # Jupyter 笔记本（可选，用于探索性分析与方法测试）
│   ├── exploratory_data_analysis.ipynb
│   └── model_testing.ipynb
│
├── README.md                                # 项目总览（本文件）
└── requirements.txt                         # 依赖包列表
```

---

## 🔧 环境配置

### 依赖包

- Python 版本：3.8+
- `pandas`
- `numpy`
- `scipy`
- `matplotlib`
- `seaborn`
- `scikit-learn` (用于回归分析等)
- `geopandas` (用于矢量数据处理和空间操作)
- `shapely` (用于几何操作)
- `networkx` (用于图论分析，如路径规划模拟)
- `osmnx` (从OpenStreetMap获取路网数据)
- `statsmodels` (高级统计模型，如多重线性回归)
- `folium` 或 `keplergl` (用于交互式地图可视化)
- `tqdm` (用于进度条显示)

### 安装步骤（推荐使用虚拟环境）

1.  **克隆或下载仓库**
    ```bash
    git clone <your-repo-url>
    cd traffic_boundary_delivery
    ```

2.  **创建并激活虚拟环境**
    ```bash
    # Linux/macOS
    python -m venv venv
    source venv/bin/activate
    
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```
    > **注意**：`geopandas` 及其依赖项在某些系统上安装可能较复杂，特别是 `GDAL`。如果遇到问题，请参考官方文档或寻求帮助。在 Windows 上，可能需要从 [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/) 下载对应版本的 `.whl` 文件手动安装。

---

## 🚀 使用方法

### 1. 数据准备

将原始订单数据、路网、POI 等数据放入 `data/raw/` 目录。根据需要，可能需要手动下载或通过脚本从 API 获取数据。

### 2. 数据预处理

运行 `data_preprocessing.py` 脚本，执行数据清洗、OD对生成、地理编码（如将文本地址转换为经纬度）等操作。

```bash
cd src
python data_preprocessing.py
```

**输入**：`data/raw/` 中的原始数据  
**输出**：处理后的订单数据、OD对等，存储于 `data/processed/`

### 3. 交通边界识别与拓扑构建

运行 `boundary_identification.py` 脚本，数字化北京市的各交通边界（如环路、河流），并建立订单OD对与这些边界之间的拓扑关系（如是否穿越、穿越次数等）。

```bash
python boundary_identification.py
```

**输入**：`data/processed/` 中的OD对，`data/raw/` 或 `data/boundaries/` 中的边界数据  
**输出**：带有边界穿越信息的OD对数据，存储于 `data/processed/`

### 4. 配送阻碍效应量化

运行 `impedance_modeling.py` 脚本，构建统计模型（如多重线性回归）来量化不同交通边界的阻碍效应，分析其对配送时间的影响。

```bash
python impedance_modeling.py
```

**输入**：`data/processed/` 中带有边界信息的OD对数据  
**输出**：模型结果（系数、R²、P值等），以及效应的量化值。

### 5. 空间分析与比较

运行 `spatial_analysis.py` 脚本，对量化后的阻碍效应进行空间统计分析，比较不同环路、不同方向的效应差异。

```bash
python spatial_analysis.py
```

**输入**：`impedance_modeling.py` 的输出结果  
**输出**：效应差异的统计结果，存储于 `data/processed/` 或直接用于可视化。

### 6. 结果可视化

运行 `visualization.py` 脚本，生成各类分析结果的可视化图表，包括交通边界地图、阻碍效应空间分布图、效应比较柱状图等。

```bash
python visualization.py
```

**输入**：前述步骤生成的所有分析结果  
**输出**：高质量图表文件，存储于 `figures/` 目录

---

## 📊 主要发现

> 以下总结基于你提供的Word文档内容，是报告中核心发现的概括。

- **整体效应**: 北京市交通边界对即时配送时间存在显著的阻碍效应，配送时间在穿越边界时会增加。
- **环线差异**: 不同环路边界的阻碍效应存在差异，具体量化了二环、三环、四环、五环以及高速公路等边界带来的额外配送时间。
- **方向性效应**: 同一交通边界，不同穿越方向（如由内向外 vs 由外向内）的阻碍效应可能不同，反映了交通组织和路网连通性的复杂性。
- **空间异质性**: 边界的阻碍效应在空间上并非均一，可能受道路类型、路口密度、交通流强度、区域功能等因素的影响。
- **河流边界**: 某些河流边界，由于桥梁数量限制和路网连通性较差，也表现出一定的阻碍效应。
- **OD距离影响**: 边界阻碍效应的比例或绝对值可能与订单的OD距离相关。
- **个体订单层面**: 识别出哪些订单由于边界的存在而遭受了显著的配送时间延长。

---

## 💡 未来工作

- **高精度边界提取**: 结合更精细的路网数据和交通规则，精确划分交通分区分界。
- **更复杂的模型**: 引入机器学习模型（如梯度提升树、神经网络）或空间计量模型（如地理加权回归）以捕捉更复杂的非线性关系和空间异质性。
- **动态交通数据**: 结合实时交通流数据，研究动态交通状况下边界阻碍效应的变化。
- **微观路段分析**: 深入分析边界上的特定路段和交叉口设计如何影响配送效率。
- **成本效益分析**: 将时间阻碍转化为经济成本，为配送平台提供更直接的决策依据。
- **多城市比较**: 将研究拓展至其他城市，进行跨城市比较，探究城市空间结构对物流效率的普适性影响。

---

## 👥 团队成员

- [范思琪] (25S156046)
- [陈妮] (25S156055)
- [徐静雯] (25S066011)
- [王骞若] (25S156059)


## 📝 参考文献与数据来源

- 北京市即时配送平台订单数据（脱敏）
- OpenStreetMap 路网数据
