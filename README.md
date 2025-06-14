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

## 🗂️ 项目任务看板说明

本项目使用 GitHub Project 管理任务进度，所有模块任务均已拆解，欢迎同学查看并认领！

🔗 **任务看板入口：**  
👉 [https://github.com/users/BalterSin/projects/1](https://github.com/users/BalterSin/projects/1)

### ✅ 看板包含三个常用分区：

| 分区        | 用途说明                     |
|-------------|------------------------------|
| 📥 To Do     | 所有待认领任务，欢迎挑选        |
| 🛠 In Progress | 当前由同学正在开发中的任务       |
| ✅ Done      | 已完成并合并入项目的任务         |

---

### 🧠 如何认领任务？

1. 打开看板，点击感兴趣的任务卡片，强烈建议先详细查看群里的 AI驱动的全维度数据情报洞察中枢系统架构设计(1).pdf
2. 在群里认领并开始开发
3. 每个任务建议创建独立分支开发，提交 Pull Request（PR）

📣 **欢迎大家积极认领任务，共同打造智能中枢系统！**