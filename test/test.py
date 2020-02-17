import os

import requests
from tqdm import tqdm


def main():
    api_url = os.environ['API_URL']
    for match_id in tqdm(open('matches').read().split()):
        requests.post(f'{api_url}/match/{match_id}').raise_for_status()

    assert requests.post(f'{api_url}/match/{match_id}').status_code == 400

    fixtures = [
        # hero_id, start, winrate
        (45, '2020-01-05', 200, 1),
        (45, None, 200, 1),
        (43, '2020-01-05', 200, 0.6),
        (43, '2020-02-05', 200, None),
        (43, '2020-02-04T09:40', 200, 0.75),
        ('zxc', '2020-02-04T09:40', 422, None),
        (43, 'start', 422, None),
        (-10, None, 200, None),
    ]
    for hero_id, start, status_code, winrate in fixtures:
        params = dict(start=start) if start else {}
        resp = requests.get(f'{api_url}/winrate/{hero_id}', params=params)
        assert resp.status_code == status_code, f"Status code {resp.status_code} != {status_code}"
        if resp.status_code == 200:
            assert resp.json()['winrate'] == winrate, f"Winrate is {resp.json()['winrate']} but should be {winrate}"


if __name__ == '__main__':
    main()
