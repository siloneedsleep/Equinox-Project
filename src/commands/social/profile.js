const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const db = require('../../database/db');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('profile')
        .setDescription('Xem hồ sơ cá nhân, tài sản và hôn nhân của bạn hoặc người khác')
        .addUserOption(opt => opt.setName('user').setDescription('Người bạn muốn xem hồ sơ')),

    async execute(ctx, client) {
        const target = ctx.options.getUser(0) || ctx.user;
        
        // --- Lấy dữ liệu từ Database ---
        const money = await db.get(`money_${target.id}`) || 0;
        const bank = await db.get(`bank_${target.id}`) || 0;
        const partnerId = await db.get(`partner_${target.id}`);
        const marryDate = await db.get(`marry_date_${target.id}`);
        const familyExp = await db.get(`family_exp_${target.id}`) || 0;

        // --- Xử lý logic hiển thị ---
        const partnerStatus = partnerId ? `<@${partnerId}>` : 'Đang tìm kiếm nửa kia...';
        const anniversary = marryDate ? `<t:${marryDate}:R>` : 'Chưa kết hôn';
        const totalWealth = money + bank;

        // --- Thiết kế Embed hoành tráng ---
        const embed = new EmbedBuilder()
            .setTitle(`🌟 HỒ SƠ CỦA ${target.username.toUpperCase()} 🌟`)
            .setThumbnail(target.displayAvatarURL({ dynamic: true, size: 512 }))
            .setColor(partnerId ? 0xff69b4 : 0x2b2d31) // Hồng nếu đã cưới, xám nếu độc thân
            .addFields(
                { name: '💰 Tài Chính', value: `💵 Tiền mặt: \`${money.toLocaleString()}$\` \n💳 Ngân hàng: \`${bank.toLocaleString()}$\` \n✨ Tổng: \`${totalWealth.toLocaleString()}$\``, inline: false },
                { name: '💍 Hôn Nhân', value: `👤 Bạn đời: ${partnerStatus}\n⏳ Bên nhau: ${anniversary}`, inline: true },
                { name: '👨‍👩‍👧‍👦 Gia Đình', value: `📈 EXP: \`${familyExp}\` \n🏆 Rank: \`Thành viên\``, inline: true }
            )
            .setFooter({ text: `ID: ${target.id}` })
            .setTimestamp();

        // Nếu là Owner (Silo), thêm cái huy hiệu cho oai
        if (target.id === '914831312295165982') {
            embed.setAuthor({ name: '👑 Vua Vibe Coding (Owner)', iconURL: client.user.displayAvatarURL() });
        }

        await ctx.reply({ embeds: [embed] });
    }
};
