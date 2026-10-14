const path = require('path');
const dotenv = require('dotenv');

// Load environment from cube/.env if present, then fallback to backend/.env
dotenv.config({ path: path.resolve(__dirname, '.env') });
dotenv.config({ path: path.resolve(__dirname, '../backend/.env') });

// Map generic DB_* environment variables to CUBEJS_DB_* if not set
if (process.env.DB_HOST && !process.env.CUBEJS_DB_HOST) {
  process.env.CUBEJS_DB_HOST = process.env.DB_HOST;
}
if (process.env.DB_PORT && !process.env.CUBEJS_DB_PORT) {
  process.env.CUBEJS_DB_PORT = process.env.DB_PORT;
}
if (process.env.DB_NAME && !process.env.CUBEJS_DB_NAME) {
  process.env.CUBEJS_DB_NAME = process.env.DB_NAME;
}
if (process.env.DB_USER && !process.env.CUBEJS_DB_USER) {
  process.env.CUBEJS_DB_USER = process.env.DB_USER;
}
if (process.env.DB_PASSWORD && !process.env.CUBEJS_DB_PASS) {
  process.env.CUBEJS_DB_PASS = process.env.DB_PASSWORD;
}

process.env.CUBEJS_DB_TYPE = process.env.CUBEJS_DB_TYPE || 'postgres';
process.env.PORT = process.env.CUBE_PORT || process.env.PORT || '4000';
process.env.CUBEJS_DEV_MODE = process.env.CUBEJS_DEV_MODE || 'true';

module.exports = {
  schemaPath: path.resolve(__dirname, 'model'),
};
