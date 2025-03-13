from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid


class UserProfile(models.Model):
    """
    Extension of the built-in Django User model for Wikipedle-specific user data.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    last_played_date = models.DateField(null=True, blank=True)
    total_games_played = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    best_score = models.IntegerField(default=0)
    
    # Notification preferences
    daily_reminder = models.BooleanField(default=True)
    friend_activity_notifications = models.BooleanField(default=True)
    
    # User interface preferences
    dark_mode = models.BooleanField(default=False)
    
    # Profile visibility
    public_profile = models.BooleanField(default=True)
    show_on_leaderboard = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def calculate_average_score(self):
        """Recalculate average score based on game history"""
        if self.total_games_played > 0:
            scores = DailyScore.objects.filter(user=self.user, completed=True)
            if scores.exists():
                self.average_score = scores.aggregate(models.Avg('score'))['score__avg']
                self.save()
        return self.average_score
    
    def update_streak(self, game_date):
        """Update user streak based on game date"""
        today = timezone.now().date()
        if self.last_played_date:
            # If last played was yesterday, increment streak
            if (today - self.last_played_date).days == 1:
                self.current_streak += 1
            # If more than one day gap, reset streak
            elif (today - self.last_played_date).days > 1:
                self.current_streak = 1
            # Same day - no change to streak
        else:
            # First time playing
            self.current_streak = 1
            
        # Update max streak if needed
        self.max_streak = max(self.max_streak, self.current_streak)
        self.last_played_date = today
        self.save()


class UserLoginHistory(models.Model):
    """Track user login history for security and analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "User login histories"
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class UserVerification(models.Model):
    """Store verification tokens for email confirmation, password reset, etc."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    purpose = models.CharField(max_length=20, choices=[
        ('email', 'Email Verification'),
        ('password', 'Password Reset'),
        ('invite', 'Friend Invitation'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "User verifications"
    
    def __str__(self):
        return f"{self.user.username} - {self.purpose} - {'Used' if self.is_used else 'Active'}"
    
    def is_valid(self):
        """Check if token is still valid"""
        now = timezone.now()
        return not self.is_used and now < self.expires_at


class UserDevice(models.Model):
    """Track user's devices for security and multi-device management"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.UUIDField(default=uuid.uuid4, editable=False)
    device_name = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, choices=[
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('mobile', 'Mobile'),
        ('other', 'Other'),
    ])
    last_login = models.DateTimeField(auto_now=True)
    is_trusted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "User devices"
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name or self.device_type}"


class DailyScore(models.Model):
    """Store user's daily game scores and statistics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    date = models.DateField()
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)  # in seconds
    guesses = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    article_title = models.CharField(max_length=255, blank=True)  # The title of the article they were guessing
    last_guess = models.CharField(max_length=255, blank=True)  # Their last guess
    hints_used = models.IntegerField(default=0)  # Number of hints used
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name_plural = "Daily scores"
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.score} points"
    
    def calculate_score(self):
        """Calculate score based on time taken, guesses, and hints used"""
        # Base score calculation
        base_score = 1000
        time_penalty = min(500, self.time_taken / 10)  # Penalty for time: max 500 points
        guess_penalty = min(300, self.guesses * 50)    # Penalty per guess: 50 points each, max 300
        hint_penalty = min(200, self.hints_used * 40)  # Penalty per hint: 40 points each, max 200
        
        # Calculate final score
        self.score = max(0, base_score - time_penalty - guess_penalty - hint_penalty)
        
        # No points if not completed
        if not self.completed:
            self.score = 0
            
        return self.score


# Signal to automatically create a UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for every new User automatically"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

# 添加到您现有的 models.py 文件末尾

class ArticleCache(models.Model):
    """Cache for Wikipedia articles to reduce API calls"""
    article_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_urls = models.JSONField(default=list, blank=True)
    retrieved_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Article caches"
    
    def __str__(self):
        return f"{self.title} ({self.article_id})"


class DailyArticle(models.Model):
    """Stores the article selected for each day's game"""
    date = models.DateField(unique=True)
    article = models.ForeignKey(ArticleCache, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Article for {self.date}: {self.article.title}"


class GlobalLeaderboard(models.Model):
    """Daily global leaderboard cache for performance"""
    date = models.DateField(unique=True)
    # Store top 100 scores as JSON to avoid excessive joins
    leaderboard_data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Leaderboard for {self.date}"
    
    def update_leaderboard(self):
        """Update the leaderboard data from daily scores"""
        # Get top scores from users who allow showing on leaderboard
        top_scores = DailyScore.objects.filter(
            date=self.date,
            completed=True,
            user__profile__show_on_leaderboard=True
        ).select_related('user__profile').order_by('-score')[:100]
        
        # Format data for frontend
        leaderboard = []
        for rank, score in enumerate(top_scores, 1):
            leaderboard.append({
                'rank': rank,
                'username': score.user.username,
                'score': score.score,
                'guesses': score.guesses,
                'time_taken': score.time_taken,
            })
        
        self.leaderboard_data = {
            'scores': leaderboard,
            'total_players': DailyScore.objects.filter(date=self.date).count(),
            'average_score': DailyScore.objects.filter(
                date=self.date, 
                completed=True
            ).aggregate(avg=models.Avg('score'))['avg'] or 0,
        }
        self.save()