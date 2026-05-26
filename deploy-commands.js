const { REST, Routes } = require('discord.js');
const fs = require('fs');
const path = require('path');
require('dotenv').config(); // Nếu bạn dùng file .env

const commands = [];
const foldersPath = path.join(__dirname, 'src/commands');
const commandFolders = fs.readdirSync(foldersPath);

for (const folder of commandFolders) {
    const commandsPath = path.join(foldersPath, folder);
    const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
    for (const file of commandFiles) {
        const filePath = path.join(commandsPath, file);
        const command = require(filePath);
        if ('data' in command && 'execute' in command) {
            commands.push(command.data.toJSON());
        }
    }
}

const rest = new REST().setToken(process.env.TOKEN || 'TOKEN_BOT_CỦA_BẠN');

(async () => {
    try {
        console.log(`🔄 Đang đăng ký ${commands.length} lệnh Slash...`);
        // Đăng ký Toàn cầu (Global)
        await rest.put(
            Routes.applicationCommands('ID_BOT_CỦA_BẠN'),
            { body: commands },
        );
        console.log('✅ Đã đồng bộ tất cả lệnh Slash lên Discord thành công!');
    } catch (error) {
        console.error(error);
    }
})();
