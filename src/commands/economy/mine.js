const { SlashCommandBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('mine')
        .setDescription('Đi đào mỏ để kiếm đá quý và tiền!'),

    async execute(ctx, client) {
        // Cooldown đơn giản (giả định 10 giây để tránh spam)
        const lastMine = await db.get(`last_mine_${ctx.user.id}`);
        const cooldown = 10000; // 10 giây

        if (lastMine !== null && cooldown - (Date.now() - lastMine) > 0) {
            const timeLeft = Math.ceil((cooldown - (Date.now() - lastMine)) / 1000);
            return ctx.reply(`⏳ Bạn đang mệt, hãy đợi thêm **${timeLeft}s** để tiếp tục đào!`, 'error');
        }

        // Tỉ lệ phần thưởng
        const rewards = [
            { name: 'Đá cuội', price: 10, chance: 50 },
            { name: 'Sắt', price: 50, chance: 30 },
            { name: 'Vàng', price: 200, chance: 15 },
            { name: 'Kim cương', price: 1000, chance: 5 }
        ];

        // Thuật toán chọn phần thưởng dựa trên tỉ lệ
        const random = Math.floor(Math.random() * 100);
        let selectedReward = rewards[0];
        let cumulativeChance = 0;

        for (const reward of rewards) {
            cumulativeChance += reward.chance;
            if (random < cumulativeChance) {
                selectedReward = reward;
                break;
            }
        }

        // Cập nhật tiền và thời gian đào vào DB
        await db.add(`money_${ctx.user.id}`, selectedReward.price);
        await db.set(`last_mine_${ctx.user.id}`, Date.now());

        // Lấy tổng số tiền hiện tại
        const totalMoney = await db.get(`money_${ctx.user.id}`);

        // Phản hồi bọc Embed cực nghệ
        await ctx.reply(
            `⛏️ **${ctx.user.username}** đã đi vào hang động...\n\n` +
            `✨ Bạn đã đào được: **${selectedReward.name}**\n` +
            `💰 Giá trị: \`+${selectedReward.price}$\` \n` +
            `💳 Tài khoản hiện tại: \`${totalMoney}$\``,
            'success'
        );
    }
};
