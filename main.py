"""
    author: Daniel Nichols
    date: June, 2020
"""
import sys
import argparse
import json
from paper import get_paper_info


def get_links(db, file_name='links.txt'):
    """ Get a list of links from the file
        returns: list of strings
    """
    current_links = [x['url'] for x in db]

    with open(file_name, 'r') as f:
        file_contents = f.read()
        links = file_contents.split('\n')
        return list(set(links) - set(current_links))
    return []


def write_paper_info(papers, output_file_name='papers_db.json'):
    """ Converts `papers` to JSON and outputs the string to `output_file_name`
    """
    output_str = json.dumps(papers)
    with open(output_file_name, 'w') as f:
        f.write(output_str)


def read_paper_info(db_file_name):
    """ Reads the contents of db_file_name into an array
        of dicts.
    """
    try:
        with open(db_file_name, 'r') as f:
            return json.loads(f.read())
    except IOError:
        return []


def show_wordcloud(papers_info):
    """ Takes an array of dicts, each containing an 'abstract' attribute
        This will split the words of the abstract and display
        a wordcloud in a new graphics window
    """
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    import string

    table = str.maketrans(dict.fromkeys(string.punctuation))
    stopwords = set(STOPWORDS)

    abstract_str = ''
    for paper in papers_info:
        abstract_words = [s.lower() for s in paper['abstract'].split()]
        abstract_words = [s.translate(table)
                          for s in abstract_words]

        abstract_str += ' '.join(abstract_words) + ' '

    wordcloud = WordCloud(width=800, height=800, background_color='white',
                          stopwords=stopwords, min_font_size=10).generate(abstract_str)

    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.tight_layout(pad=0)

    plt.show()


def main(argc, argv):
    # handle any arguments here
    parser = argparse.ArgumentParser(description='Get Paper Abstracts')
    parser.add_argument('-f', '--file', type=str,
                        default='links.txt', help='Links input file')
    parser.add_argument('--word-cloud', action='store_true',
                        help='Generate Wordcloud')
    parser.add_argument('--database', type=str,
                        help='output database; cache details', default='papers_db.json')
    args = parser.parse_args()

    # read the current db
    db = read_paper_info(args.database)

    # retrieve the links from the input file and remove duplicates
    links = get_links(db, file_name=args.file)

    # scrape paper info
    papers = get_paper_info(links, db, verbose=True)

    # write to output
    write_paper_info(papers, output_file_name=args.database)

    # if asked for, then show word cloud of abstracts
    if args.word_cloud:
        show_wordcloud(papers)


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
