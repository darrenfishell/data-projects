import requests
import pandas as pd
import os
from scrapy import Selector

def top_level_scraper():

    url = 'https://blackownedmaine.com/'

    r = requests.post(url)

    sel = Selector(text=r.text)

    local_listings = sel.xpath('//div[@class="wp-block-coblocks-accordion-item"]').getall()

    dfs = []

    for listing in local_listings:

        listing_sel = Selector(text=listing)

        link = listing_sel.xpath('//div[@class="wp-block-coblocks-accordion-item__content"]/p//a[contains(@href,"blackownedmaine")]//@href').extract()
        entity_name = listing_sel.xpath('//div[@class="wp-block-coblocks-accordion-item__content"]/p//a[contains(@href,"blackownedmaine")]//text()').extract()
        locale = listing_sel.xpath('//summary[@class="wp-block-coblocks-accordion-item__title"]//text()').extract()

        if locale == ['Lewiston']:
            print(link)
            print(len(link))
            print(entity_name)
            print(len(entity_name))

        df = pd.DataFrame({'link': link
                           , 'entity': entity_name
                           , 'city_town': [locale for entity in entity_name]})

        dfs.append(df)

    return dfs

dfs = top_level_scraper()

df = pd.concat(dfs, ignore_index=True)

df.to_csv('black-owned-maine-listings.csv')