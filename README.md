# Football Predictor

基于历史交手、近期状态、联赛排名和实时赔率的足球比赛结果预测模型，含 Web 前端。

## 功能

| 模块 | 说明 |
|------|------|
| **历史交手** | 胜率、平局率、场均进球 |
| **近期状态** | 近 N 场积分、进失球、胜率 |
| **主客场分化** | 主队主场 / 客队客场专项状态 |
| **联赛排名** | 排名、积分差、净胜球差 |
| **进阶指标** | 零封率、不败率、休息天数 |
| **实时赔率** | The Odds API → 去水隐含概率 |
| **Web 前端** | 选队预测、同步数据、可视化胜率 |

## 接入真实 API（三步）

### 第一步：注册并获取 API Key

| 服务 | 用途 | 注册地址 | 免费额度 |
|------|------|----------|----------|
| **football-data.org** | 比赛历史、排名、球队 | https://www.football-data.org/client/register | 10 次/分钟 |
| **The Odds API** | 实时赔率 | https://the-odds-api.com/ | 500 次/月 |

### 第二步：配置 `.env`

```powershell
cd C:\Users\Administrator\Projects\football-predictor
copy .env.example .env
# 编辑 .env，填入两个 API Key
```

```env
FOOTBALL_DATA_API_KEY=你的football-data密钥
ODDS_API_KEY=你的odds-api密钥
DEFAULT_COMPETITION=PL
```

### 第三步：同步数据并启动

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt

# 同步英超数据到本地缓存
python scripts/sync_data.py --competition PL

# 重新训练模型（特征已扩展，需重训）
python scripts/train_model.py --data data/cache/PL_matches.csv

# 启动 Web 服务
python scripts/run_server.py
```

浏览器打开 **http://localhost:8000**

## 支持的联赛

| 代码 | 联赛 | Odds API |
|------|------|----------|
| **WC** | **世界杯** | **soccer_fifa_world_cup** |
| PL | 英超 | soccer_epl |
| PD | 西甲 | soccer_spain_la_liga |
| SA | 意甲 | soccer_italy_serie_a |
| BL1 | 德甲 | soccer_germany_bundesliga |
| FL1 | 法甲 | soccer_france_ligue_one |

```powershell
# 世界杯专用训练（2018+2022 共 128 场）
python scripts/train_model.py --data data/world_cup_matches.csv

# 同步 2026 世界杯数据（需 API Key）
python scripts/sync_data.py --competition WC
```

## CLI 用法

```powershell
# 命令行预测（使用缓存/API 数据）
python scripts/predict_match.py "Arsenal" "Chelsea" --fetch-odds

# 仅同步数据
python scripts/sync_data.py
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/competitions` | 联赛列表 |
| GET | `/api/teams?competition=PL` | 球队列表 |
| GET | `/api/upcoming?competition=PL` | 即将开赛 |
| GET | `/api/status?competition=PL` | 同步状态 |
| POST | `/api/sync?competition=PL` | 同步数据 |
| POST | `/api/predict` | 预测 `{home_team, away_team, competition, fetch_odds}` |

## 项目结构

```
football-predictor/
├── static/              # Web 前端
├── src/
│   ├── api/             # FastAPI 服务
│   ├── data/            # API 客户端 + 数据同步
│   ├── features/        # 特征工程
│   └── model/           # 训练与预测
├── scripts/
│   ├── sync_data.py     # 同步真实 API 数据
│   ├── train_model.py
│   └── run_server.py    # 启动 Web
└── data/cache/          # 同步后的本地缓存
```

## 免责声明

仅供学习研究，不构成任何投注建议。
