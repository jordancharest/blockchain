const CryptoJS = require("crypto-js");

class Block {
    // constructor (duh), reserved by language definition
    constructor(data) {
        this.id = 0;
        this.nonce = 144445;
        this.body = data;
        this.hash = "";
    }
    
    // 
    generateHash() {
        // Use this to create a temporary reference of the class object, so that we can access it
        // (and return it) from inside the promise
        let self = this;

        let promise =  new Promise(function(resolve, reject) {
            // do a thing, possibly async, then…
            self.hash = CryptoJS.SHA256(JSON.stringify(self));

            // This can't really fail, but if it could we would return an error with "reject"
            if (true) {
                resolve(self);
            }
            else {
                reject(Error("Hash generation failed"));
            }
        });
        return promise;
    }
}

// Exporting the class Block to be reuse in other files
module.exports.Block = Block;
