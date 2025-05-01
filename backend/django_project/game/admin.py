from django.contrib import admin
from .models import UserProfile, DailyScore, ArticleCache, DailyArticle, GlobalLeaderboard

admin.site.register(UserProfile)
admin.site.register(DailyScore)


@admin.register(ArticleCache)
class ArticleCacheAdmin(admin.ModelAdmin):
    list_display = ("title", "article_id", "retrieved_date")
    search_fields = ("title", "article_id")
    list_filter = ("retrieved_date",)


@admin.register(DailyArticle)
class DailyArticleAdmin(admin.ModelAdmin):
    list_display = ("date", "article__title", "created_at")
    list_filter = ("date",)


@admin.register(GlobalLeaderboard)
class GlobalLeaderboardAdmin(admin.ModelAdmin):
    list_display = ("date", "last_updated")
    list_filter = ("date",)
