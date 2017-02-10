from __future__ import print_function

import os
import sys

from flask import Flask, render_template, request
from tt import BooleanExpression as bexpr, TruthTable as ttable
from tt.errors import GrammarError


app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/evaluate')
def evaluate():
    # TODO: cache results based on query params
    expr = request.args.get('expr')
    op = request.args.get('op')
    context = {'expr': expr}

    try:
        if not expr:
            raise ValueError('Empty expression')

        b = bexpr(expr)

        if op == 'table':
            t = ttable(b)

            # this is really inefficient
            rows = []
            for row in t._input_combos():
                l = [int(val) for val in row]
                rows.append(l)

            for i, result in enumerate(t.results):
                rows[i].append(int(result))

            context['is_table'] = True
            context['symbols'] = b.symbols
            context['rows'] = rows
        elif op == 'symbols':
            context['is_symbols'] = True
            context['symbols'] = b.symbols
        elif op == 'tokens':
            context['is_tokens'] = True
            context['tokens'] = b.tokens
        else:
            raise ValueError('Invalid option')
    except ValueError:
        context['is_error'] = True
        context['error_content'] = ['You gave us an invalid value :o']
    except GrammarError as e:
        context['is_error'] = True
        context['error_content'] = [
            'Error! ' + e.message + ':',
            e.expr_str,
            '&nbsp;' * e.error_pos + '^']
    except Exception as e:
        context['is_error'] = True
        context['error_content'] = ['An unexpected error occured :(']

    return render_template('result.html', **context)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG')
    if debug:
        app.config['DEBUG'] = True
        app.run('127.0.0.1', port=5000)
    else:
        print('Don\'t run this in production', file=sys.stderr)
