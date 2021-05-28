from google.cloud import language_v1
from pydash import map_, get, concat, nth, has, has_substr, lower_case, split
from googletrans import Translator
import urllib
import requests
import re
import os

translator = Translator()

# Categories source https://cloud.google.com/natural-language/docs/categories
GOOGLE_CATEGORIES = {
    'Adult': 'Entertainment',
    'Arts & Entertainment': 'Entertainment',
    'Autos & Vehicles': 'Transportation',
    'Beauty & Fitness': 'Health & Fitness',
    'Books & Literature': 'Books',
    'Business & Industrial': 'Business',
    'Computers & Electronics': 'Education',
    'Finance': 'Bills & Utilities',
    'Food & Drink': 'Food & Beverage',
    'Games': 'Games',
    'Health': 'Health & Fitness',
    'Hobbies & Leisure': 'Entertainment',
    'Home & Garden': 'Home Improvement',
    'Internet & Telecom': 'Bills & Utilities',
    'Jobs & Education': 'Education',
    'Law & Government': 'Fees & Charges',
    'News': 'Fees & Charges',
    'Online Communities': 'Education',
    'People & Society': 'Entertainment',
    'Pets & Animals': 'Pets',
    'Real Estate': 'Others',
    'Reference': 'Education',
    'Science': 'Education',
    'Sensitive Subjects': 'Others',
    'Shopping': 'Shopping',
    'Sports': 'Entertainment',
    'Travel': 'Travel',
}

def classify(text):
    print('Categorizer: classifying {text} with google cloud'.format(text=text))
    language_client = language_v1.LanguageServiceClient()
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT
    )
    response = language_client.classify_text(request={'document': document})
    category = get(nth(get(response, 'categories')), 'name')
    print('Categorizer: google cloud category -> {category}'.format(category=category))
    if category:
        return nth(split(category, '/'), 1)

def search(text):
    print('Categorizer: searching {text} in google'.format(text=text))
    headers = {
        "x-rapidapi-key": os.getenv('RAPID_KEY'),
        "x-rapidapi-host" : os.getenv('RAPID_HOST')
    }
    query = {
        "q": text,
        "cr": "CO",
        "num": 2
    }
    json = requests.get("https://rapidapi.p.rapidapi.com/api/v1/search/" + urllib.parse.urlencode(query), headers=headers).json()
    if json:
        return ' '.join(map_(get(json, 'results'), lambda result: get(result, 'description')))

def predefined_category(text):
    if has_substr(lower_case(text), 'une'): return 'Bills & Utilities'
    if has_substr(lower_case(text), 'rappi'): return 'Food & Beverage'
    if has_substr(lower_case(text), 'comcel'): return 'Bills & Utilities'
    if has_substr(lower_case(text), 'nequi'): return 'Nequi'
    if has_substr(lower_case(text), 'credito visa'): return 'Credit Card'
    if has_substr(lower_case(text), 'fiducredicorp'): return 'Apartment'
    if has_substr(lower_case(text), 'canon'): return 'Rentals'

def categorize(text):
    print('Categorizer: starting categorization process for {text}'.format(text=text))
    if predefined_category(text):
        print('Categorizer: returning predifined categroy')
        return predefined_category(text)
    result = search(text)
    if not result:
        print('Categorizer: not search results found (returned others)')
        return 'Others'
    print('Categorizer: translating result to english -> {result}'.format(result=result))
    translated_result = translator.translate(result).text
    category = classify(translated_result)
    if not category or not has(GOOGLE_CATEGORIES, category):
        print('Categorizer: not category found in categories (returned others)')
        return 'Others'
    print('Categorizer: Full categorization process completed (category {category})'.format(category=category))
    return get(GOOGLE_CATEGORIES, category)
