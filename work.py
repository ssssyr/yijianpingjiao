from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# 用户名密码（调试用）
#usrname = '25113070110'
#password = 'fDu063836'

# 如果需要交互式输入，可以取消下面的注释
print("请输入uis用户名")
usrname = input()
print("请输入uis密码")
password = input()

driver = webdriver.Chrome()
url = "https://yzsfwapp.fudan.edu.cn/gsapp/sys/wspjappfudan/*default/index.do?amp_sec_version_=1#/wspj"

driver.get(url)
time.sleep(3)

# 根据实际页面结构定位元素（复旦大学研究生评教系统）
# 用户名框：通过 placeholder 定位（更精确）
usr = driver.find_element(By.XPATH, "//input[@placeholder='用户名（本人学工号）']")
# 密码框：通过 placeholder 定位
pwd = driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']")

# 先点击输入框，确保它是活动状态，再输入
usr.click()
time.sleep(0.5)
usr.send_keys(usrname)   # 填入uis用户名

pwd.click()
time.sleep(0.5)
pwd.send_keys(password)   # 填入uis密码

# 等待按钮从禁用状态变为可点击状态
time.sleep(1)

# 登录按钮：通过 class="content_submit" 定位
submit = driver.find_element(By.XPATH, "//button[contains(@class, 'content_submit')]")
submit.click()
#driver.get("http://ce.fudan.edu.cn/q.aspx?id=9957450&beginTime=2020-04-24%2015:00&endTime=2020-06-20%2023:59&previewTime=2020-03-22%2008:00%20&sqid=b956f4a567ed4ab982a7aede07a4a6da&type=5&stepseq=45ff583eeca240959051a0bf2f11efee&targettype=2&targetcode=869a78ece4374719a3ee006f8661746b&tag=b956f4a567ed4ab982a7aede07a4a6da_5_869a78ece4374719a3ee006f8661746b_2_2019-2020-2-COMP130154_0_9957450&name=2020%E5%B9%B4%E6%98%A5%E5%AD%A3%E5%AD%A6%E6%9C%9F%E7%90%86%E8%AE%BA%E8%AF%BE%E8%AF%84%E6%95%99-%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%8E%9F%E7%90%86")

#driver.get("http://ce.fudan.edu.cn/q.aspx?id=9957450&sqid=b956f4a567ed4ab982a7aede07a4a6da&type=5&stepseq=45ff583eeca240959051a0bf2f11efee&targettype=2&targetcode=869a78ece4374719a3ee006f8661746b&tag=b956f4a567ed4ab982a7aede07a4a6da_5_869a78ece4374719a3ee006f8661746b_2_2019-2020-2-COMP130154_0_9957450&beginTime=2020-04-24%2015:00&endTime=2020-06-14%2023:59&previewTime=2020-03-22%2008:00&name=2020%E5%B9%B4%E6%98%A5%E5%AD%A3%E5%AD%A6%E6%9C%9F%E7%90%86%E8%AE%BA%E8%AF%BE%E8%AF%84%E6%95%99-%E8%AE%A1%E7%AE%97%E6%9C%BA%E5%8E%9F%E7%90%86")
# 等待登录后页面加载
time.sleep(3)

# 尝试关闭新手引导提示层（guideOverlay 遮挡了点击）
try:
    # 方法1: 通过JavaScript隐藏引导层
    driver.execute_script("var elem = document.getElementById('guideOverlay'); if(elem) elem.style.display='none';")
    time.sleep(0.5)
    # 方法2: 尝试点击关闭按钮（如果有）
    try:
        close_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'close') or contains(@class, 'guide-close')]")
        close_btn.click()
    except:
        pass
    time.sleep(0.5)
    # 方法3: 按ESC键关闭（有些引导层可以用ESC关闭）
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
    time.sleep(0.5)
except Exception as e:
    print(f"关闭引导层时出错（可忽略）: {e}")

# 记录当前URL，用于判断是否返回成功
course_list_url = driver.current_url

# 循环处理课程，每次都重新查找
# 每次都选第一个课程，评教完成后它会从列表消失，下次循环还是选第一个
while True:
    # 等待页面加载完成（等待课程卡片出现）
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'pjwj_card_content'))
        )
    except:
        print(f"没有找到待评教的课程，结束")
        break

    time.sleep(0.3)  # 减少等待时间

    # 每次循环开始时都尝试关闭引导提示（页面可能重新加载）
    driver.execute_script("var elem = document.getElementById('guideOverlay'); if(elem) elem.style.display='none';")
    time.sleep(0.2)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
    time.sleep(0.3)  # 减少等待时间

    # 每次都重新查找课程卡片
    course_cards = driver.find_elements(By.CLASS_NAME, 'pjwj_card_content')

    if len(course_cards) == 0:
        print(f"所有课程已评教完成！")
        break

    print(f"[调试] 找到 {len(course_cards)} 门待评教课程")

    try:
        # 始终选择第一门课程（索引0）
        card = course_cards[0]
        course_name = card.get_attribute('title')
        print(f"正在评教: {course_name}")

        # 点击课程卡片进入评教页面
        print(f"[调试] 准备点击课程卡片...")
        # 使用 JavaScript 点击（绕过遮挡）
        driver.execute_script("arguments[0].click();", card)
        print(f"[调试] 点击成功，等待页面加载...")
        time.sleep(1)  # 减少等待时间：2→1

        # 进入评教页面后，也要关闭可能出现的引导提示
        print(f"[调试] 关闭引导提示...")
        driver.execute_script("var elem = document.getElementById('guideOverlay'); if(elem) elem.style.display='none';")
        time.sleep(0.2)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.3)

        # 检查是否已评教完成（查找"提交"按钮）
        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//a[@data-action='提交']"))
            )
            has_submit = True
        except:
            has_submit = False

        # 如果没有"提交"按钮，说明已评教完成
        if not has_submit:
            print(f"[调试] 该课程已评教完成，所有课程评教完毕！")
            # 尝试找关闭按钮关闭弹窗
            try:
                close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'关闭') or contains(text(),'取消')]")
                close_btn.click()
            except:
                pass
            break  # 第一门课都评教完成了，说明所有课程都评教完了，直接退出

        # 开始评教：点击所有问题的"完全同意"选项
        print(f"[调试] 开始评教，点击所有问题的'完全同意'...")
        try:
            # 查找所有"完全同意"的选项（通过 role-mc 属性定位）
            agree_buttons = driver.find_elements(By.XPATH, "//input[@role='pj_form_radio' and @role-mc='完全同意']")
            print(f"[调试] 找到 {len(agree_buttons)} 个'完全同意'选项")

            for i, btn in enumerate(agree_buttons):
                try:
                    # 使用 JavaScript 点击（更可靠）
                    driver.execute_script("arguments[0].click();", btn)
                except:
                    # 如果 JavaScript 点击失败，尝试普通点击
                    try:
                        btn.click()
                    except:
                        pass

            time.sleep(0.2)  # 减少等待时间：0.5→0.2

            # 检查是否有"提交"按钮（已评教的课程可能只有"暂存"或没有按钮）
            try:
                print(f"[调试] 查找'提交'按钮...")
                submit_btn = driver.find_element(By.XPATH, "//a[@data-action='提交']")
                driver.execute_script("arguments[0].click();", submit_btn)
                print(f"[调试] 已点击提交")

                # 等待确认弹窗出现
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'bh-dialog-btn') and contains(text(),'确定')]"))
                )

                # 点击确定按钮确认提交
                confirm_btn = driver.find_element(By.XPATH, "//a[contains(@class, 'bh-dialog-btn') and contains(text(),'确定')]")
                driver.execute_script("arguments[0].click();", confirm_btn)
                time.sleep(0.3)
            except Exception as submit_err:
                # 没有"提交"按钮，可能已评教过或只有"暂存"按钮
                print(f"[调试] 未找到'提交'按钮，可能已评教过: {submit_err}")
                # 尝试查找是否有"暂存"按钮，如果有就点击暂存
                try:
                    save_btn = driver.find_element(By.XPATH, "//a[@data-action='暂存']")
                    driver.execute_script("arguments[0].click();", save_btn)
                    print(f"[调试] 已点击暂存")
                    time.sleep(0.5)
                except:
                    print(f"[调试] 该课程可能已评教完成，跳过")

            print(f"[调试] 评教完成！")

        except Exception as e:
            print(f"[调试] 评教过程出错: {e}")
            import traceback
            traceback.print_exc()

        # 返回课程列表（单页应用用back可能不正常，直接访问URL）
        print(f"[调试] 返回课程列表...\n")
        driver.get(course_list_url)
        time.sleep(1)  # 减少等待时间：2→1

        # 再次关闭可能出现的引导提示
        driver.execute_script("var elem = document.getElementById('guideOverlay'); if(elem) elem.style.display='none';")
        time.sleep(0.2)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.3)  # 减少等待时间：0.5→0.3

    except Exception as e:
        print(f"  评教出错: {e}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        # 尝试返回课程列表
        driver.get(course_list_url)
        time.sleep(1)
        driver.execute_script("var elem = document.getElementById('guideOverlay'); if(elem) elem.style.display='none';")
        time.sleep(0.2)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.3)

print("评教完成！")