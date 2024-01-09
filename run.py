
from bs4 import BeautifulSoup
import requests
import ujson as json 
import concurrent.futures
import re
def get_max_page(url:str):
    list_link = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content,'html.parser')
        end_pages = soup.find_all(lambda tag: tag.name == "li" and tag.get("class") == ['pageNav-page'])
        max_page = 1
        for page in end_pages:
            page_number = int(page.find('a').get_text())
            if page_number > 50:
                max_page = 50
                break
            elif page_number > max_page:
                max_page = page_number
        return max_page
    else:
        print("Error")
def remove_word_and_phrase(text, phrase):
    words = text.split()
    try:
        index_phrase = words.index(phrase)
        if index_phrase > 0:
            del words[index_phrase - 1]  # Xoá từ trước phrase
            del words[index_phrase]      # Xoá cả phrase
    except ValueError:
        pass  # Nếu không tìm thấy cụm từ, không làm gì cả
    new_text = ' '.join(words)
    return new_text
def is_sublist(sub_list, main_list):
    len_sub = len(sub_list)
    for i in range(len(main_list) - len_sub + 1):
        if main_list[i:i + len_sub] == sub_list:
            return True
    return False
import re
def is_sublist(sub_list, main_list):
    len_sub = len(sub_list)
    for i in range(len(main_list) - len_sub + 1):
        if main_list[i:i + len_sub] == sub_list:
            return True
    return False

def process_data(data):
    list_author = [] 
    for i in range(len(data)):
        list_author.append(data[i]['author'])

    for i in range(len(data)):
        for k in list_author:
            data[i]['text_content'] = data[i]['text_content'].replace(k, '')
            data[i]['text_content'] = data[i]['text_content'].strip()
    return data
def find_matching_comment(data_list):
    for i in range(len(data_list)):
        if len(data_list[i]['text_quote']) != 0:
            id_quoto_matches = []  # Danh sách để lưu trữ các id_comment khớp
            for k in range(len(data_list[i]['text_quote'])):
                quote_to_match = data_list[i]['text_quote'][k]
                for j in range(i - 1, -1, -1):
                   if  token_set_ratio(quote_to_match,data_list[j]['text_content']) > 80:
                        id_quoto_matches.append(data_list[j]['id_comment'])
            data_list[i]['id_quoto'] = id_quoto_matches
        else:
            data_list[i]['id_quoto'] = []
    return data_list


def split_text(big_string:str,small_string:str):
    index = big_string.find(small_string)  # Tìm vị trí chuỗi nhỏ trong chuỗi lớn
    if index != -1:
        # Nếu chuỗi nhỏ được tìm thấy
        text_quote = big_string[:index + len(small_string)]  # Phần đầu từ đầu chuỗi đến sau chuỗi nhỏ
        text_comment = big_string[index + len(small_string):]  # Phần còn lại từ sau chuỗi nhỏ đến cuối chuỗi lớn

        return text_quote, text_comment
    else:
        return None  # Trả về None nếu không tìm thấy chuỗi nhỏ trong chuỗi lớn
def clean_text(data_list):
    for i in range(len(data_list)):
        if data_list[i]['text_quote'] is not None:
            for j in range(len(data_list[i]['text_quote'])):
                data_list[i]['text_quote'][j] = re.sub(r'(\n)+', '', data_list[i]['text_quote'][j])
        data_list[i]['text_content'] = re.sub(r'(\n)+', '', data_list[i]['text_content'])
    return data_list
from unicodedata import normalize

def normalize_text(text):

    for type in ["NFD", "NFKD", "NFKC", "NFC"]:
        try:
            text = normalize(type, text)
        except:
            continue
    return text
import re
from thefuzz.fuzz import token_set_ratio
def replace_text(text:str):
    remove_text = ['via theNEXTvoz for iPhone','Click to expand...','said:']
    for i in remove_text:
        text = text.replace(i,'')
    return text
def get_data_vozer(url: str, page_number: int):
    data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    count = 0
    for page in range(1, page_number +1):
        formatted_url = f"{url}page-{page}"
        response = requests.get(formatted_url, headers=headers)
        print(formatted_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            data_authors = soup.find_all('article', class_=['message message--post', 'js-post', 'js-inlineModContainer'])
            content_post = {"content_post":soup.find('h1',class_='p-title-value').get_text()}
            for tag in data_authors:
                author = tag.get('data-author')
                time = tag.find('div', class_=['message-userContent', 'lbContainer', 'js-lbContainer'])
                time_desc = time.get('data-lb-caption-desc') if time else None
                text = tag.find(class_=['bbWrapper'])
                text_quotes = text.find_all('div',class_=["bbCodeBlock-expandContent","js-expandContent"])
                list_about_quotes = []
                if text_quotes is not None:
                   for i in text_quotes:
                      a = i.get_text()
                      a = replace_text(a)
                      #a = re.sub(r'\.(?!\s)', '. ', a)
                      list_about_quotes.append(a)
                
                text_content = replace_text(text.get_text()) if text else None
                text_content = remove_word_and_phrase(text_content, "said:")
                #text_quote = None 
                #quote = text.find_all('div',class_=["bbCodeBlock-expandContent","js-expandContent"])
                #for i in quote:
                   #text_quote = i.get_text() if quote else None
                #if text_quote is not None:
                   #text_quote = replace_text(text_quote)
                                                       #via theNEXTvoz for iPhone
                interaction = tag.find('a', class_=['reactionsBar-link'])
                interaction_link = "https://voz.vn" + interaction.get('href') if interaction else None
                interaction_text = interaction.get_text() if interaction else None
                data.append({
                    'author': author,
                    'time_desc': time_desc,
                    'text_quote' : list_about_quotes,
                    'text_content': text_content,
                    'interaction_link': interaction_link,
                    'interaction_text': interaction_text,
                    'Page_number' : page,
                    'id_comment' : count
                })
                count = count +1
        else:
            print(f"Error: Failed to fetch URL. Status code: {response.status_code}")
    data = clean_text(data)
    
    data = find_matching_comment(data)
    processed_data = process_data(data)
    return [content_post,processed_data]
def extract_text_from_url(url):
    # Tải nội dung của trang web
    list_link = []
    link_url_post = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content,'html.parser')
        #print(soup)
        voz_list_url = soup.find_all('div',class_=["structItem", "structItem--thread", "is-unread", "js-inlineModContainer"])
        for links in voz_list_url:
            voz_time_and_author = soup.find_all('ul', class_=['structItem-parts'])
        for block in voz_time_and_author:
           replies  = block.find_all('a')
           for reply in replies:
              list_link.append(reply.get_text())
        #for author in voz_list_url:
            #list_link.append(author.attrs.get('data-author'))
        voz_list_replie_view = soup.find_all('div',class_=['structItem-cell','structItem-cell--meta'])
        links = soup.find_all('div', class_='structItem-title')
        for div in links:      
         a_tag = div.find('a')
         if a_tag:  
          href = a_tag.get('href')
          list_link.append("https://voz.vn//"+ href)
          link_url_post.append("https://voz.vn//"+ href)
        for div in voz_list_replie_view:
           replies  = div.find_all('dl')
           for reply in replies:
              dt_text = reply.find('dt').get_text(strip=True)
              dd_text = reply.find('dd').get_text(strip=True)
              list_link.append(f"{dt_text}: {dd_text}")                       
        return link_url_post
    else:
        print("Không thể truy cập trang.")
def process_page(i):
    url = f'https://voz.vn/f/chuyen-tro-linh-tinh.17/page-{i}'
    extracted_text = extract_text_from_url(url)
    #print(extracted_text)
    max_page_list = []
    links = extracted_text
    for link in extracted_text:
        page_number = get_max_page(link)
        #print(page_number)
        data = get_data_vozer(link, page_number)
        #print(data)
        name = data[0]['content_post']
        file_name = f"{name}.json"
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False)
        except FileNotFoundError:
            print("Thư mục không tồn tại hoặc đường dẫn không chính xác.")
if __name__ == "__main__":
    num_threads =  20
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(process_page, range(4000,6000))
