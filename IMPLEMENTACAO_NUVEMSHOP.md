# Checklist de Implementação — App Nativo Nuvemshop (Cupom por Link)

Este guia transforma a documentação da Nuvemshop em um plano prático para criar um app nativo que gera links e aplica cupom automaticamente.

## 0) Pré-requisitos

- [ ] Conta de parceiro e app criado no painel da Nuvemshop.
- [ ] Backend público com HTTPS.
- [ ] Banco de dados para multi-loja.
- [ ] Rotacionar e guardar `Client Secret` em variável de ambiente (nunca no frontend).

## 1) Configuração do app no painel

- [ ] Definir **App ID / Client Secret**.
- [ ] Definir **Auth redirect URL** (callback OAuth), por exemplo:
  - `https://seuapp.com/auth/nuvemshop/callback`
- [ ] Definir **Install URL** (início da instalação), por exemplo:
  - `https://seuapp.com/install`
- [ ] Selecionar escopos mínimos necessários:
  - leitura de cupons/descontos
  - criação/gestão de cupons (se aplicável)
  - leitura de pedidos (para métricas)
- [ ] Configurar webhooks/eventos que serão usados para estatísticas de uso.

## 2) Backend OAuth + persistência

### Rotas mínimas

- [ ] `GET /install`
  - recebe contexto da loja
  - gera URL de autorização OAuth
  - redireciona para consentimento
- [ ] `GET /auth/nuvemshop/callback`
  - valida parâmetros recebidos
  - troca `code` por `access_token`
  - salva token por loja
  - redireciona para o painel do app

### Modelo de dados sugerido

- [ ] `stores`
  - `id`
  - `store_id` (id da loja na plataforma)
  - `store_domain`
  - `access_token`
  - `scopes`
  - `installed_at`
  - `uninstalled_at` (nullable)
- [ ] `coupons`
  - `id`
  - `store_id`
  - `code`
  - `status`
  - `expires_at`
- [ ] `tracked_links`
  - `id`
  - `store_id`
  - `slug`
  - `coupon_code`
  - `referrer`
  - `destination_path`
  - `clicks`
  - `conversions`
- [ ] `events`
  - `id`
  - `tracked_link_id`
  - `type` (`click`, `checkout_start`, `order_paid`)
  - `payload_json`
  - `created_at`

## 3) Geração de links com cupom

### Fluxo recomendado

- [ ] Lojista escolhe um cupom no painel do app.
- [ ] Lojista informa origem/campanha (`referrer`) e cria link.
- [ ] Backend cria `slug` único e salva em `tracked_links`.
- [ ] Link final para divulgação:
  - `https://seuapp.com/r/{slug}`

### Endpoint de redirecionamento

- [ ] `GET /r/:slug`
  - valida slug
  - registra evento `click`
  - monta URL da loja com parâmetros de cupom + rastreio
  - redireciona (302)

### Observações importantes

- [ ] Suportar configuração por loja para nome de parâmetro do cupom (ex.: `coupon`, `discount_code`, etc.).
- [ ] Manter fallback de destino (`/` ou `/checkout`) conforme comportamento da loja.

## 4) Scripts (Store e Checkout)

Scripts complementam o fluxo de link; não substituem o backend de redirecionamento.

### Script Store (recomendado)

- [ ] Criar script com:
  - local de ativação: **Store**
  - evento: **onload**
- [ ] Ler parâmetros da URL (cupom/ref)
- [ ] Salvar em `localStorage` ou `sessionStorage`
- [ ] (Opcional) limpar query string após captura

### Script Checkout (opcional)

- [ ] Usar para telemetria e UX complementar.
- [ ] Evitar depender de manipulação frágil de DOM para aplicar cupom.
- [ ] Priorizar sempre o cupom vindo no link de entrada.

## 5) API do painel do app (MVP)

- [ ] `GET /api/coupons`
- [ ] `POST /api/coupons`
- [ ] `GET /api/links`
- [ ] `POST /api/links`
- [ ] `PATCH /api/links/:id/toggle`
- [ ] `GET /api/stats?from=&to=`

## 6) Segurança e conformidade

- [ ] Nunca expor `Client Secret` no código cliente.
- [ ] Assinar/validar origem em callbacks e webhooks.
- [ ] Criptografar tokens em repouso.
- [ ] Registrar auditoria de ações sensíveis.
- [ ] Ter política de privacidade e termos para publicação.

## 7) Plano de execução (7 dias)

- [ ] Dia 1: configuração do app + OAuth funcionando.
- [ ] Dia 2: tabelas e integração com API de cupons.
- [ ] Dia 3: CRUD de links + endpoint `/r/:slug`.
- [ ] Dia 4: scripts Store/Checkout + rastreio base.
- [ ] Dia 5: dashboard de métricas (cliques/uso).
- [ ] Dia 6: testes de ponta a ponta em loja de teste.
- [ ] Dia 7: hardening, documentação e publicação.

## 8) Critérios de aceite do MVP

- [ ] Instalar app em loja de teste sem erro.
- [ ] Gerar link com cupom em menos de 30 segundos.
- [ ] Clique no link redireciona e preserva cupom.
- [ ] Métricas mostram ao menos: cliques, usos, conversão.
- [ ] Desinstalação e reinstalação não corrompem dados da loja.

## 9) Status da implementação no repositório

- [x] Estrutura inicial de backend Flask criada.
- [x] Rotas implementadas: `GET /install`, `GET /auth/nuvemshop/callback`, `GET /r/:slug`.
- [x] Persistência SQLite para `stores`, `coupons`, `tracked_links`, `events`.
- [x] APIs básicas do painel (`/api/coupons`, `/api/links`, `/api/stats`).
- [x] Scripts de exemplo para Store e Checkout adicionados.
- [x] Arquivo `.env.example` com segredos em variáveis de ambiente.
- [ ] Publicação HTTPS em produção (depende de deploy externo).
