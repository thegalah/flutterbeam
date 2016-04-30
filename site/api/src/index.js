'use strict';

let app = require('../index').app;
let router = require('koa-router')();

//define routes
let routes=[
	{
		'path':'./routes',
		'prefix':'/routes',
		'type':'public'
	}
];
//add routes
routes.forEach(function(r){
	console.log('\n__________Adding router: '+r.prefix);
	let subrouter=require(r.path).router;
	router.use(r.prefix,subrouter.routes());
});

exports={
	router:router
}

module.exports = exports;