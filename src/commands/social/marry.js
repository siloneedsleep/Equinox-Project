const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('marry')
        .setDescription('Cầu hôn một người mà bạn yêu thương')
        .addUserOption(opt => opt.setName('user').setRequired(true).setDescription('Người bạn muốn cưới')),

    async execute(ctx, client) {
        const author = ctx.user;
        const target = ctx.options.getUser(0);

        // Kiểm tra điều kiện "vô tri"
        if (target.id === author.id) return ctx.reply('⚠️ Bạn không thể tự cưới chính mình!', 'error');
        if (target.bot) return ctx.reply('⚠️ Bạn không thể cưới một con bot!', 'error');

        // Kiểm tra xem đã kết hôn chưa
        const authorPartner = await db.get(`partner_${author.id}`);
        if (authorPartner) return ctx.reply('⚠️ Bạn đã kết hôn rồi, đừng tham lam!', 'error');

        const targetPartner = await db.get(`partner_${target.id}`);
        if (targetPartner) return ctx.reply(`⚠️ **${target.username}** đã là hoa có chủ rồi!`, 'error');

        // Tạo nút xác nhận (Chỉ dùng được với Interaction hoặc Message có Button)
        // Lưu ý: Nếu là Prefix Command, nút bấm vẫn hoạt động nếu được xử lý đúng ở event interactionCreate
        const row = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('marry_accept').setLabel('Đồng ý').setStyle(ButtonStyle.Success),
            new ButtonBuilder().setCustomId('marry_deny').setLabel('Từ chối').setStyle(ButtonStyle.Danger)
        );

        const response = await ctx.channel.send({
            content: `💍 **${target}**, bạn có đồng ý kết hôn với **${author.username}** không?`,
            components: [row]
        });

        // Bộ lọc: Chỉ người được cầu hôn mới được bấm nút
        const filter = i => i.user.id === target.id;
        const collector = response.createMessageComponentCollector({ filter, time: 30000 });

        collector.on('collect', async i => {
            if (i.customId === 'marry_accept') {
                await db.set(`partner_${author.id}`, target.id);
                await db.set(`partner_${target.id}`, author.id);
                await db.set(`marry_date_${author.id}`, Date.now());

                await i.update({ content: `🎉 **${author.username}** và **${target.username}** đã chính thức về chung một nhà!`, components: [] });
            } else {
                await i.update({ content: `💔 **${target.username}** đã từ chối lời cầu hôn của **${author.username}**.`, components: [] });
            }
        });

        collector.on('end', collected => {
            if (collected.size === 0) response.edit({ content: '⏳ Lời cầu hôn đã hết hạn do không có phản hồi.', components: [] });
        });
    }
};
