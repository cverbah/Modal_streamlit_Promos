import time
from selenium import webdriver
from chromedriver_py import binary_path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from unidecode import unidecode
import sys

## functions ###


def scroll_all_website(driver, scroll_increment=100, scroll_delay=0.25,
                       increment_speed_up=300, delay_speed_up=1): # scroll from top to bottom

    page_height = driver.execute_script("return document.body.scrollHeight")
    print(f'page length: {page_height}')
    current_position = 0

    while current_position < page_height:
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(scroll_delay)

        new_page_height = driver.execute_script("return document.body.scrollHeight")
        if page_height < new_page_height:
            print(f'page length updated to: {new_page_height}')
            page_height = new_page_height

        current_position += scroll_increment
        scanned = round(current_position/page_height, 2)
        print(f' website scanned: {scanned:.2%}')
        if scanned > 0.1:  # speed up
            scroll_increment = increment_speed_up
            scroll_delay = delay_speed_up


def scroll_all_website_jumbo(driver, scroll_delay=0.7, start_delay=10):
    #popup = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'popover-delivery-close')))
    #popup.click()

    body = driver.find_element(By.TAG_NAME, "body")
    page_height = int(driver.execute_script("return document.body.scrollHeight")) # not reliable
    if page_height > 6500:
        aux = 30
    elif 4000 < page_height <= 6500:
        aux = 25
    elif page_height <= 4000:
        aux = 15

    print(f'page length: {page_height}')
    current_position = 0
    time.sleep(start_delay)
    while current_position < page_height:
        body.send_keys(Keys.DOWN)
        time.sleep(scroll_delay)

        current_position += aux
        scanned = round(current_position / page_height, 2)
        print(f'aux scanned: {scanned:.2%}')


def save_promo(name, tipo_oferta, pos, img_url):
    data = {}
    data['nombre_promocion'] = unidecode(name)
    data['tipo_oferta'] = tipo_oferta
    data['posicion'] = pos
    data['url_img'] = img_url
    return data


# jumbo
def get_top_banner_promos_jumbo(soup, tipo_oferta='ofertas_top'):
    top_banner = soup.find_all("a", {"class": 'new-home-hero-sliderv2-link'})
    data = []
    for pos, element in enumerate(top_banner, start=1):
        if element.picture:
            name = str(element.picture.find('img').get('alt')).lower()
            formatted_name = '-'.join(name.split('-')[:2])
            img_url = element.picture.find('img').get('src')
            promo = save_promo(formatted_name, tipo_oferta, pos, img_url)
            data.append(promo)

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)
    return df


def get_top_promos_jumbo(soup, tipo_oferta='ofertas_prime'):
    top_banner = soup.find_all("a", {"class": 'slider-banner-offers-content-image'})
    data = []
    for pos, element in enumerate(top_banner, start=1):
        if element.picture:
            name = str(element.picture.find('img').get('alt')).lower()
            formatted_name = '-'.join(name.split('-')[:2])
            img_url = element.picture.find('img').get('src')
            promo = save_promo(formatted_name, tipo_oferta, pos, img_url)
            data.append(promo)

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)
    return df


def get_secondary_promos_jumbo(soup, tipo_oferta='ofertas_middle'):
    timer_banner = soup.find_all("div", {"class": 'banner-timer-image'})
    shorts_banner_top = soup.find_all("section", {"class": "short-banner"})[:2]

    all_sections = [timer_banner, shorts_banner_top]
    all_sections = [i for sublist in all_sections for i in sublist]  # flatten
    data = []
    for pos, element in enumerate(all_sections, start=1):
        name = str(element.find('img').get('alt')).lower()
        formatted_name = '-'.join(name.split('-')[:2])
        img_url = element.find('img').get('src')
        # tipo_oferta = element.get('class')[0]
        promo = save_promo(formatted_name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)
    return df


def get_grid_offers_jumbo(soup, tipo_oferta='ofertas_grid'):
    bottom_long_banners = soup.find_all("section", {"class": "short-banner"})[2:]
    bottom_carousel = soup.find_all("div", {"class": "slider-banner-offers-wrap-v2"})
    bottom_categories_banners = soup.find_all("div", {"class": "section-banner-categories"})[2]
    bottom_left_side = bottom_categories_banners.find_all("div", {"class": 'banner-categories-left'})
    bottom_right_side = bottom_categories_banners.find_all("div", {"class": 'banner-categories-right'})
    bottom_promos = soup.find_all("a", {"class": "slider-banner-products-wrap"})
    bottom_doubles = soup.find_all("div", {"class": "section-banner-categories"})

    all_sections = [bottom_long_banners, bottom_carousel, bottom_left_side, bottom_right_side,
                    bottom_promos, bottom_doubles]
    all_sections = [i for sublist in all_sections for i in sublist]  # flatten
    data = []
    position = 0
    for banner in all_sections:
        imgs = banner.find_all('img')
        for pos, element in enumerate(imgs, start=1):
            name = element.get('alt').lower()
            formatted_name = '-'.join(name.split('-')[:2])
            img_url = element.get('src')
            position += 1
            promo = save_promo(formatted_name, tipo_oferta, position, img_url)
            data.append(promo)

        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)

    return df


# lider - catalogo (potencialmente identico a supermercado. Por ahora voy a separarlos
def has_specific_class_and_attribute_top_banner_lider_catalogo(tag, class_match='banners-home', attribute='id', attribute_match='home-banner-'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])


def get_top_banner_promos_lider_catalogo(soup, tipo_oferta='ofertas_principales'):
    top_banner = soup.find_all(has_specific_class_and_attribute_top_banner_lider_catalogo)
    data = []
    for element in top_banner:
        name = str(element.find('img').get('alt')).lower()
        img_url = element.find('img').get('src')
        pos = int(name.split('-')[-1]) + 1
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data).drop_duplicates()
    df = df.sort_values(by='posicion').reset_index(drop=True)
    return df


def has_specific_class_and_attribute_grid_lider_catalogo(tag, class_match='limited-time-sales', attribute='id', attribute_match='grid'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])


def has_specific_class_and_attribute_grid_banner_lider_catalogo(tag, class_match='line-breaker', attribute='id', attribute_match='line-breakers'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])


def get_grid_promos_lider_catalogo(soup, tipo_oferta='grid_ofertas'):
    grid = soup.find_all(has_specific_class_and_attribute_grid_lider_catalogo)
    grid_banner = soup.find_all(has_specific_class_and_attribute_grid_banner_lider_catalogo)
    data = []
    for element in grid: # grid
        name = str(element.get('id')).lower()
        img_url = element.get('style').split('url("')[1].split('")')[0]
        pos = int(name.split('-')[0].replace('grid',''))
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    for element in grid_banner: #lower banner grid
        name = str(element.get('id')).lower()
        img_url = element.find('img').get('src')
        pos = pos + 1

        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data).drop_duplicates()
    df = df.sort_values(by='posicion').reset_index(drop=True)
    return df


def has_specific_class_bottom_offers_lider_catalogo(tag, class_match='CampaignHomeStyledComponents__OffersBannerSection'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class']))


def has_specific_class_bottom_highlighted_lider_catalogo(tag, class_match='CampaignHomeStyledComponents__InspirationalSection'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class']))


def get_bottom_offers_lider_catalogo(soup, tipo_oferta='ofertas_final_pag'):

    bottom_offers = soup.find_all(has_specific_class_bottom_offers_lider_catalogo)
    destacados_lider = soup.find_all(has_specific_class_bottom_highlighted_lider_catalogo)

    lowest_imgs = [container.find_all("img") for container in bottom_offers][0]
    destacados_imgs = [container.find_all("img") for container in destacados_lider]
    destacados_imgs = [i for sublist in destacados_imgs for i in sublist] #flatten

    lowest_imgs.extend(destacados_imgs)
    data = []
    for pos, element in enumerate(lowest_imgs, start=1):
        name = str(element.get('alt')).lower()+'-'+str(pos)
        img_url = element.get('src')
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data).drop_duplicates()
    df = df.sort_values(by='posicion').reset_index(drop=True)
    return df


#  lider - supermarket scrapping
def has_specific_class_and_attribute_top_banner_lider_supermarket(tag, class_match='banners-home', attribute='id', attribute_match='home-banner-'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])


def get_top_banner_promos_lider_supermarket(soup, tipo_oferta='ofertas_principales'):
    top_banner = soup.find_all(has_specific_class_and_attribute_top_banner_lider_supermarket)
    data = []
    for element in top_banner:
        name = str(element.find('img').get('alt')).lower()
        img_url = element.find('img').get('src')
        pos = int(name.split('-')[-1]) + 1
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data).drop_duplicates()
    df = df.sort_values(by='posicion').reset_index(drop=True)
    return df


def has_specific_class_and_attribute_grid_lider_supermarket(tag, class_match='limited-time-sales', attribute='id', attribute_match='grid'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])

def has_specific_class_and_attribute_grid_banner_lider_supermarket(tag, class_match='line-breaker', attribute='id', attribute_match='line-breakers'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])


def get_grid_promos_lider_supermarket(soup, tipo_oferta='grid_ofertas'):
    grid = soup.find_all(has_specific_class_and_attribute_grid_lider_supermarket)
    grid_banner = soup.find_all(has_specific_class_and_attribute_grid_banner_lider_supermarket)
    data = []
    for element in grid:  # grid
        name = str(element.get('id')).lower()
        img_url = element.get('style').split('url("')[1].split('")')[0]
        pos = int(name.split('-')[0].replace('grid', ''))
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    for element in grid_banner:  # lower banner grid
        name = str(element.get('id')).lower()
        img_url = element.find('img').get('src')
        pos = pos + 1
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data).drop_duplicates()
    df = df.reset_index(drop=True)
    return df


def has_specific_class_bottom_offers_lider_supermarket(tag, class_match='CampaignHomeStyledComponents__OffersBannerSection'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class']))


def has_specific_class_bottom_highlighted_lider_supermarket(tag, class_match='CampaignHomeStyledComponents__InspirationalSection'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class']))


def get_bottom_offers_lider_supermarket(soup, tipo_oferta='ofertas_final_pag'):
    bottom_offers = soup.find_all(has_specific_class_bottom_offers_lider_supermarket)
    destacados_lider = soup.find_all(has_specific_class_bottom_highlighted_lider_supermarket)

    lowest_imgs = [container.find_all("img") for container in bottom_offers][0]
    lowest_imgs.extend([container.find_all("img") for container in destacados_lider][0])
    data = []
    for pos, element in enumerate(lowest_imgs, start=1):
        name = str(element.get('alt')).lower() + '-' + str(pos)
        img_url = element.get('src')
        promo = save_promo(name, tipo_oferta, pos, img_url)
        data.append(promo)

    df = pd.DataFrame(data).drop_duplicates()
    df = df.reset_index(drop=True)
    return df


## paris scrapping
def get_top_banner_promos_paris(soup, tipo_oferta='ofertas_principales', class_tag="flex-none rounded-lg relative"):
    paris_top_banner = soup.find_all("div", {"class": class_tag})
    data = []
    for pos, element in enumerate(paris_top_banner, start=1):
        if element.picture:
            name = str(element.find('img').get('alt')).lower().replace('en paris.cl', '').replace('paris', '')
            img_url = element.find('source').get('srcset')
            promo = save_promo(name, tipo_oferta, pos, img_url)
            data.append(promo)
    df = pd.DataFrame(data).drop_duplicates()
    df = df.reset_index(drop=True)
    return df


def get_grid_promos_paris(soup, tipo_oferta='grid_ofertas', class_tag="cursor-pointer relative"):
    paris_grid = soup.find_all("a", {"class": class_tag})
    data = []
    pos = 1
    for element in paris_grid:
        if element.picture:
            name = str(element.find('img').get('alt')).lower().replace('en paris.cl','').replace('paris','')
            img_url = element.find('source').get('srcset')
            promo = save_promo(name, tipo_oferta, pos, img_url)
            data.append(promo)
            pos += 1
    df = pd.DataFrame(data).drop_duplicates()
    df = df.reset_index(drop=True)
    return df


def has_specific_class_and_attribute_lowest_carousel_paris(tag, class_match='splide__slide', attribute='id', attribute_match='splide'):
    return (tag.has_attr('class') and any(class_match in cls for cls in tag['class'])) and \
           (tag.has_attr(attribute) and attribute_match in tag[attribute])


def get_bottom_carousel_paris(soup, tipo_oferta='lo_ultimo'):
    lowest_carousel = soup.find_all(has_specific_class_and_attribute_lowest_carousel_paris)
    data = []
    position = 1
    for pos, element in enumerate(lowest_carousel, start=1):
        promo_data = element.find_all('img')
        for i in promo_data:
            name = str(i.get('alt')).lower().replace('en paris.cl', '').replace('paris', '')
            img_url = i.get('src')
            promo = save_promo(name, tipo_oferta, position, img_url)
            data.append(promo)
            position += 1
    df = pd.DataFrame(data).drop_duplicates()
    df = df.reset_index(drop=True)
    return df


# falabella scrapping
def get_imgs_banner_principal_falabella(soup, class_type='CarouselItemstyle', promo_type='ofertas_principales'):
    assert promo_type == 'ofertas_principales' or promo_type == 'ofertas_secundarias', 'error'
    dict_promos = {'ofertas_principales': 'showcase', 'ofertas_secundarias': 'carousel'}

    carousel_items = soup.find_all(class_=lambda c: c and 'CarouselItemstyle' in c)
    pos = 1
    all_data = []
    for item in carousel_items:
        x = item.get('data-testid', '').split('-')[0]
        if x == dict_promos[promo_type]:

            if item.picture:
                img_url = item.picture.find('source').get('srcset')
                name = str(item.picture.find('img').get('alt')).lower()
                data = save_promo(name, promo_type, pos, img_url)
                all_data.append(data)

                pos += 1

    return pd.DataFrame(all_data)


def get_imgs_banner_falabella_size(soup, class_type='BannerPowerCardstyle', cols=3):
    try:
        dict_cols = {3: 'three-columns',
                     6: 'six-columns',
                     12: 'twelve-columns'}
        dict_size = {3: 'grid',
                     6: 'banner_doble',
                     12: 'banner_largo'}

        # Find all elements with both class substrings
        banner_items = soup.find_all(
            lambda tag: tag.get('class') and
                        any(class_type in cls for cls in tag['class']) and
                        any(dict_cols[cols] in cls for cls in tag['class'])
        )

        pos = 1
        all_data = []
        for item in banner_items:
            data_test_id_prefix = item.get('data-testid', '').split('-')[0]
            if data_test_id_prefix == 'power':
                if item.picture:
                    # print(item.prettify())
                    promo_type = dict_size[cols]
                    img_url = item.picture.find('source').get('srcset')
                    name = str(item.picture.find('img').get('alt')).lower()
                    # Save promo data
                    data = save_promo(name, promo_type, pos, img_url)
                    all_data.append(data)
                    pos += 1

        return pd.DataFrame(all_data)

    except Exception as e:
        print(f'Error:{e}')


blacklist = ['falabella', 'sodimac', 'tottus', 'linio', 'cmr', 'nosotros', 'ecosistema', 'seguros', 'puntospesos', 'paris', 'paris.cl', 'lider', 'lider.cl',
             'walmart', 'descubre todo lo nuevo', 'cencosud', 'puntos']
def flag_blacklist(row, blacklist=blacklist):
    row = str(row)
    tokens = re.findall(r"(?=("+'|'.join(blacklist)+r"))", row)
    if len(tokens) > 0:
      return 'flagged_as_blacklisted'
    else:
      return row


def main(argv, get_data=True):
    ''''testing: get promotions and discounts images from home site'''
    assert argv[1] in ['falabella', 'paris', 'lider-supermercado', 'lider-catalogo', 'jumbo'],\
        'retails supported: falabella, paris, lider-supermercado, lider-catalogo, jumbo as argv'

    if argv[1] == 'falabella':
        aux = 1
        url = 'https://www.falabella.com/falabella-cl'
        scroll_increment = 10
        scroll_delay = 1.5
        increment_speed_up = 300
        delay_speed_up = 1
        lazy_type = 1

    if argv[1] == 'paris':
        aux = 2
        url = 'https://paris.cl'
        scroll_increment = 15
        scroll_delay = 1
        increment_speed_up = 300
        delay_speed_up = 1
        lazy_type = 1

    if argv[1] == 'lider-supermercado':
        aux = 3
        url = 'https://www.lider.cl/supermercado/'
        scroll_increment = 5
        scroll_delay = 1.5
        increment_speed_up = 300
        delay_speed_up = 1
        lazy_type = 1

    if argv[1] == 'lider-catalogo':
        aux = 4
        url = 'https://www.lider.cl/catalogo/'
        scroll_increment = 5
        scroll_delay = 1.5
        increment_speed_up = 150
        delay_speed_up = 1
        lazy_type = 1

    if argv[1] == 'jumbo':
        aux = 5
        url = 'https://www.jumbo.cl/'
        lazy_type = 2

    # driver setup
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('disable-notifications')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options, executable_path=binary_path)
    try:
        driver.get(url)
        time.sleep(2)

        if lazy_type == 1:
            scroll_all_website(driver, scroll_increment=scroll_increment, scroll_delay=scroll_delay,
                               increment_speed_up=increment_speed_up, delay_speed_up=delay_speed_up)
        if lazy_type == 2:
            scroll_all_website_jumbo(driver)

        # get code with lazyload-wrappers imgs loaded
        website_code = driver.page_source
        with open('webpage_source.txt', 'w', encoding='utf-8') as file:
            file.write(website_code)
        driver.quit()

        soup = BeautifulSoup(website_code, 'html.parser')
        if get_data:
            if aux == 1:  # falabella
                top_banner = get_imgs_banner_principal_falabella(soup)
                medium_banners = get_imgs_banner_falabella_size(soup, cols=6)
                grid = get_imgs_banner_falabella_size(soup, cols=3)
                large_banners = get_imgs_banner_falabella_size(soup, cols=12)

                df_imgs = pd.concat([top_banner,large_banners, medium_banners, grid])
                df_imgs = df_imgs.reset_index(drop=True)

            if aux == 2:  # paris
                top_banner = get_top_banner_promos_paris(soup, tipo_oferta='ofertas_principales', class_tag="flex-none rounded-lg relative")
                grid = get_grid_promos_paris(soup, tipo_oferta='grid_ofertas', class_tag="cursor-pointer relative")
                bottom_carousel = get_bottom_carousel_paris(soup, tipo_oferta='lo_ultimo')

                df_imgs = pd.concat([top_banner, grid, bottom_carousel])
                df_imgs = df_imgs.reset_index(drop=True)

            if aux == 3:  # lider-supermercados
                top_banner = get_top_banner_promos_lider_supermarket(soup, tipo_oferta='ofertas_principales')
                grid = get_grid_promos_lider_supermarket(soup, tipo_oferta='grid_ofertas')
                bottom_offers = get_bottom_offers_lider_supermarket(soup, tipo_oferta='ofertas_final_pag')

                df_imgs = pd.concat([top_banner, grid, bottom_offers])
                df_imgs = df_imgs.reset_index(drop=True)

            if aux == 4:  # lider-catalogo
                top_banner = get_top_banner_promos_lider_catalogo(soup, tipo_oferta='ofertas_principales')
                grid = get_grid_promos_lider_catalogo(soup, tipo_oferta='grid_ofertas')
                bottom_offers = get_bottom_offers_lider_catalogo(soup, tipo_oferta='ofertas_final_pag')

                df_imgs = pd.concat([top_banner, grid, bottom_offers])
                df_imgs = df_imgs.reset_index(drop=True)

            if aux == 5:  # jumbo
                top_banner = get_top_banner_promos_jumbo(soup, tipo_oferta='ofertas_principales')
                top_offers = get_top_promos_jumbo(soup, tipo_oferta='ofertas_prime').iloc[:4]
                secondary_promos = get_secondary_promos_jumbo(soup, tipo_oferta='ofertas_middle')
                grid_offers = get_grid_offers_jumbo(soup, tipo_oferta='ofertas_grid')

                df_imgs = pd.concat([top_banner, top_offers, secondary_promos, grid_offers])
                df_imgs = df_imgs.reset_index(drop=True)


            df_imgs['nombre_promocion'] = df_imgs['nombre_promocion'].apply(lambda row: flag_blacklist(row))
            df_imgs = df_imgs[~df_imgs.nombre_promocion.isin(['flagged_as_blacklisted', ''])]  # filter out
            df_imgs = df_imgs.drop_duplicates().reset_index(drop=True)  # filter out
            df_imgs['datetime_checked'] = pd.to_datetime('today')
            df_imgs['retail'] = argv[1]
            print('\n Df Head: ')
            print(df_imgs.head(10))
            df_imgs.to_csv(f'./data_retails/promos_home/df_promos_retail_{argv[1]}.csv')

    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    main(sys.argv)
