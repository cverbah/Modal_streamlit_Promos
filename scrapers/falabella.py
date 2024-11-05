import pandas as pd
from unidecode import unidecode


def save_promo(name, tipo_oferta, pos, img_url):
    data = {}
    data['nombre_promocion'] = unidecode(name)
    data['tipo_oferta'] = tipo_oferta
    data['posicion'] = pos
    data['url_img'] = img_url
    return data


class FalabellaScraper:
    def __init__(self, soup):
        self.soup = soup

    def get_imgs_banner_principal_falabella(self, class_type='CarouselItemstyle', promo_type='ofertas_principales'):
        """
        Extracts the main or secondary promotion images from the HTML.
        """
        assert promo_type in ['ofertas_principales', 'ofertas_secundarias'], 'Invalid promo_type'

        dict_promos = {'ofertas_principales': 'showcase', 'ofertas_secundarias': 'carousel'}
        carousel_items = self.soup.find_all(class_=lambda c: c and class_type in c)

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

    def get_imgs_banner_falabella_size(self, class_type='BannerPowerCardstyle', cols=3):
        """
        Extracts promotional banner images from the HTML based on size.
        """
        try:
            dict_cols = {3: 'three-columns', 6: 'six-columns', 12: 'twelve-columns'}
            dict_size = {3: 'grid', 6: 'banner_doble', 12: 'banner_largo'}

            banner_items = self.soup.find_all(
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
                        promo_type = dict_size[cols]
                        img_url = item.picture.find('source').get('srcset')
                        name = str(item.picture.find('img').get('alt')).lower()
                        data = save_promo(name, promo_type, pos, img_url)
                        all_data.append(data)
                        pos += 1

            return pd.DataFrame(all_data)

        except Exception as e:
            print(f'Error: {e}')