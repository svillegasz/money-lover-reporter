from google.cloud import language_v1
from google.cloud import translate_v2 as translate
from pydash import map_, get, nth, has, has_substr, lower_case, split
import json
import requests
import os

translate_client = translate.Client()

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
    'Reference': 'Others',
    'Science': 'Education',
    'Sensitive Subjects': 'Others',
    'Shopping': 'Shopping',
    'Sports': 'Entertainment',
    'Travel': 'Travel',
}

def classify(text):
    print('Categorizer: classifying text with google cloud'.format(text=text))
    language_client = language_v1.LanguageServiceClient()

    if len(text.split(' ')) < 60:
        text = ' '.join([text] * (60 // len(text.split(' '))))

    document = language_v1.Document(
        content=text, 
        type_=language_v1.Document.Type.PLAIN_TEXT,
        language="en"
    )
    response = language_client.classify_text(request={'document': document})
    print(f'Categorizer: availabe categories for text -> {response}')
    category = get(nth(get(response, 'categories')), 'name')
    confidence = get(nth(get(response, 'categories')), 'confidence')
    print('Categorizer: google cloud category -> {category}'.format(category=category))
    if category and confidence > 0.5:
        return nth(split(category, '/'), 1)

def search(text):
    print('Categorizer: searching {text} in google'.format(text=text))

    response = requests.get(
        f"https://serpapi.com/search.json?api_key={os.getenv('SERPSBOT_API_KEY')}&engine=google&q={text}&gl=co&hl=es-419"
    )

    if response.status_code == 200:
        knowledge_graph = get(response.json(), 'knowledge_graph')
        if knowledge_graph and 'type' in knowledge_graph:
            return knowledge_graph['type']
        return ' '.join(map_(get(response.json(), 'organic_results'), 'snippet'))

def predefined_category(text):
    if any(has_substr(lower_case(text), concept) for concept in ['fiducredicorp', 'itau', 'decolombia']): return 'Marsella'
    if any(has_substr(lower_case(text), concept) for concept in ['abierta ali']): return 'Tierra grata'
    if any(has_substr(lower_case(text), concept) for concept in ['enlace operativo', 'finanseguro']): return 'Insurances'
    if any(has_substr(lower_case(text), concept) for concept in ['rappi', 'didi food']): return 'Food & Beverage'
    if any(has_substr(lower_case(text), concept) for concept in ['cabify', 'uber', 'didi']): return 'Transportation'
    if any(has_substr(lower_case(text), concept) for concept in ['mercado madrid', 'fruver']): return 'Groceries'
    if any(has_substr(lower_case(text), concept) for concept in ['servi estadio', 'distracom']): return 'Gas'
    if any(has_substr(lower_case(text), concept) for concept in ['icetex']): return 'Education'
    if has_substr(lower_case(text), 'davivienda'): return 'Car'
    if has_substr(lower_case(text), 'pagos electronicos s'): return 'Credit Card'
    if has_substr(lower_case(text), 'canon'): return 'Marsella'
    if any(has_substr(lower_case(text), concept) for concept in ['a toda hora', 'une', 'comcel', 'aval valor', 'factura movil', 'claro']): return 'Bills & Utilities'

def categorize(text):
    print(f'Categorizer: starting categorization process for {text}')
    if predefined_category(text):
        print('Categorizer: returning predifined categroy')
        return predefined_category(text)
    result = search(text)
    print(f'Categorizer: describing text from search enginge -> {result}')
    if not result:
        print('Categorizer: not search results found (returned others)')
        return 'Others'
    print(f'Categorizer: translating search results for "{text}" to english')
    translated_result = translate_client.translate(result, target_language='en')['translatedText']
    category = classify(translated_result)
    if not category or not has(GOOGLE_CATEGORIES, category):
        print('Categorizer: not (strong) matching  category (returned others)')
        return 'Others'
    print('Categorizer: Full categorization process completed (category {category})'.format(category=category))
    return get(GOOGLE_CATEGORIES, category)
