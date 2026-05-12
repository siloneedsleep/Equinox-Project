const { SlashCommandBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('daily')
        .setDescription('Nhận trợ cấp hàng ngày'),

    async execute(ctx) {
        const cooldown = 86400000; // 24 giờ
        const lastDaily = await db.get(`last_daily_${ctx.user.id}`);

        if (lastDaily && (Date.now() - lastDaily) < cooldown) {
            const nextDaily = lastDaily + cooldown;
            return ctx.reply(`🎁 Bạn đã nhận quà rồi! Quay lại sau <t:${Math.floor(nextDaily / 1000)}:R> nhé.`, 'error');
        }

        let prize = 5000;
        const isPre = await db.get(`premium_${ctx.user.id}`);
        if (isPre) prize += 5000; // Thưởng thêm cho đại gia

        await db.add(`money_${ctx.user.id}`, prize);
        await db.set(`last_daily_${ctx.user.id}`, Date.now());

        await ctx.reply(
            `🎁 Bạn đã nhận được quà điểm danh: \`${prize.toLocaleString()}$\` \n` +
            `${isPre ? '💎 Bonus Premium: +5,000$ đã cộng vào ví!' : '💡 Nâng cấp Premium để nhận gấp đôi quà mỗi ngày!'}`,
            'success'
        );
    }
};
