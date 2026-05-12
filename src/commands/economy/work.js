const { SlashCommandBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('work')
        .setDescription('Làm việc chăm chỉ để kiếm tiền mua nhẫn'),

    async execute(ctx) {
        const cooldown = 3600000; // 1 giờ
        const lastWork = await db.get(`last_work_${ctx.user.id}`);

        if (lastWork && (Date.now() - lastWork) < cooldown) {
            const remaining = Math.ceil((cooldown - (Date.now() - lastWork)) / 60000);
            return ctx.reply(`⏳ Bạn đang kiệt sức! Hãy nghỉ ngơi thêm **${remaining} phút** nữa.`, 'error');
        }

        // Random tiền từ 500 đến 2000
        let amount = Math.floor(Math.random() * 1501) + 500;
        
        // Check Premium x2 lương
        const isPre = await db.get(`premium_${ctx.user.id}`);
        if (isPre) amount *= 2;

        const jobs = ['Lập trình viên cho Silo', 'Bán trà sữa', 'Shipper thân thiện', 'Quét rác server', 'Đào vàng thuê'];
        const job = jobs[Math.floor(Math.random() * jobs.length)];

        await db.add(`money_${ctx.user.id}`, amount);
        await db.set(`last_work_${ctx.user.id}`, Date.now());

        await ctx.reply(
            `💼 Bạn đã làm công việc: **${job}**\n` +
            `💰 Lương nhận được: \`${amount.toLocaleString()}$\` ${isPre ? '(💎 x2 Premium)' : ''}`,
            'success'
        );
    }
};
