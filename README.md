# ai-intel-hub

AI驱动的全维度数据情报洞察中枢系统（新人大赛项目）

本系统模拟新能源汽车行业的智能情报平台，基于多Agent架构构建，支持从用户查询 → 中枢调度 → 专业分析 → 输出报告的自动化智能流程。

---

## 📂 项目目录结构

ai-intel-hub/
├── backend/ # 后端中枢系统
│ ├── app.py # 主入口程序
│ ├── hub/ # 中枢情报Agent
│ ├── agents/ # 各专业Agent（如市场、政策）
│ ├── workflows/ # 多Agent协同工作流（GraphFlow）
│ └── tools/ # 工具封装（如 ali_search）
├── frontend/ # 前端用户界面（可选Vue/React）
│ └── src/
├── config/ # 配置文件（如API密钥、参数）
├── data/ # 示例数据、文档素材
├── tests/ # 测试代码
├── docs/ # 项目文档（结构图、展示PPT）
├── requirements.txt # Python依赖列表
└── README.md