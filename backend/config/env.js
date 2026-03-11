const REQUIRED_ENV_VARS = ["NUVEMSHOP_CLIENT_SECRET"];

function validateRequiredEnv() {
  const missingVars = REQUIRED_ENV_VARS.filter((key) => {
    const value = process.env[key];
    return typeof value !== "string" || value.trim() === "";
  });

  if (missingVars.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missingVars.join(", ")}`
    );
  }

  return {
    nuvemshopClientSecret: process.env.NUVEMSHOP_CLIENT_SECRET,
  };
}

module.exports = {
  validateRequiredEnv,
};
