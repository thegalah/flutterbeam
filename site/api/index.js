'use strict';

const config=require('config');
const fs    = require("fs");
const express = require('express');
const bodyParser = require('body-parser');
const multer  = require('multer')
const upload = multer({ dest: config.app.upload_dir })

const app = express();
app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies


app.put('/upload', upload.single('picture_file'), function(req, res) {
	console.log('--------/uploadPicture\n\n\n\n\n');
	var out={}

	console.log(req.file);
    //check existence of file
    if(is_empty(req.file)){
		out['error']='No cv uploaded.';
		res.json(out);
		return;
    }
    res.json(out);
    return;
});


function attachListeners(ls,res){
	let hasErrored=false;

	ls.stdout.on('data', function (data) {
		let out={}
		//reset flag
		hasErrored=false;
		console.log('stdout: ' + data);
		data=JSON.parse(data);

		if(data.error){
			hasErrored=true;
			out['error']=data.error;
			res.json(out);
			return;
		}

		out=data;
		ctx.emit('import',out);
	});

	ls.stderr.on('data', function (data) {
		let out={};
		console.log('stderr: ' + data);
		//slack notify
		slack_error(data);
		hasErrored=true;
		out['error']='Internal server error.';
		res.json(out);
	});

	ls.on('exit', function (code) {
		let out={}
		console.log('child process exited with code ' + code);
		if(code!=0){
			out['error']='Internal server error.';
			res.json(out);
			return;
		}
		//no output needed
		if(hasErrored){
			return;
		}

		out['complete']='Import was successful!';
		res.json(out);
		return;
	});
}
app.listen(config.app.port);

console.log('\n\n\n\n**********STARTING EXPRESS SERVER ON PORT '+config.app.port+'\n\n\n\n');


function is_empty(){
	for (var i = 0; i < arguments.length; i++) {
		if(typeof arguments[i]=='undefined'||arguments[i]==null||arguments[i].length==0){
			return true;
		}
	}
	return false;
}
function isset(){
	for (var i = 0; i < arguments.length; i++) {
		if(typeof arguments[i]=='undefined'){
			return false;
		}
	}
	return true;
}
function isJSON(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}