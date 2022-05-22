from apps.user.views import api_register
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import json


class Test_REG:
    url = "http://127.0.0.1:5000/api/v1/user/?username={username}&password={password}&email={email}&role_id={role_id}"
    url2 = "http://127.0.0.1:5000/api/v1/user/?password={password}&email={email}&role_id={role_id}"

    def test_register1(self):
        res = json.loads(
            urlopen(self.url.format(username="aaa", password="123", email="1@123.com", role_id=-1),
                    data=b"").read().decode())[
            "message"]
        assert res == "身份错误"

    def test_register2(self):
        res = json.loads(
            urlopen(self.url.format(username="aaa", password="123", email="1@123.com", role_id=4),
                    data=b"").read().decode())[
            "message"]
        assert res == "身份错误"

    def test_register3(self):
        res = json.loads(
            urlopen(self.url.format(username="aaa", password="123", email="123.com", role_id=0),
                    data=b"").read().decode())[
            "message"]
        assert res == "邮箱格式错误"

    def test_register4(self):
        res = json.loads(
            urlopen(self.url2.format(password="123", email="1@123.com", role_id=0), data=b"").read().decode())[
            "message"]
        assert res == "传参缺失"

    def test_register5(self):
        res = json.loads(
            urlopen(self.url.format(username="dirver", password="123", email="1@123.com", role_id=0),
                    data=b"").read().decode())[
            "message"]
        assert res == "用户名已经注册"


class Test_Chat:
    login_url = "http://127.0.0.1:5000/api/v1/user/login?username={username}&password={password}"
    get_order_url = "http://127.0.0.1:5000/api/v1/order/chat-token"
    customer_token = ""
    driver_token = ""

    customer_browser = None
    driver_browser = None

    def setup_method(self):
        self.customer_token = \
            json.loads(urlopen(self.login_url.format(username="customer", password="123")).read().decode())["data"][
                "token"]
        self.driver_token = \
            json.loads(urlopen(self.login_url.format(username="driver", password="123")).read().decode())["data"][
                "token"]

        self.customer_browser = webdriver.Firefox()
        self.driver_browser = webdriver.Firefox()

        self.customer_browser.get("file:///F:/.PythonProject/turn-4/templates/index.html")
        self.driver_browser.get("file:///F:/.PythonProject/turn-4/templates/index.html")

        head = {
            'token': self.customer_token
        }
        req = Request(self.get_order_url, headers=head)
        self.customer_token = json.loads(urlopen(req).read().decode())["data"]["tokens"][0]["token"]

        head = {
            'token': self.driver_token
        }
        req = Request(self.get_order_url, headers=head)
        self.driver_token = json.loads(urlopen(req).read().decode())["data"]["tokens"][0]["token"]

        self.customer_browser.find_element(By.ID, "token").send_keys(self.customer_token)
        self.customer_browser.find_element(By.ID, "button-join").send_keys(Keys.ENTER)
        self.driver_browser.find_element(By.ID, "token").send_keys(self.driver_token)
        self.driver_browser.find_element(By.ID, "button-join").send_keys(Keys.ENTER)

    def test_talk(self):
        self.driver_browser.find_element(By.ID, "content").send_keys("AAA")
        self.driver_browser.find_element(By.ID, "button-submit").send_keys(Keys.ENTER)
        assert "AAA" in self.customer_browser.find_element(By.ID, "chat").get_attribute("value")
        assert "AAA" in self.driver_browser.find_element(By.ID, "chat").get_attribute("value")

        self.driver_browser.find_element(By.ID, "button-leave").send_keys(Keys.ENTER)

        self.customer_browser.find_element(By.ID, "content").send_keys("BBB")
        self.customer_browser.find_element(By.ID, "button-submit").send_keys(Keys.ENTER)
        assert "BBB" in self.customer_browser.find_element(By.ID, "chat").get_attribute("value")
        assert "BBB" not in self.driver_browser.find_element(By.ID, "chat").get_attribute("value")

    def teardown_method(self):
        self.customer_browser.quit()
        self.driver_browser.quit()
