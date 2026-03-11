# Rotação e proteção do Client Secret da Nuvemshop

## 1) Rotacionar o `Client Secret` no painel da Nuvemshop
1. Acesse o painel da Nuvemshop com conta administradora.
2. Vá até o app/configuração OAuth correspondente.
3. Gere um novo `Client Secret` (rotação).
4. Atualize imediatamente o segredo no ambiente de execução do backend.
5. Revogue/invalide o segredo antigo após confirmar o deploy.

## 2) Remover segredo de locais expostos
- Remova segredos de mensagens, issues, PRs e documentação pública.
- Garanta que o segredo não exista em código cliente (frontend/mobile).
- Revise histórico com ferramentas de secret scanning antes de publicar.

## 3) Uso obrigatório no backend via variável de ambiente
- Variável obrigatória: `NUVEMSHOP_CLIENT_SECRET`.
- Validação de startup implementada em `backend/config/env.js`.
- O backend deve falhar ao iniciar se a variável estiver ausente/vazia.

## 4) Arquivos de ambiente
- `.env.example` criado sem valores sensíveis.
- `.env` e `.env.*` bloqueados no `.gitignore`.

## 5) Fluxo de execução recomendado
```bash
export NUVEMSHOP_CLIENT_SECRET="<novo-valor>"
node backend/index.js
```
