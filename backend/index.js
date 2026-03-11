const { validateRequiredEnv } = require("./config/env");

function startServer() {
  const config = validateRequiredEnv();

  // Keep secrets in backend memory only; never expose to client-side bundles.
  console.log(
    `Backend started with required Nuvemshop secret configured (${config.nuvemshopClientSecret.length} chars).`
  );
}

startServer();
