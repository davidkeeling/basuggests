const webpack = require('webpack');

module.exports = {
  entry: [
    './static/js/recommend.js'
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader']
      }
    ]
  },
  resolve: {
    extensions: ['*', '.js', '.jsx']
  },
  output: {
    path: __dirname + '/static/build',
    filename: 'bundle.js'
  }
};
