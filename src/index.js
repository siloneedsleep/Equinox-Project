require('dotenv').config();
const { Client, GatewayIntentBits, Collection, ChannelType } = require('discord.js');
const fs = require('fs');
const path = require('path');
const db = require('./database/db');
const { joinVoiceChannel } = require('@discordjs/voice');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildVoiceStates // QUAN TRỌNG: Để treo room 24/7
    ]
});

// Khởi tạo các Collection
client.commands = new Collection();
client.ownerId = process.env.OWNER_ID || '914831312295165982';

// --- Caching để tối ưu hosting ---
const commandCache = new Map();
const eventCache = new Set();

// --- Handler nạp lệnh ---
const foldersPath = path.join(__dirname, 'commands');
if (fs.existsSync(foldersPath)) {
    const commandFolders = fs.readdirSync(foldersPath);
    for (const folder of commandFolders) {
        const commandsPath = path.join(foldersPath, folder);
        if (!fs.existsSync(commandsPath)) continue;
        
        const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
        for (const file of commandFiles) {
            try {
                const filePath = path.join(commandsPath, file);
                const command = require(filePath);
                
                if ('data' in command && 'execute' in command) {
                    client.commands.set(command.data.name, command);
                    commandCache.set(command.data.name, { folder, file });
                }
            } catch (error) {
                console.error(`❌ Lỗi khi nạp lệnh ${file}:`, error);
            }
        }
    }
}

console.log(`✅ Đã nạp ${client.commands.size} lệnh`);

// --- Handler nạp Event ---
const eventsPath = path.join(__dirname, 'events');
if (fs.existsSync(eventsPath)) {
    const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));
    for (const file of eventFiles) {
        try {
            const filePath = path.join(eventsPath, file);
            const event = require(filePath);
            
            if (event.name && event.execute) {
                if (event.once) {
                    client.once(event.name, (...args) => event.execute(...args, client));
                } else {
                    client.on(event.name, (...args) => event.execute(...args, client));
                }
                eventCache.add(event.name);
            }
        } catch (error) {
            console.error(`❌ Lỗi khi nạp event ${file}:`, error);
        }
    }
}

console.log(`✅ Đã nạp ${eventCache.size} events`);

// --- Logic Tự Động Reconnect Voice 24/7 khi Bot Restart ---
client.once('ready', async () => {
    console.log(`✅ ${client.user.tag} đã sẵn sàng!`);
    console.log(`📊 Kết nối ${client.guilds.cache.size} server`);
    
    // Quét tất cả server để xem room nào cần treo 24/7 (với timeout)
    const reconnectPromises = client.guilds.cache.map(async (guild) => {
        try {
            // Timeout cho DB query
            const stayChannelId = await Promise.race([
                db.get(`stay_vc_${guild.id}`),
                new Promise((_, reject) => setTimeout(() => reject(new Error('DB timeout')), 5000))
            ]).catch(() => null);

            if (!stayChannelId) return;

            const channel = guild.channels.cache.get(stayChannelId);
            if (!channel || channel.type !== ChannelType.GuildVoice) {
                console.warn(`⚠️ Channel ${stayChannelId} không tồn tại hoặc không phải voice channel`);
                return;
            }

            try {
                joinVoiceChannel({
                    channelId: channel.id,
                    guildId: guild.id,
                    adapterCreator: guild.voiceAdapterCreator,
                    selfDeaf: true,
                    selfMute: true
                });
                console.log(`🎙️ Đã kết nối lại Voice 24/7 tại server: ${guild.name}`);
            } catch (voiceError) {
                console.error(`❌ Lỗi reconnect voice tại ${guild.name}:`, voiceError.message);
            }
        } catch (error) {
            console.error(`❌ Lỗi xử lý reconnect voice cho guild ${guild.id}:`, error);
        }
    });

    // Chạy tất cả reconnect song song nhưng có timeout chung
    await Promise.all(reconnectPromises).catch(err => {
        console.error('❌ Lỗi trong quá trình reconnect voice:', err);
    });
});

// --- Global Error Handler ---
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
    // Optional: Restart bot hoặc ghi log
});

// --- Safe Login ---
client.login(process.env.TOKEN).catch(error => {
    console.error('❌ Không thể login:', error);
    process.exit(1);
});

module.exports = client;
