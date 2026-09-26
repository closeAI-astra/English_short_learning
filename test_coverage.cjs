// Fails when the app's NGSL+TSL coverage (in-app) or TSL coverage (all material) drops to 50% or below.
process.argv.push('--check');require('./coverage.cjs');
