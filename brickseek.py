import os
import csv
from selenium import webdriver
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('BRICKSEEK_USERNAME')
PASSWORD = os.getenv('BRICKSEEK_PASSWORD')
ZIPCODE = os.getenv('BRICKSEEK_ZIPCODE')
RADIUS = float(os.getenv('BRICKSEEK_RADIUS'))

# Filters 
def filter_by_category(Markdown):
    return True if Markdown.category in DESIRED_CATEGORIES else False

def filter_by_percent_off(Markdown):
    return True if (Markdown.percent_off >=  DESIRED_PERCENT_OFF) else False

'''
Product Categories:
    ['Apparel', 'Appliances', 'Automotive', 'Baby', 'Books', 'Electronics', 'Garden & Outdoors', 'Grocery', 'Health & Beauty', 
    'Home Goods & Furniture', 'Home Improvement', 'Movies & Music', 'Office & School', 'Tools', 'Toys & Games', 'Unknown']
'''
DESIRED_CATEGORIES = ['Electronics'] # To Do : make a dictionary of categories
DESIRED_PERCENT_OFF = 0.0
FILTERS = [filter_by_category]

class Markdown:
  def __init__(self,name, category, curr_price, msrp, percent_off, dollars_off, is_available, link):
    self.name = name
    self.category = category
    self.curr_price = curr_price
    self.msrp = msrp
    self.percent_off = percent_off
    self.dollars_off = dollars_off
    self.is_available = is_available
    self.link = link
    self.array = [name, category, curr_price, msrp, percent_off, dollars_off, is_available, link]

driver = webdriver.Chrome()

def is_desired(Markdown):
    is_desired = True
    if len(FILTERS) > 0:
        for filter in FILTERS:
            is_desired = filter(Markdown)
    return is_desired

def main():
    login()
    url = 'https://brickseek.com/walmart-clearance-stores/?zip=' + ZIPCODE
    driver.get(url)
    stores = driver.find_elements_by_class_name('item-list__item')
    nearby_stores = get_store_links_in_radius(stores, RADIUS)
    markdowns_table = get_store_markdowns(nearby_stores)
    export_to_excel(markdowns_table)

def login():
    try:
        driver.get('https://brickseek.com/login')
        username_input = driver.find_element_by_name('user_login')
        password_input = driver.find_element_by_name('user_password')
        submit_button = driver.find_element_by_name('submit')     
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        submit_button.click()
        assert driver.current_url == 'https://brickseek.com/'
        print('Login successful')
    except Exception as e:
        print(e)
        print('Error logging in')
        driver.close()

def get_store_links_in_radius(stores, radius):
    page_links = []
    for i in range(len(stores)):
        distance = parse_distance(stores[i].find_element_by_class_name('address__below').get_attribute('innerHTML'))
        if distance <= radius :
            page_links.append(get_store_page_link(stores[i]))
        else: 
            break
    return page_links

def get_store_page_link(store):
    return store.find_element_by_class_name('item-list__button-item').get_attribute('href')

def parse_distance(html):
    # html = <div class="address__below"> (2.3 Miles Away) </div>
    miles = ''
    for c in range(2, len(html)):
        if(html[c] == ' '):
            break
        miles += html[c]
    return float(miles)

def get_store_markdowns(stores):
    markdowns_table = [['Name', 'Category', 'Current Price', 'MSRP', 'Discount Percent', 'Discount Dollars', 'In Stock', 'Link']]
    print('Scraping markdowns...')
    for store in stores:
        driver.get(store)
        markdowns_table.append([get_store_address()])
        markdowns = driver.find_elements_by_class_name('item-list__item')
        next_page = None
        is_next_page = True
        while is_next_page:
            for i in range(len(markdowns)):
                Markdown = parse_markdown_item(markdowns[i])
                if Markdown is not None and is_desired(Markdown):
                    markdowns_table.append(Markdown.array)
            next_page = get_next_page()
            if next_page and next_page.get_attribute('href'):
                is_next_page = True
                next_page.click()
                markdowns = driver.find_elements_by_class_name('item-list__item')
            else:
                is_next_page = False
    
    return markdowns_table

def get_next_page():
    next_page = None
    try:
        next_page = driver.find_element_by_class_name('pagination__next')
    except Exception:
        next_page = None
        pass
    return next_page

def get_store_address():
    address_text = driver.find_element_by_class_name('address').text
    address = ''
    num_lines = 0
    for i in range(len(address_text)):
        if num_lines == 2 :
            break
        if address_text[i] == '\n':
            if num_lines == 0:
                address += ', '
            num_lines += 1
        else :
            address += address_text[i]
    return address


def parse_markdown_item(item):
    name = get_item_name(item)
    category = get_item_category(item)
    curr_price = get_item_curr_price(item)
    msrp =  get_item_msrp(item)
    percent_off = get_percent_off(curr_price, msrp)
    dollars_off = get_dollars_off(curr_price, msrp)
    is_available = get_item_availability(item)
    link = get_item_link(item)

    if not is_available:
        return None

    return  Markdown (name, category, curr_price, msrp, percent_off, dollars_off, is_available, link)

def get_item_name(item):
    return item.find_element_by_class_name('item-list__title').find_element_by_css_selector('span').get_attribute('innerHTML')

def get_item_link(item):
    return item.find_element_by_class_name('item-list__link').get_attribute('href')
    
def get_item_curr_price(item):
    price = item.find_elements_by_class_name('price-formatted')[0]
    dollars = price.find_element_by_class_name('price-formatted__dollars').get_attribute('innerHTML') 
    cents = price.find_element_by_class_name('price-formatted__cents').get_attribute('innerHTML')
    return float(f'{dollars}.{cents}')

def get_item_msrp(item):
    price = item.find_element_by_class_name('item-list__footer').text
    msrp = ''
    i = price.find('MSRP: ') + len('MSRP: $')
    while price[i] and price[i] != '\n':
        msrp += price[i]
        i+=1
    return float(msrp)

def get_item_availability(item):
    availability_text = item.find_element_by_class_name('availability-status-indicator__text').text
    return True if availability_text == 'In Stock' else False

def get_percent_off(curr_price, msrp):
    return 1 - round((curr_price/msrp), 2)

def get_dollars_off(curr_price, msrp):
    return msrp-curr_price

def get_item_category(item):
    category = None
    try:
        category = item.find_element_by_class_name('item-action').get_attribute('data-category')
    except Exception:
        category = None
        pass
    return category
    
def export_to_excel(markdowns_table):
    with open('markdowns.csv', 'a') as file:    # appends if file exists, otherwise creates new file
        csv_writter = csv.writer(file)
    
        for row in markdowns_table:
            csv_writter.writerow(row)

    print('Export to Excel complete')
    
if __name__ == "__main__":
    main()


    