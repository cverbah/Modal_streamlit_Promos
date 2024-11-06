import pandas as pd
from unidecode import unidecode
from scrapers.falabella import save_promo

## NOT WORKING
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