const Context = require('../core/Context');
const chalk = require('chalk');

module.exports = {
    name: 'interactionCreate',
    once: false,
    async execute(interaction, client) {
        if (!interaction.isChatInputCommand()) return;

        const command = client.commands.get(interaction.commandName);

        if (!command) {
            console.error(chalk.yellow(`[WARNING] Không tìm thấy lệnh /${interaction.commandName}`));
            return;
        }

        const ctx = new Context(interaction, client);

        const args = []; 

        try {
            await command.execute(ctx, args);
        } catch (error) {
            console.error(chalk.red(`[COMMAND ERROR] Lỗi khi thực thi lệnh /${interaction.commandName} (Slash):`), error);
            
            const errorMsg = { content: '❌ Đã xảy ra lỗi hệ thống khi thực thi lệnh này. Sếp vui lòng kiểm tra lại log!', ephemeral: true };
            
            if (interaction.replied || interaction.deferred) {
                await interaction.followUp(errorMsg).catch(() => null);
            } else {
                await interaction.reply(errorMsg).catch(() => null);
            }
        }
    }
};
