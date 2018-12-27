import builtins
import pandas as pd
import re
import time
import pandas
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

names_subjects = pd.read_csv('names_subjects.csv', encoding='windows-1251', sep=';')

def table_creation():
    table = pd.DataFrame(columns=['ФИО', 'Номер дела', 'Вид судопроизводства',
                                  'Инстанция', 'Категория гражданского дела', 'Субъект РФ',
                                  'Наименование суда', 'Результат',  'Сторона по делу',
                                  'Тип документа', 'Дата судебного акта', 'Дата публикации'])
    return table


class Person:
    """Definition web-session for one person"""

    def __init__(self, full_name, subject_RF):
        self.full_name = full_name
        self.subject_RF = subject_RF
        self.person = '"' + self.full_name + '" AND "' + self.subject_RF + '"'

    def input_button(self, wait):
        """Enter data into input space."""
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="portalSearchInput"]')))
        button.click()
        button.send_keys(self.person)
        button.send_keys(Keys.RETURN)

    def clear_button(self, wait):
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="portalSearchInput"]')))
        button.click()
        button.clear()
        button.click()

    def cond_button(self, wait):
        cond_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//ul[2][@id="resultsList"]')))
        cond_button.click()
        time.sleep(1 + random.random())
        cond_1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*')))
        time.sleep(1 + random.random())
        return (cond_1.text)

    def back_button(self, wait):
        """Return to ther input space."""
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//body')))
        button.click()
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="text backToList"]')))
        button.click()
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="portalSearchInput"]')))
        button.click()
        button.clear()

    def open_first_article(self, wait):
        """Open the first report."""
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//body')))
        time.sleep(3 + random.random())
        button.click()
        article = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="resultHeader openCardLink"]')))
        article.click()
        time.sleep(3 + random.random())

    def count_articles(self, wait):
        """Get the next article."""
        counts_str = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="text result-counter"]')))
        counts_str.click()
        count_str = re.split(r'из ', counts_str.text)
        count = int(count_str[1])
        return count

    def get_next_article(self, wait):
        """Return the next page."""
        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//body')))
        element.click()
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[@class="to-right-red forward-btn yui-button yui-btn-32"]')))
        element.click()

    def info_table(self, wait):
        """Return info about person"""
        table_1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[1][@class="group-box group-box-open"]')))
        table_1.click()
        info_1 = [i[1] for i in enumerate(table_1.text.split('\n')) if (i[0] % 2 != 1)][1:8]

        table_2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[2][@class="group-box group-box-open"]')))
        table_2.click()
        name_list = self.full_name.split()
        init_name = name_list[0] + ' ' + name_list[1][0] + '.' + name_list[2][0] + '.'
        all_info_2 = [i[1] for i in enumerate(table_2.text.split('\n')) if (init_name in i[1])]
        info_2 = [' '.join(all_info_2)]

        table_3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[3][@class="group-box group-box-open"]')))
        table_3.click()
        info_3 = [i[1] for i in enumerate(table_3.text.split('\n')) if (i[0] % 2 != 1)][1:-1]
        if len(info_3) == 2:
            info_3.append('No data')
        info = info_1 + info_2 + info_3
        all_info = [self.full_name] + info
        return all_info

    def table_enter(self, info, table):
        """Enter data into table."""
        table.loc[len(table)] = info
        table.to_csv('test_results.csv', index=False, encoding='cp1251', sep=';')


def main():
    """fraud base == 1."""

    url = 'https://bsr.sudrf.ru/bigs/portal.html'

    full_names = names_subjects.full_name.values
    subjects_RF = names_subjects.subject_RF.values

    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 30)
    table = table_creation()

    try:
        for i in zip(full_names, subjects_RF):
            person = Person(i[0], i[1])
            person.input_button(wait)
            cond = person.cond_button(wait)
            if ('Ничего не найдено' in cond):
                print('No court')
                info = [person.full_name] + 11 * ['No data']
                person.table_enter(info, table)
                print(f'"No data" for {person.full_name} has written into table.')
                person.clear_button(wait)
                time.sleep(5 + random.random())
            else:
                person.open_first_article(wait)
                counter = person.count_articles(wait)
                print(f'{counter} courts')
                for j in range(counter):
                    info = person.info_table(wait)
                    try:
                        person.table_enter(info, table)
                        print(f'The article №{j + 1} for {person.full_name} has written into table.')
                    except ValueError:
                        print(info)
                    if j == (counter - 1):
                        break
                    else:
                        person.get_next_article(wait)
                    time.sleep(5 + random.random())
                person.back_button(wait)
    except TimeoutException:
        print(".... wait ... wait ... wait, I'm blocked =((")
    finally:
        driver.close()


if __name__ == "__main__":
    main()