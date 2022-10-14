from google.cloud import language_v1
from pydash import map_, get, nth, has, has_substr, lower_case, split
from googletrans import Translator
import json
import requests
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
    print('Categorizer: classifying text with google cloud'.format(text=text))
    language_client = language_v1.LanguageServiceClient()
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT
    )
    response = language_client.classify_text(request={'document': document})
    print(f'Categorizer: availabe categories for text -> {response}')
    category = get(nth(get(response, 'categories')), 'name')
    print('Categorizer: google cloud category -> {category}'.format(category=category))
    if category:
        return nth(split(category, '/'), 1)

def search(text):
    print('Categorizer: searching {text} in google'.format(text=text))
    headers = {
        "X-RapidAPI-Key": os.getenv('RAPID_KEY'),
        "X-RapidAPI-Host" : os.getenv('RAPID_HOST')
    }
    payload = {
        "query": text,
        "gl": "CO",
        "hl": "es_CO",
        "pages": 2
    }
    response = requests.post(
        "https://google-search-5.p.rapidapi.com/google/organic-search",
        headers=headers,
        data=json.dumps(payload))

    if response.status_code == 200:
        return ' '.join(map_(get(response.json(), 'data.organic'), 'snippet'))

def predefined_category(text):
    if has_substr(lower_case(text), 'une'): return 'Bills & Utilities'
    if has_substr(lower_case(text), 'rappi'): return 'Food & Beverage'
    if has_substr(lower_case(text), 'comcel'): return 'Bills & Utilities'
    if has_substr(lower_case(text), 'nequi'): return 'Nequi'
    if has_substr(lower_case(text), 'credito visa'): return 'Credit Card'
    if has_substr(lower_case(text), 'fiducredicorp'): return 'Apartment'
    if has_substr(lower_case(text), 'canon'): return 'Rentals'
    if has_substr(lower_case(text), 'enlace operativo'): return 'Bills & Utilities'

def categorize(text):
    print(f'Categorizer: starting categorization process for {text}')
    if predefined_category(text):
        print('Categorizer: returning predifined categroy')
        return predefined_category(text)
    result = search(text)
    if not result:
        print('Categorizer: not search results found (returned others)')
        return 'Others'
    print(f'Categorizer: translating search results for "{text}" to english')
    translated_result = translator.translate(result).text
    category = classify(translated_result)
    if not category or not has(GOOGLE_CATEGORIES, category):
        print('Categorizer: not category found in categories (returned others)')
        return 'Others'
    print('Categorizer: Full categorization process completed (category {category})'.format(category=category))
    return get(GOOGLE_CATEGORIES, category)
