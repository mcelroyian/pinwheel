import requests
import sys
import json
import os
from bs4 import BeautifulSoup
from soupsieve.css_parser import PAT_PSEUDO_CLASS_CUSTOM

BASE_URL = 'https://apps.irs.gov'

def search_url(term):
    return BASE_URL + f"/app/picklist/list/priorFormPublication.html?indexOfFirstRow=0&sortColumn=sortOrder&value={term}&criteria=formNumber&resultsPerPage=200&isDescending=false"

def get_all_rows(url):

    rows = None

    def get_rows_from_url(url):
        nonlocal rows

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        selection = soup.select(".picklist-dataTable > tr")
        #Remove table header
        selection = selection[1:]
        rows = selection if rows is None else rows + selection

        #find next page if exists
        next_page = soup.find('a', string="Next »")
        if next_page:
            get_rows_from_url(BASE_URL + next_page['href'])

    get_rows_from_url(url)

    return rows


def get_form_data(rows, search_term):

    form_data = None

    for row in rows:
        form_number = row.find('td').find('a').get_text().strip()
        if form_number.lower() != search_term.lower():
            continue
        form_title = row.find(class_='MiddleCellSpacer').get_text().strip()
        form_year = int(row.find(class_='EndCellSpacer').get_text().strip())

        form_data = {'form_number': form_number,'form_title': form_title, 'min_year': form_year, 'max_year': form_year} if form_data is None else form_data
        form_data['min_year'] = min(form_year, form_data['min_year'])
        form_data['max_year'] = max(form_year, form_data['max_year'])

    return form_data

def output_form_json(terms):
    results = []
    for term in terms:
        rows = get_all_rows(search_url(term))
        if len(rows) == 0:
            print("No Results found")
            return json.dumps([])
        results.append(get_form_data(rows, term))
    return json.dumps(results)


#Downloading Tax Forms
def get_urls(form_name, start_year, end_year):
    years_to_download = {year:None for year in range(int(start_year), int(end_year)+1)}
    rows = get_all_rows(search_url(form_name))
    for row in rows:
        form_number = row.find('td').find('a').get_text().strip()
        if form_number.lower() != form_name.lower():
            continue
        year = int(row.find(class_='EndCellSpacer').get_text().strip())
        file_URL = row.find(class_='LeftCellSpacer').find('a')['href']
        if year in years_to_download:
            years_to_download[year] = file_URL
    return years_to_download

def download_forms(urls, form_name):
    if not os.path.exists(form_name):
        os.makedirs(form_name)

    for year in urls.keys():
        if urls[year] is None:
            continue
        print(year)
        temp = requests.get(urls[year])
        with open(os.path.join(form_name, form_name+" - "+str(year)+".pdf"), 'wb') as file:
            file.write(temp.content)
    return "OK"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please choose a command [save , data]")
        exit()
    if sys.argv[1] == 'data':
        if len(sys.argv) < 3:
            print("Incorrect arguements, please check usage of data in the README.")
            exit()
        print(output_form_json(sys.argv[2:]))
    if sys.argv[1] == 'save':
        if len(sys.argv) < 5:
            print("Incorrect arguements, please check usage of save in the README.")
            exit()
        to_download = get_urls(sys.argv[2], sys.argv[3], sys.argv[4])
        download_forms(to_download, sys.argv[2])
    else:
        exit()