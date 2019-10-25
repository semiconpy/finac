import rapidtables, neotermcolor

from finac.core import init, config

# exceptions
from finac.core import ResourceNotFound, RateNotFound
from finac.core import OverdraftError, OverlimitError
from finac.core import ResourceAlreadyExists

# currency methods
from finac.core import currency_create, currency_delete
from finac.core import currency_set_rate, currency_rate
from finac.core import currency_delete_rate

from finac.core import currency_update
from finac.core import currency_precision

# account methods
from finac.core import account_create, account_delete
from finac.core import account_info

from finac.core import account_update

# transaction methods
from finac.core import transaction_create, transaction_complete
from finac.core import transaction_move, transaction_delete

from finac.core import transaction_update

# balance methods
from finac.core import account_credit, account_debit, account_balance

# statements
from finac.core import account_statement, account_statement_summary
from finac.core import account_list, account_list_summary

# purges
from finac.core import purge, transaction_purge

tr = transaction_create
mv = transaction_move
rm = transaction_delete

stmt = account_statement_summary
balance = account_balance

lsaccs = account_list_summary


def format_money(amnt, precision):
    # return '{:,.2f}'.format(amnt)
    return ('{:,.' + str(precision) + 'f}').format(amnt).replace(',', ' ')


def ls(account=None,
       currency=None,
       code=None,
       tp=None,
       start=None,
       end=None,
       tag=None,
       pending=False,
       hide_empty=False,
       order_by=['tp', 'currency', 'account', 'balance'],
       base_currency=None):
    if account:
        result = account_statement_summary(account=account,
                                           start=start,
                                           end=end,
                                           tag=tag,
                                           pending=pending)
        stmt = result['statement'].copy()
        acc_info = account_info(account)
        precision = currency_precision(acc_info['currency'])
        for i, r in enumerate(stmt):
            r = r.copy()
            del r['is_completed']
            r['amount'] = format_money(r['amount'], precision)
            stmt[i] = r
        ft = rapidtables.format_table(
            stmt,
            fmt=rapidtables.FORMAT_GENERATOR,
            align=(rapidtables.ALIGN_LEFT, rapidtables.ALIGN_RIGHT,
                   rapidtables.ALIGN_LEFT, rapidtables.ALIGN_LEFT,
                   rapidtables.ALIGN_LEFT, rapidtables.ALIGN_LEFT,
                   rapidtables.ALIGN_LEFT))
        if not ft:
            return
        h, tbl = ft
        neotermcolor.cprint(h, 'blue')
        neotermcolor.cprint('-' * len(h), 'grey')
        for t, s in zip(tbl, result['statement']):
            neotermcolor.cprint(t,
                                'red' if s['amount'] < 0 else 'green',
                                attrs='')
        neotermcolor.cprint('-' * len(h), 'grey')
        print('Debit turnover: ', end='')
        neotermcolor.cprint(format_money(result['debit'], precision),
                            color='green',
                            attrs='bold',
                            end=', ')
        print('credit turnover: ', end='')
        neotermcolor.cprint(format_money(result['credit'], precision),
                            color='red',
                            attrs='bold')
        print()
        print('Net profit/loss: ', end='')
        neotermcolor.cprint('{} {}'.format(
            format_money(result['debit'] - result['credit'], precision),
            acc_info['currency']),
                            attrs='bold')
        print()
    else:
        if not base_currency:
            base_currency = config.base_currency
        result = account_list_summary(currency=currency,
                                      tp=tp,
                                      code=code,
                                      date=end,
                                      order_by=order_by,
                                      hide_empty=hide_empty,
                                      base_currency=base_currency)
        accounts = result['accounts']
        data = accounts.copy()
        for i, r in enumerate(accounts):
            r = r.copy()
            r['balance'] = format_money(r['balance'],
                                        currency_precision(r['currency']))
            r['balance ' + base_currency.upper()] = format_money(
                r['balance_bc'], currency_precision(base_currency))
            del r['balance_bc']
            del r['note']
            accounts[i] = r
        ft = rapidtables.format_table(
            accounts,
            fmt=rapidtables.FORMAT_GENERATOR,
            align=(rapidtables.ALIGN_LEFT, rapidtables.ALIGN_LEFT,
                   rapidtables.ALIGN_CENTER, rapidtables.ALIGN_RIGHT,
                   rapidtables.ALIGN_RIGHT))
        if not ft:
            return
        h, tbl = ft
        neotermcolor.cprint(h, 'blue')
        neotermcolor.cprint('-' * len(h), 'grey')
        for t, s in zip(tbl, data):
            neotermcolor.cprint(t,
                                'red' if s['balance'] < 0 else None,
                                attrs='')
        neotermcolor.cprint('-' * len(h), 'grey')
        neotermcolor.cprint('Total: ', end='')
        neotermcolor.cprint('{} {}'.format(
            format_money(result['total'], currency_precision(base_currency)),
            base_currency.upper()),
                            attrs='bold')
        print()
