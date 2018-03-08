import pandas as pd
from tabulate import tabulate

from .api import GfcApi

def print_active_questions(server, token):
    api = GfcApi(token, server)
    ques = api.get_questions()
    df_q = pd.DataFrame(data=ques)
    df_q = df_q.drop_duplicates(subset='name')[df_q['active?']==True][['ends_at', 'id', 'name']]
    print(tabulate(df_q, headers='keys', tablefmt='psql'))



