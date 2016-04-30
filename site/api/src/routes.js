'use strict';

const config = require('config');
const app = require('../index').app;
const router = require('koa-router')();

const multer = require('koa-multer');
const upload=multer({dest:'../uploads/'});
const parse = require('co-busboy');

const koaBody = require('koa-body')({ multipart: true });

function htmlEntities(string) {
	return string.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

router.post('upload',koaBody, function*(){
	console.log('file uploaded');
	console.log(this.request.body);
	//console.log(this.req.body);
	this.body=this;
});

router.get('test',function*(){
	this.body={'hello':'world'};
});

exports={
	router:router
}

module.exports = exports;