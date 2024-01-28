from django.db import models
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
import os
import zipfile
import pandas as pd
from pathlib import Path
import tiktoken
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Create your models here.
class ChatFiles(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    file = models.FileField(default='test.zip', upload_to='user_files')

    def __str__(self) -> str:
        return f'{self.file} File'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        zip_path = self.file.path
        out_path = str(self.file.path).split(".")[0] + "/documents/"
        # print(out_path)
        if not os.path.exists(out_path + "embeddings.csv"):
            unzip_files(zip_path, out_path)
            create_scraped(out_path)
            generate_embeddings(out_path)

def unzip_files(zip_path, output_dir):
    #Unzip Files and convert to text
    print("+++++++++++++++++HRER++++++++++++", output_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        for filename in zip_file.namelist():
            print("+++++++++++++++++HRER++++++++++++", filename)
            if filename.endswith('.html') and not filename.__contains__('GUID'):
                print("+++++++++++++++++HRER++++++++++++", filename)
                # Extract the HTML file
                html_content = zip_file.read(filename).decode('utf-8')
                # print(html_content)
                # Convert HTML to TXT and remove HTML tags
                text = html_to_txt(html_content)
                print(text)
                print(filename)
                if text == '':
                    continue
                # Construct the output file path
                txt_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.txt')

                # Create the output directory if it doesn't exist
                os.makedirs(output_dir + os.path.dirname(filename), exist_ok=True)
                # print(os.path.dirname(filename))

                # Save the text to the output file
                with open(txt_file, 'w') as file:
                    file.write(filename + '\n')
                    file.write(text)


def html_to_txt(html_content):
    # Parse the HTML content using BeautifulSoup
    text = BeautifulSoup(html_content, 'html.parser').get_text()

    # Extract the text from the parsed HTML
    # text = soup.find_all(attrs={"class": ["topictitle1", "conbody"]})
    
    # Remove extra whitespaces and newlines
    # text = ' '.join([i.get_text() for i in text])
    
    return text

def remove_newlines(serie):
    serie = serie.str.replace('\n', ' ')
    serie = serie.str.replace('\\n', ' ')
    serie = serie.str.replace('  ', ' ')
    serie = serie.str.replace('  ', ' ')
    return serie

def pdf_to_text():
    pass

def word_to_text():
    pass

def create_scraped(file_path):
    # Create a list to store the text files
    texts=[]
    file_dir = Path(file_path)
    files = list(file_dir.rglob("*.txt"))
    print(len(files))
    # print(files)

    # Get all the text files in the text directory
    for file in files:
        # print(file.name)
        # Open the file and read the text
        with open(file, "r", encoding="UTF-8") as f:
            text = f.read()
            texts.append((file.name.replace('-',' ').replace('_', ' ').replace('#update',''), text))

    # # # Create a dataframe from the list of texts
    df = pd.DataFrame(texts, columns = ['fname', 'text'])

    # # Set the text column to be the raw text with the newlines removed
    df['text'] = df.fname + ". " + remove_newlines(df.text)
    df.to_csv(str(file_dir) + '/scraped.csv', index=False)

def generate_embeddings(file_path, max_tokens = 500):
    # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
    tokenizer = tiktoken.get_encoding("cl100k_base")

    df = pd.read_csv(str(file_path) + '/scraped.csv')

    df.columns = ['title', 'text']

    # # Tokenize the text and save the number of tokens to a new column
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    shortened = []

    # Loop through the dataframe
    for row in df.iterrows():

        # If the text is None, go to the next row
        if row[1]['text'] is None:
            continue

        # If the number of tokens is greater than the max number of tokens, split the text into chunks
        if row[1]['n_tokens'] > max_tokens:
            shortened += split_into_many(row[1]['text'], tokenizer)
        
        # Otherwise, add the text to the list of shortened texts
        else:
            shortened.append( row[1]['text'] )

    df = pd.DataFrame(shortened, columns = ['text'])
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    df['embeddings'] = df.text.apply(lambda x: client.embeddings.create(input=x, model='text-embedding-ada-002').data[0].embedding)
    print(df)
    df.to_csv(str(file_path) + '/embeddings.csv', index=False)

# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, tokenizer, max_tokens = 500):

    # Split the text into sentences
    sentences = text.split('. ')

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]
    
    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater 
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of 
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks