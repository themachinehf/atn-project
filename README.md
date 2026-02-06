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
├── src/
│   ├── bot/          # Telegram Bot
│   ├── contracts/    # 智能合约
│   ├── api/          # 信任查询 API
│   └── frontend/     # Web 前端
├── scripts/          # 部署和运维脚本
└── docs/             # 文档
```

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- Telegram Bot Token

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/atn-project.git
cd atn-project

# 安装依赖
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 文件配置必要的参数
```

### 运行

```bash
python -m src.bot.main
```

## 信任机制

### 评分算法

声誉评分基于多个维度：

1. **任务完成度** (40%) - 成功完成的任务数量和质量
2. **响应速度** (20%) - 平均响应时间
3. **用户反馈** (30%) - 用户评价和评分
4. **行为一致性** (10%) - 行为模式的稳定性

### 评分范围

- **0-100**: 基础信誉分数
- **100-500**: 良好信誉
- **500-1000**: 优秀信誉
- **1000+**: 卓越信誉

## 贡献指南

参见 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 许可证

MIT License

## 联系方式

- Telegram: [@atn_project](https://t.me/atn_project)
- Email: contact@atn-project.io
