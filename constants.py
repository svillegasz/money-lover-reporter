BANCOLOMBIA_EMAIL = 'alertasynotificaciones@bancolombia.com.co OR alertasynotificaciones@notificacionesbancolombia.com OR alertasynotificaciones@an.notificacionesbancolombia.com'

SCOTIABANK_EMAIL = 'DAVIbankInforma@davibank.com'

BANCOLOMBIA_ACCOUNT = 'Bancolombia'

SCOTIABANK_ACCOUNT = 'Davibank (Credit Card)'


CATEGORY_TYPE = {
    'income': 1,
    'expense': 2
}

RECURRING_TRANSACTIONS = [
    {
        'account': BANCOLOMBIA_ACCOUNT,
        'amount': 7450,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Fees & Charges'},
        'description': 'Cuota de manejo tarjeta debito',
        'day': 14
    },
    {
        'account': BANCOLOMBIA_ACCOUNT,
        'amount': 297860,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Mother'},
        'description': 'Sura PAC',
        'day': 28
    },
    {
        'account': SCOTIABANK_ACCOUNT,
        'amount': 6290,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Insurances'},
        'description': 'Seguro de vida tarjeta',
        'day': 1
    },
    {
        'account': SCOTIABANK_ACCOUNT,
        'amount': 100761,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Insurances'},
        'description': 'Seguro de vida scotiabank',
        'day': 1
    }
]
