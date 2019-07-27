import requests
from bs4 import BeautifulSoup
import zipfile
import os
import pandas as pd


base_url = 'https://www.histdata.com/download-free-forex-historical-data\
/?/metatrader/1-minute-bar-quotes'

start_url = 'https://www.histdata.com'

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/72.0.3626.121 Safari/537.36',
    # 'Content-Type': 'application/x-www-form-urlencoded',
    'Upgrade-Insecure-Requests': '1',
    'Host': 'www.histdata.com',
    'Origin': 'https://www.histdata.com',
}

session.headers.update(headers)


init = session.get(start_url, headers=headers)
init.raise_for_status()


def get_and_post_data(url):
    print("fetching from",url)
    path = session.get(url)
    path.raise_for_status()
    source = BeautifulSoup(path.text, 'html5lib')
    form = source.find(id='file_down', attrs={'name': 'file_down'})
    input_list = form.find_all('input')
    data = {x['name']: x['value'] for x in input_list}

    session.headers.update({
        'Referer': path.url,
        'Content-Type': 'application/x-www-form-urlencoded',
    })

    resp = session.post(
        "https://www.histdata.com/get.php", data=data,
        allow_redirects=False, stream=True
    )

    try:
        content = resp.headers['Content-Disposition']
        s = content.split()
        if s[1].endswith('.zip'):
            filename = s[1].split("=")[1]
            print("Parsing zip archive....")
            with open(filename, 'wb') as fp:
                for chunk in resp.iter_content():
                    fp.write(chunk)
            print("Parsed zip archive....")

            return filename

    except KeyError:
        raise KeyError(
            "Content-Disposition not found in header after post,\
            verify that url or headers are correct")


def parse_archive(path):

    try:
        # Extract Csv file
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            file = None
            for x in names:
                if x.endswith('.csv'):
                    file = x
                    z.extract(file)
                    break

        print("Unzipped file,reading with csv....")

        # Read Csv file and parse it into dataframe
        frame = pd.read_csv(
            file,
            names=['date','hm','open','high','low','close','volume']
        )
        frame['time'] = frame['date'] + ' ' + frame['hm']
        frame.index = pd.to_datetime(frame['time'])
        frame.index = frame.index.tz_localize('UTC')
        frame.drop(columns=['date','hm','time'],inplace=True)

    except FileNotFoundError as f:
        raise f

    except Exception:
        raise Exception

    finally:
        os.unlink(file)

    return frame[['open','high','low','close']]


def build_url_list(pair,year,m_list):
    post_urls = []
    for month in m_list:
        path = f'{pair}/{year}/{month}'
        post_urls.append(os.path.join(base_url,path))
    return post_urls


def fetch_hist_data(pair, year, months=None, full=False):

    pair = pair.lower()
    frame = pd.DataFrame()
    
    if full:
        if year >= pd.Timestamp.utcnow().year:
            raise NotImplementedError(
                "Year is incorrect, should not be same with \
                current year or greater than current year"
            )
        path = os.path.join(base_url,f'{pair}/{year}')
        filename = get_and_post_data(path)
        frame2 = parse_archive(filename)
        frame = frame.append(frame2)
        print(frame[-20:],len(frame))
        return frame

    fetch_list = build_url_list(pair,year,months)
    for url in fetch_list:
        filename = get_and_post_data(url)
        frame2 = parse_archive(filename)
        frame = frame.append(frame2)
    
    return frame



if __name__ == '__main__':
    fetch_hist_data('EURUSD',2019,full=True)

