const { Events } = require('discord.js');
const db = require('../database/db');
const { sendEmbed } = require('../utils/embedWrapper');

module.exports = {
    name: Events.MessageCreate,
    async execute(message, client) {
        if (message.author.bot || !message.guild) return;

        // --- TỰ ĐỘNG CHECK HẾT HẠN PREMIUM ---
        const isPremium = await db.get(`premium_${message.author.id}`);
        if (isPremium) {
            const expireDate = await db.get(`premium_expire_${message.author.id}`);
            if (expireDate && expireDate < Date.now()) {
                // Đã hết hạn -> Xóa quyền
                await db.delete(`premium_${message.author.id}`);
                await db.delete(`premium_expire_${message.author.id}`);
                
                // Thông báo nhẹ một cái cho người dùng biết
                await sendEmbed(message, '⌛ Quyền **Premium** của bạn đã hết hạn. Hãy nạp thêm key để tiếp tục sử dụng các đặc quyền!', 'info');
            }
        }

        // --- XỬ LÝ PREFIX ---
        const customPrefix = await db.get(`prefix_${message.guild.id}`) || process.env.PREFIX || 'k!';

        if (!message.content.startsWith(customPrefix)) return;

        const args = message.content.slice(customPrefix.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();

        const command = client.commands.get(commandName);
        if (!command) return;

        // --- GIẢ LẬP CONTEXT HYBRID ---
        const context = {
            message: message,
            channel: message.channel,
            guild: message.guild,
            user: message.author,
            member: message.member,
            reply: async (content, type) => await sendEmbed(message, content, type),
            options: {
                // Lấy string theo index (0, 1, 2...)
                getString: (index) => args[index] || null,
                // Lấy user từ mention hoặc từ ID trong args
                getUser: (index) => {
                    const mention = message.mentions.users.first();
                    if (mention) return mention;
                    // Nếu không mention thì thử tìm qua ID trong args
                    const id = args[index];
                    return id ? client.users.cache.get(id) : null;
                },
                // Thêm cái này để lấy số cho tiện
                getInteger: (index) => {
                    const val = parseInt(args[index]);
                    return isNaN(val) ? null : val;
                }
            }
        };

        try {
            await command.execute(context, client);
        } catch (error) {
            console.error(error);
            await sendEmbed(message, '❌ Đã xảy ra lỗi khi thực thi lệnh này!', 'error');
        }
    },
};
