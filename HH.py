from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import json

keywords_set = {"Django", "Flask"}


def wait_element(browser, delay_seconds=0, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


chrome_webdriver_path = ChromeDriverManager().install()
browser_service = Service(executable_path=chrome_webdriver_path)
options = Options()
options.add_argument("--headless")
browser = Chrome(service=browser_service, options=options)
main_part_of_url = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page"
vacancies_list = []
for num_of_page in range(0, 1):
    browser.get(main_part_of_url + str(num_of_page))
    vacancies_main = wait_element(browser, 0, By.CLASS_NAME, "vacancy-serp-content")
    vacancies = vacancies_main.find_elements(By.CLASS_NAME, "vacancy-serp-item-body")
    for vacancy_info in vacancies:
        link_tag = wait_element(vacancy_info, 0, By.CLASS_NAME, "serp-item__title")
        vacancy_link = link_tag.get_attribute('href')
        try:
            salary_tag = vacancy_info.find_element(By.CLASS_NAME, 'bloko-header-section-2')
            salary_text = salary_tag.text
        except NoSuchElementException:
            salary_text = "no info"

        vacancies_list.append(
            {"vacancy_title": vacancy_info.text.split("\n")[0],
                "vacancy_company": vacancy_info.text.split("\n")[1],
                "vacancy_city": vacancy_info.text.split("\n")[2],
                "link": vacancy_link,
                "salary": salary_text}
        )
final_vacancy_list = []
vacancy_index_to_remove = []
for vacancy in vacancies_list:
    vacancy_text_list_with_other_symbols = []
    vacancy_text_list = []
    browser.get(vacancy["link"])
    vacancy_tag = wait_element(browser, 0, By.CLASS_NAME, "vacancy-section")
    vacancy_text_list_with_other_symbols = vacancy_tag.text.split()
    for i in vacancy_text_list_with_other_symbols:
        vacancy_text_list.append(i.strip(',.;:'))
    vacancy_text_set = set(vacancy_text_list)
    if keywords_set.issubset(vacancy_text_set):
        final_vacancy_list.append(vacancy)

with open("result.json", "w") as f:
    json.dump(final_vacancy_list, f, indent=2)

print(final_vacancy_list)

