const { ChannelType, PermissionFlagsBits } = require('discord.js');

/**
 * Hàm xử lý hybrid command (slash + prefix)
 * @param {Object} ctx - Interaction hoặc Message
 * @param {Function} executeFunc - Hàm xử lý chính
 */
async function executeHybrid(ctx, executeFunc) {
    try {
        // Determine context type
        const isSlash = ctx.isCommand?.() || ctx.isChatInputCommand?.();
        const isPrefix = ctx.isMessage?.() || typeof ctx.content === 'string';

        // Validate permissions if needed
        if (isPrefix && ctx.channel?.type === ChannelType.GuildText) {
            if (!ctx.guild.members.me?.permissions.has(PermissionFlagsBits.SendMessages)) {
                return await ctx.react('❌').catch(() => null);
            }
        }

        // Execute the command
        return await executeFunc(ctx, isSlash);
    } catch (error) {
        console.error('❌ Hybrid execution error:', error);
        
        if (ctx.deferred || ctx.replied) {
            await ctx.editReply({ 
                content: '❌ Có lỗi xảy ra. Vui lòng thử lại sau.', 
                ephemeral: true 
            }).catch(() => null);
        } else if (ctx.reply) {
            await ctx.reply({ 
                content: '❌ Có lỗi xảy ra. Vui lòng thử lại sau.', 
                ephemeral: true 
            }).catch(() => null);
        } else {
            await ctx.channel?.send({ 
                content: '❌ Có lỗi xảy ra. Vui lòng thử lại sau.' 
            }).catch(() => null);
        }
    }
}

/**
 * Nhận message argument từ prefix
 * @param {Message} message - Message object
 * @param {number} index - Chỉ số argument
 */
function getArg(message, index) {
    const args = message.content.split(/\s+/).slice(1);
    return args[index] || null;
}

/**
 * Nhận tất cả arguments từ prefix
 * @param {Message} message - Message object
 * @param {number} startIndex - Bắt đầu từ chỉ số nào
 */
function getAllArgs(message, startIndex = 1) {
    return message.content.split(/\s+/).slice(startIndex).join(' ');
}

module.exports = { executeHybrid, getArg, getAllArgs };
