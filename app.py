from __future__ import print_function

import os
import sys

from flask import Flask, render_template, request
from tt import BooleanExpression, TruthTable
from tt.errors import (
    EmptyExpressionError,
    GrammarError,
    NoEvaluationVariationError)


app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/evaluate')
def evaluate():
    # TODO: cache expression / tables objects based on query params

    try:
        expr = request.args.get('expr')
        action = request.args.get('action')
        context = {}

        if expr is None or action is None:
            raise ValueError('Missing required params')

        expr = expr.strip()
        context['expr'] = expr
        b = BooleanExpression(expr)

        if action == 'table':
            t = TruthTable(b)
            context['is_table'] = True
            context['table'] = t
        elif action == 'satone':
            context['is_sat'] = True
            context['symbols'] = b.symbols

            sat_sol = b.sat_one()
            context['sat_iter'] = [sat_sol] if sat_sol else []
        elif action == 'satall':
            context['is_sat'] = True
            context['symbols'] = b.symbols
            context['sat_iter'] = list(b.sat_all())
        else:
            raise ValueError('Invalid option')
    except ValueError:
        context['is_error'] = True
        context['error_content'] = [
            'Please don\'t go out of your way to break this '
            'already-fragile system']
    except EmptyExpressionError:
        context['is_error'] = True
        context['error_content'] = ['You gave us an invalid expression!']
    except NoEvaluationVariationError:
        context['is_error'] = True
        context['error_content'] = [
            'You should be able to figure that out on your own']
    except GrammarError as e:
        context['is_error'] = True
        context['error_content'] = [e.message]
        if e.error_pos is not None:
            underlined_error_expr = ''
            for i, char in enumerate(expr):
                underlined_error_expr += (char if i != e.error_pos else
                                          '<u>{}</u>'.format(char))
            context['underlined_error_expr'] = underlined_error_expr
    except Exception as e:
        context['is_error'] = True
        context['error_content'] = ['An unexpected error occured :(']
        raise e

    return render_template('result.html', **context)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG')
    if debug:
        app.config['DEBUG'] = True
        app.run('127.0.0.1', port=5000)
    else:
        print('Don\'t run this in production', file=sys.stderr)
