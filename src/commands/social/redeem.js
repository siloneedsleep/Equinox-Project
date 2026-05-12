const { SlashCommandBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('redeem')
        .setDescription('Nhập Key để kích hoạt Premium')
        .addStringOption(opt => opt.setName('key').setRequired(true).setDescription('Mã Key bạn nhận được')),

    async execute(ctx, client) {
        const keyInput = ctx.options.getString(0);
        const keyData = await db.get(`key_${keyInput}`);

        if (!keyData) return ctx.reply('❌ Key không tồn tại hoặc đã bị hủy!', 'error');

        // Kiểm tra xem key còn lượt dùng không
        if (keyData.currentUses >= keyData.maxUses) {
            return ctx.reply('❌ Key này đã hết lượt sử dụng!', 'error');
        }

        // Kiểm tra xem người này đã dùng key này chưa
        if (keyData.users.includes(ctx.user.id)) {
            return ctx.reply('⚠️ Bạn đã sử dụng mã Key này rồi!', 'error');
        }

        // --- CỘNG PREMIUM ---
        const now = Date.now();
        const currentExpire = await db.get(`premium_expire_${ctx.user.id}`) || now;
        
        // Nếu đang là Premium thì cộng dồn, nếu không thì lấy mốc hiện tại
        const startTime = currentExpire > now ? currentExpire : now;
        const newExpire = startTime + (keyData.days * 24 * 60 * 60 * 1000);

        await db.set(`premium_${ctx.user.id}`, true);
        await db.set(`premium_expire_${ctx.user.id}`, newExpire);

        // --- Cập nhật Key Data ---
        keyData.currentUses += 1;
        keyData.users.push(ctx.user.id);
        await db.set(`key_${keyInput}`, keyData);

        await ctx.reply(
            `💎 **KÍCH HOẠT THÀNH CÔNG!**\n\n` +
            `Bạn đã nhận được **${keyData.days} ngày** Premium.\n` +
            `📅 Hết hạn: <t:${Math.floor(newExpire / 1000)}:F>`, 
            'success'
        );
    }
};
