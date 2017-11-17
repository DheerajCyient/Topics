# -*- coding: utf-8 -*-

"""
Visualizing the Output of LDA Models
====================================


"""

__author__ = "DARIAH-DE"
__authors__ = "Steffen Pielstroem, Sina Bock, Severin Simmler"
__email__ = "pielstroem@biozentrum.uni-wuerzburg.de"
__version__ = "0.1"
__date__ = "2017-01-20"


import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import regex
from collections import defaultdict

log = logging.getLogger('visualization')
log.addHandler(logging.NullHandler())
logging.basicConfig(level = logging.ERROR,
                    format = '%(levelname)s %(name)s: %(message)s')

def create_doc_topic(corpus, model, doc_labels):
    # Adapted from code by Stefan Pernes
    """Creates a document-topic-matrix.
    
    Description:
        With this function you can create a doc-topic-maxtrix for gensim 
        output. 

    Args:
        corpus (mmCorpus): Gensim corpus.
        model: Gensim LDA model
        doc_labels (list): List of document labels.

    Returns: 
        Doc_topic-matrix as DataFrame

    ToDo:
    
    Example:
        >>> import gensim
        >>> corpus = [[(1, 0.5)], []]
        >>> gensim.corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
        >>> mm = gensim.corpora.MmCorpus('/tmp/corpus.mm')
        >>> type2id = {0 : "test", 1 : "corpus"}
        >>> doc_labels = ['doc1', 'doc2']
        >>> model = gensim.models.LdaModel(corpus=mm, id2word=type2id, num_topics=1)
        >>> doc_topic = visualization.create_doc_topic(corpus, model, doc_labels)
        >>> len(doc_topic.T) == 2
        >>> True
    """
    no_of_topics = model.num_topics
    no_of_docs = len(doc_labels)
    doc_topic = np.zeros((no_of_topics, no_of_docs))

    for doc, i in zip(corpus, range(no_of_docs)):       # use document bow from corpus
        topic_dist = model.__getitem__(doc)             # to get topic distribution from model
        for topic in topic_dist:                        # topic_dist is a list of tuples
            doc_topic[topic[0]][i] = topic[1]           # save topic probability

    topic_labels = []
    for i in range(no_of_topics):
        topic_terms = [x[0] for x in model.show_topic(i, topn=3)]  # show_topic() returns tuples (word_prob, word)
        topic_labels.append(" ".join(topic_terms))

    doc_topic = pd.DataFrame(doc_topic, index = topic_labels, columns = doc_labels)

    return doc_topic

def doc_topic_heatmap(data_frame):
    # Adapted from code by Stefan Pernes and Allen Riddell
    """Plot documnet-topic distribution in a heat map.
    
    Description:
        Use create_doc_topic() to generate a doc-topic

    Args:
        data_frame (DataFrame): Document-topic-matrix.

    Returns: 
        Plot with Heatmap

    ToDo:
    
    Example:
        >>> import gensim
        >>> corpus = [[(1, 0.5)], []]
        >>> gensim.corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
        >>> mm = gensim.corpora.MmCorpus('/tmp/corpus.mm')
        >>> type2id = {0 : "test", 1 : "corpus"}
        >>> doc_labels = ['doc1', 'doc2']
        >>> model = gensim.models.LdaModel(corpus=mm, id2word=type2id, num_topics=1)
        >>> doc_topic = visualization.create_doc_topic(corpus, model, doc_labels)
        >>> plot = doc_topic_heatmap(doc_topic)
        >>> plot.get_fignumns()
        [1]
    """
    data_frame = data_frame.sort_index()
    doc_labels = list(data_frame.index)
    topic_labels = list(data_frame)
    if len(doc_labels) > 20 or len(topic_labels) > 20: plt.figure(figsize=(20,20))    # if many items, enlarge figure
    plt.pcolor(data_frame, norm=None, cmap='Reds')
    plt.yticks(np.arange(data_frame.shape[0])+1.0, doc_labels)
    plt.xticks(np.arange(data_frame.shape[1])+0.5, topic_labels, rotation='90')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    #plt.savefig(path+"/"+corpusname+"_heatmap.png") #, dpi=80)
    return plt


def plot_doc_topics(doc_topic, document_index):
    """Plot topic disctribution in a document.
    
    Description:
        

    Args:
        Document-topic data frame.
        Index of the document to be shown.

    Returns:
        Plot.

    """
    data = doc_topic[list(doc_topic)[document_index]].copy()
    data = data[data != 0]
    data = data.sort_values()
    values = list(data)
    labels = list(data.index)

    plt.barh(range(len(values)), values, align = 'center', alpha=0.5)
    plt.yticks(range(len(values)), labels)
    plt.title(list(doc_topic)[document_index])
    plt.xlabel('Proportion')
    plt.ylabel('Topic')
    plt.tight_layout()
    return plt


try:
    from wordcloud import WordCloud

    #
    # Work in progress following
    #
    def topicwords_in_df(model):
        pattern = regex.compile(r'\p{L}+\p{P}?\p{L}+')
        topics = []
        index = []
        for n, topic in enumerate(model.show_topics()):
            topics.append(pattern.findall(topic[1]))
            index.append("Topic " + str(n+1))
        df = pd.DataFrame(topics, index=index, columns=["Key " + str(x+1) for x in range(len(topics))])
        return df

    def show_wordle_for_topic(model, topic_nr, words):
        """Plot wordle for a specific topic

        Args:
            model: Gensim LDA model
            topic_nr(int): Choose topic
            words (int): Number of words to show

        Note: Function does use wordcloud package -> https://pypi.python.org/pypi/wordcloud
            pip install wordcloud

        ToDo: Check if this function should be implemented

        """
        plt.figure()
        plt.imshow(WordCloud().fit_words(dict(model.show_topic(topic_nr, words))))
        plt.axis("off")
        plt.title("Topic #" + str(topic_nr + 1))
        return plt


    def get_color_scale(word, font_size, position, orientation, font_path, random_state=None):
        """ Create color scheme for wordle."""
        return "hsl(245, 58%, 25%)" # Default. Uniform dark blue.
        #return "hsl(0, 00%, %d%%)" % random.randint(80, 100) # Greys for black background.
        #return "hsl(221, 65%%, %d%%)" % random.randint(30, 35) # Dark blues for white background

    def get_topicRank(topic, topicRanksFile):
        #print("getting topic rank.")
        with open(topicRanksFile, "r") as infile:
            topicRanks = pd.read_csv(infile, sep=",", index_col=0)
            rank = int(topicRanks.iloc[topic]["Rank"])
            return rank

    def read_mallet_word_weights(word_weights_file):
        """Read Mallet word_weigths file

        Description:
            Reads Mallet word_weigths into pandas DataFrame.

        Args:
            word_weigts_file: Word_weights_file created with Mallet

        Returns: Pandas DataFrame

        Note:

        ToDo:

        """
        word_scores = pd.read_table(word_weights_file, header=None, sep="\t")
        word_scores = word_scores.sort(columns=[0,2], axis=0, ascending=[True, False])
        word_scores_grouped = word_scores.groupby(0)
        return word_scores_grouped

    def _get_wordcloudwords(word_scores_grouped, number_of_top_words, topic_nr):
        """Transform Mallet output for wordcloud generation.

        Description:
            Get words for wordcloud.

        Args:
            word_scores_grouped(DataFrame): Uses read_mallet_word_weights() to get
                grouped word scores.
            topic_nr(int): Topic the wordcloud should be generated for
            number_of_top_words(int): Number of top words that should be considered

        Returns: Words for wordcloud.

        Note:

        ToDo:

        """
        topic_word_scores = word_scores_grouped.get_group(topic_nr)
        top_topic_word_scores = topic_word_scores.iloc[0:number_of_top_words]
        topic_words = top_topic_word_scores.loc[:,1].tolist()
        #word_scores = top_topic_word_scores.loc[:,2].tolist()
        wordcloudwords = ""
        j = 0
        for word in topic_words:
            word = word
            #score = word_scores[j]
            j += 1
            wordcloudwords = wordcloudwords + ((word + " "))
        return wordcloudwords

    def plot_wordcloud_from_mallet(word_weights_file,
                                topic_nr,
                                number_of_top_words,
                                outfolder,
                                dpi):
        """Generate wordclouds from Mallet output.

        Description:
            This function does use the wordcloud module to plot wordclouds.
            Uses read_mallet_word_weigths() and get_wordlewords() to get
            word_scores and words for wordclouds.

        Args:
            word_weigts_file: Word_weights_file created with Mallet
            topic_nr(int): Topic the wordclouds should be generated for
            number_of_top_words(int): Number of top words that should be considered
                for the wordclouds
            outfolder(str): Specify path to safe wordclouds.
            dpi(int): Set resolution for wordclouds.

        Returns: Plot

        Note:

        ToDo:

        """

        word_scores_grouped = read_mallet_word_weights(word_weights_file)
        text = _get_wordcloudwords(word_scores_grouped, number_of_top_words, topic_nr)
        wordcloud = WordCloud(width=600, height=400, background_color="white", margin=4).generate(text)
        default_colors = wordcloud.to_array()
        figure_title = "topic "+ str(topic_nr)
        plt.imshow(default_colors)
        plt.imshow(wordcloud)
        plt.title(figure_title, fontsize=30)
        plt.axis("off")

        ## Saving the image file.
        if not os.path.exists(outfolder):
            os.makedirs(outfolder)

        figure_filename = "wordcloud_tp"+"{:03d}".format(topic_nr) + ".png"
        plt.savefig(outfolder + figure_filename, dpi=dpi)
        return plt

    def plot_wordle_from_lda(model, vocab, topic_nr, words, height, width):
        topic_dist = model.topic_word_[topic_nr]
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-words:-1]
        token_value = {}
        for token, value in zip(topic_words, topic_dist[:-words:-1]):
            token_value.update({token: value})
        return WordCloud(background_color='white', height=height, width=width).fit_words(token_value)

except ImportError as e:
    log.info('WordCloud functions not available, they require the wordcloud module')


def doc_topic_heatmap_interactive(doc_topic, title):
    """Plot interactive doc_topic_heatmap

    Description:
        With this function you can plot an interactive doc_topic matrix.

    Args:
        doc_topic (DataFrame): Doc_topic matrix in a DataFrame
        title (str): Title shown in the plot.

    Returns: bokeh plot

    Note:

    ToDo:

    """
    log.info("Importing functions from bokeh ...")
    try:
        #from ipywidgets import interact
        from bokeh.io import output_notebook
        from bokeh.plotting import figure
        from math import pi
        from bokeh.models import (
            ColumnDataSource,
            HoverTool,
            LinearColorMapper,
            BasicTicker,
            ColorBar
            )

        output_notebook()

        documents = list(doc_topic.columns)
        topics = doc_topic.index

        score = []
        for x in doc_topic.apply(tuple):
            score.extend(x)
            data = {
            'Topic': list(doc_topic.index) * len(doc_topic.columns),
            'Document':  [item for item in list(doc_topic.columns) for i in range(len(doc_topic.index))],
            'Score':   score
            }

        df = doc_topic.from_dict(data)

        colors = ["#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"]
        mapper = LinearColorMapper(palette=colors, low=df.Score.min(), high=df.Score.max())

        source = ColumnDataSource(df)

        TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

        p = figure(title=title,
               x_range=documents, y_range=list(reversed(topics)),
               x_axis_location="above", plot_width=1024, plot_height=768,
               tools=TOOLS, toolbar_location='below', responsive=True)

        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = "9pt"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = pi / 3

        p.rect(x="Document", y="Topic", width=1, height=1,
           source=source,
           fill_color={'field': 'Score', 'transform': mapper},
           line_color=None)


        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         label_standoff=6, border_line_color=None, location=(0, 0))

        p.add_layout(color_bar, 'right')

        p.select_one(HoverTool).tooltips = [
             ('Document', '@Document'),
             ('Topic', '@Topic'),
             ('Score', '@Score')
             ]
        return p

    except:
        log.info("Bokeh could not be imported now using mathplotlib")
        doc_topic_heatmap(doc_topic)

    p.add_layout(color_bar, 'right')

    p.select_one(HoverTool).tooltips = [
         ('Document', '@Document'),
         ('Topic', '@Topic'),
         ('Score', '@Score')
    ]
    return p



def _create_label(topic, outfolder):

    topic_keys=os.path.join(outfolder, 'topic_keys.txt')
    df=pd.read_csv(topic_keys, sep='\t', header=None, encoding='utf-8')
    topicLabel=' '.join(df[2][topic-1].split()[:3])
    return topicLabel

def _create_years_count_dictionary(doc_topic_df, topic, threshold):
    """private function for show_topic_over_time
    
    Description:
        create a dictionary with a amounts of texts of every year using the doc_topics file of mallet
        
    Args:

        doc_topic: doc-topic matrix created by mallet.show_doc_topic_matrix
        labels(list[str]): first three keys in a topic to select
        threshold(float): threshold set to define if a topic in a document is viable
        starttime(int): sets starting point for visualization
        endtime(int): sets ending point for visualization


    Returns: 
        matplotlib plot

    Note: this function is created for a corpus with filenames that looks like:
            1866_ArticleName.txt

    ToDo: make it compatible with gensim output
            Doctest


        outfolder(str): path to the mallet output
        topics(list[int]): list of topics to select
        threshold(float): threshold for the selection of topic probabilities
        
    Returns:
        dictionary{year:count}
        
    Note: this function is created for a corpus with filenames that looks like:
            1866_ArticleName.txt

    """
    doc_topic_matrix_T = doc_topic_df.T
    topics_over_threshold = doc_topic_matrix_T.iloc[1][doc_topic_matrix_T.iloc[topic + 1] > 0.1].values
    d = defaultdict(int)
    for filename in topics_over_threshold:
        
        year = os.path.basename(filename).split('_')
        d[year[0]]+=1    
    return d

def show_topic_over_time(outfolder, topicslist=[5,6,7], starttime = 1841, endtime=1920,threshold=0.1):
    doc_topics=os.path.join(outfolder, 'doc_topics.txt')
    doc_topic_matrix=pd.read_csv(doc_topics, sep='\t', encoding='utf-8')
    
    ##create label_list
    label_list =[]
      
    years=list(range(starttime,endtime))
    
    for topic in topicslist:
        ##create list for years_count_dictionary
        visualize_list=[]
        label = _create_label(topic, outfolder)
        topic_over_threshold_per_year= _create_years_count_dictionary(doc_topic_matrix, topic, threshold)

    
        for year in years:
            visualize_list.append(topic_over_threshold_per_year[str(year)])
            
        plt.plot(years, visualize_list, label=label)
        
    plt.xlabel('Year')
    plt.ylabel('count topics over threshold')
    plt.legend()
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    #plt.show()
 









