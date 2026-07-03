<div align="center">
    <img src="img/cover.jpg" width="320" alt="学习通作业导出工具">
    <h1>📚 学习通作业提取导出工具</h1>
    <h3>Xxt-Docx-Exporter</h3>
    <p>一键提取超星学习通课程作业 · 批量导出格式化 Word 文档 · 无需浏览器</p>
</div>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/version-v1.0.0-green.svg" alt="Version">
    <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

---

## ✨ 功能特性

### 🔥 核心功能
- **📄 作业导出为 Word (docx)**：将学习通作业一键导出为格式化的 Word 文档
  - 精美的封面排版（课程名、作业名、导出时间）
  - 彩色题型标签（单选/多选/判断/填空/简答/论述/编程）
  - 选择题正确答案**绿色高亮**显示
  - 答案区域红色标注，一目了然
- **📦 批量导出**：支持将一个课程的所有作业批量导出为一个或独立 Word 文档
- **🕷️ 作业爬取**：自动从已完成作业的账号中提取答案，保存为 JSON 格式
- **✅ 自动完成作业**：根据已爬取的答案，自动完成未做的作业
- **👥 批量多用户**：支持配置多个账号，批量完成相同作业

### 🎯 支持的题型
| 题型 | 爬取 | 导出 Word | 自动完成 |
|------|:----:|:---------:|:--------:|
| 单选题 | ✅ | ✅ | ✅ |
| 多选题 | ✅ | ✅ | ✅ |
| 判断题 | ✅ | ✅ | ✅ |
| 填空题 | ✅ | ✅ | ✅ |
| 简答题 | ✅ | ✅ | ✅ |
| 论述题 | ✅ | ✅ | ✅ |
| 编程题 | ✅ | ✅ | ✅ |
| 其他 | ✅ | ✅ | ✅ |

### 🔐 登录方式
- 手机号 + 密码登录
- 二维码扫码登录
- 多账号配置登录

---

## 📥 快速开始

### 环境要求
- Python 3.10+
- pip

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/liuwanwan1/xxt-docx-exporter.git
cd xxt-docx-exporter

# 2. 安装依赖
pip install -r requirements.txt

# 3. （可选）开发/打包依赖
pip install -r requirements-dev.txt

# 4. （可选）配置多用户批量完成
cp user.json.example user.json
# 编辑 user.json，填入账号信息

# 5. 运行
python main.py
```

### 使用流程

```
1️⃣ 选择登录方式（手机号/扫码/已有账号）
         ↓
2️⃣ 菜单选择 [5] 爬取指定作业的答案
         ↓
3️⃣ 菜单选择 [10] 导出为 Word 文档
   或选择 [11] 批量导出所有答案
   或选择 [12] 导出指定课程的全部作业
         ↓
4️⃣ 在 answers/ 目录下找到生成的 .docx 文件
```

---

## 🧪 测试与打包

```bash
# 运行单元测试
python -m unittest discover -s test

# 编译检查
python -m compileall main.py upload.py config.py my_xxt android_app test

# Windows 桌面版打包依赖
pip install -r requirements-dev.txt
```

- `requirements.txt` 仅包含运行所需依赖
- `requirements-dev.txt` 包含 PyInstaller 等打包依赖
- GitHub Actions 会在打包前执行单元测试
- Android APK 签名密码不再写入仓库，CI 优先读取 `ANDROID_KEYSTORE_PASSWORD` Secret，未配置时使用临时密码

---

## 📋 菜单说明

| 序号 | 功能 | 说明 |
|:----:|------|------|
| 1 | 查看课程 | 列出当前账号所有课程 |
| 2 | 查看答案文件 | 查看已爬取的答案 JSON 文件 |
| 3 | 查询未完成作业 | 扫描所有课程的未交作业 |
| 4 | 清除答案文件 | 清空 answers/ 目录 |
| 5 | 爬取指定作业答案 | 从已完成作业提取答案 |
| 6 | 批量爬取课程答案 | 一键爬取整个课程的所有作业答案 |
| 7 | 完成作业 | 使用已有答案自动完成未交作业 |
| 8 | 批量完成作业 | 多账号批量完成同一作业 |
| 9 | 退出登录 | 退出当前账号 |
| **10** | **导出作业为 Word** | 🆕 单个作业 → docx |
| **11** | **批量导出为 Word** | 🆕 全部答案 → docx（支持合并） |
| **12** | **导出课程作业汇总** | 🆕 指定课程 → 一个 Word 文档 |

---

## 🖼️ 导出效果预览

生成的 Word 文档包含：
- 🎨 **封面页**：课程名称 + 作业名称 + 导出时间
- 🏷️ **彩色题型标签**：单选题(蓝) 多选题(绿) 判断题(橙) 填空题(灰) 简答题(青) 论述题(紫) 编程题(红)
- 📊 **选项表格**：选择题选项以表格形式呈现，正确答案绿色高亮背景
- ✍️ **答案解析**：红色字体标明正确答案

---

## 🏗️ 项目结构

```
xxt-docx-exporter/
├── main.py                  # 程序入口
├── config.py                # 全局配置
├── requirements.txt         # 运行依赖
├── requirements-dev.txt     # 开发/打包依赖
├── user.json.example        # 多用户配置模板
├── test/                    # 单元测试
├── my_xxt/
│   ├── api.py               # 学习通 API 封装（登录/课程/作业/提交）
│   ├── login.py             # 登录模块
│   ├── answer_files.py      # 答案 JSON 文件读写与过滤
│   ├── answer_type.py       # 已提交作业答案解析
│   ├── question_type.py     # 未提交作业题目解析
│   ├── findAnswer.py        # 答案匹配算法
│   ├── submission.py        # 作业提交表单数据构造
│   ├── my_tools.py          # 菜单与交互逻辑
│   └── export_docx.py       # Word 文档导出模块
├── android_app/             # Android/Kivy 应用与 Buildozer 配置
├── answers/                 # 答案 JSON 与导出 docx 存放目录
└── img/                     # 图片资源
```

---

## 🔧 近期优化

- 修复 `requirements.txt` 编码问题，确保 `pip install -r requirements.txt` 可用
- 抽离答案文件处理逻辑，导出后的 `.docx` 不会再被误当作 JSON 解析
- 重构 Word 导出模块，单作业、批量、课程汇总共用同一套渲染流程
- 拆分菜单处理函数，降低主交互流程复杂度
- 加强题目/答案 HTML 解析容错，单题解析失败不会拖垮整份作业
- 拆出提交表单构造逻辑并补充单元测试
- 清理已跟踪的 `__pycache__` 编译产物
- Android 构建移除明文签名密码，批量操作失败会显示/记录错误
- `upload.py` 改为显式确认后再提交、推送和打标签

---

## ⚠️ 免责声明

- 本项目仅供**学习交流**使用，请勿用于商业用途
- 使用本工具时请遵守超星学习通的平台规则和相关法律法规
- 本项目遵循 MIT License 协议
- 超星学习通为北京世纪超星信息技术发展有限责任公司的商标，本项目与其无关

---

## 🙏 致谢

- 原项目 [aglorice/new_xxt](https://github.com/aglorice/new_xxt) 提供了优秀的爬虫基础
- [python-docx](https://python-docx.readthedocs.io/) 提供了强大的 Word 文档生成能力
- [Rich](https://github.com/Textualize/rich) 提供了美观的终端界面

---

## 📄 License

MIT License © 2024 [liuwanwan1](https://github.com/liuwanwan1)

---

<p align="center">
    <sub>如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！</sub>
</p>
