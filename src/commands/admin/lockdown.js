const { SlashCommandBuilder, PermissionFlagsBits, ChannelType } = require('discord.js');
const LuminousEmbed = require('../../utils/EmbedBuilder');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('lockdown')
        .setDescription('Đóng băng/Mở khóa kênh hoặc toàn bộ server (Chỉ dành cho Owner)')
        .addStringOption(option => 
            option.setName('action')
                .setDescription('Chọn hành động: Khóa hoặc Mở khóa')
                .setRequired(true)
                .addChoices(
                    { name: '🔒 Lock (Khóa)', value: 'lock' },
                    { name: '🔓 Unlock (Mở khóa)', value: 'unlock' }
                )
        )
        .addStringOption(option => 
            option.setName('scope')
                .setDescription('Phạm vi ảnh hưởng')
                .setRequired(true)
                .addChoices(
                    { name: '📺 Chỉ kênh này (Current Channel)', value: 'channel' },
                    { name: '🌐 Toàn bộ Server (All Channels)', value: 'server' }
                )
        ),
    async execute(ctx, args) {
        // Chỉ cho phép Owner tối cao thực thi
        const ownerId = '914831312295165982';
        if (ctx.user.id !== ownerId) {
            return await ctx.reply({ embeds: [LuminousEmbed.error('Bạn không có quyền sử dụng lệnh tối mật này!')] });
        }

        let action, scope;

        if (ctx.isSlash) {
            action = ctx.interaction.options.getString('action');
            scope = ctx.interaction.options.getString('scope');
        } else {
            // Cú pháp prefix: l!lockdown <lock/unlock> <channel/server>
            if (args.length < 2) {
                return await ctx.reply({ 
                    embeds: [LuminousEmbed.error('Cú pháp: `l!lockdown <lock | unlock> <channel | server>`\nVí dụ: `l!lockdown lock server`')] 
                });
            }
            action = args[0].toLowerCase();
            scope = args[1].toLowerCase();

            if (!['lock', 'unlock'].includes(action) || !['channel', 'server'].includes(scope)) {
                return await ctx.reply({ embeds: [LuminousEmbed.error('Đối số không hợp lệ! Vui lòng kiểm tra lại cú pháp.')] });
            }
        }

        await ctx.deferReply();

        const guild = ctx.isSlash ? ctx.interaction.guild : ctx.message.guild;
        const everyoneRole = guild.roles.everyone;
        
        // Xác định quyền gửi tin nhắn dựa theo hành động (null nghĩa là reset về mặc định)
        const sendPermission = action === 'lock' ? false : null; 

        try {
            if (scope === 'channel') {
                // Khóa/Mở khóa kênh hiện tại
                const currentChannel = ctx.isSlash ? ctx.interaction.channel : ctx.message.channel;
                
                await currentChannel.permissionOverwrites.edit(everyoneRole, {
                    SendMessages: sendPermission
                });

                const embed = LuminousEmbed.info(
                    action === 'lock' ? '🔒 Kênh Đã Bị Khóa' : '🔓 Kênh Đã Mở Khóa',
                    action === 'lock' 
                        ? `Kênh ${currentChannel} đã chuyển sang chế độ **Chỉ đọc** đối với thành viên thông thường.`
                        : `Kênh ${currentChannel} đã được mở khóa. Thành viên có thể chat lại bình thường.`
                );
                return await ctx.reply({ embeds: [embed] });

            } else if (scope === 'server') {
                // Khóa/Mở khóa toàn bộ kênh Text trong server
                const channels = guild.channels.cache.filter(ch => ch.type === ChannelType.GuildText);
                let count = 0;

                for (const [id, channel] of channels) {
                    try {
                        await channel.permissionOverwrites.edit(everyoneRole, {
                            SendMessages: sendPermission
                        });
                        count++;
                    } catch (err) {
                        // Bỏ qua nếu bot thiếu quyền sửa một kênh ẩn cụ thể nào đó
                        continue;
                    }
                }

                const embed = LuminousEmbed.info(
                    action === 'lock' ? '🚨 ĐÃ KÍCH HOẠT LOCKDOWN TOÀN SERVER' : '🔓 ĐÃ GỠ BỎ LOCKDOWN SERVER',
                    action === 'lock'
                        ? `Hệ thống đã đóng băng thành công **${count}** kênh văn bản. Mọi thành viên thông thường không thể chat lúc này!`
                        : `Hệ thống đã mở khóa lại **${count}** kênh văn bản. Server trở lại hoạt động bình thường.`
                );
                return await ctx.reply({ embeds: [embed] });
            }

        } catch (error) {
            console.error(error);
            await ctx.reply({ embeds: [LuminousEmbed.error('Có lỗi xảy ra khi thiết lập quyền hạn kênh. Hãy chắc chắn rằng Role của Bot nằm cao hơn các Role khác!')] });
        }
    }
};
