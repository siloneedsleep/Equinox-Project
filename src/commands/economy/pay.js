const { SlashCommandBuilder } = require('discord.js');
const LuminousEmbed = require('../../utils/EmbedBuilder');
const db = require('../../database/JsonManager');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('pay')
        .setDescription('Chuyển Star cho người dùng khác')
        .addUserOption(option => 
            option.setName('target')
                .setDescription('Người nhận Star')
                .setRequired(true)
        )
        .addIntegerOption(option => 
            option.setName('amount')
                .setDescription('Số Star muốn chuyển')
                .setRequired(true)
        ),
    async execute(ctx, args) {
        let targetUser;
        let amount;

        if (ctx.isSlash) {
            targetUser = ctx.interaction.options.getUser('target');
            amount = ctx.interaction.options.getInteger('amount');
        } else {
            if (args.length < 2) {
                return await ctx.reply({ embeds: [LuminousEmbed.error('Bạn vui lòng tag người nhận và nhập số Star! Cú pháp: `l!pay @user 100`')] });
            }
            targetUser = ctx.message.mentions.users.first();
            amount = parseInt(args[1]);

            if (!targetUser) {
                return await ctx.reply({ embeds: [LuminousEmbed.error('Không tìm thấy người dùng bạn đã tag!')] });
            }
        }

        if (isNaN(amount) || amount <= 0) {
            return await ctx.reply({ embeds: [LuminousEmbed.error('Số Star cần chuyển phải là một con số hợp lệ và lớn hơn 0!')] });
        }

        if (targetUser.id === ctx.user.id) {
            return await ctx.reply({ embeds: [LuminousEmbed.error('Bạn không thể tự chuyển Star cho chính mình!')] });
        }

        if (targetUser.bot) {
            return await ctx.reply({ embeds: [LuminousEmbed.error('Bạn không thể chuyển Star cho Bot!')] });
        }

        await ctx.deferReply();

        const senderId = ctx.user.id;
        const receiverId = targetUser.id;
        
        const senderKey = `balance_${senderId}`;
        const receiverKey = `balance_${receiverId}`;

        const senderBalance = await db.get(senderKey, 0);

        if (senderBalance < amount) {
            return await ctx.reply({ embeds: [LuminousEmbed.error(`Bạn không có đủ Star để thực hiện giao dịch này! Số dư hiện tại của bạn là **${senderBalance}** Star.`)] });
        }

        const receiverBalance = await db.get(receiverKey, 0);

        await db.set(senderKey, senderBalance - amount);
        await db.set(receiverKey, receiverBalance + amount);

        const embed = LuminousEmbed.success(
            `Giao dịch thành công!\nBạn đã chuyển **${amount}** Star cho **${targetUser.username}**.`
        );

        await ctx.reply({ embeds: [embed] });
    }
};
