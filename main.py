import requests
from fake_headers import Headers
import bs4
import json


headers = Headers(browser="firefox", os="win")
headers_data = headers.generate()

main_html = requests.get(
    "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2", headers=headers_data
).text
main_soup = bs4.BeautifulSoup(main_html, "lxml")

vacancy_serp_tag = main_soup.find("div", id="a11y-main-content")
serp_item_tag = vacancy_serp_tag.find_all("div", class_="serp-item")

vacancies_info = []


for vacancy in serp_item_tag:
    vacancy_body_tag = vacancy.find("div", class_="vacancy-serp-item-body")
    a_tag = vacancy_body_tag.find("a")
    vacancy_name = a_tag.text  # Название вакансии
    link = a_tag["href"]  # Ссылка на вакансию
    salary_tag = vacancy_body_tag.find("span", class_="bloko-header-section-3")
    if salary_tag is None:
        salary = "Зарплата не указана"
    else:
        salary = salary_tag.text.replace("\u202f", " ")

    vacancy_company_tag = vacancy_body_tag.find(
        "div", class_="vacancy-serp-item-company"
    )
    company_name_tag = vacancy_company_tag.find("a")
    company_name = company_name_tag.text.replace("\xa0", " ")  # Название компании
    vacancy_address = vacancy_company_tag.find_all("div", "bloko-text")

    full_vacancy = requests.get(link, headers=headers.generate()).text
    full_vacancy_soup = bs4.BeautifulSoup(full_vacancy, "lxml")
    vacancy_section_tag = full_vacancy_soup.find("div", class_="vacancy-section")
    vacancy_description = " ".join(
        vacancy_section_tag.text.split()
    )  # Полное описание вакансии
    company_address_tag = full_vacancy_soup.find(
        "div", class_="vacancy-company-redesigned"
    )
    company_address = company_address_tag.find("p")
    if company_address is None:
        company_address = company_address_tag.find(
            "a", class_="bloko-link bloko-link_kind-tertiary bloko-link_disable-visited"
        )
    company_address = company_address.text

    key_word = ["Django", "Flask"]

    for word in key_word:
        if word in vacancy_description:
            vacancy_info = {
                "vacancy_name": vacancy_name,
                "link": link,
                "salary": salary,
                "company_name": company_name,
                "company_address": company_address,
            }
            vacancies_info.append(vacancy_info)


with open("vacancy.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(vacancies_info, ensure_ascii=False, indent=2))
