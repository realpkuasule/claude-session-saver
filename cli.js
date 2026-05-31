#!/usr/bin/env node
// Wrapper that reliably locates the package directory via __dirname,
// then delegates to install.sh. __dirname works regardless of how
// npx, npm, or a symlink invokes this script.
const { execSync } = require('child_process');
const path = require('path');

process.env.PKG_DIR = __dirname;

try {
  execSync('bash "' + path.join(__dirname, 'install.sh') + '"', { stdio: 'inherit' });
} catch (e) {
  process.exit(e.status || 1);
}
