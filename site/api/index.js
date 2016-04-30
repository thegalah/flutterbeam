'use strict';

let config=require('config');
let fs    = require("fs");
let express = require('express');
let bodyParser = require('body-parser');
let multer  = require('multer');
let upload = multer({ dest: config.app.upload_dir });
let mmm = require('mmmagic'),
 Magic = mmm.Magic;
let magic = new Magic(mmm.MAGIC_MIME_TYPE);

let spawn = require('child_process').spawn

let exec = require('child_process').exec,
	child;
let app = express();
app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies


app.put('/upload', upload.single('picture_file'), function(req, res) {
	console.log('--------/uploadPicture\n\n\n\n\n');
	var out={}

	console.log(req.file);
    //check existence of file
    if(is_empty(req.file)){
		out['error']='No image uploaded.';
		res.json(out);
		return;
    }

    //run flutter
    attachListeners(res,req.file.filename);
    return;
});
app.get('/flutters/:filename', function(req, res){
	var filename=req.params.filename;
	var file=config.app.output_dir+filename;
	var out={};


	fs.readFile(file, function (err,data){
		if(err){
			out['error']='File does not exist.';
			res.json(out);
			return;
		}
		magic.detectFile(file, function(err, result) {
			if (err) throw err;
			// output on Windows with 32-bit node:
			//    application/x-dosexec; charset=binary
			res.contentType(result);
			res.send(data);
			return;
		});
	});
});


function attachListeners(res,filename){

    let path_to_input=config.flutter.uploads+filename;
    let path_to_output=config.flutter.output+filename;

	let hasErrored=false;
	let ls = spawn('python', [config.app.path_to_flutter,path_to_input, path_to_output, config.app.path_to_moustache]);

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
		res.json(out);
	});

	ls.stderr.on('data', function (data) {
		let out={};
		console.log('stderr: ' + data);
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

		out['filename']=filename;
		res.json(out);
		//update gallery.txt


		fs.appendFile(config.app.path_to_gallery, filename+'\n', function (err) {
		});


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