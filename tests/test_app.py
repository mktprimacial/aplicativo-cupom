from app.main import create_app
from app.db import ensure_db, get_conn


def make_client(tmp_path):
    db_path = tmp_path / 'test.sqlite3'
    app = create_app(
        {
            'TESTING': True,
            'APP_BASE_URL': 'http://localhost:5000',
            'NUVEMSHOP_APP_ID': '123',
            'NUVEMSHOP_CLIENT_SECRET': 'secret',
            'NUVEMSHOP_AUTH_URL': 'https://example.com/auth',
            'NUVEMSHOP_TOKEN_URL': 'https://example.com/token',
            'DATABASE_PATH': str(db_path),
            'DEFAULT_COUPON_PARAM': 'coupon',
        }
    )
    ensure_db(str(db_path))
    return app.test_client(), str(db_path)


def test_create_link_and_redirect(tmp_path):
    client, db_path = make_client(tmp_path)

    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO stores (store_id, store_domain, access_token, scopes, coupon_param_name) VALUES (?, ?, ?, ?, ?)",
            ('1', 'minhaloja.com.br', 'token', 'read_orders', 'coupon'),
        )

    coupon_resp = client.post('/api/coupons', json={'store_id': '1', 'code': 'BEMVINDO10'})
    assert coupon_resp.status_code == 201

    link_resp = client.post('/api/links', json={'store_id': '1', 'coupon_code': 'BEMVINDO10', 'referrer': 'instagram'})
    assert link_resp.status_code == 201
    slug = link_resp.get_json()['slug']

    redirect_resp = client.get(f'/r/{slug}', follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert 'https://minhaloja.com.br/' in redirect_resp.headers['Location']
    assert 'coupon=BEMVINDO10' in redirect_resp.headers['Location']
    assert 'ref=instagram' in redirect_resp.headers['Location']


def test_stats_endpoint(tmp_path):
    client, db_path = make_client(tmp_path)
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO stores (store_id, store_domain, access_token, scopes, coupon_param_name) VALUES (?, ?, ?, ?, ?)",
            ('99', 'teste.com', 'token', '', 'coupon'),
        )
        conn.execute(
            "INSERT INTO tracked_links (store_id, slug, coupon_code, clicks, conversions) VALUES (?, ?, ?, ?, ?)",
            ('99', 'abc123', 'OFF10', 5, 2),
        )

    stats = client.get('/api/stats?store_id=99')
    assert stats.status_code == 200
    payload = stats.get_json()
    assert payload['links'] == 1
    assert payload['clicks'] == 5
    assert payload['conversions'] == 2


def test_callback_rejects_invalid_state(tmp_path):
    client, _ = make_client(tmp_path)

    response = client.get(
        '/auth/nuvemshop/callback?code=abc&store_id=1&store_domain=minhaloja.com.br&state=invalid'
    )
    assert response.status_code == 400
    assert response.get_json()['error'] == 'invalid_or_expired_state'


def test_callback_accepts_valid_state_once(tmp_path, monkeypatch):
    client, db_path = make_client(tmp_path)

    install_resp = client.get('/install?store_domain=minhaloja.com.br', follow_redirects=False)
    assert install_resp.status_code == 302
    location = install_resp.headers['Location']
    state = location.split('state=')[1].split('&')[0]

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return {'access_token': 'access123', 'scope': 'read_orders'}

        text = 'ok'

    def fake_post(url, json, timeout):
        return FakeResponse()

    monkeypatch.setattr('app.main.requests.post', fake_post)

    callback_url = (
        '/auth/nuvemshop/callback'
        f'?code=code123&store_id=42&store_domain=minhaloja.com.br&state={state}'
    )
    callback_resp = client.get(callback_url, follow_redirects=False)
    assert callback_resp.status_code == 302

    second_try = client.get(callback_url)
    assert second_try.status_code == 400
    assert second_try.get_json()['error'] == 'invalid_or_expired_state'

    with get_conn(db_path) as conn:
        store = conn.execute('SELECT store_id, store_domain FROM stores WHERE store_id = ?', ('42',)).fetchone()
        assert store is not None



def test_ensure_db_works_with_filename_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ensure_db('app.sqlite3')
    assert (tmp_path / 'app.sqlite3').exists()
