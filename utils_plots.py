import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from unidecode import unidecode
import matplotlib
matplotlib.use('Agg')
import plotly.express as px


def plot_col_against_date(df, col, plot_type='bar', top=5, height=400, width=600):
    assert plot_type in ['bar', 'line'], 'wrong type of chart, suported: bar, line'
    dates = df['date_checked'].unique().tolist()
    data = []
    for date in dates:
        col_list = df[col][df.date_checked == date].tolist()
        col_list_flatten = [val for sublist in col_list for val in sublist]
        col_list_flatten_format = list(map(lambda x: unidecode(x.lower()), col_list_flatten))
        count = Counter(col_list_flatten_format).most_common()[:top]
        df_date = pd.DataFrame(count, columns=[f'{col}', 'total'])
        df_date['date_checked'] = date
        data.append(df_date)

    df_reshaped = pd.concat(data)
    df_reshaped = df_reshaped.sort_values(by=['date_checked', 'total', f'{col}'], ascending=[True, False, True])
    aux = ' '.join(col.split('_'))
    if plot_type == 'bar':
        fig = px.bar(df_reshaped, x='date_checked', y='total', color=f'{col}', height=height, width=width, title=f'Top {top}: {aux}/día')

    if plot_type == 'line':
        fig = px.line(df_reshaped, x="date_checked", y="total", color=f'{col}', symbol=f'{col}', markers=True,
                      height=height, width=width, title=f'Top {top}: {aux}/día')

    return fig


def plot_wordcloud(df, col, color='black', max_words=20, height=200):
    assert col in ['categorias_en_promo', 'marcas_en_promo', 'publico_objetivo'], 'wrong key'
    keywords = df[col].tolist()
    keywords_flatten = [val for sublist in keywords for val in sublist]
    keywords_flatten_format = list(map(lambda x: unidecode(x.lower()), keywords_flatten))
    keywords_promo_all_tokens = ' '.join(keywords_flatten_format)

    wordcloud = WordCloud(background_color=color, max_words=max_words, height=height).generate(keywords_promo_all_tokens)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    return plt


def plot_against_offer_type(df, col, top=10, height=200, width=300):
    assert col in ['categorias_en_promo', 'marcas_en_promo', 'publico_objetivo'], 'wrong key'
    keywords = df[col].tolist()
    keywords_flatten = [val for sublist in keywords for val in sublist]
    keywords_flatten_format = list(map(lambda x: unidecode(x.lower()), keywords_flatten))
    col_counter = Counter(keywords_flatten_format).most_common()[:top]
    df_counter = pd.DataFrame(col_counter, columns=[f'{col}', 'total'])
    df_counter = df_counter.sort_values(by='total', ascending=True)

    aux = ' '.join(col.split('_'))
    fig = px.bar(df_counter, x="total", y=f"{col}", height=height, width=width, title=f'Top {top}')
    return fig

        
