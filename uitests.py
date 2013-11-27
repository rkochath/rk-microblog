import unittest

from selenium.webdriver import Firefox
#from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener



"""
def test_create_post():
    
    try:
	wait = WebDriverWait(driver, 10)
        
    	#post = wait.until(EC.presence_of_element_located((By.NAME, "post")))
	post = driver.find_element_by_name("post")
	post.send_keys("Automated post...")
	savepost = driver.find_element_by_name("savepost")
	savepost.click()
    finally:
    	#driver.quit()
	pass
"""    

class MyListener(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print("Before navigate to %s" % url)
    def after_navigate_to(self, url, driver):
        print("After navigate to %s" % url)

    

class GoogleTestCase(unittest.TestCase):

    def setUp(self):

        self.driver = Firefox()
        self.browser = EventFiringWebDriver(self.driver, MyListener())
        #self.addCleanup(self.browser.quit)

    def testContractslist(self):
        self.browser.get("http://localhost/contracts_list")

        inputElement = self.browser.find_element_by_name("openid")
        inputElement.send_keys("https://me.yahoo.com")
        loginElement = self.browser.find_element_by_name("sign_in")
        loginElement.click()
 
        loginBox = self.browser.find_element_by_id("username");
        loginBox.send_keys("techkoch")
        pwBox = self.browser.find_element_by_id("passwd");
        pwBox.send_keys("Holtsville137")
	 
        signinBtn = self.browser.find_element_by_id(".save");
        signinBtn.click()
 
	wait = WebDriverWait(self.browser, 100)
	wait.until(EC.title_contains('Contracts'))
	newbtn = WebDriverWait(self.browser, 100).until(lambda x: x.find_element_by_name("new_btn"))	
	newbtn.click()

    def testPost(self):
        self.browser.get("http://localhost")
        inputElement = self.browser.find_element_by_name("openid")
        inputElement.send_keys("https://me.yahoo.com")
        loginElement = self.browser.find_element_by_name("sign_in")
        loginElement.click()
 
        loginBox = self.browser.find_element_by_id("username");
        loginBox.send_keys("techkoch")
        pwBox = self.browser.find_element_by_id("passwd");
        pwBox.send_keys("Holtsville137")
	 
        signinBtn = self.browser.find_element_by_id(".save");
        signinBtn.click()
	wait = WebDriverWait(self.browser, 100)
	wait.until(EC.title_contains('microblog'))

	#wait = WebDriverWait(self.browser, 100)
        #self.assertIn('microblog', self.browser.title)
	#post = wait.until(EC.presence_of_element_located(By.ID,'post'))
	post = WebDriverWait(self.browser, 100).until(lambda x: x.find_element_by_id("post"))	

	#post = self.browser.find_element_by_name("post")
	post.send_keys("Automated post...")
	savepost = self.browser.find_element_by_name("savepost")
	savepost.click()


if __name__ == '__main__':
    unittest.main(verbosity=2)
    



#    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='http://localhost/contracts_list/']")))
#    blog = driver.find_element_by_xpath("//a[@href='http://irwinhkwan.wordpress.com/']")
#    blog.click()
    
    #driver.quit()
