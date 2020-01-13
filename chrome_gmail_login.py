import selenium,time
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.maximize_window()
driver.get('https://accounts.google.com/signin/v2/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&service=mail&sacu=1&rip=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
time.sleep(5)
action = webdriver.ActionChains(driver)
driver.find_element_by_id('identifierId').send_keys("YOUR_USERNAME_HERE")
driver.find_element_by_id('identifierNext').click()
time.sleep(2)
driver.find_element_by_name('password').send_keys("YOUR_PASSWORD_HERE")
driver.find_element_by_id('passwordNext').click()
