import requests
import json
from bs4 import BeautifulSoup


def get_paper_type(link):
    """ Get which vendor this paper belongs to
        return: string that is one of ['IEEE', 'ACM_DL', 'SPRINGER', 'SCIENCE_DIRECT']
    """
    if 'ieeexplore.ieee.org' in link:
        return 'IEEE'
    elif 'dl.acm.org' in link:
        return 'ACM_DL'
    elif 'link.springer.com' in link:
        return 'SPRINGER'
    elif 'sciencedirect.com' in link:
        return 'SCIENCE_DIRECT'
    else:
        return None


def get_IEEE_info(link):
    """ IEEE does not label its abstract html tags. BUT it does have all the paper metadata set
        in the `global.document.metadata` variable in a script tag. Rather than use a JS interpreter
        just parse the JSON in Python.
    """
    page_content = requests.get(link).content
    page_content_str = page_content.decode('utf-8')

    location = page_content_str.find('global.document.metadata=')
    end_location = page_content_str.find('};', location)

    identifier_len = len('global.document.metadata=')
    json_metadata_str = page_content_str[(
        location + identifier_len):end_location] + '}'

    json_metadata = json.loads(json_metadata_str)
    return {'abstract': json_metadata['abstract'], 'title': json_metadata['title'], 'url': link}


def get_ACM_DL_info(link):
    """ Gets ACM DL abstract and title info. Uses BeautifulSoup HTML parser
        to find correct elements within page.
    """
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    # get abstract
    abstract_parent_div = soup.find(
        'div', class_='abstractSection abstractInFull')
    abstract_paragraphs = abstract_parent_div.find_all('p')
    abstract_str = '\n'.join([e.text for e in abstract_paragraphs])

    # get the title
    title_element = soup.find('h1', class_='citation__title')
    title = title_element.text

    return {'abstract': abstract_str, 'title': title, 'url': link}


def get_SPRINGER_info(link):
    """ Gets Springer abstract and title info. Uses BeautifulSoup HTML parser
        to find correct elements within page.
    """
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    # get abstract text
    abstract_parent_section = soup.find('section', class_='Abstract')
    abstract_paragraphs = abstract_parent_section.find_all('p')
    abstract_str = '\n'.join([e.text for e in abstract_paragraphs])

    # get paper title
    title_element = soup.find('h1', class_='ChapterTitle')
    title = title_element.text

    return {'abstract': abstract_str, 'title': title, 'url': link}


def get_SCIENCE_DIRECT_info(link):
    """ Gets Science Direct abstract and title info. Uses BeautifulSoup HTML parser
        to find correct elements within page.
        CURRENTLY NOT WORKING: ELSEVIER has a public API; see if that works
    """
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    # get abstract text
    abstract_parent_div = soup.find('div', class_='abss0001')

    if abstract_parent_div is None:
        return None

    abstract_paragraphs = abstract_parent_div.find_all('p')
    abstract_str = '\n'.join([e.text for e in abstract_paragraphs])

    # get paper title
    title_element = soup.find('span', class_='title-text')
    title = title_element.text

    return {'abstract': abstract_str, 'title': title, 'url': link}


def get_paper_info(links, db, verbose=False):
    """
        Get the available info on a paper from provided link
        return: an array of dicts with the url, title, abstract, and ERROR
    """

    info_array = db
    action_map = {'IEEE': get_IEEE_info,
                  'ACM_DL': get_ACM_DL_info, 'SPRINGER': get_SPRINGER_info,
                  'SCIENCE_DIRECT': get_SCIENCE_DIRECT_info}

    for link in links:
        paper_type = get_paper_type(link)

        if paper_type is None:
            if verbose:
                print('Unknown paper paper source...\tSkipping')
            continue

        if verbose:
            print('Retrieving (' + paper_type + ') ' +
                  str(link) + '...\t', end='', flush=True)

        info_func = action_map[paper_type]
        info = info_func(link)

        if verbose:
            if info is None:
                print('ERROR')
                continue
            else:
                print('Done')

        info_array.append(info)

    return info_array
