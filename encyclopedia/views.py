from django.shortcuts import render
from django import forms
from . import util
import markdown
from bs4 import BeautifulSoup
import re
from django.utils.safestring import mark_safe

# My personal form is called 'NewSearchForm'. This is the child form of a
# general Django which exists in the django forms module
class NewSearchForm(forms.Form):
    # Widget code attributed to
    # http://www.learningaboutelectronics.com/Articles/How-to-add-a-
    # placeholder-to-a-Django-form-field.php#:~:text=In%20the%20forms.
    # py%20file,attribute%20of%20the%20form%20field.
    search_entry = forms.CharField(label="", widget=forms.TextInput
                           (attrs={'placeholder':'Search Encyclopedia'}))

# Widgets allow for form to include HTML tag textarea and
class NewEntry(forms.Form):
    title = forms.CharField(label="Enter title of new page", label_suffix="",
                    widget=forms.TextInput
                    (attrs={'placeholder':'Title of new page', 'size': 40}))
    text = forms.CharField(label="Use Markdown to enter text", widget=forms.Textarea)

class EditEntry(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)

def index(request):
    if request.method == "POST":
        # Populates a new NewSearchForm with data from form in HTML
        form = NewSearchForm(request.POST)
        # Must check validity of form
        if form.is_valid():
            # .cleaned_data[] method returns an element from the form class
            search_entry = form.cleaned_data["search_entry"].lower()
            list_of_entries = util.list_entries()
            for i in range(len(list_of_entries)):
                list_of_entries[i] = list_of_entries[i].lower()
            if search_entry in list_of_entries:
                # .markdown converts markdown in the selected entry into HTML
                search_entry = markdown.markdown(util.get_entry(search_entry))
                # BeautifulSoup module finds the h1 or title in the markdown-to-HTML text
                soup = BeautifulSoup(search_entry, 'html.parser').find('h1').text
                return render(request, "encyclopedia/entry.html", {
                    # Returns "Search" form to the layout.html page every time
                    "form": NewSearchForm(),
                    "title": soup, "entry": search_entry, "random_entries": util.list_entries()
                })
            else:
                # Escapes all special regex characters someone searched for,
                # treating them as normal characters
                search_entry = re.escape(search_entry)
                # Creates a regular expression for the search entry ignoring case
                search_entry = re.compile("%s" % search_entry, re.IGNORECASE)
                matches = []
                # Checks if the query is a substring of existing entries
                for entry in list_of_entries:
                    if re.search(search_entry, entry):
                        # Appends entry including that substring to matches
                        matches.append(entry)
                # New non-lowercase list of entries defined
                list_entries = util.list_entries()
                for i in range(len(matches)):
                    for j in range(len(list_entries)):
                        if matches[i] == list_entries[j].lower():
                            matches[i] = list_entries[j]
                return render(request, "encyclopedia/index.html", {
                        "entries": matches, "form": NewSearchForm(),
                        "search_entry": search_entry,"random_entries": util.list_entries()
                    })
        else:
            return render(request, "encyclopedia/index.html", {
                "form": form, "random_entries": util.list_entries()
            })
    return render(request, "encyclopedia/index.html", {
        "entries": sorted(util.list_entries()), "form": NewSearchForm(),
        "random_entries": util.list_entries()
    })

def edit(request, title):
    if request.method == "POST":
        form = EditEntry(request.POST)
        if form.is_valid():
            entry = form.cleaned_data["text"]
            # Uses string concatenation to convert title into Markdown
            entry = '#' + ' ' + title + "\n\n" + entry
            util.save_entry(title, entry)
            # Converts Markdown into HTML
            entry = markdown.markdown(util.get_entry(title))
            return render(request, "encyclopedia/entry.html", {
                        "form": NewSearchForm(), "title": title,
                        "entry": entry, "random_entries": util.list_entries()
                    })
        else:
            return render(request, "encyclopedia/edit_entry.html", {
                "form": NewSearchForm(), "edit_form": EditEntry(),
                "title": title,
                "inner_title": title,
                "entry": entry, "random_entries": util.list_entries()
            })
    else:
        entry = util.get_entry(title)
        # Gets rest of entry excluding the title, the first line
        entry = entry.split('\n', 1)[1]
        return render(request, "encyclopedia/edit_entry.html", {
            "title": title,
            "inner_title": title,
            "entry": entry,
            "form": NewSearchForm(),
            # Pre-populates the textarea with existing entry
            "edit_form": EditEntry(initial={'text': entry}),
            "random_entries": util.list_entries()
        })



def entry(request, entry):
    if util.get_entry(entry):
        # Converts markdown text to HTML code
        html_entry = markdown.markdown(util.get_entry(entry.lower()))
        # Parses the HTML code to find h1 element and convert it into the text
        if BeautifulSoup(html_entry, 'html.parser').find('h1'):
            soup = BeautifulSoup(html_entry, 'html.parser').find('h1').text
            return render(request, "encyclopedia/entry.html", {
                "form": NewSearchForm(), "title": soup, "entry": html_entry,
                "random_entries": util.list_entries()
            })
        else:
            return render(request, "encyclopedia/entry.html", {
                "form": NewSearchForm(), "title": entry, "inner_title": entry, "entry": html_entry,
                "random_entries": util.list_entries()
            })
    else:
        return render(request, "encyclopedia/entry.html", {
            "form": NewSearchForm(),
            "title": "Error",
            "inner_title": "<h1>Error</h1>",
            "entry": "Error: Your requested page has not been found",
            "random_entries": util.list_entries()
        })

def new(request):
    if request.method == "POST":
        form = NewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            existing_entries = util.list_entries()
            for i in range(len(existing_entries)):
                existing_entries[i] = existing_entries[i].lower()
            if title.lower() in existing_entries:
                return render(request, "encyclopedia/entry.html",{
                              "form": NewSearchForm(),
                              "title": "Error", "inner_title": "<h1>Error</h1>",
                              "entry": "This encyclopedia entry already exists.",
                              "random_entries": util.list_entries()
                            })
            else:
                entry = form.cleaned_data["text"]
                entry = '#' + ' ' + title + "\n\n" + entry
                util.save_entry(form.cleaned_data["title"], entry)
                entry = markdown.markdown(util.get_entry(title))
                return render(request, "encyclopedia/entry.html", {
                    "form": NewSearchForm(), "title": title,
                    "entry": entry,
                    "random_entries": util.list_entries()
                })
        else:
            return render(request, "encyclopedia/new.html", {
                "form": NewSearchForm(), "form2": NewEntry(),
                "random_entries": util.list_entries()
            })
    else:
        return render(request, "encyclopedia/new.html", {
            "form": NewSearchForm(), "form2": NewEntry(),
            "random_entries": util.list_entries()
        })