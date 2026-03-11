import json
import secrets
import string
from urllib.parse import urlencode

import requests
from flask import Flask, jsonify, redirect, render_template, request

from app.config import load_settings
from app.db import ensure_db, get_conn


def _slug(size: int = 8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(size))


def create_app(test_config=None):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    if test_config is not None:
        app.config.update(test_config)
    else:
        settings = load_settings()
        app.config.update(
            APP_BASE_URL=settings.app_base_url,
            NUVEMSHOP_APP_ID=settings.app_id,
            NUVEMSHOP_CLIENT_SECRET=settings.client_secret,
            NUVEMSHOP_AUTH_URL=settings.nuvemshop_auth_url,
            NUVEMSHOP_TOKEN_URL=settings.nuvemshop_token_url,
            DATABASE_PATH=settings.db_path,
            DEFAULT_COUPON_PARAM=settings.default_coupon_param,
        )

    ensure_db(app.config["DATABASE_PATH"])

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/install")
    def install():
        store_domain = request.args.get("store_domain")
        if not store_domain:
            return jsonify({"error": "store_domain is required"}), 400

        callback_url = f"{app.config['APP_BASE_URL']}/auth/nuvemshop/callback"
        state = _slug(24)
        params = {
            "client_id": app.config["NUVEMSHOP_APP_ID"],
            "redirect_uri": callback_url,
            "response_type": "code",
            "state": state,
            "store_domain": store_domain,
        }
        auth_url = f"{app.config['NUVEMSHOP_AUTH_URL']}?{urlencode(params)}"
        return redirect(auth_url)

    @app.get("/auth/nuvemshop/callback")
    def callback():
        code = request.args.get("code")
        store_id = request.args.get("store_id")
        store_domain = request.args.get("store_domain")
        if not code or not store_id or not store_domain:
            return jsonify({"error": "code, store_id and store_domain are required"}), 400

        payload = {
            "client_id": app.config["NUVEMSHOP_APP_ID"],
            "client_secret": app.config["NUVEMSHOP_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "code": code,
        }

        token_response = requests.post(app.config["NUVEMSHOP_TOKEN_URL"], json=payload, timeout=15)
        if token_response.status_code >= 400:
            return jsonify({"error": "token_exchange_failed", "details": token_response.text}), 502

        token_data = token_response.json()
        access_token = token_data.get("access_token")
        scope = token_data.get("scope", "")
        if not access_token:
            return jsonify({"error": "missing_access_token"}), 502

        with get_conn(app.config["DATABASE_PATH"]) as conn:
            conn.execute(
                """
                INSERT INTO stores (store_id, store_domain, access_token, scopes, coupon_param_name)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(store_id)
                DO UPDATE SET
                  store_domain=excluded.store_domain,
                  access_token=excluded.access_token,
                  scopes=excluded.scopes,
                  uninstalled_at=NULL
                """,
                (store_id, store_domain, access_token, scope, app.config["DEFAULT_COUPON_PARAM"]),
            )

        return redirect("/")

    @app.get("/api/coupons")
    def list_coupons():
        store_id = request.args.get("store_id")
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400

        with get_conn(app.config["DATABASE_PATH"]) as conn:
            rows = conn.execute(
                "SELECT code, status, expires_at FROM coupons WHERE store_id = ? ORDER BY id DESC",
                (store_id,),
            ).fetchall()

        return jsonify([dict(row) for row in rows])

    @app.post("/api/coupons")
    def create_coupon():
        data = request.get_json(force=True)
        store_id = data.get("store_id")
        code = (data.get("code") or "").strip().upper()
        if not store_id or not code:
            return jsonify({"error": "store_id and code are required"}), 400

        with get_conn(app.config["DATABASE_PATH"]) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO coupons (store_id, code, status, expires_at) VALUES (?, ?, ?, ?)",
                (store_id, code, data.get("status", "active"), data.get("expires_at")),
            )

        return jsonify({"ok": True, "code": code}), 201

    @app.get("/api/links")
    def list_links():
        store_id = request.args.get("store_id")
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400

        with get_conn(app.config["DATABASE_PATH"]) as conn:
            rows = conn.execute(
                """
                SELECT id, slug, coupon_code, referrer, destination_path, clicks, conversions, active
                FROM tracked_links
                WHERE store_id = ?
                ORDER BY id DESC
                """,
                (store_id,),
            ).fetchall()

        return jsonify([dict(row) for row in rows])

    @app.post("/api/links")
    def create_link():
        data = request.get_json(force=True)
        store_id = data.get("store_id")
        coupon_code = (data.get("coupon_code") or "").strip().upper()
        if not store_id or not coupon_code:
            return jsonify({"error": "store_id and coupon_code are required"}), 400

        destination_path = data.get("destination_path", "/")
        referrer = data.get("referrer")

        link_slug = _slug()
        with get_conn(app.config["DATABASE_PATH"]) as conn:
            conn.execute(
                """
                INSERT INTO tracked_links (store_id, slug, coupon_code, referrer, destination_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (store_id, link_slug, coupon_code, referrer, destination_path),
            )

        short_link = f"{app.config['APP_BASE_URL']}/r/{link_slug}"
        return jsonify({"ok": True, "slug": link_slug, "link": short_link}), 201

    @app.patch("/api/links/<int:link_id>/toggle")
    def toggle_link(link_id: int):
        data = request.get_json(force=True)
        active = 1 if bool(data.get("active", False)) else 0

        with get_conn(app.config["DATABASE_PATH"]) as conn:
            cur = conn.execute("UPDATE tracked_links SET active = ? WHERE id = ?", (active, link_id))
            if cur.rowcount == 0:
                return jsonify({"error": "link not found"}), 404

        return jsonify({"ok": True, "active": bool(active)})

    @app.get("/api/stats")
    def stats():
        store_id = request.args.get("store_id")
        if not store_id:
            return jsonify({"error": "store_id is required"}), 400

        with get_conn(app.config["DATABASE_PATH"]) as conn:
            summary = conn.execute(
                """
                SELECT COUNT(*) AS links, COALESCE(SUM(clicks), 0) AS clicks, COALESCE(SUM(conversions), 0) AS conversions
                FROM tracked_links
                WHERE store_id = ?
                """,
                (store_id,),
            ).fetchone()

        return jsonify(dict(summary))

    @app.get("/r/<slug>")
    def redirect_slug(slug: str):
        with get_conn(app.config["DATABASE_PATH"]) as conn:
            link_row = conn.execute(
                """
                SELECT tl.id, tl.store_id, tl.slug, tl.coupon_code, tl.referrer, tl.destination_path, tl.active,
                       s.store_domain, s.coupon_param_name
                FROM tracked_links tl
                JOIN stores s ON s.store_id = tl.store_id
                WHERE tl.slug = ?
                """,
                (slug,),
            ).fetchone()

            if not link_row:
                return jsonify({"error": "link not found"}), 404
            if link_row["active"] == 0:
                return jsonify({"error": "link inactive"}), 410

            conn.execute("UPDATE tracked_links SET clicks = clicks + 1 WHERE id = ?", (link_row["id"],))
            conn.execute(
                "INSERT INTO events (tracked_link_id, type, payload_json) VALUES (?, 'click', ?)",
                (
                    link_row["id"],
                    json.dumps({"user_agent": request.headers.get("user-agent", "")}),
                ),
            )

        coupon_param = link_row["coupon_param_name"] or app.config["DEFAULT_COUPON_PARAM"]
        query = {coupon_param: link_row["coupon_code"]}
        if link_row["referrer"]:
            query["ref"] = link_row["referrer"]

        destination_path = link_row["destination_path"] or "/"
        destination = f"https://{link_row['store_domain']}{destination_path}?{urlencode(query)}"
        return redirect(destination, code=302)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
