// Require file system access
fs = require('fs');

// Read file buffer 
imgReadBuffer = fs.readFileSync('img2hex.js');


// Encode image buffer to hex
imgHexEncode = new Buffer(imgReadBuffer).toString('hex');

// Output encoded data to console
console.log(imgHexEncode);


// Decode hex
var imgHexDecode = new Buffer(imgHexEncode, 'hex');

// Save decoded file file system 
fs.writeFileSync('decodedimg2hex.js', imgHexDecode);
