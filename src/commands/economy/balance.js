const { SlashCommandBuilder } = require('discord.js');
const LuminousEmbed = require('../../utils/EmbedBuilder');
const db = require('../../database/JsonManager');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('balance')
        .setDescription('Xem số dư tài khoản của bạn hoặc người khác')
        .addUserOption(option => 
            option.setName('target')
                .setDescription('Người dùng bạn muốn xem số dư')
                .setRequired(false)
        ),
    async execute(ctx, args) {
        let targetUser;

        if (ctx.isSlash) {
            targetUser = ctx.interaction.options.getUser('target') || ctx.user;
        } else {
            targetUser = ctx.message.mentions.users.first() || ctx.user;
        }

        await ctx.deferReply();

        const dbKey = `balance_${targetUser.id}`;
        const balance = await db.get(dbKey, 0);

        const embed = LuminousEmbed.info(
            '💰 Số dư tài khoản',
            `Người dùng **${targetUser.username}** hiện đang có **${balance}** coin trong ví.`
        );

        await ctx.reply({ embeds: [embed] });
    }
};
