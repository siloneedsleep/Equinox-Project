const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('profile')
        .setDescription('Xem hồ sơ cá nhân. (Soi người khác yêu cầu Premium)')
        .addUserOption(opt => opt.setName('user').setDescription('Người bạn muốn xem hồ sơ')),

    async execute(ctx, client) {
        const target = ctx.options.getUser(0) || ctx.user;
        
        // --- Check Quyền Soi ---
        if (target.id !== ctx.user.id) {
            const isPremium = await db.get(`premium_${ctx.user.id}`);
            const isOwner = ctx.user.id === '914831312295165982';
            
            if (!isPremium && !isOwner) {
                return ctx.reply('⚠️ Bạn cần nâng cấp lên **Premium** để soi hồ sơ người khác!', 'error');
            }
        }

        const money = await db.get(`money_${target.id}`) || 0;
        const bank = await db.get(`bank_${target.id}`) || 0;
        const partnerId = await db.get(`partner_${target.id}`);
        const marryDate = await db.get(`marry_date_${target.id}`);
        const familyExp = await db.get(`family_exp_${target.id}`) || 0;

        const partnerStatus = partnerId ? `<@${partnerId}>` : 'Đang tìm kiếm nửa kia...';
        const anniversary = marryDate ? `<t:${marryDate}:R>` : 'Chưa kết hôn';

        const embed = new EmbedBuilder()
            .setTitle(`🌟 HỒ SƠ CỦA ${target.username.toUpperCase()} 🌟`)
            .setThumbnail(target.displayAvatarURL({ dynamic: true }))
            .setColor(partnerId ? 0xff69b4 : 0x2b2d31)
            .addFields(
                { name: '💰 Tài Chính', value: `💵 Tiền mặt: \`${money.toLocaleString()}$\` \n✨ Tổng: \`${(money + bank).toLocaleString()}$\``, inline: false },
                { name: '💍 Hôn Nhân', value: `👤 Bạn đời: ${partnerStatus}\n⏳ Bên nhau: ${anniversary}`, inline: true },
                { name: '👨‍👩‍👧‍👦 Gia Đình', value: `📈 EXP: \`${familyExp}\``, inline: true }
            )
            .setTimestamp();

        if (await db.get(`premium_${target.id}`)) embed.setAuthor({ name: '💎 Người Dùng Premium' });
        if (target.id === '914831312295165982') embed.setAuthor({ name: '👑 Owner' });

        await ctx.reply({ embeds: [embed] });
    }
};
