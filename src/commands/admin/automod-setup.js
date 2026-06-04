const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const dataManager = require('../../utils/DataManager');

module.exports = {
    // 1. DỮ LIỆU ĐẨY LÊN DISCORD (Gồm lệnh chính và 4 lệnh con)
    data: new SlashCommandBuilder()
        .setName('automod-setup')
        .setDescription('Bảng điều khiển hệ thống AutoMod của Luminous (Chỉ Admin)')
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator) // Chỉ Admin mới dùng được
        
        // Lệnh con 1: Xem trạng thái
        .addSubcommand(subcommand =>
            subcommand.setName('status')
                .setDescription('Xem toàn bộ cấu hình AutoMod hiện tại của server')
        )
        // Lệnh con 2: Bật tắt các tính năng bằng True/False
        .addSubcommand(subcommand =>
            subcommand.setName('toggle')
                .setDescription('Bật/tắt các lõi bảo vệ')
                .addBooleanOption(option => option.setName('anti_spam').setDescription('Chống spam tin nhắn tốc độ cao'))
                .addBooleanOption(option => option.setName('anti_invite').setDescription('Chống gửi link mời server khác'))
        )
        // Lệnh con 3: Giới hạn Ping
        .addSubcommand(subcommand =>
            subcommand.setName('mention')
                .setDescription('Thiết lập giới hạn số người được ping trong 1 tin nhắn')
                .addIntegerOption(option => option.setName('limit').setDescription('Số lượng người tối đa').setRequired(true))
        )
        // Lệnh con 4: Quản lý từ điển cấm
        .addSubcommand(subcommand =>
            subcommand.setName('banned-word')
                .setDescription('Thêm hoặc gỡ bỏ từ khóa cấm trong server')
                .addStringOption(option => 
                    option.setName('action')
                        .setDescription('Bạn muốn làm gì?')
                        .setRequired(true)
                        .addChoices({ name: 'Thêm từ cấm', value: 'add' }, { name: 'Xóa từ cấm', value: 'remove' })
                )
                .addStringOption(option => option.setName('word').setDescription('Từ khóa cần xử lý').setRequired(true))
        ),

    // 2. LÕI XỬ LÝ LỆNH
    async execute(interaction) {
        // Đặt ephemeral: true để toàn bộ thông báo cài đặt này chỉ mình sếp đọc được
        await interaction.deferReply({ ephemeral: true });
        
        const guildId = interaction.guild.id;
        const subCommand = interaction.options.getSubcommand();

        // Kéo dữ liệu cấu hình hiện tại của server từ storage.json (nếu chưa có thì tự tạo default)
        let settings = await dataManager.get(`automod.guild_settings.${guildId}`, {
            anti_spam: true,
            anti_invite: true,
            anti_mention: 4,
            banned_words: []
        });

        // Tạo khung Embed mặc định cho các phản hồi
        const responseEmbed = new EmbedBuilder()
            .setColor('#2b2d31')
            .setTimestamp()
            .setFooter({ text: 'Luminous V15 - AutoMod Engine' });

        // Xử lý logic chia nhánh theo lệnh con mà sếp vừa chọn
        if (subCommand === 'status') {
            responseEmbed
                .setTitle('🛡️ BẢNG ĐIỀU KHIỂN AUTOMOD SERVER')
                .addFields(
                    { name: '⚡ Chống Spam (Tốc độ cao)', value: settings.anti_spam ? '🟢 Bật' : '🔴 Tắt', inline: true },
                    { name: '🔗 Chống Link Invite', value: settings.anti_invite ? '🟢 Bật' : '🔴 Tắt', inline: true },
                    { name: '🎯 Giới hạn Ping (Mass Mention)', value: `Tối đa **${settings.anti_mention}** người/tin nhắn`, inline: true },
                    { name: '🚫 Từ Điển Cấm', value: settings.banned_words.length > 0 ? `\`${settings.banned_words.join('\`, \`')}\`` : '*Chưa thiết lập từ cấm nào*' }
                );

        } else if (subCommand === 'toggle') {
            const spam = interaction.options.getBoolean('anti_spam');
            const invite = interaction.options.getBoolean('anti_invite');

            if (spam !== null) settings.anti_spam = spam;
            if (invite !== null) settings.anti_invite = invite;

            await dataManager.set(`automod.guild_settings.${guildId}`, settings);
            
            responseEmbed
                .setColor('#00ff00')
                .setTitle('✅ Cập Nhật Tính Năng Thành Công')
                .setDescription(`**Chống Spam:** ${settings.anti_spam ? '🟢 Bật' : '🔴 Tắt'}\n**Chống Link Invite:** ${settings.anti_invite ? '🟢 Bật' : '🔴 Tắt'}`);

        } else if (subCommand === 'mention') {
            const limit = interaction.options.getInteger('limit');
            settings.anti_mention = limit;
            
            await dataManager.set(`automod.guild_settings.${guildId}`, settings);
            
            responseEmbed
                .setColor('#00ff00')
                .setTitle('✅ Cập Nhật Giới Hạn Ping')
                .setDescription(`Đã thiết lập hệ thống trừng phạt nếu một người ping quá **${limit} người** trong cùng 1 tin nhắn.`);

        } else if (subCommand === 'banned-word') {
            const action = interaction.options.getString('action');
            const word = interaction.options.getString('word').toLowerCase().trim();

            if (action === 'add') {
                if (!settings.banned_words.includes(word)) settings.banned_words.push(word);
                responseEmbed.setColor('#00ff00').setTitle('✅ Đã Thêm Từ Cấm').setDescription(`Từ khóa **"${word}"** đã bị liệt vào danh sách đen.`);
            } else {
                settings.banned_words = settings.banned_words.filter(w => w !== word);
                responseEmbed.setColor('#00ff00').setTitle('✅ Đã Xóa Từ Cấm').setDescription(`Từ khóa **"${word}"** đã được gỡ khỏi danh sách đen.`);
            }
            
            await dataManager.set(`automod.guild_settings.${guildId}`, settings);
        }

        // Bắn Embed trả về cho sếp
        await interaction.followUp({ embeds: [responseEmbed] });
    }
};
