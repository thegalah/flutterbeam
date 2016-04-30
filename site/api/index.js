'use strict';

let koa = require('koa-framework');
let app = koa();
let api = require('koa-router')();
let config = require('config');

let json = require('koa-json');


exports.app=app;

//use json
app.use(json());

// logger

app.use(function *(next){
	//yield delayThunk(500);
	let start = new Date;
	yield next;
	let ms = new Date - start;
	console.log('----%s %s - %sms', this.method, this.url, ms);
});

function delayThunk(time) {
	return function(callback) {
		setTimeout(callback,time);
	};
}
let router=require('./src').router;
app.use(router.routes());

//catching errors
/*app.use(function *(next) {
	try {
		yield next;
	} catch (err) {
		console.log(err);
		//slack_notify(err);
		//rethrow error
		throw err;
		yield next;
	}
});*/



app.listen(config.app.port);

console.log('\n\n\n\n**********SERVER RUNNING ON PORT %d\n\n\n\n',config.app.port);