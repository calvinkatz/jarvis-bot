import os
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords

def read_text_files(folder_path):
    content = ""
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content += f.read() + "\n"
    return content

folder_path = "./prompts/"
all_text = read_text_files(folder_path)

wc = WordCloud(width=1024,height=1024).generate(all_text)
wc.to_file('wc.png')
