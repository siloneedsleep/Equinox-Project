const Jsoning = require('jsoning');
const path = require('path');
const fs = require('fs');

class JsonManager {
    constructor() {
        const dbPath = path.join(__dirname, '../../database');
        if (!fs.existsSync(dbPath)) {
            fs.mkdirSync(dbPath, { recursive: true });
        }
        this.db = new Jsoning(path.join(dbPath, 'luminous_data.json'));
    }

    async get(key, defaultValue = null) {
        try {
            const data = await this.db.get(key);
            return data !== undefined ? data : defaultValue;
        } catch (error) {
            console.error(`[DB ERROR] Lỗi khi lấy key ${key}:`, error);
            return defaultValue;
        }
    }

    async set(key, value) {
        try {
            await this.db.set(key, value);
            return true;
        } catch (error) {
            console.error(`[DB ERROR] Lỗi khi ghi key ${key}:`, error);
            return false;
        }
    }

    async delete(key) {
        try {
            await this.db.delete(key);
            return true;
        } catch (error) {
            console.error(`[DB ERROR] Lỗi khi xóa key ${key}:`, error);
            return false;
        }
    }

    async push(key, value) {
        try {
            await this.db.push(key, value);
            return true;
        } catch (error) {
            console.error(`[DB ERROR] Lỗi khi push vào key ${key}:`, error);
            return false;
        }
    }
}

module.exports = new JsonManager();
