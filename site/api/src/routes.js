'use strict';

let config = require('config');
let app = require('../index').app;
let router = require('koa-router')();



function htmlEntities(string) {
	return string.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

exports={
	router:router
}

module.exports = exports;