# ai-intel-hub

AI驱动的全维度数据情报洞察中枢系统（新人大赛项目）

本系统模拟新能源汽车行业的智能情报平台，基于多Agent架构构建，支持从用户查询 → 中枢调度 → 专业分析 → 输出报告的自动化智能流程。

---

## 📁 项目结构

```text
ai-intel-hub/
├── backend/                  # 后端中枢系统
│   ├── app.py
│   ├── hub/                 # 中枢情报Agent逻辑
│   ├── agents/              # 专业Agent（市场/政策/技术等）
│   ├── workflows/           # GraphFlow工作流逻辑
│   └── tools/               # 工具类（如搜索/数据接入）
├── frontend/                # 前端用户界面（Vue/React）
│   └── src/
├── config/                  # 配置文件
├── data/                    # 示例数据与资料
├── tests/                   # 测试代码
├── docs/                    # 文档与汇报材料
├── requirements.txt
└── README.md
