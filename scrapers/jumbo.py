import pandas as pd
from unidecode import unidecode
from scrapers.falabella import save_promo


class JumboScraper:
    def __init__(self, soup):
        """
        initializes the scraper with a BeautifulSoup object.
        """
        self.soup = soup

    def get_top_banner_promos(self, tipo_oferta='ofertas_top'):
        """
        extracts the top banner promotions.
        """
        top_banner = self.soup.find_all("a", {"class": 'new-home-hero-sliderv2-link'})
        data = []
        for pos, element in enumerate(top_banner, start=1):
            if element.picture:
                name = str(element.picture.find('img').get('alt')).lower()
                formatted_name = '-'.join(name.split('-')[:2])
                img_url = element.picture.find('img').get('src')
                promo = save_promo(formatted_name, tipo_oferta, pos, img_url)
                data.append(promo)

        df = pd.DataFrame(data)
        return df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)

    def get_top_promos(self, tipo_oferta='ofertas_prime'):
        """
        extracts the top promotions (ofertas prime).
        """
        top_banner = self.soup.find_all("a", {"class": 'slider-banner-offers-content-image'})
        data = []
        for pos, element in enumerate(top_banner, start=1):
            if element.picture:
                name = str(element.picture.find('img').get('alt')).lower()
                formatted_name = '-'.join(name.split('-')[:2])
                img_url = element.picture.find('img').get('src')
                promo = save_promo(formatted_name, tipo_oferta, pos, img_url)
                data.append(promo)

        df = pd.DataFrame(data)
        return df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)

    def get_secondary_promos(self, tipo_oferta='ofertas_middle'):
        """
        extracts the secondary promotions.
        """
        timer_banner = self.soup.find_all("div", {"class": 'banner-timer-image'})
        shorts_banner_top = self.soup.find_all("section", {"class": "short-banner"})[:2]

        all_sections = [timer_banner, shorts_banner_top]
        all_sections = [i for sublist in all_sections for i in sublist]  # Flatten list
        data = []
        for pos, element in enumerate(all_sections, start=1):
            name = str(element.find('img').get('alt')).lower()
            formatted_name = '-'.join(name.split('-')[:2])
            img_url = element.find('img').get('src')
            promo = save_promo(formatted_name, tipo_oferta, pos, img_url)
            data.append(promo)

        df = pd.DataFrame(data)
        return df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)

    def get_grid_offers(self, tipo_oferta='ofertas_grid'):
        """
        extracts the grid format offers.
        """
        bottom_long_banners = self.soup.find_all("section", {"class": "short-banner"})[2:]
        bottom_carousel = self.soup.find_all("div", {"class": "slider-banner-offers-wrap-v2"})
        bottom_categories_banners = self.soup.find_all("div", {"class": "section-banner-categories"})[2]
        bottom_left_side = bottom_categories_banners.find_all("div", {"class": 'banner-categories-left'})
        bottom_right_side = bottom_categories_banners.find_all("div", {"class": 'banner-categories-right'})
        bottom_promos = self.soup.find_all("a", {"class": "slider-banner-products-wrap"})
        bottom_doubles = self.soup.find_all("div", {"class": "section-banner-categories"})

        all_sections = [
            bottom_long_banners, bottom_carousel, bottom_left_side, bottom_right_side,
            bottom_promos, bottom_doubles
        ]
        all_sections = [i for sublist in all_sections for i in sublist]  # Flatten list
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
        return df.drop_duplicates(subset='nombre_promocion').reset_index(drop=True)