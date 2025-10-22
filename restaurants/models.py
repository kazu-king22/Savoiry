from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


STATUS_CHOICES = [
    ('want', '気になる'),
    ('went', '行った'),
]


class Tag(models.Model):
    CATEGORY_CHOICES = [
        ('genre', 'ジャンル'),
        ('area', 'エリア'),
        ('scene', 'シーン'),
        ('group', 'グループ'),
        ('custom', 'カスタム'),  
    ]

    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='custom')  


    def __str__(self):
        return self.name
    
class Restaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store_name=models.CharField(max_length=100)
    area = models.CharField(max_length=50)
    url = models.URLField(blank=True, null=True)
    genre = models.CharField(max_length=50)
    companions = models.CharField(max_length=50, blank=True, null=True)
    scene = models.CharField(max_length=50, blank=True, null=True)
    holiday = models.CharField(max_length=50, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='want', verbose_name='ステータス')

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.store_name
    
class Visit(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="visits")
    date = models.DateField(null=True, blank=True)
    comment = models.TextField(blank=True)
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        blank=True, null=True
    )
    feeling = models.CharField(
        max_length=20,
        choices=[
            ('again', 'また行きたい'),
            ('recommend', 'おすすめしたい'),
            ('no', 'もう行かない')
        ],
        blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant.store_name} ({self.date})"


class VisitImage(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='visit_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.visit.restaurant.store_name} ({self.visit.date})"



