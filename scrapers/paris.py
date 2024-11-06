import pandas as pd
from unidecode import unidecode
from scrapers.falabella import save_promo


class ParisScraper:
    def __init__(self, soup):
        """
        initializes the scraper with a BeautifulSoup object.
        """
        self.soup = soup

    def get_top_banner_promos_paris(self, tipo_oferta='ofertas_principales', class_tag="flex-none rounded-lg relative"):
        """
        extracts top banner promotion images.
        """
        paris_top_banner = self.soup.find_all("div", {"class": class_tag})
        data = []
        for pos, element in enumerate(paris_top_banner, start=1):
            if element.picture:
                name = str(element.find('img').get('alt')).lower().replace('en paris.cl', '').replace('paris', '')
                img_url = element.find('source').get('srcset')
                promo = save_promo(name, tipo_oferta, pos, img_url)
                data.append(promo)

        df = pd.DataFrame(data).drop_duplicates().reset_index(drop=True)
        return df

    def get_grid_promos_paris(self, tipo_oferta='grid_ofertas', class_tag="cursor-pointer relative"):
        """
        extracts grid-style promotion images.
        """
        paris_grid = self.soup.find_all("a", {"class": class_tag})
        data = []
        pos = 1
        for element in paris_grid:
            if element.picture:
                name = str(element.find('img').get('alt')).lower().replace('en paris.cl', '').replace('paris', '')
                img_url = element.find('source').get('srcset')
                promo = save_promo(name, tipo_oferta, pos, img_url)
                data.append(promo)
                pos += 1

        df = pd.DataFrame(data).drop_duplicates().reset_index(drop=True)
        return df

    def has_specific_class_and_attribute_lowest_carousel_paris(self, tag, class_match='splide__slide', attribute='id',
                                                               attribute_match='splide'):
        """
        checks if a tag has a specific class and attribute pattern.
        """
        return (
                tag.has_attr('class') and any(class_match in cls for cls in tag['class'])
        ) and (
                tag.has_attr(attribute) and attribute_match in tag[attribute]
        )

    def get_bottom_carousel_paris(self, tipo_oferta='lo_ultimo'):
        """
        extracts images from the bottom section.
        """
        lowest_carousel = self.soup.find_all(self.has_specific_class_and_attribute_lowest_carousel_paris)
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

        df = pd.DataFrame(data).drop_duplicates().reset_index(drop=True)
        return df
