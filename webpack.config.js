const path = require('path');

module.exports = {
  entry: path.resolve(__dirname, 'js', 'app.js'),

  output: {
    path: path.resolve(__dirname, 'static'),
    filename: 'bundle.js'
  },

  module: {
    loaders: [
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      }
    ]
  }
};
