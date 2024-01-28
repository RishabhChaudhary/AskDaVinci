# from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.forms import UserUpdate
from .forms import ChatUpdate
from .models import Chats
from users.models import client
import numpy as np
import pandas as pd

# Create your views here.
@login_required
def home_page_view(request):
    if request.method == "POST":
        print("+++++++++++++++++++++++I WAS HERE+++++++++++++++++++++++++++=")
        file_form = UserUpdate(request.POST, request.FILES, instance=request.user.chatfiles)
        
        if file_form.is_valid():
            file_form.save()
            file_name = file_form.cleaned_data.get("file")
            messages.success(request, f'File {file_name} Uploaded. You can now chat.')
            return redirect("chatbot")
    else:
        file_form = UserUpdate(instance=request.user.chatfiles)

    context = {
        'file_form': file_form
    }

    return render(request, "pages/home.html", context)

@login_required
def bot_page_view(request):
    if request.method == "POST":
        chat_ques = request.POST.get("question")
        out_path = str(request.user.chatfiles.file.path).split(".")[0] + "/documents/"
        chat_ans = answer_question(out_path=out_path, question=chat_ques)
        chat_form = ChatUpdate({"question": chat_ques, "answer": chat_ans}, instance=Chats.objects.create(user=request.user))
        chat_form.user = request.user

        
        if chat_form.is_valid():
            chat_form.save()
    
    context = {
        'chats': Chats.objects.filter(user=request.user).all()
    }

    return render(request, "pages/chat_bot.html", context)

def cosine_similarity(vector1, embedding):
    # Normalize the vectors
    similarities = []
    for vector2 in embedding:
        norm_vector1 = np.linalg.norm(vector1)
        norm_vector2 = np.linalg.norm(vector2)

        # Avoid division by zero
        if norm_vector1 == 0 or norm_vector2 == 0:
            return 0

        # Calculate the dot product
        dot_product = np.dot(vector1, vector2)

        # Calculate the cosine similarity
        similarity = dot_product / (norm_vector1 * norm_vector2)
        similarities.append(similarity)
    return similarity

def create_context(
    question, df, max_len=1800, size="ada"
):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = client.embeddings.create(input=question, model='text-embedding-ada-002').data[0].embedding
    
    # Get the distances from the embeddings
    df['distances'] = cosine_similarity(q_embeddings, df['embeddings'].values)


    returns = []
    cur_len = 0
    # print("===============", df["distances"])
    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4
        
        # If the context is too long, break
        if cur_len > max_len:
            break
        
        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
    out_path,
    model="gpt-3.5-turbo-instruct",
    question="Am I allowed to publish model outputs to Twitter, without a human review?",
    max_len=1900,
    size="ada",
    debug=True,
    max_tokens=600,
    stop_sequence=None
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    df=pd.read_csv(str(out_path) + 'embeddings.csv')
    print("=========================", df.columns)
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        # Create a completions using the question and context
        response = client.completions.create(
            prompt=f"Answer the question in two parts one is text part and one is example code part based on the context below, always prefix the example part with example:, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response.choices[0].text
    except Exception as e:
        print(e)
        return ""