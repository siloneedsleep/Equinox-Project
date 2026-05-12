const { SlashCommandBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('setpremium')
        .setDescription('Cấp quyền Premium cho người dùng (Chỉ Owner)')
        .addUserOption(opt => opt.setName('user').setRequired(true).setDescription('Người được cấp'))
        .addIntegerOption(opt => opt.setName('days').setRequired(true).setDescription('Số ngày cấp (0 để xóa)')),

    async execute(ctx, client) {
        if (ctx.user.id !== '914831312295165982') return ctx.reply('⛔ Bạn không có quyền này!', 'error');

        const target = ctx.options.getUser(0);
        const days = ctx.options.getString(1); // Lấy đối số thứ 2 (số ngày)

        if (parseInt(days) === 0) {
            await db.delete(`premium_${target.id}`);
            await db.delete(`premium_expire_${target.id}`);
            return ctx.reply(`✅ Đã gỡ quyền Premium của **${target.username}**.`, 'success');
        }

        const expireDate = Date.now() + (parseInt(days) * 24 * 60 * 60 * 1000);
        await db.set(`premium_${target.id}`, true);
        await db.set(`premium_expire_${target.id}`, expireDate);

        await ctx.reply(`💎 Đã cấp **Premium** cho **${target.username}** trong **${days} ngày**!\nHết hạn lúc: <t:${Math.floor(expireDate / 1000)}:F>`, 'success');
    }
};
