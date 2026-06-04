const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
    // 1. DỮ LIỆU ĐẨY LÊN DISCORD API
    data: new SlashCommandBuilder()
        .setName('avatar')
        .setDescription('Soi ảnh đại diện của bạn hoặc người khác ở độ phân giải siêu nét (HD)')
        .addUserOption(option =>
            option.setName('target')
                .setDescription('Người mà bạn muốn soi avatar (Bỏ trống nếu muốn xem của chính mình)')
                .setRequired(false)), // Không bắt buộc, nếu trống thì tự lấy avatar của người gõ lệnh

    // 2. LÕI XỬ LÝ LỆNH
    async execute(interaction) {
        // Lấy đối tượng mục tiêu. Nếu không ai được tag, mặc định là người gõ lệnh (interaction.user)
        const targetUser = interaction.options.getUser('target') || interaction.user;

        // Trích xuất URL avatar ở chất lượng cao nhất (Size 4096)
        const avatarUrl = targetUser.displayAvatarURL({ size: 4096 });

        // Bọc vào Embed theo chuẩn quân đội
        const avatarEmbed = new EmbedBuilder()
            .setColor('#2b2d31') // Màu xám tàng hình chuẩn Discord
            .setTitle(`🖼️ Ảnh đại diện của ${targetUser.username}`)
            .setURL(avatarUrl) // Cho phép click vào tiêu đề để mở ảnh full trình duyệt
            .setImage(avatarUrl) // Phóng to ảnh vào giữa Embed
            .setFooter({ 
                text: `Yêu cầu bởi ${interaction.user.tag}`, 
                iconURL: interaction.user.displayAvatarURL() 
            })
            .setTimestamp();

        // Bắn kết quả lên khung chat
        await interaction.reply({ embeds: [avatarEmbed] });
    }
};
