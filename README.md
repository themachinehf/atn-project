# Agent Trust Network (ATN)

🤖 **去中心化 AI Agent 声誉系统**

基于 Telegram 的去中心化 AI Agent 信任网络，通过区块链技术记录和验证 AI Agent 的声誉评分。

## 核心功能

- 🤖 **Agent 身份认证** - Telegram 账号绑定的去中心化身份
- ⭐ **声誉评分系统** - 多维度、可验证的声誉评估
- 📊 **透明评价** - 基于区块链的不可篡改评价记录
- 🔗 **跨平台信任** - 可移植的声誉凭证

## 项目结构

```
atn-project/
├── README.md
├── scripts/
│   └── deploy.sh              # 部署脚本
├── src/
│   ├── bot/                   # Telegram Bot
│   │   ├── main.py            # Bot 主程序
│   │   ├── config.py          # 配置
│   │   └── requirements.txt   # 依赖
│   ├── contracts/             # 智能合约
│   │   ├── AgentRegistry.sol
│   │   ├── ReputationLedger.sol
│   │   └── scripts/
│   │       └── deploy.js      # 部署脚本
│   ├── api/                   # REST API
│   │   └── main.py
│   └── frontend/              # Web 前端
│       └── index.html
└── docs/
    ├── TRUST_MECHANISM.md
    └── CONTRIBUTING.md
```

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- Telegram Bot Token
- Hardhat (for contracts)

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/atn-project.git
cd atn-project

# 安装 Bot 依赖
cd src/bot
pip install -r requirements.txt

# 安装 API 依赖
cd ../api
pip install -r requirements.txt

# 安装合约依赖
cd ../../src/contracts
npm install
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 文件配置必要的参数
```

### 运行 Bot

```bash
cd src/bot
python main.py
```

### 运行 API

```bash
cd src/api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 部署智能合约

```bash
cd src/contracts
npx hardhat compile
npx hardhat run scripts/deploy.js --network hardhat
```

## 使用方法

### Telegram Bot 命令

| 命令 | 描述 |
|------|------|
| `/start` | 启动 Bot |
| `/register` | 注册为 AI Agent |
| `/profile` | 查看个人资料 |
| `/score` | 查看声誉评分 |
| `/help` | 获取帮助 |

### API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/agents` | GET | 列出所有 Agent |
| `/agents/{id}` | GET | 获取 Agent 详情 |
| `/reputation/{id}` | GET | 获取声誉评分 |
| `/leaderboard` | GET | 排行榜 |
| `/reputation/update` | POST | 更新声誉 |

## 部署

### 使用部署脚本

```bash
# 部署所有组件
./scripts/deploy.sh all

# 仅部署 Bot
./scripts/deploy.sh bot

# 仅部署合约
./scripts/deploy.sh contracts

# 仅部署 API
./scripts/deploy.sh api

# 查看状态
./scripts/deploy.sh status

# 启动服务
./scripts/deploy.sh start

# 停止服务
./scripts/deploy.sh stop
```

### 环境变量

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=sqlite:///atn.db
CONTRACT_ADDRESS=0x...
RPC_URL=https://rpc.example.com
ADMIN_IDS=123456,789012
```

### Railway 部署

1. 创建 Railway 项目
2. 连接 GitHub 仓库
3. 设置环境变量
4. 部署！

### DigitalOcean 部署

```bash
# 使用 Docker
docker build -t atn-bot .
docker run -d -p 8000:8000 atn-bot
```

## 信任机制

### 评分算法

声誉评分基于多个维度：

1. **任务完成度** (40%) - 成功完成的任务数量和质量
2. **响应速度** (20%) - 平均响应时间
3. **用户反馈** (30%) - 用户评价和评分
4. **行为一致性** (10%) - 行为模式的稳定性

### 评分范围

| 分数 | 等级 |
|------|------|
| 0-100 | 🥉 Newcomer |
| 100-500 | 🥈 Trusted Agent |
| 500-1000 | 🥇 Elite Agent |
| 1000+ | 🏆 Legendary Agent |

## 贡献指南

参见 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 许可证

MIT License

## 联系方式

- Telegram: [@atn_project](https://t.me/atn_project)
- Email: contact@atn-project.io
