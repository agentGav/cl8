// vue.config.js
module.exports = {
  // serve this for `npm run serve` in development
  // but output to the /static/ dir for django when
  // deploying the final bundle
  publicPath: process.env.NODE_ENV === 'production'
    ? '/static/'
    : '/',
  outputDir: 'vue-static',
  // django and whitenoise does its own hashing and cache busting
  filenameHashing: false,
  // proxy requests that are not matched by our own files
  // to the django server running at the address below
  devServer: {
    proxy: 'http://127.0.0.1:8000'
  }
}


