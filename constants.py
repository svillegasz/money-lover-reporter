BANCOLOMBIA_EMAIL = 'alertasynotificaciones@bancolombia.com.co OR alertasynotificaciones@notificacionesbancolombia.com'

SCOTIABANK_EMAIL = 'colpatriainforma@scotiabankcolpatria.com'

BANCOLOMBIA_ACCOUNT = 'Bancolombia'

SCOTIABANK_ACCOUNT = 'Scotiabank (Credit Card)'


CATEGORY_TYPE = {
    'income': 1,
    'expense': 2
}

RECURRING_TRANSACTIONS = [
    {
        'account': BANCOLOMBIA_ACCOUNT,
        'amount': 7100,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Fees & Charges'},
        'description': 'Cuota de manejo tarjeta debito',
        'day': 14
    },
    {
        'account': BANCOLOMBIA_ACCOUNT,
        'amount': 268182,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Fees & Charges'},
        'description': 'Sura PAC',
        'day': 28
    },
    {
        'account': SCOTIABANK_ACCOUNT,
        'amount': 5000,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Fees & Charges'},
        'description': 'Seguro de vida tarjeta',
        'day': 1
    },
    {
        'account': SCOTIABANK_ACCOUNT,
        'amount': 95590,
        'category': {'type': CATEGORY_TYPE['expense'], 'name': 'Fees & Charges'},
        'description': 'Seguro de vida scotiabank',
        'day': 1
    }
]
