const jsoning = require("jsoning");
const db = new jsoning("database.json"); // Nó sẽ tạo file database.json tự động

module.exports = db;
