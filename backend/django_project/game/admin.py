from django.contrib import admin
from .models import ArticleCache, DailyArticle, GlobalLeaderboard

@admin.register(ArticleCache)
class ArticleCacheAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_id', 'retrieved_date')
    search_fields = ('title', 'article_id')
    list_filter = ('retrieved_date',)

@admin.register(DailyArticle)
class DailyArticleAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_article_title', 'created_at')
    list_filter = ('date',)
    
    def get_article_title(self, obj):
        return obj.article.title if obj.article else "NO title"
    get_article_title.short_description = 'title'

@admin.register(GlobalLeaderboard)
class GlobalLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('date', 'last_updated')
    list_filter = ('date',)