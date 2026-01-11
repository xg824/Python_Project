# 🏘️ Python 房产数据自动化采集爬虫 (Real Estate Crawler)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Requests](https://img.shields.io/badge/Library-Requests-green)
![BeautifulSoup](https://img.shields.io/badge/Library-BeautifulSoup4-yellow)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey)

## 📖 项目介绍 (Project Overview)

本项目是一个基于 Python 的网络爬虫系统，专为采集房产交易平台（如房天下/链家）的二手房源数据而设计。该项目作为 Python 课程设计作品，实现了从网页请求、数据解析到持久化存储的全流程自动化。

系统能够自动处理分页、模拟浏览器行为以规避反爬机制，并将抓取到的房源信息（标题、价格、户型、地址等）存储至本地 SQLite 数据库中，方便后续进行数据分析或可视化展示。

## ✨ 核心功能 (Features)

*   **自动化采集**：支持自定义爬取页数（默认 40 页，约 1000+ 条数据）。
*   **反爬虫策略**：
    *   内置 User-Agent 池，随机切换身份。
    *   智能随机延时（Random Delay），模拟真人浏览行为。
    *   自动检测验证码页面并进行重试。
*   **断点续传**：支持实时数据写入，防止因网络中断导致数据丢失。
*   **数据清洗**：自动去除 HTML 标签中的换行符和空格，提取纯净文本。
*   **轻量级存储**：使用 SQLite 数据库，无需安装额外的数据库软件。

## 📂 文件结构 (File Structure)

```text
Python_Project/
├── Project/
│   ├── main.py            # 爬虫核心启动脚本
│   ├── house_data.db      # 爬取结果数据库 (SQLite)
│   └── .idea/             # PyCharm 项目配置文件夹
└── README.md              # 项目说明文档
