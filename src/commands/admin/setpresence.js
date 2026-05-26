const { SlashCommandBuilder } = require('discord.js');
const LuminousEmbed = require('../../utils/EmbedBuilder');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('setpresence')
        .setDescription('Thay đổi chấm trạng thái hiển thị của bot (Chỉ dành cho Owner)')
        .addStringOption(option => 
            option.setName('status')
                .setDescription('Chọn trạng thái bạn muốn đặt')
                .setRequired(true)
                .addChoices(
                    { name: '🟢 Online (Trực tuyến)', value: 'online' },
                    { name: '🟡 Idle (Chờ/Vắng mặt)', value: 'idle' },
                    { name: '🔴 DND (Không làm phiền)', value: 'dnd' },
                    { name: '⚪ Invisible (Ẩn danh/Ngoại tuyến)', value: 'invisible' }
                )
        ),
    async execute(ctx, args) {
        // Bảo mật quyền Owner
        const ownerId = '914831312295165982';

        if (ctx.user.id !== ownerId) {
            return await ctx.reply({ embeds: [LuminousEmbed.error('Lệnh này chỉ dành cho Owner của bot!')] });
        }

        let statusToSet;

        if (ctx.isSlash) {
            statusToSet = ctx.interaction.options.getString('status');
        } else {
            // Hỗ trợ lệnh prefix: l!setpresence <online/idle/dnd/invisible> hoặc l!sp <...>
            if (args.length < 1) {
                return await ctx.reply({ 
                    embeds: [LuminousEmbed.error('Vui lòng nhập trạng thái cần đổi!\nCú pháp: `l!setpresence <online | idle | dnd | invisible>`')] 
                });
            }
            
            const input = args[0].toLowerCase();
            
            // Chuẩn hóa input từ lệnh chat
            if (['online', '🟢'].includes(input)) statusToSet = 'online';
            else if (['idle', 'away', 'chờ', '🟡'].includes(input)) statusToSet = 'idle';
            else if (['dnd', 'do-not-disturb', '🔴'].includes(input)) statusToSet = 'dnd';
            else if (['invisible', 'offline', '⚪'].includes(input)) statusToSet = 'invisible';
            else {
                return await ctx.reply({ 
                    embeds: [LuminousEmbed.error('Trạng thái không hợp lệ! Hãy chọn: `online`, `idle`, `dnd`, hoặc `invisible`.')] 
                });
            }
        }

        await ctx.deferReply();

        try {
            // Giữ nguyên nội dung hoạt động cũ, chỉ đổi chấm màu hiển thị
            const currentActivities = ctx.client.user.presence?.activities || [];
            
            ctx.client.user.setPresence({
                status: statusToSet,
                activities: currentActivities
            });

            // Định dạng lại tên hiển thị trên Embed thông báo thành công
            const statusNames = {
                online: '🟢 Trực tuyến (Online)',
                idle: '🟡 Chờ/Vắng mặt (Idle)',
                dnd: '🔴 Không làm phiền (DND)',
                invisible: '⚪ Ẩn danh (Invisible)'
            };

            const embed = LuminousEmbed.success(`Đã cập nhật chấm trạng thái của bot thành: **${statusNames[statusToSet]}**`);
            await ctx.reply({ embeds: [embed] });

        } catch (error) {
            console.error(error);
            await ctx.reply({ embeds: [LuminousEmbed.error('Đã xảy ra lỗi khi cố gắng cập nhật trạng thái của bot.')] });
        }
    }
};
