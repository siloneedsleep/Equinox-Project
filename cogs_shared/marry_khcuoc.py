import os
import discord
from discord import app_commands
from discord.ext import commands
from database.redis_client import get_redis_connection
from config.settings import LUMINOUS_ID, TENEBRIS_ID

class MarrySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==============================================================================
    # 📑 LỆNH SLASH: CHECK MARRY (CHO PHÉP TẤT CẢ USER XEM TÌNH TRẠNG HÔN NHÂN)
    # ==============================================================================
    @app_commands.command(name="check-marry", description="Xem tình trạng hôn nhân của bạn hoặc của ai đó trong Server")
    @app_commands.describe(user="Người bạn muốn kiểm tra (Để trống nếu tự kiểm tra bản thân)")
    async def check_marry(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        r = await get_redis_connection()
        
        # 👑 TRƯỜNG HỢP ĐẶC BIỆT: CẶP ĐÔI CỐT TRUYỆN HỆ THỐNG (Luminous x Tenebris)
        if target_user.id in [LUMINOUS_ID, TENEBRIS_ID]:
            embed = discord.Embed(
                title="🔮 ĐỊNH MỆNH HOÀNG GIA - EQUINOX NETWORK ☀️",
                description="Mối liên kết vĩnh cửu giữa Ánh Sáng và Bóng Tối thống trị Thần Điện.",
                color=0xFFD700
            )
            embed.add_field(name="Vợ (Thần Điện Ca Ngày)", value=f"<@{LUMINOUS_ID}>", inline=True)
            embed.add_field(name="Chồng (Chợ Đen Ca Đêm)", value=f"<@{TENEBRIS_ID}>", inline=True)
            embed.add_field(name="Trạng thái", value="🔒 Hôn nhân vĩnh cửu (Cốt truyện Hệ thống)", inline=False)
            await interaction.response.send_message(embed=embed)
            return

        # 👥 TRƯỜNG HỢP USER THƯỜNG: Tra cứu từ Database Redis
        spouse_id_bytes = await r.get(f"equinox:marry:{target_user.id}")
        
        if not spouse_id_bytes:
            await interaction.response.send_message(
                f"❌ <@{target_user.id}> hiện tại vẫn đang độc thân vui tính, chưa kết hôn với ai cả!", 
                ephemeral=False
            )
            return

        spouse_id = spouse_id_bytes.decode('utf-8') if isinstance(spouse_id_bytes, bytes) else str(spouse_id_bytes)

        embed = discord.Embed(
            title="💖 GIẤY CHỨNG NHẬN HÔN NHÂN DÂN SỰ 💖",
            description="Thông tin dân sự được trích xuất từ văn phòng hộ tịch Equinox Network.",
            color=0xFFB6C1
        )
        embed.add_field(name="Người phối ngẫu 1", value=f"<@{target_user.id}>", inline=True)
        embed.add_field(name="Người phối ngẫu 2", value=f"<@{spouse_id}>", inline=True)
        embed.add_field(name="Tình trạng", value="💞 Đang trong mối quan hệ hôn nhân hợp pháp (chắc vậy).", inline=False)
        
        await interaction.response.send_message(embed=embed)

    # ==============================================================================
    # 💍 LỆNH SLASH: KẾT HÔN DÀNH CHO USER (MARRY)
    # ==============================================================================
    @app_commands.command(name="marry", description="Cầu hôn người thương của bạn để lập hôn thú")
    @app_commands.describe(user="Người phối ngẫu tương lai mà bạn muốn cầu hôn")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Bro không thể tự cưới chính mình được đâu, tỉnh lại đi! =))", ephemeral=True)
            return
            
        if user.bot:
            await interaction.response.send_message("❌ Bro thật sự thiếu thốn tình cảm đến mức đi cưới BOT ạ, lậy bố =))", ephemeral=True)
            return

        r = await get_redis_connection()
        
        # Check xem bản thân hoặc đối phương đã cưới ai chưa
        my_spouse = await r.get(f"equinox:marry:{interaction.user.id}")
        their_spouse = await r.get(f"equinox:marry:{user.id}")
        
        if my_spouse:
            await interaction.response.send_message("❌ Ông đã kết hôn rồi, chung thủy tí đi đừng đi ngoại tình! =))", ephemeral=True)
            return
        if their_spouse:
            await interaction.response.send_message(f"❌ Người ta là hoa đã có chủ rồi, <@{user.id}> đã kết hôn với người khác!", ephemeral=True)
            return

        # Tạo nút bấm để đối phương xác nhận đồng ý kết hôn
        class MarryConsent(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.value = None

            @discord.ui.button(label="Đồng Ý Đeo Nhẫn 💍", style=discord.ButtonStyle.success)
            async def confirm(self, inter: discord.Interaction, button: discord.ui.Button):
                if inter.user.id != user.id:
                    await inter.response.send_message("❌ Lệnh này dành cho người được cầu hôn bấm cơ mà!", ephemeral=True)
                    return
                self.value = True
                self.stop()

            @discord.ui.button(label="Từ Chối 💔", style=discord.ButtonStyle.danger)
            async def cancel(self, inter: discord.Interaction, button: discord.ui.Button):
                if inter.user.id != user.id:
                    await inter.response.send_message("❌ Kệ người ta từ chối đi ông gõ lệnh đừng bấm bậy bạ!", ephemeral=True)
                    return
                self.value = False
                self.stop()

        view = MarryConsent()
        await interaction.response.send_message(
            f"🔔 <@{user.id}> ơi! Bạn nhận được một lời cầu hôn lãng mạn từ <@{interaction.user.id}>. Bạn có đồng ý bước vào lễ đường không?", 
            view=view
        )
        
        await view.wait()
        
        if view.value is None:
            await interaction.edit_original_response(content="⏰ Hết thời gian chờ đợi phản hồi... Lời cầu hôn đã trôi vào dĩ vãng.", view=None)
        elif view.value:
            # Lưu hai chiều vào Redis vĩnh viễn
            await r.set(f"equinox:marry:{interaction.user.id}", str(user.id))
            await r.set(f"equinox:marry:{user.id}", str(interaction.user.id))
            
            embed = discord.Embed(
                title="🎉 ĐÁM CƯỚI THẾ KỶ CHÍNH THỨC DIỄN RA! 🎉",
                description=f"Chúc mừng hai bạn <@{interaction.user.id}> và <@{user.id}> đã chính thức thuộc về nhau vĩnh viễn trên hệ thống Equinox Network! 💞",
                color=0xFF69B4
            )
            await interaction.channel.send(embed=embed)
            await interaction.edit_original_response(content="❤️ Hôn lễ hoàn tất!", view=None)
        else:
            await interaction.edit_original_response(content=f"💔 Đau lòng quá... <@{user.id}> đã tàn nhẫn từ chối lời cầu hôn của ông rồi!", view=None)

    # ==============================================================================
    # 💔 LỆNH SLASH: LY HÔN (DIVORCE)
    # ==============================================================================
    @app_commands.command(name="divorce", description="Cắt đứt mối quan hệ hôn nhân hiện tại của bạn")
    async def divorce(self, interaction: discord.Interaction):
        r = await get_redis_connection()
        spouse_id_bytes = await r.get(f"equinox:marry:{interaction.user.id}")
        
        if not spouse_id_bytes:
            await interaction.response.send_message("❌ Ông đang độc thân chổng mông lên thì ly hôn với ai? =))", ephemeral=True)
            return
            
        spouse_id = spouse_id_bytes.decode('utf-8') if isinstance(spouse_id_bytes, bytes) else str(spouse_id_bytes)
        
        if int(spouse_id) in [LUMINOUS_ID, TENEBRIS_ID]:
            await interaction.response.send_message("❌ Đây là hôn nhân cốt truyện hệ thống tối cao, ông không có quyền can thiệp ly hôn đâu nha!", ephemeral=True)
            return

        # Xóa dữ liệu hai chiều trên Redis
        await r.delete(f"equinox:marry:{interaction.user.id}")
        await r.delete(f"equinox:marry:{spouse_id}")
        
        await interaction.response.send_message(f"💔 Đường tình đôi ngả... <@{interaction.user.id}> đã chính thức ký giấy ly hôn, giải phóng tự do cho cả hai và <@{spouse_id}>!")

async def setup(bot):
    await bot.add_cog(MarrySystem(bot))
