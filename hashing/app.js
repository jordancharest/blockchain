const CryptoJS = require("crypto-js");
const BlockClass = require('./block.js');


console.log("Testing using the crypto js library")
// Use the crypto JS library
const data1 = "Blockchain Rock!";
const dataObject = {
	id: 1,
  	body: "With Object Works too",
  	time: new Date().getTime().toString().slice(0,-3)
};

// typical javascript comment that apparently is useful if you use an IDE
/**
 * Function that generate the SHA256 Hash
 * @param {*} obj 
 */
function generateHash(obj) {
    return CryptoJS.SHA256(JSON.stringify(obj));
}

console.log(`SHA256 Hash: ${generateHash(data1)}`);
console.log("************************************");
console.log(`SHA256 Hash: ${generateHash(dataObject)}`);







// Use a JS class and a promise
console.log("\n\nTesting javascript classes and promises")
const block = new BlockClass.Block("Test Block");

// Generating the block hash
block.generateHash().then((result) => {
    console.log(`Block Hash: ${result.hash}`);
    console.log(`Block: ${JSON.stringify(result)}`);
}).catch((error) => {console.log(error)});
