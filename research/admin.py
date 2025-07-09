from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Website, ChatUser, ChatMessage, IngestedFile


# ✅ Inline for Ingested Files
class IngestedFileInline(admin.TabularInline):
    model = IngestedFile
    extra = 0
    fields = ('file', 'url', 'uploaded_at', 'processed', 'process_button')
    readonly_fields = ('uploaded_at', 'processed', 'process_button')

    def process_button(self, obj):
        if not obj.id:
            return format_html('''
                <button type="submit" name="_continue" class="button">💾 Save Ingested Files</button>
            ''')
        if not obj.processed:
            url = reverse('process_ingestion', args=[obj.id])
            return format_html('<a class="button" href="{}">Process Now</a>', url)
        return "✅ Processed"

    process_button.short_description = "Process"


# ✅ Inline for Chat Messages inside ChatUser
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('prompt', 'response', 'timestamp')


# ✅ Main Website Admin with IngestedFile Inline + Bulk Upload Button
@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'api_key', 'created_at', 'embed_code_display')
    readonly_fields = ('created_at', 'api_key', 'embed_code_display', 'bulk_upload_link')
    fields = ('domain', 'api_key', 'created_at', 'embed_code_display', 'bulk_upload_link')
    inlines = [IngestedFileInline]

    def embed_code_display(self, obj):
        embed_code = f"""
<!-- Chatbot Embed Code -->
<div id="chatbot-container"></div>
<script>
  const CHATBOT_API_KEY = "{obj.api_key}";
  const CHATBOT_SERVER = "http://127.0.0.1:8000";  // Replace with your chatbot server URL

  const script = document.createElement('script');
  script.src = CHATBOT_SERVER + "/static/chatbot.js";
  script.onload = () => {{
    window.initChatbot(CHATBOT_API_KEY);
  }};
  document.body.appendChild(script);
</script>
"""
        return format_html(
            '<pre style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>',
            embed_code
        )
    embed_code_display.short_description = "Embed Code"

    def bulk_upload_link(self, obj):
        url = reverse('bulk_upload', args=[obj.id])
        return mark_safe(f'<a class="button" href="{url}">📂 Upload Multiple Files</a>')

    bulk_upload_link.short_description = "Bulk Upload"


# ✅ ChatUser Admin
@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company_name", "mobile_number", "website", "created_at", "view_messages_link")
    search_fields = ("name", "email", "company_name", "mobile_number")
    list_filter = ("website", "created_at")
    actions = ["delete_selected_users_and_messages"]
    inlines = [ChatMessageInline]

    def delete_selected_users_and_messages(self, request, queryset):
        for user in queryset:
            ChatMessage.objects.filter(user=user).delete()
            user.delete()
        self.message_user(request, "Selected users and their messages were deleted.")
    delete_selected_users_and_messages.short_description = "Delete selected users and their messages"

    def view_messages_link(self, obj):
        url = reverse("admin:research_chatmessage_changelist") + f"?user__id__exact={obj.id}"
        return format_html('<a href="{}">View Messages</a>', url)
    view_messages_link.short_description = "Messages"


# ✅ ChatMessage Admin
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "website", "prompt", "response", "timestamp")
    search_fields = ("prompt", "response", "user__name", "user__email")
    list_filter = ("website", "timestamp")
    actions = ["delete_selected"]
