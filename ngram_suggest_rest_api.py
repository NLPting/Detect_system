from starlette.responses import UJSONResponse
from fastapi import FastAPI
import enchant

from linggle_api import linggle
from fuzzy_query import fuzzy_query


app = FastAPI()
spell = enchant.Dict('en')


def gen_replace_query(word):
    if spell.check(word):
        # check forms
        return '_'
    else:
        # TODO: this is a temporary workaround
        candidates = spell.suggest(word)
        candidates.append(word)
        return '/'.join(candidates).replace(' ', '_')


def gen_check_query(query: str, err_type: str, index: int):
    tokens = query.split()
    if err_type == 'replace':
        tokens[index] = gen_replace_query(tokens[index])
    elif err_type == 'delete':
        tokens[index] = '?' + tokens[index]
    elif err_type == 'insert':
        tokens.insert(index, '?_')
    else:
        pass
    return ' '.join(tokens)



@app.get("/suggest/{query:path}", response_class=UJSONResponse)
async def check_ngram(query: str, err_type: str = None, index: int = -1):
    if err_type and index >= 0:
        query = gen_check_query(query, err_type, index)
    ngrams = linggle(query)
    # if no result, change query to get partial result
    if not ngrams:
        query, ngrams = fuzzy_query(query, index)
    return {'query': query, 'ngrams': ngrams}
