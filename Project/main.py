import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random

# ================= 核心配置 =================
# 目标：北京房天下二手房
BASE_URL = "https://bj.esf.fang.com/"
# 爬取 20 页 * 60 条/页 = 1200 条，确保覆盖 1000 条的要求
TOTAL_PAGES = 20
DB_NAME = "house_data.db"

# ===========================================

def init_db():
    """初始化数据库"""
    print(f"正在初始化数据库: {DB_NAME} ...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 为了避免数据重复，如果表存在则清空（如果你想累加数据，请注释掉下面这行 DROP）
    cursor.execute('DROP TABLE IF EXISTS houses')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS houses
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       title TEXT,          -- 标题
                       details TEXT,        -- 户型/面积/楼层
                       address TEXT,        -- 地址
                       total_price TEXT,    -- 总价
                       unit_price TEXT      -- 单价
                   )
                   ''')
    conn.commit()
    return conn

def get_headers():
    """生成的请求头，模拟真实浏览器"""
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(ua_list),
        "Referer": "https://bj.esf.fang.com/",
        "Connection": "keep-alive"
    }

def crawl():
    conn = init_db()
    cursor = conn.cursor()
    total_count = 0

    print(f"\n>>> 🚀 任务开始：计划爬取 {TOTAL_PAGES} 页 (约 {TOTAL_PAGES * 60} 条数据) <<<")
    print(">>> ⚠️  警告：为了防止被封 IP，程序运行会比较慢，请耐心等待，不要关闭窗口...\n")

    for page in range(1, TOTAL_PAGES + 1):
        url = BASE_URL.format(page)
        retries = 3  # 每页允许重试 3 次
        success = False

        while retries > 0:
            try:
                print(f"📡 正在请求第 [{page}/{TOTAL_PAGES}] 页...")
                response = requests.get(url, headers=get_headers(), timeout=15)
                response.encoding = 'utf-8'

                # 检查是否被重定向到了验证码页面
                soup = BeautifulSoup(response.text, 'html.parser')
                page_title = soup.title.text.strip() if soup.title else ""

                if "验证" in page_title or "跳转" in page_title:
                    print("🛑 触发了反爬验证！正在尝试等待 20 秒后重试...")
                    time.sleep(20)
                    retries -= 1
                    continue

                # 提取房源列表
                house_items = soup.select('div[class*="shop_list"] dl')

                if not house_items:
                    print(f"⚠️  本页未获取到数据 (可能是网络波动)，剩余重试次数: {retries - 1}")
                    time.sleep(3)
                    retries -= 1
                    continue

                # 解析数据
                page_count = 0
                for item in house_items:
                    try:
                        # 1. 标题
                        title_elem = item.select_one('.tit_shop')
                        if not title_elem: continue
                        title = title_elem.text.strip()

                        # 2. 详情
                        desc_elem = item.select_one('.tel_shop')
                        details = desc_elem.text.strip().replace('\n', '').replace('\t', '') if desc_elem else ""

                        # 3. 地址
                        add_elem = item.select_one('.add_shop')
                        address = add_elem.text.strip().replace('\n', '') if add_elem else ""

                        # 4. 总价
                        price_elem = item.select_one('.red, .price_right')
                        price = price_elem.text.strip() + "万" if price_elem else ""

                        # 5. 单价
                        unit_elem = item.select_one('span', string=lambda t: t and '元/㎡' in t)
                        unit_price = unit_elem.text.strip() if unit_elem else ""

                        # 写入数据库
                        cursor.execute('''
                                       INSERT INTO houses (title, details, address, total_price, unit_price)
                                       VALUES (?, ?, ?, ?, ?)
                                       ''', (title, details, address, price, unit_price))

                        page_count += 1
                        total_count += 1

                    except Exception as e:
                        continue  # 跳过单条错误

                # 每页提交一次保存（断点续传的关键）
                conn.commit()
                print(f"✅ 第 {page} 页完成 | 本页: {page_count} 条 | 累计: {total_count} 条")
                success = True
                break  # 成功了就跳出重试循环

            except Exception as e:
                print(f"❌ 请求异常: {e}")
                retries -= 1
                time.sleep(5)

        if not success:
            print(f"💀 第 {page} 页多次尝试失败，跳过该页...")

        # =======================================================
        # 关键安全机制：随机休眠 8 到 15 秒
        # 不要手动改小这个数字，否则爬到第 20 页左右大概率被封
        # =======================================================
        if page < TOTAL_PAGES:
            sleep_time = random.uniform(8, 15)
            print(f"⏳  安全休息 {sleep_time:.1f} 秒... (去喝杯水吧)")
            time.sleep(sleep_time)

    conn.close()
    print("\n" + "=" * 40)
    print(f"🎉 爬取任务结束！")
    print(f"📊 最终获取数据总数：{total_count} 条")
    print(f"📁 数据已保存至: {DB_NAME}")
    print("=" * 40)


if __name__ == "__main__":
    crawl()