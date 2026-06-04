const { EmbedBuilder } = require('discord.js');
const autoMod = require('../utils/AutoMod');
const aiEngine = require('../utils/AIEngine');
const levelSystem = require('../utils/LevelSystem'); // 👈 Nạp lõi cày cấp

module.exports = {
    name: 'messageCreate',
    once: false,
    async execute(message) {
        const client = message.client;

        if (message.author.bot || !message.guild) return;

        // 1. TRẠM KIỂM SOÁT AUTOMOD
        const isViolated = await autoMod.processMessage(message);
        if (isViolated) return; 

        // 2. KÍCH HOẠT LÕI CÀY CẤP (Cộng XP cho dân chơi hệ lương thiện)
        // AutoMod tha cho thì mới được cộng điểm nha
        await levelSystem.processXp(message);

        // 3. BỘ KÍCH HOẠT LÕI AI
        if (message.mentions.has(client.user)) {
            const userQuestion = message.content.replace(`<@${client.user.id}>`, '').trim();

            if (!userQuestion) {
                const pingEmbed = new EmbedBuilder()
                    .setColor('#2b2d31')
                    .setAuthor({ name: 'Luminous V15 - Core System', iconURL: client.user.displayAvatarURL() })
                    .setDescription(`Xin chào ${message.author}! Tui là Luminous. Đang đợi lệnh từ sếp!\n⚡ Gõ câu hỏi của bạn sau khi tag tôi, hoặc dùng dấu \`/\` để xem các lệnh hệ thống.`)
                    .setFooter({ text: 'Developed by Silo' });
                return message.reply({ embeds: [pingEmbed] });
            }

            await message.channel.sendTyping();
            const aiResponse = await aiEngine.generateResponse(message.author.id, userQuestion);

            const aiEmbed = new EmbedBuilder()
                .setColor('#2b2d31')
                .setAuthor({ name: 'Luminous AI', iconURL: client.user.displayAvatarURL() })
                .setDescription(aiResponse)
                .setFooter({ text: `Powered by Gemini AI • Giao tiếp với ${message.author.username}` })
                .setTimestamp();

            return message.reply({ embeds: [aiEmbed] });
        }
    }
};
