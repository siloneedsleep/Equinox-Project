const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const db = require('../../database/db');
const { rings } = require('../../utils/items');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('profile')
        .setDescription('Xem ví tiền, ngân hàng và tình trạng hôn nhân'),

    async execute(ctx) {
        const target = ctx.options.getUser(0) || ctx.user;
        
        // Check Premium khi soi người khác
        if (target.id !== ctx.user.id) {
            const isPre = await db.get(`premium_${ctx.user.id}`);
            if (!isPre && ctx.user.id !== '914831312295165982') {
                return ctx.reply('⚠️ Soi ví người khác cần có **Premium**!', 'error');
            }
        }

        // --- Lấy toàn bộ dữ liệu tài chính ---
        const cash = await db.get(`money_${target.id}`) || 0;
        const bank = await db.get(`bank_${target.id}`) || 0;
        const total = cash + bank;

        // --- Lấy dữ liệu hôn nhân ---
        const partnerId = await db.get(`partner_${target.id}`);
        const ringId = await db.get(`couple_ring_${target.id}`);
        const ringInfo = rings.find(r => r.id === ringId);

        const embed = new EmbedBuilder()
            .setTitle(`🌟 HỒ SƠ: ${target.username.toUpperCase()} 🌟`)
            .setThumbnail(target.displayAvatarURL({ dynamic: true }))
            .setColor(ringInfo ? ringInfo.color : 0x2b2d31)
            .addFields(
                { 
                    name: '💰 TÀI CHÍNH', 
                    value: `💵 Ví: \`${cash.toLocaleString()}$\` \n🏦 Bank: \`${bank.toLocaleString()}$\` \n📊 Tổng: \`${total.toLocaleString()}$\``, 
                    inline: false 
                },
                { 
                    name: '💍 HÔN NHÂN', 
                    value: partnerId ? `👤 Bạn đời: <@${partnerId}>\n✨ Nhẫn: ${ringInfo ? `${ringInfo.emoji} ${ringInfo.name}` : 'Không có'}` : 'Chủ nghĩa độc thân', 
                    inline: true 
                }
            )
            .setFooter({ text: `Luminous Economy • 2026` })
            .setTimestamp();

        // Icon đặc biệt cho đại gia hoặc Owner
        if (target.id === '914831312295165982') {
            embed.setAuthor({ name: '👑 Vua Vibe Coding (Silo)', iconURL: target.displayAvatarURL() });
        } else if (await db.get(`premium_${target.id}`)) {
            embed.setAuthor({ name: '💎 Hội Viên Premium', iconURL: target.displayAvatarURL() });
        }

        await ctx.reply({ embeds: [embed] });
    }
};
