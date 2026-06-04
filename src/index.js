require('dotenv').config(); // Nạp tệp bảo mật .env chứa TOKEN
const fs = require('fs');
const path = require('path');
const { Client, GatewayIntentBits, Collection, ActivityType } = require('discord.js');

// Khởi tạo Client với các đặc quyền (Intents) tối thượng để đọc tin nhắn và quản lý server
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent, // Bắt buộc phải có để AutoMod đọc được nội dung chat
        GatewayIntentBits.GuildMembers
    ]
});

// Tạo một bộ nhớ chứa toàn bộ Slash Commands
client.commands = new Collection();

// ---------------------------------------------------------
// 1. BỘ QUÉT VÀ NẠP SỰ KIỆN (EVENTS LOADER)
// ---------------------------------------------------------
const eventsPath = path.join(__dirname, 'events');
const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

for (const file of eventFiles) {
    const filePath = path.join(eventsPath, file);
    const event = require(filePath);
    
    // Cắm tệp sự kiện vào Client
    if (event.once) {
        client.once(event.name, (...args) => event.execute(...args));
    } else {
        client.on(event.name, (...args) => event.execute(...args));
    }
    console.log(`[Trạm Sự Kiện] Đã nạp thành công: ${file}`);
}

// ---------------------------------------------------------
// 2. BỘ QUÉT VÀ NẠP LỆNH (COMMANDS LOADER)
// ---------------------------------------------------------
const commandsPath = path.join(__dirname, 'commands');

// Kiểm tra xem thư mục commands đã tồn tại chưa để tránh lỗi crash
if (fs.existsSync(commandsPath)) {
    const commandFolders = fs.readdirSync(commandsPath);
    for (const folder of commandFolders) {
        const commandsSubPath = path.join(commandsPath, folder);
        
        // Bỏ qua nếu không phải là thư mục (để sếp tha hồ chia nhánh admin, general...)
        if (fs.statSync(commandsSubPath).isDirectory()) {
            const commandFiles = fs.readdirSync(commandsSubPath).filter(file => file.endsWith('.js'));
            for (const file of commandFiles) {
                const filePath = path.join(commandsSubPath, file);
                const command = require(filePath);
                
                // Kiểm tra tính hợp lệ của file lệnh
                if ('data' in command && 'execute' in command) {
                    client.commands.set(command.data.name, command);
                    console.log(`[Kho Lệnh] Đã nạp thành công lệnh: /${command.data.name}`);
                } else {
                    console.log(`[CẢNH BÁO] Lệnh tại ${filePath} bị thiếu thuộc tính 'data' hoặc 'execute'.`);
                }
            }
        }
    }
} else {
    console.log(`[Hệ Thống] Thư mục commands chưa tồn tại. Vui lòng tạo thư mục src/commands/ để chứa lệnh.`);
}

// ---------------------------------------------------------
// 3. KÍCH NỔ ĐẦU NÃO
// ---------------------------------------------------------
client.once('ready', () => {
    console.log(`\n==============================================`);
    console.log(`✅ [LUMINOUS CORE V15] TẤT CẢ HỆ THỐNG ĐÃ ONLINE!`);
    console.log(`🤖 Đăng nhập thành công dưới danh tính: ${client.user.tag}`);
    console.log(`==============================================\n`);
    
    // Set Status sương sương cho ngầu
    client.user.setPresence({
        activities: [{ name: 'Luminous V15 System', type: ActivityType.Watching }],
        status: 'dnd', // Trạng thái Do Not Disturb (Đỏ) cho nguy hiểm
    });
});

// Cắm điện bằng TOKEN (Lấy từ .env)
client.login(process.env.TOKEN);
