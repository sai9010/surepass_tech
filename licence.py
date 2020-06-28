from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
from webdriver_manager.chrome import ChromeDriverManager
import fire

def details(licence_num, dob):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    time.sleep(5)
    driver.get('https://parivahan.gov.in/rcdlstatus/?pur_cd=101')
    time.sleep(5)
    data = driver.find_element_by_css_selector("#form_rcdl\:tf_dlNO")
    data.send_keys(licence_num.upper())

    def verify(dob):
        try:
            my_date = datetime.strptime(dob, "%Y-%m-%d")
        except Exception as e:
            print(e)
            dob = input("please enter date of birth in shown format yyyy-mm-dd eg:1976-02-09 : ")
            my_date = verify(dob)
        return my_date
    my_date = verify(dob)
    holder = driver.find_element_by_xpath('//*[@id="form_rcdl:tf_dob_input"]')
    holder.click()
    time.sleep(2)
    select1 = Select(driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    value = my_date.month - 1

    def mont(value):
        try:
            select1.select_by_value(str(value))
        except Exception as e:
            month = input("please enter valid month starts at 01 for january and ends at 06 for june: eg: 01 ")
            my_date = my_date.replace(month=int(month))
            value = my_date.month - 1
            mont(value)
    mont(value)
    select2 = Select(driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/div/select[2]'))
    yr = my_date.year

    def yer(yr):
        try:
            select2.select_by_visible_text(str(yr))
        except Exception as e:
            year = input("please enter valid year starts at 1900 and ends at 2020 eg: 1976 : ")
            my_date = my_date.replace(year=int(year))
            yr = my_date.year
            yer(yr)
    yer(yr)
    dateWidget = driver.find_element_by_id("ui-datepicker-div")
    columns = dateWidget.find_elements_by_tag_name("td")
    for cell in columns:
        if str(cell.text) == str(my_date.day):
            cell.find_element_by_link_text(str(my_date.day)).click()
            break

    captcha_data = driver.find_element_by_xpath('//*[@id="form_rcdl:j_idt32:CaptchaID"]')


    def dummy():
        code = input("please enter verifiation code:")
        return code


    captcha_data.send_keys(dummy())
    button = driver.find_element_by_css_selector("#form_rcdl\:j_idt43")
    button.click()
    time.sleep(5)

    def next_page():
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            tabl = soup.find("table", {"class", "table table-responsive table-striped table-condensed table-bordered"})
            if tabl is not None:
                tab2 = soup.find("table", {"class", "table table-responsive table-striped table-condensed table-bordered data-table"})
                tab3 = soup.find("div", {"class", "ui-datatable-tablewrapper"})
                cov = tab3.find("tr", {"class", "ui-widget-content ui-datatable-even"})
                dic = {}
                for ind, item in enumerate(tabl.find_all("td")):
                    if ind == 3:
                        dic["name"] = item.get_text()
                    elif ind == 5:
                        dic["date_of_issue"] = item.get_text()
                    else:
                        pass

                for ind, item in enumerate(tab2.tr.find_all("td")):
                    if ind == 2:
                        dic["date_of_expiry"] = item.get_text()[3:]

                for ins, item in enumerate(cov.find_all("td")):
                    if ins == 1:
                        dic["class_of_vehicle"] = item.get_text()

                json_object = json.dumps(dic, indent=4)
                return(json_object)
            elif driver.find_element_by_xpath('//*[@id="primefacesmessagedlg"]/div[1]/a/span') is not None:
                print("please enter valid details: Eg: avoid using space in licence number")
            elif driver.find_element_by_xpath('//*[@id="form_rcdl:j_idt13"]/div/ul/li/span[1]') is not None:
                code = input("re-enter captcha")
                captcha_data.send_keys(code)
                button.click()
                time.sleep(5)
            else:
                pass

        except Exception as e:
            print("error:",e)
    return(next_page())
    driver.quit()

if __name__ == "__main__":
#    l=input("enter licence num:")
#    d=input("enter dob")
 #   details(l,d)
    fire.Fire(details)

