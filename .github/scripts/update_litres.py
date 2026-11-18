"""Берёт оценку и возрастное ограничение книги с ЛитРес и записывает их в litres.json рядом с index.html.

Страница сама подставляет цифры из litres.json. Запускается GitHub раз в сутки (.github/workflows/litres.yml),
можно запустить и вручную: python .github/scripts/update_litres.py
Если ЛитРес не ответил или прислал странные данные, файл не меняется.
"""
import datetime
import json
import os
import urllib.request

BOOK_ID = 73949334
URL = f'https://api.litres.ru/foundation/api/arts/{BOOK_ID}'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'litres.json')


def main():
    try:
        req = urllib.request.Request(URL, headers={'Accept': 'application/json', 'User-Agent': 'kapital-vopreki.ru rating updater'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)['payload']['data']
        new = {
            'rating': round(float(data['rating']['rated_avg']), 1),
            'votes': int(data['rating']['rated_total_count']),
            'age': int(data.get('min_age') or 0),
        }
    except Exception as exc:  # сеть, формат ответа — оставляем прежний файл
        print('ЛитРес не ответил, файл не меняю:', exc)
        return
    if not (1 <= new['rating'] <= 5 and new['votes'] > 0):
        print('Странные данные, файл не меняю:', new)
        return
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            old = json.load(f)
    if all(old.get(k) == v for k, v in new.items()):
        print('Без изменений:', new)
        return
    new['updated'] = datetime.date.today().isoformat()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('Обновлено:', new)


if __name__ == '__main__':
    main()
