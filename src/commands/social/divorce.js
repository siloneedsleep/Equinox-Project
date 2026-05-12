const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('divorce')
        .setDescription('Ly hôn với người hiện tại'),

    async execute(ctx, client) {
        const author = ctx.user;
        const partnerId = await db.get(`partner_${author.id}`);

        if (!partnerId) return ctx.reply('⚠️ Bạn đang độc thân mà, ly hôn ai?', 'error');

        // Check xem có đang bị ban kết hôn không
        const banUntil = await db.get(`marry_ban_${author.id}`);
        if (banUntil && banUntil > Date.now()) {
            return ctx.reply(`⚠️ Bạn đang bị cấm kết hôn cho đến <t:${Math.floor(banUntil / 1000)}:R>!`, 'error');
        }

        // Đếm số lần đòi ly hôn
        const requestCount = (await db.get(`divorce_req_${author.id}_${partnerId}`)) || 0;

        // Nếu đã đòi đủ 3 lần -> Cho phép đơn phương
        if (requestCount >= 3) {
            await db.delete(`partner_${author.id}`);
            await db.delete(`partner_${partnerId}`);
            await db.delete(`divorce_req_${author.id}_${partnerId}`);
            
            // Phạt: Cấm kết hôn 3 ngày
            const banTime = Date.now() + (3 * 24 * 60 * 60 * 1000);
            await db.set(`marry_ban_${author.id}`, banTime);

            return ctx.reply(`⚡ **LY HÔN ĐƠN PHƯƠNG!** Sau 3 lần nỗ lực không thành, bạn đã được tự do. \n🚫 Hình phạt: Bạn bị cấm kết hôn trong 3 ngày tới.`, 'success');
        }

        // Nếu chưa đủ 3 lần -> Gửi yêu cầu thuận tình
        const row = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('divorce_yes').setLabel('Đồng ý chia tay').setStyle(ButtonStyle.Danger),
            new ButtonBuilder().setCustomId('divorce_no').setLabel('Không! Em vẫn còn yêu').setStyle(ButtonStyle.Secondary)
        );

        const msg = await ctx.channel.send({
            content: `💔 <@${partnerId}> ơi, **${author.username}** muốn ly hôn với bạn. (Lần thứ ${requestCount + 1}/3)`,
            components: [row]
        });

        const filter = i => i.user.id === partnerId;
        const collector = msg.createMessageComponentCollector({ filter, time: 30000 });

        collector.on('collect', async i => {
            if (i.customId === 'divorce_yes') {
                await db.delete(`partner_${author.id}`);
                await db.delete(`partner_${partnerId}`);
                await i.update({ content: '🥀 Cuộc hôn nhân đã kết thúc trong êm đẹp. Cả hai đã trở lại độc thân.', components: [] });
            } else {
                await db.add(`divorce_req_${author.id}_${partnerId}`, 1);
                await i.update({ content: `🚫 <@${partnerId}> đã từ chối ly hôn. Lần đòi thứ ${requestCount + 1} đã được ghi nhận!`, components: [] });
            }
        });
    }
};
