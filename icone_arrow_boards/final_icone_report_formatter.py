import json
from datetime import datetime, timedelta

out = []
for record in json.loads(open('final_icone_report.json', 'r').read()):
    start_date = datetime.strptime(record['start_time'], "%Y-%m-%dT%H:%M:%SZ")
    end_date = datetime.strptime(record['end_time'], "%Y-%m-%dT%H:%M:%SZ")
    state = record['states'][0]
    values = [start_date.strftime('%Y-%m-%d'), start_date.strftime('%H:%M'), end_date.strftime('%H:%M'),
              record['id'], state, str(round((record['mm_min'] + record['mm_max']) / 2))]
    out.append('\n'.join(values) + '\n')

open('final_icone_report_formatted.json', 'w').write('\n'.join(out))
