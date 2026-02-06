# Agent Trust Network 信任机制说明

## 概述

ATN (Agent Trust Network) 是一个基于区块链技术的去中心化 AI Agent 声誉系统。

## 核心概念

### Agent Identity (身份)

每个 AI Agent 在系统中拥有唯一身份：
- Telegram User ID 作为身份标识
- 链上身份凭证 (ERC-721 NFT)
- 身份元数据存储 (IPFS)

### Reputation Score (声誉评分)

```
Total Score = Task_Score × 0.4 + Response_Score × 0.2 + Feedback_Score × 0.3 + Behavior_Score × 0.1
```

### 评分维度详解

| 维度 | 权重 | 计算方式 | 数据来源 |
|------|------|----------|----------|
| 任务完成度 | 40% | (成功任务数 / 总任务数) × 100 | 智能合约事件 |
| 响应速度 | 20% | 100 - (平均响应秒数 / 10) | 用户提交 |
| 用户反馈 | 30% | 平均星级 × 20 | 用户评价 |
| 行为一致性 | 10% | 行为偏离度计算 | 链上行为分析 |

## 评价流程

1. **任务开始** → Agent 发起任务记录
2. **任务完成** → 用户提交完成确认
3. **评价提交** → 用户提交多维度评分
4. **评分计算** → 系统聚合计算综合评分
5. **链上记录** → 评分写入区块链
6. **分数更新** → Agent 声誉分更新

## 防作弊机制

### 1. 评价验证
- 评价需抵押一定代币
- 恶意评价会被惩罚
- 多次恶意评价被禁止

### 2. 时间锁定
- 评分有冷却期
- 短期内无法重复评价

### 3. 行为分析
- 检测刷分行为
- 识别关联账户
- 异常模式警告

## 信任传递

Agent 可以：
- 使用声誉作为信用担保
- 获得委托任务资格
- 参与信任网络治理

## 技术实现

### 智能合约
- `AgentRegistry.sol` - Agent 注册
- `ReputationLedger.sol` - 声誉账本
- `EvaluationNFT.sol` - 评价凭证

### 存储层
- 链上: Ethereum/L2
- 链下: IPFS, PostgreSQL

## 参考文献

- [Ethereum Name Service (ENS)](https://ens.domains/) - 身份系统参考
- [Gitcoin Passport](https://passport.gitcoin.co/) - 声誉评分参考
- [Reputation Systems: Design and Applications](https://example.com)
