class CommandContext {
    /**
     * Khởi tạo một Context để đồng bộ cả Lệnh Slash và Lệnh Prefix
     * @param {object} data Interaction hoặc Message
     * @param {boolean} isSlash Xác định xem đây có phải là lệnh Slash hay không
     */
    constructor(data, isSlash = false) {
        this.isSlash = isSlash;
        
        if (isSlash) {
            this.interaction = data;
            this.client = data.client;
        } else {
            this.message = data;
            this.client = data.client;
        }
    }

    /**
     * Lấy thông tin người dùng thực hiện lệnh
     */
    get user() {
        return this.isSlash ? this.interaction.user : this.message.author;
    }

    /**
     * Trì hoãn phản hồi để bot có thời gian xử lý (tránh lỗi Timeout)
     */
    async deferReply() {
        if (this.isSlash) {
            if (!this.interaction.deferred && !this.interaction.replied) {
                await this.interaction.deferReply();
            }
        } else {
            await this.message.channel.sendTyping();
        }
    }

    /**
     * Phản hồi lại người dùng
     * @param {object|string} content Nội dung phản hồi (có thể là chuỗi hoặc đối tượng chứa embeds)
     */
    async reply(content) {
        if (this.isSlash) {
            if (this.interaction.deferred) {
                return await this.interaction.editReply(content);
            } else if (this.interaction.replied) {
                return await this.interaction.followUp(content);
            } else {
                return await this.interaction.reply(content);
            }
        } else {
            return await this.message.reply(content);
        }
    }
}

module.exports = CommandContext;
