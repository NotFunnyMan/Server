from bs4 import BeautifulStoneSoup

xml_file = open('rss.xml', encoding='utf-8')
soup = BeautifulStoneSoup(xml_file)
print(soup)
print("\n\n")


items_list = soup.findAll('item')
print(items_list)

for item in items_list:
    test = item.find('title').text
    print(test)
    break
