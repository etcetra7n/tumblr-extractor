from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from requests import get

print("Enter Tumblr username: ", end='')
uname = input()
print("Enter Tumblr password: ", end='')
pword = input()

cap = 1000
outfile = r"./tumblr_extractor.log"
print("Loading webdriver...")
opts = Options()
opts.add_argument("--headless")
driver = webdriver.Firefox(options = opts)
fname = 1
count = 1
halt = False
urls = []
with open(f"./rip.var", "r") as f:
    lines = f.readlines()
    if len(lines) >= 1:
        fname = int(lines[0])
        urls = [x.replace("\n", "") for x in lines[1:]]

#logging in
print("Logging in...")
driver.get("https://www.tumblr.com/login")
sleep(1)
driver.find_element(By.NAME, "email").send_keys(uname)
driver.find_element(By.NAME, "password").send_keys(pword)
driver.find_element(By.XPATH, "//button[@type='submit']").click()
sleep(2)

print("Starting..")
driver.get("https://www.tumblr.com/dashboard/hubs")
sleep(3)
last_height = driver.execute_script("return document.body.scrollHeight")
# driver.find_element(By.CLASS_NAME, "HsI7c")
scrolling_required = False 
error_count = 0
while(True):
    try:
        if scrolling_required:
            scroll_n = 1
            while True:
                print("Scrolling down...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll down to bottom
                sleep(0.8) # Wait to load page
                new_height = driver.execute_script("return document.body.scrollHeight") # Calculate new scroll height and compare with last scroll height
                if new_height == last_height:
                    break
                if scroll_n >= 3:
                    break
                last_height = new_height
                scroll_n += 1
        sleep(0.2)
        scrolling_required = True
        imgs = driver.find_elements(By.XPATH, "//img[@class='RoN4R tPU70 xhGbM']")
        imgs += driver.find_elements(By.XPATH, "//imgs[@class='RoN4R xhGbM']")
        #print(len(imgs))
        for img in imgs:
            srcset = img.get_attribute("srcset")
            begin = srcset.rfind("https://")
            end = srcset.rfind(" ")
            img_url = srcset[begin:end]
            if(img_url in urls):
                print("url already exists")
                continue
            with open(f"./tumblr_downloaded_content/{fname}.jpg", "wb") as f:
                #l = driver.find_element(By.CLASS_NAME, "J9AiF")
                print(f"Downloading {fname}.jpg ({count}/{cap})")
                tries = 1
                recieved = True
                while(tries<=2):
                    try:
                        response = get(img_url)
                        break
                    except:
                        if(tries == 2):
                            recieved = False
                    tries+=1
                if not recieved:
                    print("Cannot fetch file...")
                    continue
                f.write(response.content)
                urls.append(img_url)
                count += 1
                fname += 1
            #sleep(4)
            if(count >= cap):
                halt = True
                break
            
        if halt:
            break
    except:
        error_count+=1
        if (error_count>=5):
            print("Encountered an error. Retrying...")
            sleep(8)
        elif (error_count>=20):
            print("20+ errors. Hard reset...")
            driver.get("https://www.tumblr.com/dashboard/hubs")
            sleep(3)
            last_height = driver.execute_script("return document.body.scrollHeight")
            sleep(12)
            scrolling_required = False 
            error_count = 0
        sleep(4)
        with open(f"./tumblr_extractor.var", "w") as f:
            f.seek(0)
            f.write(f"{str(fname)}\n")
            for i in urls:
                f.write(f"{i}\n")
        continue

with open(f"./tumblr_extractor.var", "w") as f:
    f.seek(0)
    f.write(f"{str(fname)}\n")
    for i in urls:
        f.write(f"{i}\n")
print("Task completed with 0 errors")
driver.quit()
