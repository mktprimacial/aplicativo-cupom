# aplicativo-cupom

Implementação inicial de app nativo para Nuvemshop com foco em:

- OAuth de instalação por loja
- Persistência multi-loja
- Geração de links rastreáveis com cupom
- Scripts Store/Checkout para captura de contexto

## Configuração do app no painel

Configure no painel da Nuvemshop:

- Install URL: `https://SEU_DOMINIO/install`
- Auth Redirect URL: `https://SEU_DOMINIO/auth/nuvemshop/callback`

Escopos mínimos recomendados:

- leitura/escrita de descontos/cupons
- leitura de pedidos

## Segurança

- Rotacione o `Client Secret` imediatamente caso tenha sido exposto.
- Nunca coloque segredo no frontend.
- Use variáveis de ambiente (veja `.env.example`).

## Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Endpoints

- `GET /health`
- `GET /install?store_domain=minhaloja.com`
- `GET /auth/nuvemshop/callback`
- `GET /api/coupons?store_id=...`
- `POST /api/coupons`
- `GET /api/links?store_id=...`
- `POST /api/links`
- `PATCH /api/links/:id/toggle`
- `GET /api/stats?store_id=...`
- `GET /r/:slug`

## Deploy (merge/deploy)

1. Faça push da branch:
   ```bash
   git push origin <branch>
   ```
2. Abra PR para `main`.
3. Faça merge do PR.
4. Faça deploy na plataforma escolhida (ou deploy automático após merge).
5. Ajuste `APP_BASE_URL` para domínio HTTPS público.

