const { SlashCommandBuilder } = require('discord.js');
const GeminiService = require('../../services/GeminiService');
const LuminousEmbed = require('../../utils/EmbedBuilder');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('gemini')
        .setDescription('Trò chuyện với AI Gemini siêu tốc')
        .addStringOption(option => 
            option.setName('prompt')
                .setDescription('Nội dung bạn muốn hỏi AI')
                .setRequired(true)
        ),
    async execute(ctx, args) {
        let prompt = '';
        
        if (ctx.isSlash) {
            prompt = ctx.interaction.options.getString('prompt');
        } else {
            prompt = args.join(' ');
        }

        if (!prompt) {
            return await ctx.reply({ embeds: [LuminousEmbed.error('Bạn vui lòng nhập nội dung cần hỏi!')] });
        }

        await ctx.deferReply();

        const response = await GeminiService.generateResponse(prompt);

        const textToSend = response.length > 2000 ? response.slice(0, 1997) + '...' : response;

        await ctx.reply(textToSend);
    }
};
