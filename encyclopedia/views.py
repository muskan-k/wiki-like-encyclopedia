from django.shortcuts import render
import random
from . import util
from django.http import HttpResponse, HttpResponseRedirect
import markdown2
from django import forms
from django.urls import reverse
from django.contrib import messages



def index(request):
    entries= util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries
    })

def entry(request,title):
    try:
        result= util.get_entry(title)
        html =markdown2.markdown(result)
        return render(request, "encyclopedia/entry.html",{
            "content": html, "entry": title
        })
    except:
        return render(request, "encyclopedia/error.html")

class EntryInput(forms.Form):
    name= forms.CharField(label='Title of entry:', widget=forms.TextInput(attrs={'class':"col"}))
    entry=forms.CharField(label='Enter content in markdown syntax', widget=forms.Textarea(attrs={'class':"form-control"}))

def randomentry(request):
    entries= util.list_entries()
    choice= random.choice(entries)
    return entry(request,choice)

def edit(request,title):
    content=util.get_entry(title)
    if request.method=='POST':
        form= EntryInput(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            data= form.cleaned_data["entry"]
            util.save_entry(name ,data)
            return HttpResponseRedirect(reverse("entry", args=[name]))
        else:
            return render(request, "encyclopedia/edit.html", {
            "form":form, "title": "Edit"
            })
    else:
        form = EntryInput(initial={'name':title,'entry':content})

        return render(request, "encyclopedia/edit.html", {
        "form":form, "title": "Edit"
        })

def check(word, item):
    lower_item= item.lower()
    lower_word= word.lower()
    if lower_word==lower_item:
        return 1
    if lower_word in lower_item:
        return 0


def new(request):
    entries= util.list_entries()
    if request.method=='POST':
        form=EntryInput(request.POST)
        if form.is_valid():
            name=form.cleaned_data["name"]
            for e in entries:
                if check(name,e)==1:
                    messages.add_message(request, messages.ERROR, 'Title already exists. Try another.')
                    return render(request,"encyclopedia/edit.html",{
                    "form":form, "title": "New"
                    })
            else:
                content=form.cleaned_data["entry"]
                util.save_entry(name,content)
                entries.append(name)
                return HttpResponseRedirect(reverse("entry", args=[name]))
    else:
        form= EntryInput()
        return render(request, "encyclopedia/edit.html", {
        "form":form, "title": "New"
        })



def search(request):
        entries= util.list_entries()
        key= request.GET.get("q")
        new=[]
        for e in entries:
            value=check(key,e)
            if value==1:
                return HttpResponseRedirect(reverse("entry", args=[key]))

            if value==0:
                new.append(e)

        return render(request, "encyclopedia/search.html", {"result":new, "key":key})
